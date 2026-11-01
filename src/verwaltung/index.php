<?php
/**
 * Terminverwaltung für die Praxis.
 * Anmeldung ohne Passwort: Ein 6-stelliger Code wird an die Praxis-E-Mail-Adresse geschickt.
 */

declare(strict_types=1);
require __DIR__ . '/../api/lib/booking.php';

header('X-Robots-Tag: noindex, nofollow');
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

$secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
session_name('schick_verwaltung');
session_set_cookie_params(['lifetime' => 0, 'path' => '/verwaltung/', 'secure' => $secure, 'httponly' => true, 'samesite' => 'Strict']);
session_start();

$c = cfg();
$flash = '';
$error = '';

if (empty($_SESSION['csrf'])) {
    $_SESSION['csrf'] = bin2hex(random_bytes(16));
}
$csrf = $_SESSION['csrf'];
$isPost = $_SERVER['REQUEST_METHOD'] === 'POST';
if ($isPost && !hash_equals($csrf, (string) ($_POST['csrf'] ?? ''))) {
    $error = 'Sitzung abgelaufen. Bitte erneut versuchen.';
    $isPost = false;
}

$loggedIn = !empty($_SESSION['auth']) && ($_SESSION['auth'] > time());
$do = $_POST['do'] ?? '';

/* ---------------- Anmeldung per E-Mail-Code ---------------- */
function login_file(): string
{
    return data_dir() . '/login.json';
}

if (!$loggedIn && $isPost && $do === 'send_code') {
    $state = is_file(login_file()) ? (json_decode((string) file_get_contents(login_file()), true) ?: []) : [];
    if (($state['sent'] ?? 0) > time() - 60) {
        $error = 'Bitte warten Sie eine Minute, bevor Sie einen neuen Code anfordern.';
    } else {
        $code = (string) random_int(100000, 999999);
        $state = ['hash' => password_hash($code, PASSWORD_DEFAULT), 'exp' => time() + 900, 'sent' => time(), 'tries' => 0];
        file_put_contents(login_file(), json_encode($state));
        @chmod(login_file(), 0600);
        $ok = send_mail($c['email'], "Anmeldecode Terminverwaltung: $code",
            "Ihr Anmeldecode für die Terminverwaltung lautet:\n\n    $code\n\nDer Code ist 15 Minuten gültig.\n"
            . "Falls Sie keinen Code angefordert haben, können Sie diese E-Mail ignorieren.\n");
        $_SESSION['code_sent'] = true;
        $flash = $ok ? 'Der Code wurde an ' . $c['email'] . ' gesendet.' : 'Die E-Mail konnte nicht gesendet werden. Bitte prüfen Sie, ob das Postfach bei Hostinger eingerichtet ist.';
    }
}

if (!$loggedIn && $isPost && $do === 'check_code') {
    $state = is_file(login_file()) ? (json_decode((string) file_get_contents(login_file()), true) ?: []) : [];
    $code = preg_replace('/\D/', '', (string) ($_POST['code'] ?? ''));
    if (!$state || $state['exp'] < time() || $state['tries'] >= 5) {
        $error = 'Der Code ist abgelaufen. Bitte fordern Sie einen neuen an.';
        @unlink(login_file());
    } elseif (password_verify($code, $state['hash'])) {
        @unlink(login_file());
        session_regenerate_id(true);
        $_SESSION['auth'] = time() + 12 * 3600;
        $_SESSION['csrf'] = bin2hex(random_bytes(16));
        header('Location: ./');
        exit;
    } else {
        $state['tries']++;
        file_put_contents(login_file(), json_encode($state));
        $error = 'Der Code ist nicht korrekt.';
        $_SESSION['code_sent'] = true;
    }
}

if ($loggedIn && $isPost && $do === 'logout') {
    $_SESSION = [];
    session_destroy();
    header('Location: ./');
    exit;
}

/* ---------------- Aktionen (angemeldet) ---------------- */
if ($loggedIn && $isPost) {
    if ($do === 'cancel') {
        $id = (string) ($_POST['id'] ?? '');
        $notify = !empty($_POST['notify']);
        $b = with_store(function (array &$store) use ($id) {
            foreach ($store['bookings'] as &$bk) {
                if ($bk['id'] === $id && $bk['status'] === 'gebucht') {
                    $bk['status'] = 'abgesagt';
                    $bk['cancelled'] = date('c') . ' (Praxis)';
                    return $bk;
                }
            }
            return null;
        });
        if ($b) {
            $flash = 'Termin von ' . $b['name'] . ' am ' . date_de($b['date'], $b['time']) . ' wurde abgesagt. Der Termin ist wieder frei.';
            if ($notify) {
                send_mail($b['email'], 'Absage Ihres Termins am ' . date_de($b['date'], $b['time']),
                    "Guten Tag {$b['name']},\n\nleider muss ich Ihren Termin am " . date_de($b['date'], $b['time']) . " absagen. "
                    . "Bitte buchen Sie gern einen neuen Termin: " . site_url('termin-buchen/') . "\n\nIch bitte um Ihr Verständnis.\n\n"
                    . "Herzliche Grüße\n{$c['owner']} – {$c['practice']}\n{$c['email']}\n", $c['email']);
                $flash .= ' Die Patientin bzw. der Patient wurde per E-Mail informiert.';
            }
        }
    }
    if ($do === 'block') {
        $date = (string) ($_POST['date'] ?? '');
        $whole = !empty($_POST['whole']);
        $from = (string) ($_POST['from'] ?? '');
        $to = (string) ($_POST['to'] ?? '');
        $note = trim(mb_substr((string) ($_POST['note'] ?? ''), 0, 120));
        if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
            $error = 'Bitte ein Datum wählen.';
        } elseif (!$whole && (!preg_match('/^\d{2}:\d{2}$/', $from) || !preg_match('/^\d{2}:\d{2}$/', $to) || $from >= $to)) {
            $error = 'Bitte eine gültige Uhrzeit von–bis angeben oder „ganzer Tag“ wählen.';
        } else {
            with_store(function (array &$store) use ($date, $whole, $from, $to, $note) {
                $store['blocks'][] = ['id' => bin2hex(random_bytes(6)), 'date' => $date, 'from' => $whole ? '' : $from, 'to' => $whole ? '' : $to, 'note' => $note];
            });
            $flash = 'Zeitraum gesperrt: ' . date_de($date) . ($whole ? ' (ganzer Tag)' : " $from–$to Uhr") . '.';
        }
    }
    if ($do === 'unblock') {
        $id = (string) ($_POST['id'] ?? '');
        with_store(function (array &$store) use ($id) {
            $store['blocks'] = array_values(array_filter($store['blocks'], fn($b) => $b['id'] !== $id));
        });
        $flash = 'Sperre aufgehoben.';
    }
    if ($flash || $error) {
        $_SESSION['flash'] = [$flash, $error];
        header('Location: ./');
        exit;
    }
}
if (!empty($_SESSION['flash'])) {
    [$flash, $error] = $_SESSION['flash'];
    unset($_SESSION['flash']);
}

/* ---------------- Ausgabe ---------------- */
$store = $loggedIn ? with_store(function (array &$s) {
    cleanup_store($s);
    return $s;
}) : null;

?><!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Terminverwaltung | <?= h($c['brand']) ?></title>
<link rel="stylesheet" href="/assets/css/style.css">
<style>
  .admin-table { width: 100%; border-collapse: collapse; font-size: .95rem; }
  .admin-table th, .admin-table td { text-align: left; padding: 10px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
  .admin-table th { font: 500 .72rem/1.3 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--bronze-dark); }
  .admin-day { margin: 26px 0 8px; font-size: 1.5rem; }
  .tag { display: inline-block; padding: 2px 10px; border-radius: 999px; background: rgba(207,221,225,.6); color: var(--teal); font-size: .8rem; }
  .tag.off { background: #f3e1dc; color: #8a3b2b; }
  .msg { padding: 14px 18px; border-radius: 12px; margin-bottom: 18px; }
  .msg.ok { background: #e3f0e6; color: #24563a; }
  .msg.err { background: #f6e1dc; color: #8a3b2b; }
  .inline { display: inline; }
  .admin-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
  @media (max-width: 760px) { .admin-table thead { display: none; } .admin-table td { display: block; border: 0; padding: 4px 0; } .admin-table tr { display: block; padding: 12px 0; border-bottom: 1px solid var(--line); } }
</style>
</head>
<body>
<div class="water-bg" aria-hidden="true"></div>
<main class="section-sm">
<div class="container">
  <div class="admin-head">
    <p class="brand"><img class="brand-logo" src="/assets/img/logo-dr-schick.svg" width="3675" height="1389" alt="Dr. Schick"><svg class="brand-sub" viewBox="0 0 1000 78" aria-hidden="true" focusable="false"><defs><linearGradient id="gold-sub-v" x1="0" y1="0" x2="1" y2="0.4"><stop offset="0" stop-color="#5e3f1a"/><stop offset=".35" stop-color="#82633d"/><stop offset=".5" stop-color="#a8875a"/><stop offset=".65" stop-color="#82633d"/><stop offset="1" stop-color="#5e3f1a"/></linearGradient></defs><text x="500" y="62" text-anchor="middle" textLength="860" lengthAdjust="spacing" font-family="Jost, Helvetica Neue, Arial, sans-serif" font-size="64" font-weight="500" fill="url(#gold-sub-v)">MEDICAL AESTHETICS</text></svg></p>
    <?php if ($loggedIn): ?>
      <form method="post" class="inline"><input type="hidden" name="csrf" value="<?= h($csrf) ?>"><button class="btn btn-ghost btn-sm" name="do" value="logout">Abmelden</button></form>
    <?php endif; ?>
  </div>
  <?php if ($flash): ?><p class="msg ok"><?= h($flash) ?></p><?php endif; ?>
  <?php if ($error): ?><p class="msg err"><?= h($error) ?></p><?php endif; ?>

<?php if (!$loggedIn): ?>
  <div class="glass panel narrow" style="margin:30px auto 0">
    <h1 style="font-size:2.2rem">Anmelden</h1>
    <p>Zur Anmeldung wird ein Code an <strong><?= h($c['email']) ?></strong> gesendet.</p>
    <form method="post" class="form" style="margin-bottom:22px">
      <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
      <button class="btn" name="do" value="send_code">Anmeldecode per E-Mail senden</button>
    </form>
    <?php if (!empty($_SESSION['code_sent'])): ?>
    <form method="post" class="form">
      <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
      <div><label for="code">Code aus der E-Mail</label><input id="code" name="code" type="text" inputmode="numeric" autocomplete="one-time-code" maxlength="6" required></div>
      <div><button class="btn" name="do" value="check_code">Anmelden</button></div>
    </form>
    <?php endif; ?>
  </div>
<?php else:
    $today = date('Y-m-d');
    $upcoming = array_filter($store['bookings'], fn($b) => $b['date'] >= $today);
    usort($upcoming, fn($a, $b) => strcmp($a['date'] . $a['time'], $b['date'] . $b['time']));
    $active = array_filter($upcoming, fn($b) => $b['status'] === 'gebucht');
    $blocks = $store['blocks'];
    usort($blocks, fn($a, $b) => strcmp($a['date'] . $a['from'], $b['date'] . $b['from']));
?>
  <h1 style="font-size:2.4rem;margin-top:10px">Kommende Termine <span class="tag"><?= count($active) ?> gebucht</span></h1>
  <div class="glass panel">
    <?php if (!$upcoming): ?>
      <p class="muted">Aktuell sind keine Termine gebucht.</p>
    <?php else:
        $lastDay = '';
        foreach ($upcoming as $b):
            if ($b['date'] !== $lastDay):
                if ($lastDay !== '') echo '</tbody></table>';
                $lastDay = $b['date']; ?>
      <h2 class="admin-day"><?= h(date_de($b['date'])) ?></h2>
      <table class="admin-table"><thead><tr><th>Uhrzeit</th><th>Patient/in</th><th>Termin</th><th>Nachricht</th><th></th></tr></thead><tbody>
            <?php endif; ?>
        <tr>
          <td><strong><?= h($b['time']) ?> Uhr</strong><br><?php if ($b['status'] !== 'gebucht'): ?><span class="tag off">abgesagt</span><?php endif; ?></td>
          <td><?= h($b['name']) ?><br><a href="mailto:<?= h($b['email']) ?>"><?= h($b['email']) ?></a><?php if ($b['phone']): ?><br><a href="tel:<?= h(preg_replace('/[^\d+]/', '', $b['phone'])) ?>"><?= h($b['phone']) ?></a><?php endif; ?></td>
          <td><?= h(type_label($b['type'])) ?><br><span class="muted small"><?= h(treatment_label($b['treatment'])) ?></span></td>
          <td class="small"><?= nl2br(h($b['message'] ?: '–')) ?></td>
          <td>
            <?php if ($b['status'] === 'gebucht'): ?>
            <form method="post" onsubmit="return confirm('Termin wirklich absagen?');">
              <input type="hidden" name="csrf" value="<?= h($csrf) ?>"><input type="hidden" name="id" value="<?= h($b['id']) ?>">
              <label class="check small"><input type="checkbox" name="notify" value="1" checked> Patient/in per E-Mail informieren</label>
              <button class="btn btn-ghost btn-sm" name="do" value="cancel">Absagen</button>
            </form>
            <?php endif; ?>
          </td>
        </tr>
        <?php endforeach; echo '</tbody></table>'; endif; ?>
  </div>

  <div class="grid grid-2" style="margin-top:28px;align-items:start">
    <div class="glass panel">
      <h2 style="font-size:1.8rem">Zeit sperren</h2>
      <p class="small muted">Z. B. für Urlaub oder telefonisch vergebene Termine. Gesperrte Zeiten erscheinen im Kalender als belegt.</p>
      <form method="post" class="form">
        <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
        <div><label for="b-date">Datum</label><input id="b-date" name="date" type="date" min="<?= h($today) ?>" required style="width:100%;padding:12px;border-radius:12px;border:1px solid rgba(47,85,96,.22)"></div>
        <label class="check"><input type="checkbox" name="whole" value="1" checked onchange="document.getElementById('b-times').hidden=this.checked"> Ganzer Tag</label>
        <div class="form-row" id="b-times" hidden>
          <div><label for="b-from">Von</label><input id="b-from" name="from" type="time" step="1800" style="width:100%;padding:12px;border-radius:12px;border:1px solid rgba(47,85,96,.22)"></div>
          <div><label for="b-to">Bis</label><input id="b-to" name="to" type="time" step="1800" style="width:100%;padding:12px;border-radius:12px;border:1px solid rgba(47,85,96,.22)"></div>
        </div>
        <div><label for="b-note">Notiz (nur für Sie)</label><input id="b-note" name="note" type="text" maxlength="120" placeholder="z. B. Urlaub, Frau M. (telefonisch)"></div>
        <div><button class="btn" name="do" value="block">Sperren</button></div>
      </form>
    </div>
    <div class="glass panel">
      <h2 style="font-size:1.8rem">Gesperrte Zeiten</h2>
      <?php if (!$blocks): ?><p class="muted">Keine Sperren eingetragen.</p><?php else: ?>
      <table class="admin-table"><tbody>
        <?php foreach ($blocks as $bl): ?>
        <tr>
          <td><?= h(date_de($bl['date'])) ?><br><span class="small muted"><?= $bl['from'] ? h($bl['from'] . '–' . $bl['to'] . ' Uhr') : 'ganzer Tag' ?><?= $bl['note'] ? ' · ' . h($bl['note']) : '' ?></span></td>
          <td><form method="post"><input type="hidden" name="csrf" value="<?= h($csrf) ?>"><input type="hidden" name="id" value="<?= h($bl['id']) ?>"><button class="btn btn-ghost btn-sm" name="do" value="unblock">Freigeben</button></form></td>
        </tr>
        <?php endforeach; ?>
      </tbody></table>
      <?php endif; ?>
      <h3 style="margin-top:24px;font-size:1.3rem">Sprechzeiten</h3>
      <ul class="small">
        <?php foreach (WEEKDAYS_DE as $wd): $r = $c['hours'][$wd] ?? []; ?>
          <li><?= h($wd) ?>: <?= $r ? h(implode(', ', array_map(fn($x) => $x[0] . '–' . $x[1], $r))) . (!empty($c['rhythm'][$wd]) ? ' (alle ' . (int) $c['rhythm'][$wd]['weeks'] . ' Wochen ab ' . h(date_de($c['rhythm'][$wd]['start'])) . ')' : '') : 'keine Online-Termine' ?></li>
        <?php endforeach; ?>
      </ul>
      <p class="small muted">Die regelmäßigen Sprechzeiten werden in <code>content.py</code> festgelegt.</p>
    </div>
  </div>
<?php endif; ?>
</div>
</main>
</body>
</html>

<?php
/**
 * Öffentliche Schnittstelle der Online-Terminbuchung.
 *
 *   GET  termine.php?action=slots           freie / belegte Termine
 *   POST termine.php?action=book            Termin buchen (JSON)
 *   GET  termine.php?action=absagen&id&key  Absage-Seite für Patienten
 *   POST termine.php?action=absagen         Absage bestätigen
 */

declare(strict_types=1);
require __DIR__ . '/lib/booking.php';

header('X-Robots-Tag: noindex, nofollow');
header('X-Content-Type-Options: nosniff');

$action = $_GET['action'] ?? 'slots';

try {
    if ($action === 'slots') {
        $av = with_store(fn(array &$store) => availability($store), false);
        $c = cfg();
        json_out(['ok' => true, 'slot_minutes' => $c['slot_minutes'], 'types' => $c['types']] + $av);
    }

    if ($action === 'book' && $_SERVER['REQUEST_METHOD'] === 'POST') {
        handle_book();
    }

    if ($action === 'absagen') {
        handle_cancel();
    }

    json_out(['ok' => false, 'error' => 'Unbekannte Aktion.'], 400);
} catch (Throwable $e) {
    error_log('Schick-Termine: ' . $e->getMessage());
    if ($action === 'absagen') {
        cancel_page('Es ist ein Fehler aufgetreten', '<p>Bitte schreiben Sie uns eine E-Mail an <a href="mailto:' . h(cfg()['email']) . '">' . h(cfg()['email']) . '</a>.</p>');
    }
    json_out(['ok' => false, 'error' => 'Technischer Fehler. Bitte versuchen Sie es später erneut oder schreiben Sie uns eine E-Mail.'], 500);
}

/* ------------------------------------------------------------------------ */

function handle_book(): void
{
    $c = cfg();
    $in = json_decode((string) file_get_contents('php://input'), true);
    if (!is_array($in)) {
        json_out(['ok' => false, 'error' => 'Ungültige Anfrage.'], 400);
    }
    $str = fn(string $k, int $max) => trim(mb_substr((string) ($in[$k] ?? ''), 0, $max));

    // Spam-Schutz: verstecktes Feld muss leer sein, Formular nicht in < 3 Sekunden abgeschickt
    if ($str('website', 200) !== '' || (int) ($in['elapsed'] ?? 0) < 3000) {
        json_out(['ok' => false, 'error' => 'Die Anfrage konnte nicht verarbeitet werden.'], 400);
    }

    $date = $str('date', 10);
    $time = $str('time', 5);
    $type = $str('type', 30);
    $treatment = $str('treatment', 80);
    $name = $str('name', 100);
    $email = $str('email', 150);
    $phone = $str('phone', 40);
    $message = $str('message', 2000);

    $errors = [];
    if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date) || !preg_match('/^\d{2}:\d{2}$/', $time)) {
        $errors[] = 'Bitte wählen Sie einen Termin aus.';
    }
    if (!in_array($type, array_column($c['types'], 'id'), true)) {
        $errors[] = 'Bitte wählen Sie die Art des Termins.';
    }
    if (!isset($c['treatments'][$treatment])) {
        $treatment = 'allgemein';
    }
    if (mb_strlen($name) < 2) {
        $errors[] = 'Bitte geben Sie Ihren Namen an.';
    }
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = 'Bitte geben Sie eine gültige E-Mail-Adresse an.';
    }
    if ($type === 'telefon' && !preg_match('/\d{5,}/', preg_replace('/\D/', '', $phone))) {
        $errors[] = 'Für die telefonische Beratung benötigen wir Ihre Telefonnummer.';
    }
    if (empty($in['consent'])) {
        $errors[] = 'Bitte bestätigen Sie die Datenschutzhinweise.';
    }
    if ($errors) {
        json_out(['ok' => false, 'error' => implode(' ', $errors)], 422);
    }

    $booking = with_store(function (array &$store) use ($date, $time, $type, $treatment, $name, $email, $phone, $message) {
        cleanup_store($store);
        $ip = client_ip_hash();
        if (count($store['rate'][$ip] ?? []) >= 5) {
            return ['error' => 'Zu viele Buchungen in kurzer Zeit. Bitte kontaktieren Sie uns per E-Mail.', 'code' => 429];
        }
        $active = array_filter($store['bookings'], fn($b) => strcasecmp($b['email'], $email) === 0
            && ($b['status'] ?? '') === 'gebucht' && $b['date'] >= date('Y-m-d'));
        if (count($active) >= 3) {
            return ['error' => 'Mit dieser E-Mail-Adresse sind bereits mehrere Termine gebucht. Bitte kontaktieren Sie uns direkt.', 'code' => 429];
        }
        if (!is_slot_bookable($store, $date, $time)) {
            return ['error' => 'Dieser Termin ist leider nicht mehr frei. Bitte wählen Sie einen anderen.', 'code' => 409];
        }
        $b = [
            'id' => bin2hex(random_bytes(8)),
            'key' => bin2hex(random_bytes(16)),
            'date' => $date,
            'time' => $time,
            'type' => $type,
            'treatment' => $treatment,
            'name' => $name,
            'email' => $email,
            'phone' => $phone,
            'message' => $message,
            'status' => 'gebucht',
            'created' => date('c'),
        ];
        $store['bookings'][] = $b;
        $store['rate'][$ip][] = time();
        return $b;
    });

    if (isset($booking['error'])) {
        json_out(['ok' => false, 'error' => $booking['error'], 'refresh' => $booking['code'] === 409], $booking['code']);
    }

    $mailOk = send_booking_mails($booking);
    json_out([
        'ok' => true,
        'mail' => $mailOk,
        'date' => $booking['date'],
        'time' => $booking['time'],
        'label' => date_de($booking['date'], $booking['time']),
    ]);
}

function send_booking_mails(array $b): bool
{
    $c = cfg();
    $when = date_de($b['date'], $b['time']);
    $cancelUrl = site_url('api/termine.php?action=absagen&id=' . $b['id'] . '&key=' . $b['key']);
    $details = "Termin:      $when\n"
        . 'Art:         ' . type_label($b['type']) . "\n"
        . 'Interesse:   ' . treatment_label($b['treatment']) . "\n";

    $toPractice = "Neue Online-Terminbuchung\n\n" . $details
        . "\nName:        {$b['name']}\n"
        . "E-Mail:      {$b['email']}\n"
        . 'Telefon:     ' . ($b['phone'] ?: '–') . "\n\n"
        . "Nachricht:\n" . ($b['message'] ?: '–') . "\n\n"
        . "Alle Termine verwalten: " . site_url('verwaltung/') . "\n";
    $ok1 = send_mail($c['email'], 'Neuer Termin: ' . $when . ' – ' . $b['name'], $toPractice, $b['email'], ics_for($b));

    $where = $b['type'] === 'telefon'
        ? "Ich rufe Sie zum vereinbarten Zeitpunkt unter {$b['phone']} an."
        : "Adresse: {$c['address']}";
    $toPatient = "Guten Tag {$b['name']},\n\n"
        . "vielen Dank für Ihre Buchung. Hiermit bestätige ich Ihren Termin:\n\n" . $details . "\n$where\n\n"
        . "Bitte bringen Sie – falls vorhanden – aktuelle Befunde, eine Medikamentenliste und bei ästhetischen Behandlungen Ihren Injektionspass mit. "
        . "Den Anamnesebogen können Sie vorab ausfüllen: " . site_url('patientenformulare/anamnesebogen/') . "\n\n"
        . "Falls Sie den Termin nicht wahrnehmen können, sagen Sie bitte spätestens " . (int) $c['cancel_notice_hours'] . " Stunden vorher ab:\n"
        . "$cancelUrl\n\n"
        . "Ich freue mich auf Sie!\n\n"
        . "Herzliche Grüße\n{$c['owner']}\n{$c['profession']}\n{$c['address']}\n{$c['email']}\n";
    $ok2 = send_mail($b['email'], 'Ihre Terminbestätigung: ' . $when, $toPatient, $c['email'], ics_for($b));
    return $ok1 && $ok2;
}

function handle_cancel(): void
{
    $c = cfg();
    $id = (string) ($_REQUEST['id'] ?? '');
    $key = (string) ($_REQUEST['key'] ?? '');
    $post = $_SERVER['REQUEST_METHOD'] === 'POST';

    $res = with_store(function (array &$store) use ($id, $key, $post, $c) {
        foreach ($store['bookings'] as &$b) {
            if ($b['id'] !== $id || !hash_equals($b['key'], $key)) {
                continue;
            }
            if ($b['status'] !== 'gebucht') {
                return ['state' => 'already', 'b' => $b];
            }
            $start = new DateTimeImmutable($b['date'] . ' ' . $b['time']);
            $deadline = $start->modify('-' . (int) $c['cancel_notice_hours'] . ' hours');
            if (new DateTimeImmutable('now') > $deadline) {
                return ['state' => 'late', 'b' => $b];
            }
            if (!$post) {
                return ['state' => 'confirm', 'b' => $b];
            }
            $b['status'] = 'abgesagt';
            $b['cancelled'] = date('c') . ' (Patient)';
            return ['state' => 'done', 'b' => $b];
        }
        return ['state' => 'notfound'];
    }, $post);

    $b = $res['b'] ?? null;
    switch ($res['state']) {
        case 'confirm':
            cancel_page('Termin absagen', '<p>Möchten Sie Ihren Termin am <strong>' . h(date_de($b['date'], $b['time'])) . '</strong> ('
                . h(type_label($b['type'])) . ') wirklich absagen?</p>'
                . '<form method="post"><input type="hidden" name="id" value="' . h($id) . '"><input type="hidden" name="key" value="' . h($key) . '">'
                . '<button class="btn" type="submit">Ja, Termin absagen</button></form>');
            // no break
        case 'done':
            send_mail($c['email'], 'Absage: ' . date_de($b['date'], $b['time']) . ' – ' . $b['name'],
                "Der folgende Termin wurde vom Patienten online abgesagt und ist wieder frei:\n\n"
                . date_de($b['date'], $b['time']) . "\n" . type_label($b['type']) . "\n{$b['name']} ({$b['email']})\n", $b['email']);
            cancel_page('Termin abgesagt', '<p>Ihr Termin am <strong>' . h(date_de($b['date'], $b['time'])) . '</strong> wurde abgesagt. Vielen Dank für Ihre Rückmeldung.</p>'
                . '<p><a class="btn" href="/termin-buchen/">Neuen Termin buchen</a></p>');
            // no break
        case 'already':
            cancel_page('Bereits abgesagt', '<p>Dieser Termin wurde bereits abgesagt.</p><p><a class="btn" href="/termin-buchen/">Neuen Termin buchen</a></p>');
            // no break
        case 'late':
            cancel_page('Online-Absage nicht mehr möglich', '<p>Eine Online-Absage ist nur bis ' . (int) $c['cancel_notice_hours']
                . ' Stunden vor dem Termin möglich. Bitte melden Sie sich direkt per E-Mail an <a href="mailto:' . h($c['email']) . '">' . h($c['email']) . '</a>'
                . ($c['phone'] ? ' oder telefonisch unter ' . h($c['phone']) : '') . '.</p>');
            // no break
        default:
            cancel_page('Termin nicht gefunden', '<p>Der Link ist ungültig oder abgelaufen. Bitte schreiben Sie uns an <a href="mailto:' . h($c['email']) . '">' . h($c['email']) . '</a>.</p>');
    }
}

function cancel_page(string $title, string $html): void
{
    header('Content-Type: text/html; charset=utf-8');
    header('Cache-Control: no-store');
    echo '<!DOCTYPE html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        . '<meta name="robots" content="noindex, nofollow"><title>' . h($title) . ' | ' . h(cfg()['brand']) . '</title>'
        . '<link rel="stylesheet" href="/assets/css/style.css"></head><body><div class="water-bg" aria-hidden="true"></div>'
        . '<main class="section"><div class="container narrow"><div class="glass panel">'
        . '<p class="brand"><span class="brand-name">Dr. Schick</span><span class="brand-sub">Medical Aesthetics</span></p>'
        . '<h1 style="font-size:2.2rem;margin-top:24px">' . h($title) . '</h1>' . $html
        . '<p class="small muted" style="margin-top:28px"><a href="/">Zur Startseite</a></p></div></div></main></body></html>';
    exit;
}

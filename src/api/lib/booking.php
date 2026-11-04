<?php
/**
 * Dr. Schick Medical Aesthetics – Online-Terminbuchung (gemeinsame Funktionen)
 *
 * Die Einstellungen (Sprechzeiten, E-Mail-Adresse …) kommen aus config.json,
 * die build.py aus content.py erzeugt. Buchungen werden als JSON-Datei
 * außerhalb des öffentlichen Webordners gespeichert.
 */

declare(strict_types=1);

date_default_timezone_set('Europe/Berlin');

const WEEKDAYS_DE = [1 => 'Montag', 2 => 'Dienstag', 3 => 'Mittwoch', 4 => 'Donnerstag', 5 => 'Freitag', 6 => 'Samstag', 7 => 'Sonntag'];

function cfg(): array
{
    static $cfg = null;
    if ($cfg === null) {
        $raw = file_get_contents(__DIR__ . '/config.json');
        $cfg = json_decode($raw === false ? '{}' : $raw, true) ?: [];
    }
    return $cfg;
}

/* ------------------------------------------------------------------------
 * Datenablage
 * --------------------------------------------------------------------- */

/** Ordner für Buchungsdaten: möglichst außerhalb von public_html. */
function data_dir(): string
{
    static $dir = null;
    if ($dir !== null) {
        return $dir;
    }
    $candidates = [];
    if (getenv('SCHICK_DATA_DIR')) {
        $candidates[] = rtrim((string) getenv('SCHICK_DATA_DIR'), '/');
    }
    $docroot = rtrim((string) ($_SERVER['DOCUMENT_ROOT'] ?? ''), '/');
    if ($docroot === '') {
        // Aufruf über Cron/Kommandozeile: public_html = drei Ebenen über api/lib
        $docroot = dirname(__DIR__, 3);
    }
    if ($docroot !== '') {
        $candidates[] = dirname($docroot) . '/schick-termine-daten';
    }
    // Rückfall: innerhalb von public_html, aber per .htaccess gesperrt
    $candidates[] = dirname(__DIR__, 3) . '/.termine-daten';

    foreach ($candidates as $c) {
        if (is_dir($c) || @mkdir($c, 0700, true)) {
            if (is_writable($c)) {
                $dir = $c;
                if (!file_exists($c . '/.htaccess')) {
                    @file_put_contents($c . '/.htaccess', "Require all denied\n<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n");
                }
                return $dir;
            }
        }
    }
    throw new RuntimeException('Kein beschreibbarer Datenordner gefunden.');
}

function empty_store(): array
{
    return ['bookings' => [], 'blocks' => [], 'rate' => []];
}

/**
 * Liest die Buchungsdaten unter exklusiver Sperre, ruft $fn auf und speichert
 * das Ergebnis atomar. So können zwei gleichzeitige Buchungen nie denselben
 * Termin bekommen.
 */
function with_store(callable $fn, bool $write = true)
{
    $dir = data_dir();
    $lock = fopen($dir . '/bookings.lock', 'c');
    if (!$lock || !flock($lock, $write ? LOCK_EX : LOCK_SH)) {
        throw new RuntimeException('Datenablage gesperrt.');
    }
    try {
        $file = $dir . '/bookings.json';
        $store = empty_store();
        if (is_file($file)) {
            $data = json_decode((string) file_get_contents($file), true);
            if (is_array($data)) {
                $store = array_merge($store, $data);
            }
        }
        $result = $fn($store);
        if ($write) {
            $tmp = $file . '.' . bin2hex(random_bytes(4)) . '.tmp';
            file_put_contents($tmp, json_encode($store, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
            @chmod($tmp, 0600);
            rename($tmp, $file);
        }
        return $result;
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
    }
}

/** Entfernt alte Termine (Datensparsamkeit) und alte Rate-Limit-Einträge. */
function cleanup_store(array &$store): void
{
    $keep = (int) (cfg()['keep_days'] ?? 90);
    $limit = (new DateTimeImmutable('today'))->modify("-{$keep} days")->format('Y-m-d');
    $store['bookings'] = array_values(array_filter($store['bookings'], fn($b) => ($b['date'] ?? '') >= $limit));
    $today = date('Y-m-d');
    $store['blocks'] = array_values(array_filter($store['blocks'], fn($b) => ($b['date'] ?? '') >= $today));
    $cut = time() - 86400;
    foreach ($store['rate'] as $k => $times) {
        $store['rate'][$k] = array_values(array_filter((array) $times, fn($t) => $t > $cut));
        if (!$store['rate'][$k]) {
            unset($store['rate'][$k]);
        }
    }
}

/* ------------------------------------------------------------------------
 * Kalender
 * --------------------------------------------------------------------- */

/** Gesetzliche Feiertage in Rheinland-Pfalz für ein Jahr (Y-m-d => Name). */
function holidays_rlp(int $year): array
{
    // Osterdatum (Gaußsche Osterformel, Anonymer Gregorianischer Algorithmus)
    $a = $year % 19; $b = intdiv($year, 100); $c = $year % 100;
    $d = intdiv($b, 4); $e = $b % 4; $f = intdiv($b + 8, 25); $g = intdiv($b - $f + 1, 3);
    $h = (19 * $a + $b - $d - $g + 15) % 30; $i = intdiv($c, 4); $k = $c % 4;
    $l = (32 + 2 * $e + 2 * $i - $h - $k) % 7; $m = intdiv($a + 11 * $h + 22 * $l, 451);
    $month = intdiv($h + $l - 7 * $m + 114, 31); $day = (($h + $l - 7 * $m + 114) % 31) + 1;
    $easter = new DateTimeImmutable(sprintf('%04d-%02d-%02d', $year, $month, $day));
    $rel = fn(int $days) => $easter->modify(($days >= 0 ? '+' : '') . $days . ' days')->format('Y-m-d');
    return [
        "$year-01-01" => 'Neujahr',
        $rel(-2) => 'Karfreitag',
        $rel(1) => 'Ostermontag',
        "$year-05-01" => 'Tag der Arbeit',
        $rel(39) => 'Christi Himmelfahrt',
        $rel(50) => 'Pfingstmontag',
        $rel(60) => 'Fronleichnam',
        "$year-10-03" => 'Tag der Deutschen Einheit',
        "$year-11-01" => 'Allerheiligen',
        "$year-12-25" => '1. Weihnachtstag',
        "$year-12-26" => '2. Weihnachtstag',
    ];
}

function is_closed_date(string $date): bool
{
    $c = cfg();
    if (in_array($date, $c['closed_dates'] ?? [], true)) {
        return true;
    }
    if (!empty($c['holidays_rlp'])) {
        $year = (int) substr($date, 0, 4);
        if (isset(holidays_rlp($year)[$date])) {
            return true;
        }
    }
    return false;
}

/** Sprechzeiten eines Tages als Zeitfenster [Beginn, Ende] (leer = keine Sprechzeit). */
function day_ranges(string $date): array
{
    $c = cfg();
    $dt = new DateTimeImmutable($date);
    $wd = WEEKDAYS_DE[(int) $dt->format('N')];
    $ranges = $c['hours'][$wd] ?? [];
    // Rhythmus, z. B. Samstag nur alle 3 Wochen ab einem Starttag
    if (!empty($c['rhythm'][$wd])) {
        $r = $c['rhythm'][$wd];
        $start = new DateTimeImmutable($r['start']);
        $weeks = max(1, (int) $r['weeks']);
        $diff = (int) $start->diff($dt)->format('%r%a');
        if ($diff < 0 || intdiv($diff, 7) % $weeks !== 0) {
            return [];
        }
    }
    $out = [];
    foreach ($ranges as $r) {
        $out[] = [new DateTimeImmutable("$date {$r[0]}"), new DateTimeImmutable("$date {$r[1]}")];
    }
    return $out;
}

function slot_minutes(): int
{
    return max(5, (int) (cfg()['slot_minutes'] ?? 30));
}

/** Dauer eines Termins in Minuten: je Terminart, bei Behandlungen je Behandlung. */
function duration_for(string $type, string $treatment = ''): int
{
    $c = cfg();
    if ($type === 'behandlung') {
        $m = $c['treatment_minutes'][$treatment] ?? ($c['default_treatment_minutes'] ?? 60);
    } else {
        $m = slot_minutes();
        foreach ($c['types'] ?? [] as $t) {
            if ($t['id'] === $type && !empty($t['minutes'])) {
                $m = $t['minutes'];
            }
        }
    }
    return max(slot_minutes(), (int) $m);
}

function booking_minutes(array $b): int
{
    return max(5, (int) ($b['duration'] ?? slot_minutes()));
}

/** Prüft, ob der Zeitraum [start, end) frei ist (keine Buchung, keine Sperre). */
function is_range_free(array $store, string $date, DateTimeImmutable $start, DateTimeImmutable $end): bool
{
    foreach ($store['bookings'] as $b) {
        if ($b['date'] !== $date || ($b['status'] ?? 'gebucht') !== 'gebucht') {
            continue;
        }
        $bs = new DateTimeImmutable($b['date'] . ' ' . $b['time']);
        $be = $bs->modify('+' . booking_minutes($b) . ' minutes');
        if ($bs < $end && $start < $be) {
            return false;
        }
    }
    foreach ($store['blocks'] as $bl) {
        if (($bl['date'] ?? '') !== $date) {
            continue;
        }
        if (empty($bl['from'])) {
            return false; // ganzer Tag gesperrt
        }
        $bs = new DateTimeImmutable("$date {$bl['from']}");
        $be = new DateTimeImmutable("$date {$bl['to']}");
        if ($bs < $end && $start < $be) {
            return false;
        }
    }
    return true;
}

function is_day_blocked(array $store, string $date): bool
{
    foreach ($store['blocks'] as $b) {
        if (($b['date'] ?? '') === $date && empty($b['from'])) {
            return true;
        }
    }
    return false;
}

/**
 * Kalenderdaten für die Website: Tage mit Status und Startzeiten (frei / belegt).
 * Bei längeren Terminen wird nur angeboten, was komplett in die Sprechzeit passt
 * und über die ganze Dauer frei ist.
 */
function availability(array $store, ?int $minutes = null): array
{
    $c = cfg();
    $minutes = $minutes ?: slot_minutes();
    $step = slot_minutes();
    $now = new DateTimeImmutable('now');
    $earliest = $now->modify('+' . (int) ($c['min_notice_hours'] ?? 24) . ' hours');
    $start = new DateTimeImmutable('today');
    $end = $start->modify('+' . (7 * (int) ($c['weeks_ahead'] ?? 10)) . ' days');
    $days = [];
    for ($d = $start; $d <= $end; $d = $d->modify('+1 day')) {
        $date = $d->format('Y-m-d');
        $slots = [];
        if (!is_closed_date($date) && !is_day_blocked($store, $date)) {
            foreach (day_ranges($date) as [$from, $to]) {
                for ($t = $from; $t->modify("+{$minutes} minutes") <= $to; $t = $t->modify("+{$step} minutes")) {
                    if ($t < $earliest) {
                        continue;
                    }
                    $free = is_range_free($store, $date, $t, $t->modify("+{$minutes} minutes"));
                    $slots[] = ['t' => $t->format('H:i'), 'free' => $free];
                }
            }
        }
        if (!$slots) {
            $status = 'geschlossen';
        } else {
            $status = count(array_filter($slots, fn($s) => $s['free'])) ? 'frei' : 'ausgebucht';
        }
        $days[$date] = ['status' => $status, 'slots' => $slots];
    }
    return ['from' => $start->format('Y-m-d'), 'to' => $end->format('Y-m-d'), 'days' => $days, 'minutes' => $minutes];
}

function is_slot_bookable(array $store, string $date, string $time, ?int $minutes = null): bool
{
    $av = availability($store, $minutes);
    foreach ($av['days'][$date]['slots'] ?? [] as $s) {
        if ($s['t'] === $time) {
            return $s['free'];
        }
    }
    return false;
}

/** Endzeit eines Termins als "HH:MM". */
function booking_end(array $b): string
{
    return (new DateTimeImmutable($b['date'] . ' ' . $b['time']))->modify('+' . booking_minutes($b) . ' minutes')->format('H:i');
}

/* ------------------------------------------------------------------------
 * Hilfsfunktionen
 * --------------------------------------------------------------------- */

function type_label(string $id): string
{
    foreach (cfg()['types'] ?? [] as $t) {
        if ($t['id'] === $id) {
            return $t['label'];
        }
    }
    return $id;
}

function treatment_label(string $id): string
{
    return cfg()['treatments'][$id] ?? 'Allgemeine Beratung';
}

function date_de(string $date, string $time = ''): string
{
    $dt = new DateTimeImmutable($date);
    $months = [1 => 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
    $s = WEEKDAYS_DE[(int) $dt->format('N')] . ', ' . (int) $dt->format('j') . '. ' . $months[(int) $dt->format('n')] . ' ' . $dt->format('Y');
    return $time ? "$s um $time Uhr" : $s;
}

function client_ip_hash(): string
{
    return hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|' . (cfg()['email'] ?? ''));
}

function h(?string $s): string
{
    return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8');
}

function site_url(string $path = ''): string
{
    if (empty($_SERVER['HTTP_HOST'])) {
        // Cron/Kommandozeile: Adresse aus der Konfiguration
        return rtrim((string) cfg()['site_url'], '/') . '/' . ltrim($path, '/');
    }
    $https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
    $host = $_SERVER['HTTP_HOST'] ?? parse_url((string) (cfg()['site_url'] ?? ''), PHP_URL_HOST);
    return ($https ? 'https' : 'http') . '://' . $host . '/' . ltrim($path, '/');
}

/* ------------------------------------------------------------------------
 * E-Mail
 * --------------------------------------------------------------------- */

function ics_for(array $b): string
{
    $c = cfg();
    $start = new DateTimeImmutable($b['date'] . ' ' . $b['time'], new DateTimeZone('Europe/Berlin'));
    $end = $start->modify('+' . booking_minutes($b) . ' minutes');
    $utc = new DateTimeZone('UTC');
    $fmt = fn(DateTimeImmutable $d) => $d->setTimezone($utc)->format('Ymd\THis\Z');
    $esc = fn(string $s) => addcslashes($s, ",;\\");
    $loc = $b['type'] === 'telefon' ? 'Telefonische Beratung' : $c['address'];
    return implode("\r\n", [
        'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Dr. Schick Medical Aesthetics//Termine//DE', 'METHOD:PUBLISH',
        'BEGIN:VEVENT',
        'UID:' . $b['id'] . '@' . (parse_url((string) $c['site_url'], PHP_URL_HOST) ?: 'schick'),
        'DTSTAMP:' . $fmt(new DateTimeImmutable('now')),
        'DTSTART:' . $fmt($start), 'DTEND:' . $fmt($end),
        'SUMMARY:' . $esc(type_label($b['type']) . ' – ' . $c['owner'] . ' – ' . ($c['practice'] ?? 'Medical Aesthetics')),
        'LOCATION:' . $esc($loc),
        'END:VEVENT', 'END:VCALENDAR', '',
    ]);
}

/**
 * SMTP-Zugangsdaten (optional) aus <Datenordner>/smtp.json, z. B.:
 *   {"host": "smtp.hostinger.com", "port": 465, "secure": "ssl",
 *    "user": "praxis@schick-aesthetics.com", "pass": "PASSWORT"}
 * Die Datei liegt außerhalb von public_html und nicht auf GitHub.
 * Ohne diese Datei wird PHP mail() verwendet.
 */
function smtp_cfg(): ?array
{
    static $smtp = false;
    if ($smtp === false) {
        $smtp = null;
        try {
            $file = data_dir() . '/smtp.json';
            if (is_file($file)) {
                $data = json_decode((string) file_get_contents($file), true);
                if (is_array($data) && !empty($data['pass'])) {
                    $smtp = $data + [
                        'host' => 'smtp.hostinger.com',
                        'port' => 465,
                        'secure' => 'ssl',
                        'user' => cfg()['email'],
                    ];
                }
            }
        } catch (Throwable $e) {
            $smtp = null;
        }
    }
    return $smtp;
}

/** Versendet eine fertig aufgebaute Nachricht per SMTP (AUTH LOGIN). */
function smtp_send(array $smtp, string $from, string $to, string $data): bool
{
    $secure = strtolower((string) $smtp['secure']);
    $remote = ($secure === 'ssl' ? 'ssl://' : 'tcp://') . $smtp['host'] . ':' . (int) $smtp['port'];
    $ctx = stream_context_create(['ssl' => ['verify_peer' => true, 'verify_peer_name' => true]]);
    $fp = @stream_socket_client($remote, $errno, $errstr, 15, STREAM_CLIENT_CONNECT, $ctx);
    if (!$fp) {
        error_log("Schick-Termine SMTP: Verbindung fehlgeschlagen ($errno $errstr)");
        return false;
    }
    stream_set_timeout($fp, 15);
    $read = function () use ($fp): string {
        $out = '';
        while (($line = fgets($fp, 1024)) !== false) {
            $out .= $line;
            if (strlen($line) < 4 || $line[3] === ' ') {
                break;
            }
        }
        return $out;
    };
    $cmd = function (string $c, array $ok) use ($fp, $read): bool {
        if ($c !== '') {
            fwrite($fp, $c . "\r\n");
        }
        $resp = $read();
        if (!in_array((int) substr($resp, 0, 3), $ok, true)) {
            $shown = strlen($c) > 200 ? '[Nachricht]' : (stripos($c, 'AUTH') === 0 || preg_match('/^[A-Za-z0-9+\/=]+$/', $c) ? '[Anmeldung]' : $c);
            error_log('Schick-Termine SMTP: ' . $shown . ' -> ' . trim($resp));
            return false;
        }
        return true;
    };
    $host = parse_url((string) (cfg()['site_url'] ?? ''), PHP_URL_HOST) ?: 'localhost';
    $ok = $cmd('', [220]) && $cmd("EHLO $host", [250]);
    if ($ok && $secure === 'tls') {
        $ok = $cmd('STARTTLS', [220])
            && stream_socket_enable_crypto($fp, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)
            && $cmd("EHLO $host", [250]);
    }
    $ok = $ok
        && $cmd('AUTH LOGIN', [334])
        && $cmd(base64_encode((string) $smtp['user']), [334])
        && $cmd(base64_encode((string) $smtp['pass']), [235])
        && $cmd("MAIL FROM:<$from>", [250])
        && $cmd("RCPT TO:<$to>", [250, 251])
        && $cmd('DATA', [354]);
    if ($ok) {
        // Punkt am Zeilenanfang verdoppeln (SMTP-Regel)
        $body = preg_replace('/^\./m', '..', str_replace(["\r\n", "\r"], "\n", $data));
        $ok = $cmd(str_replace("\n", "\r\n", $body) . "\r\n.", [250]);
    }
    @fwrite($fp, "QUIT\r\n");
    fclose($fp);
    return $ok;
}

/** Versendet eine Text-E-Mail (UTF-8), optional mit Kalenderdatei – per SMTP, sonst mit mail(). */
function send_mail(string $to, string $subject, string $body, string $replyTo = '', ?string $ics = null): bool
{
    $c = cfg();
    $from = $c['email'];
    $fromName = $c['brand'] ?? 'Praxis';
    $headers = [];
    $headers[] = 'From: ' . mb_encode_mimeheader($fromName, 'UTF-8', 'Q') . " <$from>";
    if ($replyTo !== '' && filter_var($replyTo, FILTER_VALIDATE_EMAIL)) {
        $headers[] = "Reply-To: $replyTo";
    }
    $headers[] = 'MIME-Version: 1.0';
    $headers[] = 'X-Mailer: Schick-Termine';
    if ($ics === null) {
        $headers[] = 'Content-Type: text/plain; charset=UTF-8';
        $headers[] = 'Content-Transfer-Encoding: base64';
        $message = chunk_split(base64_encode($body));
    } else {
        $boundary = 'b' . bin2hex(random_bytes(12));
        $headers[] = "Content-Type: multipart/mixed; boundary=\"$boundary\"";
        $message = "--$boundary\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n"
            . chunk_split(base64_encode($body))
            . "--$boundary\r\nContent-Type: text/calendar; charset=UTF-8; method=PUBLISH; name=\"termin.ics\"\r\n"
            . "Content-Disposition: attachment; filename=\"termin.ics\"\r\nContent-Transfer-Encoding: base64\r\n\r\n"
            . chunk_split(base64_encode($ics))
            . "--$boundary--\r\n";
    }
    $subj = mb_encode_mimeheader($subject, 'UTF-8', 'B', "\r\n");

    $smtp = smtp_cfg();
    if ($smtp) {
        $domain = substr(strrchr($from, '@') ?: '@localhost', 1);
        $data = implode("\r\n", array_merge([
            'Date: ' . date('r'),
            'Message-ID: <' . bin2hex(random_bytes(12)) . '@' . $domain . '>',
            "To: <$to>",
            "Subject: $subj",
        ], $headers)) . "\r\n\r\n" . $message;
        if (smtp_send($smtp, $from, $to, $data)) {
            return true;
        }
        error_log('Schick-Termine: SMTP-Versand fehlgeschlagen, versuche mail()');
    }
    return @mail($to, $subj, $message, implode("\r\n", $headers), '-f' . $from);
}

/* ------------------------------------------------------------------------
 * Terminerinnerung
 * --------------------------------------------------------------------- */

/**
 * Verschickt Erinnerungs-E-Mails für Termine, die in den nächsten
 * reminder_hours Stunden beginnen. Jeder Termin wird nur einmal erinnert.
 * Gibt die Anzahl der versendeten Erinnerungen zurück.
 */
function send_due_reminders(): int
{
    $c = cfg();
    $hours = (int) ($c['reminder_hours'] ?? 24);
    if ($hours <= 0) {
        return 0;
    }
    $now = new DateTimeImmutable('now');
    $due = with_store(function (array &$store) use ($now, $hours) {
        $list = [];
        foreach ($store['bookings'] as &$b) {
            if (($b['status'] ?? '') !== 'gebucht' || !empty($b['reminded'])) {
                continue;
            }
            $start = new DateTimeImmutable($b['date'] . ' ' . $b['time']);
            // fällig: weniger als $hours Stunden bis zum Termin, aber noch mindestens 1 Stunde
            if ($start > $now->modify('+1 hour') && $start <= $now->modify("+{$hours} hours")) {
                $b['reminded'] = date('c');
                $list[] = $b;
            }
        }
        return $list;
    });
    $sent = 0;
    foreach ($due as $b) {
        $when = date_de($b['date'], $b['time']);
        $where = $b['type'] === 'telefon'
            ? "Ich rufe Sie zum vereinbarten Zeitpunkt unter {$b['phone']} an."
            : "Adresse: {$c['address']}";
        $text = "Guten Tag {$b['name']},\n\n"
            . "ich möchte Sie an Ihren Termin erinnern:\n\n"
            . "Termin:      $when (bis " . booking_end($b) . " Uhr)\n"
            . 'Art:         ' . type_label($b['type']) . "\n\n"
            . "$where\n\n"
            . "Bitte bringen Sie – falls vorhanden – aktuelle Befunde, eine Medikamentenliste und bei ästhetischen Behandlungen Ihren Injektionspass mit. "
            . "Den Anamnesebogen können Sie vorab ausfüllen: " . site_url('patientenformulare/anamnesebogen/') . "\n\n"
            . "Falls Sie den Termin nicht wahrnehmen können, geben Sie mir bitte so schnell wie möglich per E-Mail Bescheid.\n\n"
            . "Ich freue mich auf Sie!\n\n"
            . "Herzliche Grüße\n{$c['owner']} – {$c['practice']}\n{$c['profession']}\n{$c['address']}\n{$c['email']}\n";
        if (send_mail($b['email'], 'Erinnerung an Ihren Termin: ' . $when, $text, $c['email'], ics_for($b))) {
            $sent++;
        } else {
            // Versand fehlgeschlagen: beim nächsten Durchlauf erneut versuchen
            $id = $b['id'];
            with_store(function (array &$store) use ($id) {
                foreach ($store['bookings'] as &$x) {
                    if ($x['id'] === $id) {
                        unset($x['reminded']);
                    }
                }
            });
        }
    }
    return $sent;
}

/** Rückfall ohne Cron: höchstens alle 15 Minuten beim Aufruf der Website prüfen. */
function maybe_send_reminders(): void
{
    try {
        $flag = data_dir() . '/reminder.last';
        if (is_file($flag) && filemtime($flag) > time() - 900) {
            return;
        }
        @touch($flag);
        send_due_reminders();
    } catch (Throwable $e) {
        error_log('Schick-Termine Erinnerung: ' . $e->getMessage());
    }
}

function json_out(array $data, int $code = 200): void
{
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    header('X-Robots-Tag: noindex');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

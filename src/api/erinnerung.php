<?php
/**
 * Terminerinnerungen verschicken – für den Cron-Job bei Hostinger (stündlich).
 * Läuft nur über die Kommandozeile, nicht über den Browser.
 */

declare(strict_types=1);

if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
require __DIR__ . '/lib/booking.php';
$sent = send_due_reminders();
echo date('c') . " Erinnerungen versendet: $sent\n";

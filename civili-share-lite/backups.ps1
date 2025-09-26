# === Définition des variables ===
$BackupDir = ".\backups"
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$MainDbDir = ".\main"
$ScdDbDir = ".\scd"

# === Créer le dossier de sauvegarde ===
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "=== Sauvegarde des bases SQLite ==="

# === Sauvegarder les DB depuis main ===
Copy-Item "$MainDbDir\users.db" "$BackupDir\users_main_$Date.db" -Force
Copy-Item "$MainDbDir\notes.db" "$BackupDir\notes_main_$Date.db" -Force

# === Sauvegarder les DB depuis scd ===
Copy-Item "$ScdDbDir\users.db" "$BackupDir\users_scd_$Date.db" -Force
Copy-Item "$ScdDbDir\notes.db" "$BackupDir\notes_scd_$Date.db" -Force

Write-Host "Sauvegardes créées dans $BackupDir"

# === Synchronisation main → scd (main = source de vérité) ===
Write-Host "=== Synchronisation main → scd ==="
Copy-Item "$MainDbDir\users.db" "$ScdDbDir\users.db" -Force
Copy-Item "$MainDbDir\notes.db" "$ScdDbDir\notes.db" -Force
Write-Host "Synchronisation terminée"

# === Nettoyer les anciennes sauvegardes (garder 7 jours) ===
Write-Host "=== Nettoyage des anciennes sauvegardes ==="
Get-ChildItem $BackupDir -Filter *.db |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |
    Remove-Item -Force

Write-Host "Nettoyage terminé"

$URL = "http://localhost:3000/health"  # Mets l'adresse de ton backend
$Interval = 300  # 5 minutes en secondes
$LogFile = "C:\Users\gabin\Documents\supervision.log"  # chemin du fichier log

while ($true) {
    $Now = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    try {
        $response = Invoke-WebRequest -Uri $URL -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            $status = "$Now ✅ Serveur OK"
            Write-Output $status
        } else {
            $status = "$Now ⚠️ Réponse inattendue: $($response.StatusCode)"
            Write-Output $status
            [console]::beep(1000,500)  # bip de 500ms
        }
    }
    catch {
        $status = "$Now ❌ Serveur DOWN !"
        Write-Output $status
        [console]::beep(500,1000)  # bip grave de 1s
    }

    # Écriture dans le fichier log
    Add-Content -Path $LogFile -Value $status

    Start-Sleep -Seconds $Interval
}

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$PythonExe = "python"
$PyScript  = ".\make_podcast_edge.py"
$OutputRoot = ".\outputs"
$OpenOutputFolder = $true

function Show-Toast([string]$title, [string]$message) {
    try {
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null

        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $t = $title.Replace("&","&amp;").Replace("<","&lt;").Replace(">","&gt;")
        $m = $message.Replace("&","&amp;").Replace("<","&lt;").Replace(">","&gt;")
        $xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>$t</text><text>$m</text></binding></visual></toast>")
        $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("PodcastMaker").Show($toast)
    } catch { }
}

try {
    if (-not (Test-Path $PyScript)) { throw "找不到脚本：$PyScript" }
    if (-not (Test-Path ".\script.txt")) { throw "找不到输入文件：.\script.txt" }

    Write-Host "== PodcastMaker 开始 ==" -ForegroundColor Cyan
    Write-Host ("工作目录：{0}" -f (Get-Location))

    & $PythonExe -u $PyScript
    $rc = $LASTEXITCODE
    if ($rc -ne 0) { throw "Python 返回错误码：$rc" }

    $latestDir = $null
    if (Test-Path $OutputRoot) {
        $latestDir = Get-ChildItem $OutputRoot -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    }

    $latestMp3 = $null
    if ($latestDir) {
        $latestMp3 = Get-ChildItem $latestDir.FullName -Filter "podcast_*.mp3" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    }

    $msg = if ($latestMp3) { "✅ 生成完成：" + $latestMp3.FullName }
           elseif ($latestDir) { "✅ 生成完成：" + $latestDir.FullName }
           else { "✅ 生成完成（未定位到 outputs）" }

    Show-Toast "PodcastMaker" $msg
    Write-Host $msg -ForegroundColor Green

    if ($OpenOutputFolder -and $latestDir) {
        Start-Process explorer.exe $latestDir.FullName
    }

    exit 0
}
catch {
    $err = $_.Exception.Message
    Show-Toast "PodcastMaker" ("❌ 生成失败：" + $err)
    Write-Host ("❌ 生成失败：{0}" -f $err) -ForegroundColor Red
    exit 1
}

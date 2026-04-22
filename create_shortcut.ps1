$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\BookBot 06.lnk")
$Shortcut.TargetPath = "E:\Coding\BookBot_06\run_bookbot_06.bat"
$Shortcut.WorkingDirectory = "E:\Coding\BookBot_06"
$Shortcut.IconLocation = "E:\Coding\BookBot_06\venv\Scripts\python.exe, 0"
$Shortcut.Save()

echo "Shortcut 'BookBot 06' created on Desktop."

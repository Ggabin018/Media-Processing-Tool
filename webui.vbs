' Starts the app without any console window (pythonw), only the browser tab.
' The app stops by itself when its last tab is closed. Logs: logs\app.log
' For a console (debug), use webui.bat instead.
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = root & "\venv\Scripts\pythonw.exe"

If Not fso.FileExists(pythonw) Then
    MsgBox "venv not found: run install.bat first.", vbExclamation, "Media Processing Tool"
    WScript.Quit 1
End If

shell.CurrentDirectory = root
shell.Run """" & pythonw & """ ""src\main.py""", 0, False

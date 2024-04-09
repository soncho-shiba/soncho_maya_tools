
ECHO  off

NET SESSION >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO This script needs to be run with administrator privileges
    ECHO このスクリプトは管理者権限で実行する必要があります
    pause
)

set MAYA_DEFAULT_SCRIPT_PATH="C:\Users\%username%\Documents\maya\scripts"
set TOOLS_NAME=soncho_maya_tools

IF EXIST "%MAYA_DEFAULT_SCRIPT_PATH%\%TOOLS_NAME%" (
    ECHO The symbolic link already exists
    ECHO [%TOOLS_NAME%] へのシンボリックリンクは既に存在しています
) ELSE (
    mklink /D "%MAYA_DEFAULT_SCRIPT_PATH%\%TOOLS_NAME%" "%~dp0%TOOLS_NAME%" 
    ECHO Created a symbolic link to [%TOOLS_NAME%] in the default directory of Maya
    ECHO Mayaのデフォルトディレクトリに [%TOOLS_NAME%] へのシンボリックリンクを作成しました
)

explorer "%MAYA_DEFAULT_SCRIPT_PATH%\%TOOLS_NAME%"
pause


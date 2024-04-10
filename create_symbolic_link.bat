
ECHO  off

NET SESSION >NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO This script needs to be run with administrator privileges
    ECHO ���̃X�N���v�g�͊Ǘ��Ҍ����Ŏ��s����K�v������܂�
    pause
)

set MAYA_DEFAULT_SCRIPT_PATH="C:\Users\%username%\Documents\maya\scripts"
set TOOLS_NAME=soncho_maya_tools

IF EXIST "%MAYA_DEFAULT_SCRIPT_PATH%\%TOOLS_NAME%" (
    ECHO The symbolic link already exists
    ECHO [%TOOLS_NAME%] �ւ̃V���{���b�N�����N�͊��ɑ��݂��Ă��܂�
) ELSE (
    mklink /D "%MAYA_DEFAULT_SCRIPT_PATH%\%TOOLS_NAME%" "%~dp0%TOOLS_NAME%" 
    ECHO Created a symbolic link to [%TOOLS_NAME%] in the default directory of Maya
    ECHO Maya�̃f�t�H���g�f�B���N�g���� [%TOOLS_NAME%] �ւ̃V���{���b�N�����N���쐬���܂���
)

explorer "%MAYA_DEFAULT_SCRIPT_PATH%\%TOOLS_NAME%"
pause


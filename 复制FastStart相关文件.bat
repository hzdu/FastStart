@echo off
setlocal

REM ����Ŀ��·��
set targetDir=output\FastStart

REM ���� start.json �ļ�
if exist start.json (
    copy /Y "start.json" "%targetDir%\start.json" >nul
    echo start.json �ļ��Ѹ��ơ�
) else (
    echo start.json �ļ������ڣ��޷����ơ�
)

REM ���� assets Ŀ¼
if exist assets (
    if not exist "%targetDir%\assets" (
        xcopy /E /I /Y "assets" "%targetDir%\assets"
    ) else (
        echo ���� assets Ŀ¼����ΪĿ��Ŀ¼�Ѵ��ڡ�
    )
)

echo ��ɸ��Ʋ���.
endlocal
@echo off
setlocal

REM 设置目标路径
set targetDir=output\FastStart

REM 复制 start.json 文件
if exist start.json (
    copy /Y "start.json" "%targetDir%\start.json" >nul
    echo start.json 文件已复制。
) else (
    echo start.json 文件不存在，无法复制。
)

REM 复制 assets 目录
if exist assets (
    if not exist "%targetDir%\assets" (
        xcopy /E /I /Y "assets" "%targetDir%\assets"
    ) else (
        echo 跳过 assets 目录，因为目标目录已存在。
    )
)

echo 完成复制操作.
endlocal
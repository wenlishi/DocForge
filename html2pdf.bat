@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo  知识分享 PDF 生成工具
echo ========================================

:: 检查参数
if "%1"=="" (
    echo 用法: html2pdf.bat ^<输入HTML文件^> [输出PDF文件]
    echo 示例: html2pdf.bat output.html output.pdf
    exit /b 1
)

set "INPUT=%~f1"
if "%2"=="" (
    set "OUTPUT=%~dpn1.pdf"
) else (
    set "OUTPUT=%~f2"
)

if not exist "%INPUT%" (
    echo 错误: 找不到输入文件 %INPUT%
    exit /b 1
)

:: 尝试使用 Chrome
set "CHROME="
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set "CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set "CHROME=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    set "CHROME=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    set "CHROME=C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

if "%CHROME%"="" (
    echo 错误: 未找到 Chrome 或 Edge 浏览器
    echo 请安装 Google Chrome 或 Microsoft Edge
    exit /b 1
)

echo 使用浏览器: %CHROME%
echo 输入文件: %INPUT%
echo 输出文件: %OUTPUT%
echo.

"%CHROME%" --headless --disable-gpu --no-header-footer --print-to-pdf="%OUTPUT%" "%INPUT%"

if errorlevel 1 (
    echo [失败] PDF 生成出错
    exit /b 1
) else (
    echo [成功] PDF 已生成: %OUTPUT%
)

endlocal

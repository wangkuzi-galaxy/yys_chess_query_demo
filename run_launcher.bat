@echo on
setlocal enabledelayedexpansion
chcp 65001 >nul

echo 开始执行脚本...

:: 安装一个python，如果本地有python环境可以直接使用python运行launcher.py
python --version
if %errorlevel% neq 0 (
    echo Python 未安装，开始安装过程...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe', 'python-installer.exe')"
    echo 下载完成，开始安装...
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    if %errorlevel% neq 0 (
        echo Python 安装失败，错误代码: %errorlevel%
        goto :error
    )
    del python-installer.exe
    echo Python 安装完成
) else (
    echo Python 已安装
)

:: 刷新环境变量
echo 刷新环境变量...
call refreshenv

:: 创建虚拟环境
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 创建虚拟环境失败，错误代码: %errorlevel%
        goto :error
    )
)

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo 激活虚拟环境失败，错误代码: %errorlevel%
    goto :error
)

:: 安装依赖
echo 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 安装依赖失败，错误代码: %errorlevel%
    goto :error
)

:: 杀掉占用 7860 端口的进程
echo 正在关闭占用 7860 端口的进程...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":7860"') do (
    echo 关闭进程 PID: %%a
    taskkill /F /PID %%a
    if %errorlevel% neq 0 (
        echo 关闭进程失败，错误代码: %errorlevel%
    )
)

:: 运行 launcher.py
echo 启动程序...
python dist\launcher.py
if %errorlevel% neq 0 (
    echo 程序运行失败，错误代码: %errorlevel%
    goto :error
)

echo 程序执行完成
goto :end

:error
echo 脚本执行过程中遇到错误，请查看上方输出以获取详细信息。

:end
echo 按任意键退出...
pause >nul
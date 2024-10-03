import os
import subprocess
import sys
import webbrowser
import time
import re
import threading

LOGO = """
( o o )
/  V  \\
/( \^/ )\\
^^ "" ^^
"""

MAIN_APP = "main.py"

def open_browser(url):
    time.sleep(2)  # 给应用一些启动时间
    webbrowser.open(url)
    print("✅ 页面已在浏览器中成功打开！")

def run_app():
    print("启动 页面 ....请等待页面弹出....")
    print("私货时间：你知道吗？zen现在居然还在用茨林的形象替代茨木，太过分了！")
    print("如果页面长时间没有打开，并且端口7860没有被占用，那么请手动打开url：http://127.0.0.1:7860/")
    cmd = [sys.executable, MAIN_APP]
    
    process = subprocess.Popen(cmd, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT,
                               text=True, 
                               bufsize=1, 
                               universal_newlines=True)
    
    url = None
    browser_opened = False
    start_time = time.time()
    
    while True:
        line = process.stdout.readline()
        if not line:
            break
        
        print(line, end='', flush=True)  # 实时打印输出
        
        if "Running on local URL:" in line and not browser_opened:
            match = re.search(r'Running on local URL:\s*(http://\S+)', line)
            if match:
                url = match.group(1)
                print(f"找到本地 URL: {url}")
                threading.Thread(target=open_browser, args=(url,), daemon=True).start()
                browser_opened = True
        
        if "Gradio app started" in line:
            print("Gradio 应用已成功启动！")
            break
        
        # 如果10秒后还没有检测到应用启动，就退出循环
        if time.time() - start_time > 10:
            print("应用启动超时，但页面可能已经打开。如果端口7860没有被占用，那么本地url为：http://127.0.0.1:7860/")
            break
    
    if not url:
        print("❌ 无法找到 Gradio 应用的 URL，请查看环境是否配错，或者手动打开url,如果端口7860没有被占用，那么本地url为：http://127.0.0.1:7860/")
    
    # 继续打印剩余的输出
    for line in iter(process.stdout.readline, ''):
        print(line, end='', flush=True)

def main():
    print(LOGO)
    print("欢迎使用 对弈竞猜结果查询 启动器！")
    
    if not os.path.exists(MAIN_APP):
        print(f"错误：找不到 {MAIN_APP} 文件。")
        print("请确保 main.py 文件在当前目录中。")
        input("按任意键退出...")
        sys.exit(1)
    
    run_app()

if __name__ == "__main__":
    main()
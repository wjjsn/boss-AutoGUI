import webbrowser
import time
import os
import sys
import pyautogui
import traceback

# 开启安全保护：鼠标移动到屏幕左上角 (0,0) 可立即停止脚本
pyautogui.FAILSAFE = True

import numpy as np
from scipy.interpolate import splprep, splev

def bezier_curve(p0, p1, p2, t):
    """简单二次贝塞尔曲线"""
    return (1-t)**2 * np.array(p0) + 2*(1-t)*t * np.array(p2) + t**2 * np.array(p1)

def human_curve_move(target_x, target_y, duration=0.8):
    start = pyautogui.position()
    
    # 控制点：在起点和终点之间随机偏移，形成曲线
    ctrl_x = (start[0] + target_x) / 2 + random.randint(-150, 150)
    ctrl_y = (start[1] + target_y) / 2 + random.randint(-100, 100)
    
    steps = max(20, int(duration * 60))  # 按帧数平滑移动
    for i in range(steps):
        t = i / steps
        # 应用缓动让曲线移动也带速度变化
        t_eased = pyautogui.easeInOutQuad(t)
        x, y = bezier_curve(start, (target_x, target_y), (ctrl_x, ctrl_y), t_eased)
        pyautogui.moveTo(x, y, duration=0.01)  # 微小步进移动
        time.sleep(duration / steps)

def process_single_url(url, button_image='button.png', delay_load=5, delay_click=2):
    print(f"\n正在处理网址: {url}")
    
    # 1. 打开默认浏览器
    webbrowser.open(url)
    
    # 2. 等待网页加载完成
    time.sleep(delay_load)
    
    clicked = False
    try:
        # 3. 尝试图像识别定位按钮
        # 确保提前截好了按钮图保存为 button.png
        button_location = pyautogui.locateOnScreen(button_image, confidence=0.9)
        
        if button_location:
            button_x, button_y = pyautogui.center(button_location)
            # 模拟人类平滑移动并点击
            human_curve_move(button_x, button_y, duration=0.8)
            pyautogui.click()
            print(" -> 点击成功！")
            clicked = True
        else:
            print(" -> 未在屏幕上找到目标按钮，尝试使用固定坐标（备份方案）...")
            # 如果按钮位置绝对固定，可以取消下行注释
            # pyautogui.click(x=500, y=400)
            print("未找到目标按钮")
            
    except Exception as e:
        print(f" -> 操作异常: {e}")
        traceback.format_exc()
        
        
    
    # 4. 等待请求发送完毕，然后关闭当前标签页
    time.sleep(delay_click)
    pyautogui.hotkey('ctrl', 'w') 
    
    return clicked

def main():
    json_file = 'urls.txt'
    if not os.path.exists(json_file):
        print(f"错误: 找不到 {json_file} 文件，请在同级目录下创建。")
        sys.exit(1)
        
    with open(json_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
    print(f"已加载 {len(urls)} 个任务，准备开始批处理...")
    time.sleep(2)  # 给用户2秒钟准备，不要动鼠标
    
    for index, url in enumerate(urls, 1):
        print(f"进度: [{index}/{len(urls)}]")
        process_single_url(url)
        # 每个网页任务之间稍微停顿，防止浏览器卡死
        time.sleep(random.randint(1, 10))

    print("\n所有批处理任务已完成！")

if __name__ == "__main__":
    main()
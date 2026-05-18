import json
import os
import random
import sys
import time
import traceback
import webbrowser

import numpy as np
import pyautogui
from dotenv import load_dotenv
from openai import OpenAI

pyautogui.FAILSAFE = True

load_dotenv()

BASRURL = os.getenv("BASRURL")
APIKEY = os.getenv("APIKEY")
RESUME = os.getenv("RESUME")
if RESUME is None:
    raise ValueError("RESUME environment variable is not set")
else:
    RESUME = RESUME.replace("\\n", "\n")

# 初始化 OpenAI 客户端
client = OpenAI(api_key=APIKEY, base_url=BASRURL)


def bezier_curve(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    t: float,
) -> np.ndarray:
    """Simple quadratic Bézier curve."""
    return (
        (1 - t) ** 2 * np.array(p0)
        + 2 * (1 - t) * t * np.array(p2)
        + t**2 * np.array(p1)
    )


def human_curve_move(target_x: float, target_y: float, duration: float = 0.3):
    start = pyautogui.position()

    # 控制点：在起点和终点之间随机偏移，形成曲线
    ctrl_x = (start[0] + target_x) / 2 + random.randint(-150, 150)
    ctrl_y = (start[1] + target_y) / 2 + random.randint(-100, 100)

    steps = max(15, int(duration * 60))
    for i in range(steps):
        t = i / steps
        # 应用缓动让曲线移动也带速度变化
        t_eased = pyautogui.easeInOutQuad(t)
        x, y = bezier_curve(start, (target_x, target_y), (ctrl_x, ctrl_y), t_eased)
        pyautogui.moveTo(x, y)
        time.sleep(duration / steps)  # 仅保留一个可控延迟


def call_llm(resume, description: str) -> str:
    """调用 LLM API 处理职位描述"""
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "system",
                "content": f"""你是一名有十年经验的简历优化师。
我现在需要求职，所以请你来写求职招呼语来向boss或hr打招呼，你需要代入我的身份也就是一名求职者。注意！打招呼语的前20个字最重要，前20个字一定要突显我对这个岗位的掌握情况，前20个字一定要吸睛，让老板想招我！不要啰哩叭嗦，注意你面对的是老板，不是我。你说的话会直接发送给boss或hr，所以不要回复markdown，只准回复纯文本。
## 我的简历:
```
{resume}
```
## 我的职位描述:
```
{description}
```
""",
            },
            {"role": "user", "content": description},
        ],
    )
    content = response.choices[0].message.content
    return content if content is not None else ""


def process_single_url(
    url,
    llm_result,
    button_image="button.png",
    delay_load=5,
    delay_click=2,
):
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
    pyautogui.hotkey("ctrl", "w")

    return clicked


def main():
    json_file = "boss_jobs.json"
    if not os.path.exists(json_file):
        print(f"错误: 找不到 {json_file} 文件，请在同级目录下创建。")
        sys.exit(1)

    # 从 JSON 文件读取数据
    with open(json_file, encoding="utf-8") as f:
        jobs = json.load(f)

    print(f"已加载 {len(jobs)} 个任务，准备开始批处理...")
    time.sleep(2)  # 给用户2秒钟准备，不要动鼠标

    for index, job in enumerate(jobs, 1):
        url = job.get("url")
        description = job.get("description", "")

        # 调用 LLM 处理职位描述
        print(f"\n[{index}/{len(jobs)}] 调用LLM...")
        llm_result = call_llm(RESUME, description)
        print(f"LLM返回: {llm_result}")

        time.sleep(1)

        # process_single_url(url, llm_result)
        # 每个网页任务之间稍微停顿，防止浏览器卡死
        time.sleep(random.randint(1, 10))

    print("\n所有批处理任务已完成！")


if __name__ == "__main__":
    main()

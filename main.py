import json
import os
import random
import sys
import time
import traceback
import webbrowser

import numpy as np
import pyautogui
import pyperclip
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
                "content": """你是一名有十年经验的简历优化师。用户是求职者，要写一句发给老板/HR的打招呼语。
约束条件：
1. 整体语气专业、自信、简洁，90字左右。
2. 打招呼语的前20个字最重要，前20个字一定要将用户的简历语JD关联起来，前20个字一定要吸睛（不要说“你好”等废话，20个字宝贵），让老板想招用户！
3. 你面对的是老板，不是用户。你说的话会直接发送给boss或hr，不要回复markdown，直接回复纯文本。
4. 重点应该关注如何将用户的简历语JD关联起来。不要仅仅罗列技术名词，而是应该直击岗位的关键需求！
""",
            },
            {
                "role": "user",
                "content": f"""## 我的简历:
```
{resume}
```
## 我的职位描述:
```
{description}
```
""",
            },
        ],
    )
    content = response.choices[0].message.content
    return content if content is not None else ""


def send_image_resume(
    send_image_button="send_image_button.png",
    imagelib_button="imagelib_button.png",
    resume_image="resume_image.png",
):
    button_location = pyautogui.locateOnScreen(send_image_button, confidence=0.9)
    if button_location:
        button_x, button_y = pyautogui.center(button_location)
        # 模拟人类平滑移动并点击
        human_curve_move(button_x, button_y)
        pyautogui.click()
        time.sleep(1.5)
        # pyautogui.write(r"C:\Users\wjjsn\Pictures\resume.png")
        pyperclip.copy(r"C:\Users\wjjsn\Pictures\resume.png")
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")
        # pyautogui.hotkey("alt", "o")
    return False


def process_single_url(
    url, llm_result, lijigbts_button="lijigbts_button.png", delay_load=5
):
    print(f"\n正在处理网址: {url}")

    # 1. 打开默认浏览器
    webbrowser.open(url)

    # 2. 等待网页加载完成
    time.sleep(delay_load)

    clicked = False
    try:
        # 3. 尝试图像识别定位按钮
        button_location = pyautogui.locateOnScreen(lijigbts_button, confidence=0.9)

        if button_location:
            button_x, button_y = pyautogui.center(button_location)
            # 模拟人类平滑移动并点击
            human_curve_move(
                button_x + random.uniform(-25, 25), button_y + random.uniform(-25, 25)
            )
            pyautogui.click()
            print(" -> 立即沟通点击成功！")
            time.sleep(1)

    except pyautogui.ImageNotFoundException:
        print(" -> 无立即沟通按钮，跳过")
        return False
    except Exception as e:
        print(f" -> 操作异常: {e}")
        traceback.print_exc()
    try:
        button_location = pyautogui.locateOnScreen(
            "close_after_lijigbts.png", confidence=0.98
        )

        if button_location:
            button_x, button_y = pyautogui.center(button_location)
            # 模拟人类平滑移动并点击
            human_curve_move(
                button_x + random.uniform(-10, 10), button_y + random.uniform(-10, 10)
            )
            pyautogui.click()
            print(" -> 关闭对话框成功！")
            time.sleep(1)

    except pyautogui.ImageNotFoundException:
        print(" -> 无关闭对话按钮，错误")
    except Exception as e:
        print(f" -> 操作异常: {e}")
        traceback.print_exc()
    try:
        button_location = pyautogui.locateOnScreen(
            "jixugbts_button.png", confidence=0.9
        )
        if button_location:
            button_x, button_y = pyautogui.center(button_location)
            # 模拟人类平滑移动并点击
            human_curve_move(
                button_x + random.uniform(-25, 25), button_y + random.uniform(-25, 25)
            )
            pyautogui.click()
            print(" -> 继续沟通点击成功！")
            time.sleep(1)
    except pyautogui.ImageNotFoundException:
        print(" -> 无继续沟通按钮，错误")
    except Exception as e:
        print(f" -> 操作异常: {e}")
        traceback.print_exc()
    time.sleep(1)
    send_image_resume()
    time.sleep(1)
    pyperclip.copy(llm_result)
    try:
        button_location = pyautogui.locateOnScreen(
            "send_image_button.png", confidence=0.9
        )
        if button_location:
            button_x, button_y = pyautogui.center(button_location)
            # 模拟人类平滑移动并点击
            human_curve_move(
                button_x + random.uniform(-25, 25), button_y + random.uniform(100, 150)
            )
            pyautogui.click()
    except pyautogui.ImageNotFoundException:
        print(" -> 无法输入，错误")
    pyautogui.hotkey("ctrl", "v")
    time.sleep(random.uniform(1.0, 3.0))
    pyautogui.press("enter")
    time.sleep(random.uniform(1.0, 3.0))
    clicked = True

    # 4. 等待请求发送完毕，然后关闭当前标签页
    pyautogui.hotkey("ctrl", "w")

    return clicked


def load_processed_urls(filename="processed_urls.txt"):
    if os.path.exists(filename):
        with open(filename, encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_processed_url(url, filename="processed_urls.txt"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(url + "\n")


def main():
    json_file = "boss_jobs.json"
    if not os.path.exists(json_file):
        print(f"错误: 找不到 {json_file} 文件，请在同级目录下创建。")
        sys.exit(1)

    # 从 JSON 文件读取数据
    with open(json_file, encoding="utf-8") as f:
        jobs = json.load(f)

    processed_urls = load_processed_urls()
    print(
        f"已加载 {len(jobs)} 个任务，已处理 {len(processed_urls)} 个，准备开始批处理..."
    )
    time.sleep(2)

    for index, job in enumerate(jobs, 1):
        url = job.get("url")

        if url in processed_urls:
            print(f"\n[{index}/{len(jobs)}] URL已处理过，跳过: {url}")
            continue

        description = job.get("description", "")

        # 调用 LLM 处理职位描述
        print(f"\n[{index}/{len(jobs)}] 调用LLM...")
        llm_result = call_llm(RESUME, description)
        print(f"LLM返回: {llm_result}")

        time.sleep(1)

        process_single_url(url, llm_result)
        save_processed_url(url)
        processed_urls.add(url)

    print("\n所有批处理任务已完成！")


if __name__ == "__main__":
    main()

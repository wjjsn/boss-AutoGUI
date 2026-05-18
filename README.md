# Boss 直聘自动沟通工具

自动化求职工具，通过 AI 生成个性化招呼语并自动发送简历。

## 功能

- 读取 `boss_jobs.json` 中的职位列表，可使用[这个仓库](https://github.com/wjjsn/boss_crawler_analyzer)生成
- 调用 LLM 根据简历和职位描述生成招呼语
- 自动打开浏览器，点击"立即沟通"按钮
- 自动发送图片简历和 AI 生成的招呼语

## 效果演示

<img width="1080" height="506" alt="output" src="https://github.com/user-attachments/assets/e2ad4d3d-fe9d-4b69-950b-fbbbf1929173" />


## 环境配置

1. 复制 `.env.example` 为 `.env`
2. 填入以下环境变量：
   - `BASRURL` - API 地址
   - `APIKEY` - API 密钥
   - `RESUME` - 简历内容（支持换行）

## 运行

```bash
uv.exe sync #先同步环境
uv.exe run main.py
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `main.py` | 主程序入口 |
| `boss_jobs.json` | 职位数据（需手动创建） |
| `*.png` | 按钮定位图片 |

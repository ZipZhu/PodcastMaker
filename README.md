# 🎙️ PodcastMaker

**本地运行的多角色中文播客自动生成工具**
将文字脚本一键转为自然、清晰、可回听的对话播客音频。

> 设计目标：**让“记录思考”这件事，比写字还轻松**

---

## ✨ Features

* 🎭 **双角色对话播客**

  * `A`：女生 ｜ `B`：男生
  * 支持同一角色连续发言，不强制轮流

* 🗣️ **高质量中文语音**

  * 基于 **Microsoft Edge TTS**
  * 无需 GPU / 无需模型下载

* 📂 **自动化输出管理**

  * 每次运行按时间生成独立目录
  * 自动保存：

    * 完整播客音频
    * 分段音频
    * 本次使用的脚本文本

* ⚡ **一键运行**

  * 双击 `run.bat`
  * 任务完成后自动关闭并发送系统通知

---

## 📁 Project Structure

```
PodcastMaker/
├── 点我运行.bat              # 一键启动
├── run.ps1              # 主执行脚本
├── make_podcast_edge.py # 核心逻辑
├── script.txt           # 播客脚本（主要编辑）
├── outputs/
│   └── YYYYMMDD_HHMMSS/
│       ├── podcast_*.mp3
│       ├── script_*.txt
│       └── segments/
└── README.md
```

---

## 🧾 Script Format (`script.txt`)

**规则：**

* 每行以角色标识开头：

  * `A：` 女生
  * `B：` 男生
* 一行可包含多句
* 角色可连续多行
* 不要求严格轮流

**示例：**

```
A：今天我们聊聊最近让我反复思考的一件事。
A：这篇文章我读了三遍，每一遍感受都不同。

B：是哪一段触动你最深？

A：作者说“选择本身就是一种放弃”。
```

---

## ▶️ Usage

1. 编辑播客脚本：

   ```text
   script.txt
   ```

2. 双击运行：

   ```text
   run.bat
   ```

3. 在 `outputs/` 中收听生成的播客音频

---

## 🧠 AI Script Prompt（推荐）

* 输出格式必须为 `A：` / `B：`
* A 为女生，B 为男生
* 语气自然、偏真实对话
* 可连续多行同一角色
* 每行适合语音朗读
* 不输出任何说明文字

生成内容可直接保存为 `script.txt` 使用。

---

## ⚙️ Requirements

* Python **3.10+**
* `edge-tts`
* `ffmpeg`
* Windows 10 / 11

---

## 📝 License
个人使用、学习和研究可免费使用。
商业用途请查看微软Edge TTS条款。
---

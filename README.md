# 🤖 Office Agent - 智能办公助手

一个基于大语言模型的多功能办公辅助系统，集成智能对话、邮件处理、文档问答、会议纪要四大核心功能。


## 📌 项目简介

Office Agent 是一个面向日常办公场景的 AI 助手系统，旨在帮助用户提高工作效率。项目采用 RAG（检索增强生成）技术实现文档智能问答，通过 Function Calling 机制让 AI 能够调用真实工具（如发送邮件），并集成了语音识别能力。项目定位为个人学习与面试展示项目，展示 AI 应用开发的全栈能力。


## ✨ 功能列表

- 💬 智能对话：多轮对话，带记忆功能，支持语音输入，技术：DeepSeek API + Streamlit
- 📧 邮件助手：AI 撰写/润色邮件，支持真实 SMTP 发送，技术：Prompt Engineering + SMTP
- 📄 文档问答：上传 PDF/TXT，AI 基于内容回答问题，技术：RAG + ChromaDB + 向量检索
- 📝 会议纪要：录音转文字，AI 整理成结构化纪要，技术：语音识别 + 信息提取


## 🛠️ 技术栈

- 前端：Streamlit
- AI 服务：DeepSeek API（大模型）、智谱 GLM-ASR（语音识别）
- 核心框架：LangChain（Agent 编排）、ChromaDB（向量数据库）
- 工具集成：SMTP（邮件发送）、SiliconFlow API（向量化）


## 📁 项目结构
```
office-agent/
├── app.py                         # 应用主入口
├── pages/                         # 功能页面
│   ├── 01_智能对话.py              # 智能对话
│   ├── 02_邮件助手.py              # 邮件助手
│   ├── 03_文档问答.py              # 文档问答
│   └── 04_会议纪要.py              # 会议纪要
├── config/
│   └── .env                        # API 密钥配置
├── data/
│   └── chroma_db/                  # 向量数据库存储
├── components/
│   └── speech_to_text.html         # 语音识别组件
├── requirements.txt                # 项目依赖
└── README.md                       # 项目文档
```


## 🚀 快速开始

1. 克隆项目：
   git clone https://github.com/wangyajing626/office-agent.git
   cd office-agent

2. 创建虚拟环境：
   python -m venv venv
   Windows: venv\Scripts\activate
   Mac/Linux: source venv/bin/activate

3. 安装依赖：
   pip install -r requirements.txt

4. 配置 API 密钥：
   在 config/.env 文件中填入你的 API 密钥：
   DEEPSEEK_API_KEY=你的DeepSeek密钥
   ZHIPU_API_KEY=你的智谱密钥（语音识别需要）
   EMAIL_SENDER=你的邮箱@qq.com（邮件发送需要）
   EMAIL_AUTH_CODE=你的邮箱授权码（邮件发送需要）

5. 运行应用：
   streamlit run app.py
   浏览器访问 http://localhost:8501


## 📸 功能预览

- 智能对话：支持多轮对话，带记忆功能，可语音输入
- 邮件助手：输入要点，AI 自动生成正式邮件，支持一键发送
- 文档问答：上传 PDF 文档，AI 基于内容回答问题，并显示引用来源
- 会议纪要：录音转文字，AI 自动提取决策和待办事项


## 🧠 核心技术原理

RAG（检索增强生成）：
文档上传 → 切片 → 向量化 → 存入 ChromaDB → 用户提问 → 问题向量化 → 相似度检索 → AI 生成回答

Function Calling：
用户输入 → AI 分析 → 决定调用工具 → 执行 → 返回结果


## ⚠️ 注意事项

- 项目使用 Python 3.10+
- API 调用会产生费用，DeepSeek 价格较低，建议先充值 5-10 元测试
- 语音识别功能需要配置智谱 API Key
- 请勿将 .env 文件提交到公开仓库


## 📝 开发心得

遇到的主要挑战：
1. Windows 安全策略拦截 _regex.pyd 和 llvmlite.dll，最终通过切换到 API 方案解决
2. 向量化服务从本地 sentence-transformers 迁移到 SiliconFlow API
3. SMTP 授权码的获取与配置

技术收获：
深入理解了 RAG 的完整流程，掌握了 LangChain 的 Agent 开发模式，学会了 API 集成和错误处理。


## 🔮 未来规划

- 接入飞书/钉钉机器人
- 支持更多文档格式（DOCX、Markdown）
- 增加日程管理功能
- 多 Agent 协作

## 👨‍💻 作者

GitHub: wangyajing626

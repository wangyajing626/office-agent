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
- 后端：FastAPI + JWT 鉴权
- AI 服务：DeepSeek API（大模型）、智谱 GLM-ASR（语音识别）
- 核心框架：LangChain（Agent 编排）、ChromaDB（向量数据库）
- 工具集成：SMTP（邮件发送）、SiliconFlow API（向量化）
- 数据库：MySQL + Redis

## 📁 项目结构
```
office-agent/
├── app.py # 应用主入口
├── pages/ # 前端页面
│ ├── 智能对话.py # 智能对话
│ ├── 邮件助手.py # 邮件助手
│ ├── 文档问答.py # 文档问答
│ ├── 会议纪要.py # 会议纪要
│ ├── 登录.py # 用户登录
│ └── 注册.py # 用户注册
├── backend/ # FastAPI 后端
│ ├── main.py # 后端入口
│ ├── api/ # API 接口
│ │ ├── users.py # 用户注册/登录
│ │ ├── chat.py # 智能对话
│ │ ├── email.py # 邮件生成
│ │ ├── rag.py # 文档问答
│ │ └── meeting.py # 会议纪要
│ ├── core/ # 核心模块
│ │ ├── auth.py # JWT 认证
│ │ ├── database.py # 数据库连接
│ │ └── dependencies.py # 鉴权依赖
│ ├── models/ # 数据模型
│ └── services/ # 业务逻辑
├── config/
│ └── .env # API 密钥配置
├── docker-compose.yml # Docker 部署配置
├── requirements.txt # 项目依赖
└── README.md # 项目文档                    # 项目文档
```

## 🚀 快速开始

### 1. 克隆项目

git clone https://github.com/wangyajing626/office-agent.git
cd office-agent

### 2. 启动 MySQL + Redis（Docker 方式）

docker-compose up -d

### 3. 配置后端环境

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

### 4. 配置 API 密钥

在 config/.env 文件中填入：

DEEPSEEK_API_KEY=你的DeepSeek密钥
ZHIPU_API_KEY=你的智谱密钥
SILICONFLOW_API_KEY=你的硅基流动密钥

### 5. 启动后端

uvicorn main:app --reload --port 8000

### 6. 启动前端（新终端）

streamlit run app.py

浏览器访问 http://localhost:8501


## 📸 功能预览

- 智能对话：支持多轮对话，带记忆功能，可语音输入
- 邮件助手：输入要点，AI 自动生成正式邮件，支持一键发送
- 文档问答：上传 PDF 文档，AI 基于内容回答问题，并显示引用来源
- 会议纪要：录音转文字，AI 自动提取决策和待办事项


## 🧠 核心技术原理

RAG（检索增强生成）：
文档上传 → 切片 → 向量化 → 存入 ChromaDB → 用户提问 → 问题向量化 → 相似度检索 → AI 生成回答 → 显示引用来源

用户认证流程：
注册 → 密码加密（bcrypt）→ 存入 MySQL → 登录 → 验证密码 → 生成 JWT Token → 前端保存 → 请求 API → 携带 Token → 后端验证 → 返回数据


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
4. Windows 安全策略拦截：_regex.pyd 和 llvmlite.dll 被系统阻止加载，最终通过切换到 API 方案解决
5. 向量化服务选型：从本地 sentence-transformers 迁移到 SiliconFlow API
6. 前后端分离改造：将原 Streamlit 单体应用拆分为 FastAPI 后端 + Streamlit 前端

技术收获：
- 深入理解 RAG 完整流程
- 掌握 JWT 用户认证与密码加密
- 学会 FastAPI 分层架构设计


## 🔮 未来规划

- 接入飞书/钉钉机器人
- 支持更多文档格式（DOCX、Markdown）
- 增加日程管理功能
- 多 Agent 协作

## 👨‍💻 作者

GitHub: wangyajing626

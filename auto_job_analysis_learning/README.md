# 求职岗位智能分析系统（开源学习版）

> **本项目仅为「求职岗位智能分析、文本解析、AI匹配学习项目」**
> **不包含任何自动化投递、页面操作或平台批量操作功能**
> **仅用于个人技术复盘与学习展示**

---

## 项目概述

基于 **LangChain + DeepSeek API** 的求职岗位智能分析工具，能够：
- 📄 读取 PDF 简历并提取文本
- 🔍 解析岗位描述（JD）文本
- 📊 五档岗位匹配度评分
- 📝 自动生成求职信
- 📈 记录分析历史

### 核心技术栈

| 技术 | 用途 |
|------|------|
| LangChain 0.0.354 | AI 编排框架 |
| DeepSeek Chat | AI 模型（兼容 OpenAI API） |
| python-dotenv | 环境变量管理 |
| PyPDFLoader | PDF 简历解析 |

---

## 快速开始

### 1. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 DeepSeek API Key
# 获取地址：https://platform.deepseek.com/
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 放置简历

将你的 PDF 格式简历放入 `auto_job_analysis/resume/` 目录

### 4. 运行

```bash
python auto_job_analysis/main.py
```

---

## 评分规则（五档）

| 梯队 | 分数 | 说明 |
|------|------|------|
| 第一梯队 | 90-100 | 运营助理、电商运营、数据运营等 |
| 第二梯队 | 78-88 | 用户运营、内容运营 |
| 第三梯队 | 70-77 | 运营专员、互联网运营等 |
| 第四梯队 | 60-68 | 新媒体运营 |
| 不匹配 | 0 | 专业背景不匹配 |

---

## 项目结构

```
auto_job_analysis_learning/
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略规则
├── requirements.txt        # Python 依赖
├── README.md               # 本文件
└── auto_job_analysis/      # 核心模块
    ├── __init__.py
    ├── main.py             # 入口文件（交互式分析）
    ├── langchain_functions.py  # LangChain + DeepSeek 核心引擎
    ├── jd_analyzer.py      # JD 纯文本分析模块
    ├── prompts.py          # 提示词模板
    ├── functions.py        # OpenAI Assistants 接口
    └── resume/             # 简历目录（请放置你的 PDF 简历）
```

---

## 功能说明

### ✅ 保留的核心能力

- LangChain 框架架构
- DeepSeek 模型调用
- JD 文本解析与结构化
- 五档岗位评分规则
- 异常容错处理
- 日志与分析记录体系
- 完整项目依赖

### ❌ 已移除的风险功能

- 浏览器自动化操作（Selenium）
- 自动点击与投递
- 页面劫持与反检测
- 风控绕过机制
- 批量自动化操作
- 平台特定适配代码

---

## 许可证

本项目仅用于学习和研究目的。
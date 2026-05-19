# RagasToTestRag

基于 [Ragas](https://github.com/explodinggradients/ragas) 的 **RAG 系统全流程工具**，支持**测试集生成**和**RAG 系统评测**两大核心功能。可本地 Ollama 运行，完全免费！

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![Ragas](https://img.shields.io/badge/Ragas-0.1.10-orange)](https://github.com/explodinggradients/ragas)

---

## ✨ 功能特性

### 📝 测试集生成
- 📄 **多格式文档支持**：PDF、TXT、DOCX、DOC、XLSX
- 📁 **批量上传**：可同时上传多个文档，合并生成一份测试集
- 🤖 **灵活 LLM 选择**：Ollama 本地运行（免费）/ DeepSeek / OpenAI
- 🌐 **高质量 Embedding**：HuggingFace multilingual-e5-large（中英文通用）
- 🇨🇳 **原生中文支持**：自动生成中文问答对（需配合中文模型如 Qwen2.5）
- ⚡ **GPU 加速**：CUDA 加速（速度提升 3-15 倍）
- 🎨 **现代化 Web UI**：拖拽上传，实时进度，结果预览与下载

### 📊 RAG 系统评测
- 🔬 **四大核心指标**：
  - **上下文精确度 (Context Precision)** — 检索到的上下文有多少是真正相关的
  - **上下文召回率 (Context Recall)** — 相关上下文有多少被成功检索到
  - **回答忠实度 (Faithfulness)** — 回答是否基于提供的上下文（不含幻觉）
  - **回答相关性 (Answer Relevance)** — 回答是否与问题相关
- 📋 **逐条明细**：每个样本的详细评分表格
- 📈 **综合评分**：等级评定（🟢优秀 / 🟡良好 / 🟠一般 / 🔴较差）
- 📥 **完整报告**：JSON 格式下载，便于后续分析

---

## 🚀 快速开始

### 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | ≥ 3.10 | 推荐 3.12 |
| Ollama | 最新版 | [下载地址](https://ollama.com) |
| GPU | 可选 | NVIDIA CUDA 12.x（RTX 30/40 系列）|

### 步骤 1: 安装 Ollama 并拉取模型

```bash
# 安装 Ollama: https://ollama.com
ollama serve                    # 启动 Ollama 服务

# 拉取 LLM 模型（根据你的语言需求选择）
ollama pull gemma2:latest       # 英文测试集（默认）
ollama pull qwen2.5:7b          # 中文测试集（推荐）
```

> ⚠️ **重要：模型语言能力说明**
>
> 不同 LLM 模型生成的问题语言不同，`TEST_LANGUAGE=chinese` 只是向模型发送中文指令，**实际输出语言取决于模型本身的能力**：
>
> | 模型 | 生成问题语言 | 推荐场景 |
> |------|------------|----------|
> | **gemma2:latest** | 🇬🇧 仅英文 | 英文文档 / 英文测试集 |
> | **qwen2.5:7b** | 🇨🇳 中文 | 中文文档 / 中文测试集（推荐）|
> | **qwen2.5:14b** | 🇨🇳 中文 | 更高质量中文（需更多显存）|
> | **deepseek-chat** | 🇨🇳+🇬🇧 中英皆可 | API 方式，质量最佳 |
>
> 如需生成**中文问答对**，请使用 `qwen2.5` 系列或 `deepseek`，不要使用 `gemma2`。

### 步骤 2: 克隆项目并安装依赖

```bash
git clone https://github.com/CuiTengG/RagasToTestRag.git
cd RagasToTestRag

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

> 💡 **首次安装会下载 HuggingFace embedding 模型 (~2GB) 和 PyTorch GPU 包 (~2.5GB)，请耐心等待**

### 步骤 3: 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# ===== LLM 配置 =====
LLM_PROVIDER=ollama                              # ollama / deepseek / openai
OLLAMA_MODEL_NAME=qwen2.5:7b                     # 中文用 qwen2.5，英文用 gemma2
OLLAMA_BASE_URL=http://localhost:11434           # Ollama 地址

# ===== Embedding 配置 =====
EMBEDDING_PROVIDER=huggingface                   # huggingface / openai
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-base  # 多语言嵌入模型（base 版本更轻量）

# ===== 计算设备 =====
DEVICE=auto                                      # auto / cuda / cpu

# ===== 测试集语言 =====
TEST_LANGUAGE=chinese                            # chinese / english（需配合对应语言能力的模型）

# ===== API 密钥（使用 DeepSeek/OpenAI 时必填）=====
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.deepseek.com/v1      # DeepSeek 或 OpenAI 地址
OPENAI_MODEL_NAME=deepseek-chat                  # 对应模型名
```

### 步骤 4: 启动应用

```bash
python app.py
```

启动后访问 http://localhost:5000 ，你会看到类似输出：

```
==================================================
🚀 Ragas 测试集生成器启动中...
==================================================

📌 LLM 提供商: ollama
   - Ollama 模型: gemma2:latest
   - Ollama 地址: http://localhost:11434

📌 Embedding 提供商: huggingface
   - 模型: intfloat/multilingual-e5-large

📌 计算设备: auto
   ✓ GPU: NVIDIA GeForce RTX 4090

访问地址: http://localhost:5000
==================================================
```

---

## 📖 使用指南

### 功能一：生成测试集 📝

**流程**: `上传文档 → 文档分块 → Ragas LLM 生成问答 → 过滤验证 → 下载 JSON`

1. 打开 http://localhost:5000
2. 点击或拖拽上传一个或多个文档（PDF / TXT / DOCX / DOC / XLSX）
3. 设置测试集大小（1-50 条，默认 10 条）
4. 点击"🚀 生成测试集"
5. 等待处理完成（首次需下载模型）
6. 预览前 5 条数据，点击"⬇️ 下载完整测试集"

#### 生成的测试集 JSON 格式示例

```json
[
  {
    "question": "林长的主要职责是什么？",
    "ground_truth": "林长负责组织领导责任区域的森林资源保护和发展工作",
    "contexts": ["林长制度规定各级林长要落实...", "森林资源保护是林长的首要任务..."],
    "answer": null,
    "evolution_type": "simple"
  }
]
```

### 功能二：评测 RAG 系统 📊

**流程**: `收集 RAG 输出 → 整理评测数据 → 上传文件 → 四大指标计算 → 评分报告`

1. 打开 http://localhost:5000/evaluate
2. 准备评测数据文件（CSV / JSON / XLSX 格式）
3. 上传文件，点击"🔬 开始评测"
4. 查看：
   - 🎯 **综合得分卡片**（样本数 + 总分 + 等级）
   - 📊 **四大指标卡片**（每个指标的分数 + 等级 + 含义说明）
   - 📋 **逐条明细表**（每条数据的各项指标得分）
5. 点击"⬇️ 下载完整评测结果"

#### 评测数据格式要求

| 字段 | 必需 | 类型 | 说明 |
|------|:--:|------|------|
| `question` | ✅ | string | 用户提出的问题 |
| `answer` | ✅ | string | 你的 RAG 系统生成的回答 |
| `contexts` | ✅ | list/string | 检索到的上下文（JSON 数组字符串或列表）|
| `ground_truth` | ⭕ | string | 标准答案（可选，提升 Context Recall 准确度）|

**CSV 示例：**

```csv
question,answer,contexts,ground_truth
林长的主要职责是什么？,林长负责组织领导责任区域的森林资源保护和发展。,"[""林长制度规定...""，""各级林长要落实...""]",林长负责森林资源保护和发展
如何考核林长？,考核主要看森林覆盖率和生态保护成效。,"[""考核指标包含...""，""评价标准源于政策...""]",
```

**JSON 示例：**

```json
[
  {
    "question": "林长的主要职责是什么？",
    "answer": "林长负责组织领导责任区域的森林资源保护和发展。",
    "contexts": ["林长制度规定...", "各级林长要落实..."],
    "ground_truth": "林长负责森林资源保护和发展"
  }
]
```

---

## 📁 项目结构

```
RagasToTestRag/
├── app.py                    # Flask 主程序（含完整中文注释）
├── requirements.txt          # Python 依赖清单（基于实际环境版本）
├── .env.example              # 环境变量配置模板
├── .gitignore                # Git 忽略规则
├── GPU_INSTALL_GUIDE.md      # PyTorch GPU 安装详细指南
├── README.md                 # 项目说明文档
├── templates/
│   ├── index.html            # 测试集生成页面（含 JS 注释）
│   └── evaluate.html         # RAG 评测页面（含 JS 注释）
└── uploads/                  # 上传文件目录（已 Git 忽略）
    └── .gitkeep
```

### 核心模块说明

| 模块 | 路径 | 功能 |
|------|------|------|
| **文档加载** | [app.py:38-96](app.py#L38-L96) | 支持 PDF/TXT/DOCX/DOC/XLSX 五种格式 |
| **LLM 工厂** | [app.py:108-152](app.py#L108-L152) | 动态切换 Ollama/DeepSeek/OpenAI |
| **Embedding 工厂** | [app.py:166-216](app.py#L166-L216) | HuggingFace/OpenAI 双方案 + 降级备选 |
| **测试集生成** | [app.py:218-298](app.py#L218-L298) | Ragas TestsetGenerator 中文指令注入 |
| **RAG 评测** | [app.py:310-440](app.py#L310-L440) | 四大指标计算 + pydantic_v1 兼容性修复 |

---

## 🔧 配置说明

### LLM 提供商对比

| 提供商 | 成本 | 延迟 | 语言支持 | 适用场景 | 环境变量 |
|--------|:--:|:--:|:------:|----------|----------|
| **Ollama (Qwen2.5)** | 🆓 免费 | ~30s/条 | 🇨🇳 中文 | 中文文档 / 本地开发 | `OLLAMA_MODEL_NAME=qwen2.5:7b` |
| **Ollama (Gemma2)** | 🆓 免费 | ~30s/条 | 🇬🇧 英文 | 英文文档 / 本地开发 | `OLLAMA_MODEL_NAME=gemma2:latest` |
| **DeepSeek** | 💰 低 | ~2s/条 | 🇨🇳🇬🇧 中英 | 生产环境 / 中文优化 | `LLM_PROVIDER=deepseek` |
| **OpenAI** | 💰💰 高 | ~1s/条 | 🇬🇧 英文为主 | 高质量英文场景 | `LLM_PROVIDER=openai` |

> 💡 **中文场景推荐**: Ollama + Qwen2.5（免费）或 DeepSeek API（高质量）

### Embedding 方案对比

| 提供商 | 模型 | 大小 | 语言 | 环境变量 |
|--------|------|:--:|------|----------|
| **HuggingFace** | multilingual-e5-large | ~2GB | 中英日韩等 | `EMBEDDING_PROVIDER=huggingface` |
| **OpenAI** | text-embedding-3 | 在线 | 英文为主 | `EMBEDDING_PROVIDER=openai` |

### 计算设备选项

| 设备 | 说明 |
|------|------|
| `auto`（默认）| 自动检测 GPU，不可用则回退 CPU |
| `cuda` | 强制使用 GPU（需 CUDA + PyTorch GPU 版）|
| `cpu` | 强制使用 CPU（无 GPU 时自动选择）|

---

## 📊 评测指标详解

| 指标 | 英文名 | 评测维度 | 计算方式 | 满分 |
|------|--------|----------|----------|:--:|
| **上下文精确度** | Context Precision | 检索质量 | 相关上下文 ÷ 检索到的总上下文 | 1.0 |
| **上下文召回率** | Context Recall | 检索完整性 | 检索到的相关上下文 ÷ 所有相关上下文 | 1.0 |
| **回答忠实度** | Faithfulness | 幻觉检测 | 回答中可验证陈述的比例 | 1.0 |
| **回答相关性** | Answer Relevance | 回答质量 | LLM 逆向生成的相关问题与原问题的相关性 | 1.0 |

### 评分等级标准

| 分数范围 | 等级 | 图标 | 行动建议 |
|----------|:--:|:--:|----------|
| **≥ 0.8** | 优秀 | 🟢 | 系统表现良好，可上线使用 |
| **0.6 - 0.8** | 良好 | 🟡 | 部分指标有优化空间 |
| **0.4 - 0.6** | 一般 | 🟠 | 建议改进检索或生成策略 |
| **< 0.4** | 较差 | 🔴 | 存在较大问题，需全面排查 |

---

## ⚡ 性能参考

基于 RTX 4090 + CUDA 12.4 + Ollama Gemma2:

| 操作 | CPU (i7-12700) | GPU (RTX 4090) | 加速比 |
|------|:--------------:|:---------------:|:-----:|
| Embedding 向量化 (E5-Large) | ~120 秒 | **~8 秒** | **~15x** |
| 测试集生成 (10 条) | ~20 分钟 | **~5 分钟** | **~4x** |
| RAG 评测 (10 样本 × 4 指标) | ~10 分钟 | **~3 分钟** | **~3x** |

> 💡 **提示**: GPU 主要加速 Embedding 计算；LLM 推理速度取决于 Ollama/GPU 型号

---

## 🛠️ 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| **Web 框架** | Flask | 3.0.0 |
| **RAG 框架** | Ragas | 0.1.10 |
| **LLM 编排** | LangChain | 0.2.11 |
| **本地 LLM** | Ollama + Gemma2 | latest |
| **Embedding** | sentence-transformers | 5.5.0 |
| **前端** | HTML5 + CSS3 + JavaScript | 原生（无框架）|
| **深度学习** | PyTorch | 2.6.0+cu124 |

---

## 🔄 完整工作流

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  第 1 步         │     │  第 2 步         │     │  第 3 步         │     │  第 4 步         │
│                 │     │                 │     │                 │     │                 │
│  上传文档        │ ──▶ │  调用你的 RAG    │ ──▶ │  整理成 CSV/    │ ──▶ │  四大指标评分    │
│  生成测试集      │     │  系统获取答案    │     │  JSON 格式      │     │  下载详细报告    │
│  (中文问答对)    │     │  和上下文        │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## ❗ 常见问题

<details>
<summary><b>❓ 首次运行报错 SSL_CERT_FILE 不存在？</b></summary>

这是 Windows Conda 环境的已知问题。代码已内置修复（使用 certifi 替代无效的环境变量路径）。如果仍遇到，请确保已安装 certifi:
```bash
pip install certifi
```
</details>

<details>
<summary><b>❓ 评测时报错 No module named 'langchain_core.pydantic_v1'？</b></summary>

这是 langchain-core 版本升级导致的兼容性问题。代码已在导入 Ragas 前动态创建兼容垫片，无需手动处理。
</details>

<details>
<summary><b>❓ 设置了 TEST_LANGUAGE=chinese 但生成的测试集仍是英文？</b></summary>

这是**正常现象**。`TEST_LANGUAGE=chinese` 只是向 LLM 发送"请用中文生成"的指令，但**最终输出语言取决于模型本身的能力**：

- **Gemma2** → 模型训练数据以英文为主，即使收到中文指令也倾向于生成英文
- **Qwen2.5** → 模型原生支持中文，能正确生成中文问答对
- **DeepSeek** → 中英文均支持良好

**解决方案**：切换到中文模型：
```bash
# 拉取中文模型
ollama pull qwen2.5:7b

# 修改 .env
OLLAMA_MODEL_NAME=qwen2.5:7b
TEST_LANGUAGE=chinese

# 重启应用
python app.py
```
</details>

<details>
<summary><b>❓ 如何切换到 DeepSeek API？</b></summary>

修改 `.env` 文件:
```bash
LLM_PROVIDER=deepseek
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_API_BASE=https://api.deepseek.com/v1
OPENAI_MODEL_NAME=deepseek-chat
```
</details>

<details>
<summary><b>❓ 生成速度太慢怎么办？</b></summary>

1. **启用 GPU**: 确保 PyTorch 是 GPU 版本（CUDA 12.4），设置 `DEVICE=cuda`
2. **减少数量**: 将测试集大小从 10 减少到 5
3. **换用更小模型**: 
   - 英文: `gemma2:2b`（2B 参数，速度快）
   - 中文: `qwen2.5:3b` 或 `qwen2.5:1.5b`（中文支持 + 体积小）
4. **切换到 API**: 使用 DeepSeek/API 方式比本地 Ollama 更快
</details>

<details>
<summary><b>❓ 支持哪些文档格式？</b></summary>

| 格式 | 扩展名 | 处理方式 |
|------|--------|----------|
| PDF | `.pdf` | PyPDFLoader |
| 纯文本 | `.txt` | TextLoader |
| Word 新版 | `.docx` | Docx2txtLoader |
| Word 旧版 | `.doc` | textract / antiword |
| Excel | `.xlsx` | UnstructuredExcelLoader |
</details>

---

## ⚠️ 注意事项

1. **首次运行**会下载 HuggingFace embedding 模型（~2GB），请确保网络通畅
2. **Ollama 服务**需要在后台保持运行状态（`ollama serve`）
3. **单次上传限制**为 **50MB**（支持多文件合并）
4. **生成时间**取决于：文档长度 × 测试集大小 × LLM 速度
5. **评测时间**约 **30-60 秒/样本**（4 个指标 × LLM 调用）
6. **GPU 建议**: 如有 NVIDIA 显卡，强烈建议安装 GPU 版 PyTorch（详见 [GPU_INSTALL_GUIDE.md](GPU_INSTALL_GUIDE.md)）

---

## 📄 License

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！贡献流程：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

---

<div align="center">

**Made with ❤️ using Ragas + Ollama + Flask**

If this project helps you, please give it a ⭐!

</div>
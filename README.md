# RagasToTestRag

基于 [Ragas](https://github.com/explodinggradients/ragas) 的 RAG 系统全流程工具，支持**测试集生成**和**RAG 系统评测**两大功能。可本地 Ollama 运行，完全免费！

---

## ✨ 功能特性

### 📝 测试集生成
- 📄 **多格式文档**：PDF、TXT、DOCX、DOC、XLSX
- 📁 **多文件上传**：可同时上传多个文档，合并生成一份测试集
- 🤖 **本地 LLM**：Ollama + Gemma2（无需 API 费用，也支持 DeepSeek/OpenAI）
- 🌐 **多语言 Embedding**：HuggingFace multilingual-e5-large
- 🇨🇳 **中文测试集**：自动生成中文问答对
- ⚡ **GPU 加速**：CUDA 加速（速度提升 3-15 倍）
- 🎨 **Web UI**：拖拽上传，进度显示，结果预览

### 📊 RAG 系统评测
- 🔬 **四大核心指标**：
  - 上下文精确度（Context Precision）
  - 上下文召回率（Context Recall）
  - 回答忠实度（Faithfulness）
  - 回答相关性（Answer Relevance）
- 📋 **逐条明细**：每个样本的详细评分
- 📈 **综合评分**：等级评定（优秀/良好/一般/较差）
- 📥 **结果导出**：JSON 格式完整报告下载

---

## 🚀 快速开始

### 前提条件

1. **安装 Ollama** 并拉取模型：
   ```bash
   # 下载安装: https://ollama.com
   ollama serve
   ollama pull gemma2:latest
   ```

2. **安装 GPU 版 PyTorch**（可选，强烈推荐）：
   ```bash
   # CUDA 12.4 (RTX 30/40 系列)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   
   # 详细说明见 GPU_INSTALL_GUIDE.md
   ```

### 安装依赖

```bash
cd RagasToTestRag
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
```

主要配置项：

```bash
LLM_PROVIDER=ollama                              # LLM 提供商
OLLAMA_MODEL_NAME=gemma2:latest                  # Ollama 模型
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-large  # Embedding 模型
DEVICE=auto                                      # 计算设备: auto / cuda / cpu
TEST_LANGUAGE=chinese                            # 测试集语言: chinese / english
```

### 启动应用

```bash
python app.py
```

访问 http://localhost:5000

---

## 📖 使用指南

### 功能一：生成测试集

```
上传文档 → 文档分块 → Ragas 生成 → 下载 JSON 测试集
```

1. 打开 http://localhost:5000
2. 上传一个或多个文档（PDF/TXT/DOCX/DOC/XLSX）
3. 设置测试集大小（1-50 条）
4. 点击"🚀 生成测试集"
5. 等待完成（首次会下载 HuggingFace 模型）
6. 预览并下载 JSON 测试集

### 功能二：评测 RAG 系统

```
收集 RAG 输出 → 整理评测数据 → 上传评测 → 查看评分报告
```

1. 打开 http://localhost:5000/evaluate
2. 准备评测数据（CSV/JSON/XLSX 格式，含 question / answer / contexts）
3. 上传评测数据
4. 点击"🔬 开始评测"
5. 查看四大指标得分 + 逐条明细
6. 下载完整评测报告

#### 评测数据格式

**CSV 示例：**

```csv
question,answer,contexts,ground_truth
什么是RAG？,RAG是检索增强生成技术。,"[""RAG结合检索和生成""，""检索增强提升准确性""]",RAG是一种结合检索和生成的AI技术
```

**JSON 示例：**

```json
[
  {
    "question": "什么是RAG？",
    "answer": "RAG是检索增强生成技术。",
    "contexts": ["RAG结合检索和生成", "检索增强提升准确性"],
    "ground_truth": "RAG是一种结合检索和生成的AI技术"
  }
]
```

| 字段 | 必需 | 说明 |
|------|:--:|------|
| `question` | ✅ | 用户问题 |
| `answer` | ✅ | RAG 系统生成的回答 |
| `contexts` | ✅ | 检索到的上下文（JSON 数组字符串或列表）|
| `ground_truth` | ⭕ | 标准答案（可选，用于提升 Context Recall 准确度）|

---

## 📁 项目结构

```
RagasToTestRag/
├── app.py                    # Flask 主程序
├── requirements.txt          # Python 依赖
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略规则
├── GPU_INSTALL_GUIDE.md      # GPU 安装指南
├── templates/
│   ├── index.html            # 测试集生成页面
│   └── evaluate.html         # RAG 评测页面
├── uploads/                  # 上传文件目录（已忽略）
│   └── .gitkeep
└── README.md                 # 项目说明
```

---

## 🔧 配置说明

### LLM 提供商

| 提供商 | 说明 | 环境变量 |
|--------|------|----------|
| `ollama` | 本地运行（默认，免费）| `LLM_PROVIDER=ollama` |
| `deepseek` | DeepSeek API | `LLM_PROVIDER=deepseek` |
| `openai` | OpenAI API | `LLM_PROVIDER=openai` |

### Embedding 提供商

| 提供商 | 说明 | 环境变量 |
|--------|------|----------|
| `huggingface` | 本地运行（默认）| `EMBEDDING_PROVIDER=huggingface` |
| `openai` | OpenAI/DeepSeek API | `EMBEDDING_PROVIDER=openai` |

### 计算设备

| 设备 | 说明 |
|------|------|
| `auto` | 自动检测 GPU/CPU（推荐）|
| `cuda` | 强制使用 GPU |
| `cpu` | 强制使用 CPU |

### 测试集语言

| 语言 | 说明 |
|------|------|
| `chinese` | 中文问答（默认）|
| `english` | 英文问答 |

---

## 📊 评测指标详解

| 指标 | 中文名 | 评测内容 | 满分 |
|------|--------|----------|:--:|
| **Context Precision** | 上下文精确度 | 检索到的上下文有多少是真正相关的 | 1.0 |
| **Context Recall** | 上下文召回率 | 相关上下文有多少被成功检索到 | 1.0 |
| **Faithfulness** | 回答忠实度 | 回答是否基于提供的上下文（不含幻觉）| 1.0 |
| **Answer Relevance** | 回答相关性 | 回答是否与问题相关 | 1.0 |

### 评分等级

| 分数 | 等级 | 说明 |
|------|:--:|------|
| ≥ 0.8 | 🟢 优秀 | 系统表现很好 |
| 0.6 - 0.8 | 🟡 良好 | 部分指标可优化 |
| 0.4 - 0.6 | 🟠 一般 | 需要进行改进 |
| < 0.4 | 🔴 较差 | 存在较大问题 |

---

## 📊 性能对比

使用 RTX 4090 + CUDA 12.4：

| 操作 | CPU (i7) | GPU (RTX 4090) | 提升 |
|------|----------|-----------------|------|
| Embedding 计算 | ~120 秒 | ~8 秒 | **~15x** |
| 总体生成时间 (10条) | ~20 分钟 | ~5 分钟 | **~4x** |
| 评测时间 (10 样本) | ~10 分钟 | ~3 分钟 | **~3x** |

---

## 🛠️ 技术栈

- **后端**: Flask + LangChain + Ragas
- **前端**: HTML5 + CSS3 + JavaScript（原生，无框架依赖）
- **LLM**: Ollama (Gemma2) / DeepSeek / OpenAI
- **Embedding**: HuggingFace (multilingual-e5-large) / OpenAI
- **文档处理**: PyPDF, python-docx, unstructured
- **评测框架**: Ragas evaluate

---

## 🔄 典型工作流程

```
第 1 步: 上传文档 → 生成测试集（中文问答对）
第 2 步: 用测试集的问题，调用你的 RAG 系统获取回答和上下文
第 3 步: 整理成 CSV/JSON 格式的评测数据
第 4 步: 上传评测数据 → 四大指标评分 → 下载详细报告
```

---

## ⚠️ 注意事项

1. **首次运行**会下载 HuggingFace embedding 模型（~2GB），请耐心等待
2. **Ollama 服务**需要保持运行状态
3. **上传文件大小限制**为 **50MB**（多文件）
4. **生成/评测时间**取决于文档长度、测试集大小和硬件配置
5. **评测需要 LLM**，会消耗一定推理时间（每个样本约 30-60 秒）
6. 如有 GPU，**强烈建议安装 GPU 版 PyTorch**（详见 GPU_INSTALL_GUIDE.md）

---

## 📄 License

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
# RagasToTestRag

基于 Ragas 的 RAG 系统测试集生成器，支持本地 Ollama 运行，完全免费！

## ✨ 功能特性

- 📄 **多格式文档支持**：PDF、TXT、DOCX、DOC、XLSX
- 🤖 **本地 LLM**：使用 Ollama + Gemma2（无需 API 费用）
- 🌐 **多语言 Embedding**：HuggingFace multilingual-e5-large
- 🇨🇳 **中文测试集**：自动生成中文问答对
- ⚡ **GPU 加速**：支持 CUDA 加速（速度提升 3-15 倍）
- 🎨 **Web UI**：简洁美观的上传界面
- 📥 **一键下载**：JSON 格式测试集下载

## 🚀 快速开始

### 前提条件

1. **安装 Ollama** 并启动服务：
   ```bash
   # 下载安装: https://ollama.ai
   ollama serve
   
   # 拉取模型
   ollama pull gemma2:latest
   ```

2. **安装 GPU 版 PyTorch**（可选，用于加速）：
   ```bash
   # CUDA 12.4 (RTX 30/40 系列)
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   
   # 或其他版本见 GPU_INSTALL_GUIDE.md
   ```

### 安装依赖

```bash
cd RagasToTestRag
pip install -r requirements.txt
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置你的参数
```

主要配置项：
```bash
LLM_PROVIDER=ollama                    # 使用 Ollama
OLLAMA_MODEL_NAME=gemma2:latest       # Gemma2 模型
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-large  # 多语言嵌入模型
DEVICE=auto                            # 自动检测 GPU/CPU
TEST_LANGUAGE=chinese                  # 中文测试集
```

### 启动应用

```bash
python app.py
```

访问 http://localhost:5000

## 📁 项目结构

```
RagasToTestRag/
├── app.py                 # Flask 主程序
├── requirements.txt        # Python 依赖
├── .env.example           # 环境变量示例
├── .gitignore             # Git 忽略规则
├── templates/
│   └── index.html         # Web 前端界面
├── uploads/               # 上传文件目录（已忽略）
│   └── .gitkeep
└── README.md              # 项目说明
```

## 🔧 配置说明

### LLM 提供商选项

| 提供商 | 说明 |
|--------|------|
| `ollama` | 本地运行（默认，免费）|
| `deepseek` | DeepSeek API |
| `openai` | OpenAI API |

### 计算设备选项

| 设备 | 说明 |
|------|------|
| `auto` | 自动检测（推荐）|
| `cuda` | 强制使用 GPU |
| `cpu` | 强制使用 CPU |

### 测试集语言选项

| 语言 | 说明 |
|------|------|
| `chinese` | 中文问答（默认）|
| `english` | 英文问答 |

## 📊 性能对比

使用 RTX 4090 + CUDA 12.4：

| 操作 | CPU (i7) | GPU (RTX 4090) | 提升 |
|------|----------|-----------------|------|
| Embedding 计算 | ~120 秒 | ~8 秒 | **~15x** |
| 总体生成时间 (10条) | ~20 分钟 | ~5 分钟 | **~4x** |

## 🛠️ 技术栈

- **后端**: Flask + LangChain + Ragas
- **前端**: HTML5 + CSS3 + JavaScript
- **LLM**: Ollama (Gemma2)
- **Embedding**: HuggingFace (multilingual-e5-large)
- **文档处理**: PyPDF, python-docx, unstructured

## 📝 使用流程

1. 打开浏览器访问 http://localhost:5000
2. 上传文档（PDF/TXT/DOCX/DOC/XLSX）
3. 设置测试集大小（1-50 条）
4. 点击"生成测试集"
5. 等待生成完成（首次会下载模型）
6. 预览并下载 JSON 格式的测试集

## ⚠️ 注意事项

1. **首次运行**会下载 HuggingFace embedding 模型（~2GB）
2. **Ollama 服务**需要保持运行状态
3. **上传文件大小限制**为 16MB
4. **生成时间**取决于文档长度和测试集大小

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

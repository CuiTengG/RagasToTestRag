# ============================================
# Ragas 测试集生成器 - PyTorch GPU 安装指南
# ============================================

## 🚀 快速安装步骤（GPU 模式）

### 步骤 1: 检查你的 CUDA 版本

打开命令行运行：
```bash
nvidia-smi
```

找到 `CUDA Version` 行，例如：
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 545.29       Driver Version: 545.29       CUDA Version: 12.4   |
+-----------------------------------------------------------------------------+
```
**这里显示的是 CUDA 12.4**

---

### 步骤 2: 安装 GPU 版本的 PyTorch（⚠️ 必须先安装这个！）

**根据你的 CUDA 版本选择对应命令：**

| 你的 CUDA 版本 | 安装命令 |
|---------------|---------|
| **CUDA 12.4** (RTX 30/40 系列) | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124` |
| **CUDA 12.1** (较新) | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121` |
| **CUDA 11.8** (RTX 20 系列) | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118` |
| **无 GPU / CPU only** | `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu` |

**示例（假设你是 CUDA 12.4）：**
```bash
# 先卸载旧版本（如果有）
pip uninstall torch torchvision torchaudio -y

# 安装 GPU 版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

---

### 步骤 3: 安装其他依赖

```bash
cd RagasToTestRag
pip install -r requirements.txt
```

---

### 步骤 4: 验证 PyTorch GPU 是否正常

创建测试文件 `test_gpu.py`：
```python
import torch
print(f"PyTorch 版本: {torch.__version__}")
print(f"CUDA 是否可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU 设备名称: {torch.cuda.get_device_name(0)}")
    print(f"GPU 显存: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB")
else:
    print("❌ 未检测到 GPU，将使用 CPU")
```

运行测试：
```bash
python test_gpu.py
```

**成功输出示例：**
```
PyTorch 版本: 2.2.0+cu124
CUDA 是否可用: True
GPU 设备名称: NVIDIA GeForce RTX 4090
GPU 显存: 24.0 GB
```

---

### 步骤 5: 启动应用

```bash
python app.py
```

启动信息应该显示：
```
📌 计算设备: auto
   ✓ GPU: NVIDIA GeForce RTX 4090
```

---

## ⚠️ 常见问题

### Q1: 已经安装了 CPU 版本的 PyTorch，怎么升级到 GPU？

```bash
# 卸载当前版本
pip uninstall torch torchvision torchaudio -y

# 重新安装 GPU 版本（选择对应的 CUDA 版本）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

### Q2: 如何确认我安装的是 GPU 版本？

```python
import torch
print(torch.version.cuda)  # 应该输出类似 "12.4" 的版本号
print(torch.cuda.is_available())  # 应该输出 True
```

### Q3: Ollama 也需要配置 GPU 吗？

**不需要！** Ollama 会自动使用 GPU。只要你安装了正确的 NVIDIA 驱动和 CUDA toolkit 即可。

检查 Ollama GPU 状态：
```bash
ollama ps
```

### Q4: 多个 Conda 环境怎么办？

建议在 **专门的 conda 环境** 中安装：

```bash
# 创建新环境
conda create -n ragas-gpu python=3.10
conda activate ragas-gpu

# 安装 PyTorch GPU 版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 安装项目依赖
pip install -r requirements.txt

# 运行应用
python app.py
```

---

## 📊 性能对比

使用 RTX 4090 + CUDA 12.4 的性能提升：

| 操作 | CPU (i7-12700) | GPU (RTX 4090) | 加速比 |
|------|----------------|-----------------|--------|
| Embedding 计算 (E5-Large) | ~120 秒 | ~8 秒 | **~15x** |
| 总体生成时间 (10条数据) | ~20 分钟 | ~5 分钟 | **~4x** |

---

## 🔧 故障排除

### 问题: `torch.cuda.is_available()` 返回 False

**解决方案：**
1. 确认已安装 **NVIDIA 显卡驱动**
2. 确认安装了对应版本的 **CUDA Toolkit**
3. 确认安装了 **GPU 版本的 PyTorch**（不是 CPU 版本）

检查命令：
```bash
nvidia-smi          # 查看驱动和 CUDA 版本
nvcc --version       # 查看 CUDA Toolkit 版本
python -c "import torch; print(torch.cuda.is_available())"
```

### 问题: OOM (Out of Memory) 错误

**解决方案：减小 batch_size**

编辑 `.env` 文件：
```bash
EMBEDDING_BATCH_SIZE=16   # 默认是 32，显存不够时改小
```

或者在 `app.py` 的 `get_embeddings()` 函数中修改：
```python
encode_kwargs={'normalize_embeddings': True, 'batch_size': 16},
```

---

## ✅ 完整安装流程总结

```bash
# 1. 检查 CUDA 版本
nvidia-smi

# 2. 创建 conda 环境（可选但推荐）
conda create -n ragas-gpu python=3.10
conda activate ragas-gpu

# 3. 安装 GPU 版 PyTorch（根据 CUDA 版本选择）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 4. 安装项目依赖
cd TestRagas
pip install -r requirements.txt

# 5. 验证 GPU
python test_gpu.py

# 6. 启动应用
python app.py
```

---

祝你 GPU 加速愉快！🚀🎉

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
import traceback
from dotenv import load_dotenv
import certifi

load_dotenv()

# 修复 SSL_CERT_FILE 不存在问题
os.environ["SSL_CERT_FILE"] = certifi.where()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc', 'xlsx'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_document(file_path):
    if '.' not in file_path:
        raise ValueError("文件名缺少扩展名")
    
    file_ext = file_path.rsplit('.', 1)[1].lower()
    
    try:
        if file_ext == 'pdf':
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
        elif file_ext == 'txt':
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path)
        elif file_ext == 'docx':
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(file_path)
        elif file_ext == 'doc':
            return load_doc_file(file_path)
        elif file_ext == 'xlsx':
            from langchain_community.document_loaders import UnstructuredExcelLoader
            loader = UnstructuredExcelLoader(file_path, mode="elements")
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
        
        documents = loader.load()
    except Exception as e:
        raise Exception(f"加载文档失败 ({file_ext}): {str(e)}")
    
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    return chunks

def load_doc_file(file_path):
    from langchain_core.documents import Document
    
    try:
        import textract
        text = textract.process(file_path).decode('utf-8')
        documents = [Document(page_content=text, metadata={'source': file_path})]
    except ImportError:
        try:
            import subprocess
            result = subprocess.run(['antiword', file_path], capture_output=True, text=True)
            if result.returncode == 0:
                documents = [Document(page_content=result.stdout, metadata={'source': file_path})]
            else:
                raise Exception("antiword 处理失败")
        except FileNotFoundError:
            raise Exception("处理 .doc 文件需要安装 textract (pip install textract) 或 antiword")
    except Exception as e:
        raise Exception(f"无法读取 .doc 文件: {str(e)}")
    
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    return chunks

def get_llm():
    llm_provider = os.getenv('LLM_PROVIDER', 'ollama').lower()
    
    print(f"使用 LLM 提供商: {llm_provider}")
    
    if llm_provider == 'ollama':
        model_name = os.getenv('OLLAMA_MODEL_NAME', 'gemma2:latest')
        base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            model=model_name,
            openai_api_key="ollama",
            openai_api_base=f"{base_url}/v1",
            temperature=0.7,
        )
    
    elif llm_provider == 'openai' or llm_provider == 'deepseek':
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE')
        model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo')
        
        if not api_key:
            raise Exception("未找到 OPENAI_API_KEY")
        
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base=api_base,
        )
    
    else:
        raise Exception(f"不支持的 LLM 提供商: {llm_provider}")

def get_device():
    device = os.getenv('DEVICE', 'auto').lower()
    
    if device == 'auto':
        try:
            import torch
            if torch.cuda.is_available():
                device = 'cuda'
                print(f"✓ 检测到 GPU: {torch.cuda.get_device_name(0)}")
            else:
                device = 'cpu'
                print("⚠️ 未检测到 GPU，使用 CPU 模式")
        except ImportError:
            device = 'cpu'
            print("⚠️ PyTorch 未安装，使用 CPU 模式")
    else:
        print(f"使用设备: {device}")
    
    return device

def get_embeddings():
    embedding_provider = os.getenv('EMBEDDING_PROVIDER', 'huggingface').lower()
    
    print(f"使用 Embedding 提供商: {embedding_provider}")
    
    device = get_device()
    
    if embedding_provider == 'huggingface':
        model_name = os.getenv('EMBEDDING_MODEL_NAME', 'intfloat/multilingual-e5-large')
        
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': device},
                encode_kwargs={'normalize_embeddings': True, 'batch_size': 32},
            )
        except ImportError:
            from sentence_transformers import SentenceTransformer
            from langchain_core.embeddings import Embeddings
            import numpy as np
            
            class LocalEmbeddings(Embeddings):
                def __init__(self, model_name, device):
                    self.model = SentenceTransformer(model_name, device=device)
                
                def embed_documents(self, texts):
                    return self.model.encode(texts, normalize_embeddings=True, batch_size=32).tolist()
                
                def embed_query(self, text):
                    return self.model.encode([text], normalize_embeddings=True)[0].tolist()
            
            return LocalEmbeddings(model_name, device)
    
    elif embedding_provider == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE')
        
        if not api_key:
            raise Exception("未找到 OPENAI_API_KEY")
        
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            openai_api_key=api_key,
            openai_api_base=api_base,
        )
    
    else:
        raise Exception(f"不支持的 Embedding 提供商: {embedding_provider}")

def generate_testset(documents, test_size=10):
    try:
        from ragas.testset import TestsetGenerator
        from langchain_core.documents import Document
        
        language = os.getenv('TEST_LANGUAGE', 'chinese').lower()
        print(f"测试集语言: {language}")
        
        if language == 'chinese':
            instruction = Document(
                page_content=(
                    "【重要指令】以下所有文档都是中文内容。"
                    "请基于文档内容，使用中文生成所有的问题和答案。"
                    "问题应该以中文提问，答案也应该是中文。"
                    "生成的问题应该与文档内容相关且有价值。"
                ),
                metadata={'source': 'language_instruction'}
            )
            documents = [instruction] + list(documents)
        
        generator_llm = get_llm()
        critic_llm = get_llm()
        embeddings = get_embeddings()
        
        print(f"LLM 类型: {type(generator_llm).__name__}")
        print(f"Embeddings 类型: {type(embeddings).__name__}")
        print(f"文档数量: {len(documents)}")
        print(f"测试集大小: {test_size}")
        
        generator = TestsetGenerator.from_langchain(
            generator_llm=generator_llm,
            critic_llm=critic_llm,
            embeddings=embeddings,
        )
        
        testset = generator.generate_with_langchain_docs(
            documents,
            test_size=test_size,
            raise_exceptions=False,
        )
        
        return testset
        
    except Exception as e:
        print(f"生成测试集失败: {str(e)}")
        traceback.print_exc()
        raise Exception(f"生成测试集失败: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，请上传 PDF、TXT、DOCX、DOC 或 XLSX 文件'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        print(f"\n{'='*50}")
        print(f"开始处理文件: {file.filename}")
        print(f"{'='*50}\n")
        
        test_size = int(request.form.get('test_size', 10))
        
        print("步骤 1/3: 加载文档...")
        documents = load_document(filepath)
        print(f"✓ 文档已分割为 {len(documents)} 个块")
        
        print("步骤 2/3: 生成测试集...")
        testset = generate_testset(documents, test_size)
        test_df = testset.to_pandas()
        print(f"✓ 测试集已生成，包含 {len(test_df)} 条数据")
        
        print("步骤 3/3: 保存结果...")
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], f'testset_{filename}.json')
        test_df.to_json(output_file, orient='records', force_ascii=False, indent=2)
        print(f"✓ 结果已保存到: {output_file}")
        
        result_data = {
            'success': True,
            'message': f'成功生成 {len(test_df)} 条测试数据',
            'filename': f'testset_{filename}.json',
            'download_url': f'/download/{f"testset_{filename}.json"}',
            'preview': test_df.head(5).to_dict(orient='records')
        }
        
        print(f"\n{'='*50}")
        print("处理完成!")
        print(f"{'='*50}\n")
        
        return jsonify(result_data)
        
    except Exception as e:
        print(f"\n❌ 错误发生: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Ragas 测试集生成器启动中...")
    print("="*50 + "\n")
    
    llm_provider = os.getenv('LLM_PROVIDER', 'ollama')
    embedding_provider = os.getenv('EMBEDDING_PROVIDER', 'huggingface')
    device = os.getenv('DEVICE', 'auto')
    
    print(f"📌 LLM 提供商: {llm_provider}")
    if llm_provider.lower() == 'ollama':
        ollama_model = os.getenv('OLLAMA_MODEL_NAME', 'gemma2:latest')
        ollama_base = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        print(f"   - Ollama 模型: {ollama_model}")
        print(f"   - Ollama 地址: {ollama_base}")
    elif llm_provider.lower() in ['openai', 'deepseek']:
        api_base = os.getenv('OPENAI_API_BASE', '')
        print(f"   - API Base: {api_base}")
    
    print(f"\n📌 Embedding 提供商: {embedding_provider}")
    if embedding_provider.lower() == 'huggingface':
        emb_model = os.getenv('EMBEDDING_MODEL_NAME', 'intfloat/multilingual-e5-large')
        print(f"   - 模型: {emb_model}")
    
    print(f"\n📌 计算设备: {device}")
    if device.lower() == 'auto':
        try:
            import torch
            if torch.cuda.is_available():
                print(f"   ✓ GPU: {torch.cuda.get_device_name(0)}")
            else:
                print("   ⚠️ 未检测到 GPU，将使用 CPU")
        except ImportError:
            print("   ⚠️ PyTorch 未安装，使用 CPU")
    
    print("\n访问地址: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)

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
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  
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
        
        import httpx
        from langchain_openai import ChatOpenAI
        
        http_client = httpx.Client(verify=False, timeout=300.0)
        
        return ChatOpenAI(
            model=model_name,
            openai_api_key="ollama",
            openai_api_base=f"{base_url}/v1",
            temperature=0.7,
            http_client=http_client,
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

@app.route('/evaluate')
def evaluate_page():
    return render_template('evaluate.html')

@app.route('/evaluate', methods=['POST'])
def evaluate_rag():
    try:
        file = request.files.get('file')
        import pandas as pd
        
        if file and file.filename != '':
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith('.json'):
                df = pd.read_json(file)
            elif file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                return jsonify({'error': '请上传 CSV、JSON 或 XLSX 格式的评测数据文件'}), 400
        else:
            data = request.get_json()
            if not data or 'samples' not in data:
                return jsonify({'error': '请提供评测数据（文件或 JSON）'}), 400
            df = pd.DataFrame(data['samples'])
        
        required_cols = ['question', 'answer', 'contexts']
        for col in required_cols:
            if col not in df.columns:
                return jsonify({'error': f'缺少必需列: {col}'}), 400
        
        from ragas import evaluate
        from ragas.metrics import (
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        )
        from datasets import Dataset
        
        eval_llm = get_llm()
        eval_embeddings = get_embeddings()
        
        records = []
        for _, row in df.iterrows():
            record = {
                'question': str(row['question']),
                'answer': str(row['answer']),
            }
            
            ctx = row['contexts']
            if isinstance(ctx, str):
                try:
                    ctx = json.loads(ctx)
                except json.JSONDecodeError:
                    ctx = [ctx]
            if not isinstance(ctx, list):
                ctx = [str(ctx)]
            record['contexts'] = [str(c) for c in ctx]
            
            if 'ground_truth' in df.columns and pd.notna(row['ground_truth']):
                record['ground_truth'] = str(row['ground_truth'])
            
            records.append(record)
        
        dataset = Dataset.from_list(records)
        
        metrics = [
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ]
        
        print(f"\n{'='*50}")
        print(f"开始评测 RAG 系统")
        print(f"评测样本数: {len(records)}")
        print(f"评测指标: Context Precision, Context Recall, Faithfulness, Answer Relevance")
        print(f"{'='*50}\n")
        
        result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=eval_llm,
            embeddings=eval_embeddings,
        )
        
        result_df = result.to_pandas()
        
        scores = {}
        for col in result_df.columns:
            if col in ['context_precision', 'context_recall', 'faithfulness', 'answer_relevancy']:
                scores[col] = round(float(result_df[col].mean()), 4)
        
        overall = round(sum(scores.values()) / len(scores), 4) if scores else 0
        
        output_filename = f'evaluation_result_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.json'
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        result_df.to_json(output_file, orient='records', force_ascii=False, indent=2)
        
        def get_level(score):
            if score >= 0.8:
                return '优秀'
            elif score >= 0.6:
                return '良好'
            elif score >= 0.4:
                return '一般'
            else:
                return '较差'
        
        metric_details = []
        name_map = {
            'context_precision': '上下文精确度',
            'context_recall': '上下文召回率',
            'faithfulness': '回答忠实度',
            'answer_relevancy': '回答相关性',
        }
        descriptions = {
            'context_precision': '检索到的上下文有多少是真正相关的',
            'context_recall': '相关上下文有多少被成功检索到',
            'faithfulness': '回答是否基于提供的上下文（不含幻觉）',
            'answer_relevancy': '回答是否与问题相关',
        }
        
        for key, value in scores.items():
            metric_details.append({
                'name': name_map.get(key, key),
                'key': key,
                'score': value,
                'level': get_level(value),
                'description': descriptions.get(key, ''),
            })
        
        result_data = {
            'success': True,
            'scores': scores,
            'overall': overall,
            'overall_level': get_level(overall),
            'metric_details': metric_details,
            'sample_count': len(records),
            'per_sample': result_df[['question', 'context_precision', 'context_recall', 'faithfulness', 'answer_relevancy']].to_dict(orient='records'),
            'download_url': f'/download/{output_filename}',
        }
        
        print(f"\n{'='*50}")
        print("评测完成!")
        print(f"综合得分: {overall} ({get_level(overall)})")
        for key, value in scores.items():
            print(f"  {name_map.get(key, key)}: {value} ({get_level(value)})")
        print(f"{'='*50}\n")
        
        return jsonify(result_data)
        
    except Exception as e:
        print(f"\n❌ 评测错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('files')
    
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': '没有选择文件'}), 400
    
    for f in files:
        if f.filename == '':
            continue
        if not allowed_file(f.filename):
            return jsonify({'error': f'不支持的文件格式: {f.filename}，请上传 PDF、TXT、DOCX、DOC 或 XLSX 文件'}), 400
    
    try:
        test_size = int(request.form.get('test_size', 10))
        valid_files = [f for f in files if f.filename != '']
        file_names = []
        all_documents = []
        
        print("步骤 1/3: 加载文档...")
        file_count = 0
        for file in valid_files:
            file_count += 1
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            file_names.append(file.filename)
            
            print(f"\n{'='*50}")
            print(f"加载文件 {file_count}/{len(valid_files)}: {file.filename}")
            print(f"{'='*50}")
            
            chunks = load_document(filepath)
            all_documents.extend(chunks)
            print(f"✓ {filename}: {len(chunks)} 个块")
        
        total_chunks = len(all_documents)
        print(f"\n📊 共加载 {len(valid_files)} 个文件，总计 {total_chunks} 个文档块\n")
        
        print("步骤 2/3: 生成测试集...")
        testset = generate_testset(all_documents, test_size)
        test_df = testset.to_pandas()
        print(f"✓ 测试集已生成，包含 {len(test_df)} 条数据")
        
        print("步骤 3/3: 保存结果...")
        base_name = secure_filename('_'.join(f.rsplit('.', 1)[0] for f in file_names[:2]))
        if len(file_names) > 2:
            base_name = base_name + f'_等{len(file_names)}个文件'
        output_filename = f'testset_{base_name}.json'
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        test_df.to_json(output_file, orient='records', force_ascii=False, indent=2)
        print(f"✓ 结果已保存到: {output_file}")
        
        result_data = {
            'success': True,
            'message': f'成功处理 {len(valid_files)} 个文件，生成 {len(test_df)} 条测试数据',
            'filename': output_filename,
            'download_url': f'/download/{output_filename}',
            'preview': test_df.head(5).to_dict(orient='records'),
            'file_list': file_names,
            'total_chunks': total_chunks,
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

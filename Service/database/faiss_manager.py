import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# faiss db 向量数据库,存储心理学领域文本的向量
class FaissDB:
    def __init__(self, model, texts):
        self.model = model  # 模型
        self.index = None  # 索引
        self.data = texts  # 原始数据

    # 初始化数据库
    def build(self):
        vectors = self.model.encode(self.data, normalize_embeddings=True)  # 将所有文本转为向量,归一化
        self.index = faiss.IndexFlatL2(vectors.shape[1])  # 创建一个Falss的l2距离索引器
        self.index.add(np.array(vectors))  # 传入数据,构建索引
        self.data = texts

    # 查询
    # q 要查询的文本
    # k 查询是数据条数
    def query(self, q, k=3):
        vec = self.model.encode([q], normalize_embeddings=True)
        D, I = self.index.search(vec, k)
        return [(self.data[i], D[0][j]) for j, i in enumerate(I[0])]

# 使用的模型
model = SentenceTransformer('all-MiniLM-L6-v2')

# 文本数据
texts = []

faiss_db = FaissDB(model=model, texts=texts)


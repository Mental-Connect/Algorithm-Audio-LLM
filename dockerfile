# 使用官方 Python 3.12 作为基础镜像
FROM python:3.12.2

# 设置工作目录
WORKDIR /BACKEND-ALGORITHM-LLM

# 复制 requirements.txt 到容器中
COPY docker-requirements.txt .

# 安装ffmpeg
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装依赖
RUN pip install --no-cache-dir -r docker-requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制 modelscope 到缓存目录
COPY modelscope /root/.cache/modelscope

# 复制你的 FastAPI 代码到容器中
COPY . .

# 暴露服务端口
EXPOSE 8000
EXPOSE 8001

# 运行 FastAPI 应用，启动 main.py，处理 FastAPI 和 WebSocket 服务
CMD ["sh", "-c", "uvicorn Service.main:app --host 0.0.0.0 --port 8000 & python3 -m Service.main"]

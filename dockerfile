# ✅ 使用支持 CUDA 的官方 NVIDIA 镜像
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu20.04

# 设置工作目录
WORKDIR /BACKEND-ALGORITHM-LLM

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && apt-get update && apt-get install -y tzdata

RUN apt-get update -y \
    && apt-get install -y ffmpeg \
    && apt-get install  -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i 's|http://archive.ubuntu.com/ubuntu|http://mirrors.aliyun.com/ubuntu|g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y software-properties-common \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ✅ 安装 Python 3.12
RUN add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && apt-get install -y python3.12 python3-distutils python3.12-venv python3.12-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ✅ 设置 Python3.12 为默认
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# ✅ 安装 pip（新版）
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# 复制你的 FastAPI 代码到容器中
COPY . .

# 复制 modelscope 到缓存目录
RUN mkdir -p /root/.cache && mv modelscope /root/.cache/

# 安装依赖
RUN pip install --no-cache-dir -r docker-requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# 暴露服务端口
EXPOSE 8000
EXPOSE 8001

# 运行 FastAPI 应用，启动 main.py，处理 FastAPI 和 WebSocket 服务
CMD ["python3", "-m", "Service.main"]

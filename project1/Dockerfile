# 1. 指定使用 bullseye 版本，避开 Debian 12 的配置变动
FROM python:3.10-slim-bullseye

# 2. 设置工作目录
WORKDIR /app

# 3. 更换为国内阿里云镜像源 (针对 bullseye 路径)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 4. 安装 Linux 系统依赖 (一次性安装，减少镜像层数)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libglib2.0-0 \
    libx11-6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 5. 安装 Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable

# 6. 安装 Python 库 (使用清华源)
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    selenium \
    mysql-connector-python

# 7. 复制文件
COPY . .

CMD ["python", "task1.py"]
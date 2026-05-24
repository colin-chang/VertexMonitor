FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY proxy.py .
COPY store.py .
COPY static/ static/

# 数据目录（通过 volume 挂载持久化）
RUN mkdir -p /app/data

ENV PORT=8899

EXPOSE 8899

CMD ["python", "proxy.py"]

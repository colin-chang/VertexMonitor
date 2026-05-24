FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m appuser

# 复制项目文件
COPY proxy.py .
COPY store.py .
COPY static/ static/

# 数据目录（通过 volume 挂载持久化）
RUN mkdir -p /app/data && chown appuser:appuser /app/data

USER appuser

ENV PORT=8897

EXPOSE 8897

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8897/health || exit 1

CMD ["uvicorn", "proxy:app", "--host", "0.0.0.0", "--port", "8897"]

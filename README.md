# Vertex Monitor

Vertex AI Gemini 预算代理 — 实时计费 + Web UI 仪表盘，支持**手动余额 & 自动循环**两种模式。

---

## 核心能力

| 功能 | 说明 |
|------|------|
| 🔒 **实时计费** | liteLLM 自动匹配 Vertex AI 官方定价，每次调用精确到 $0.00001 |
| ✋ **手动模式** | 自由设定余额 & 截止日期，随时修改 |
| 🔄 **自动循环** | 设定每月重置日 & 金额，自动归零 spent |
| 📊 **Web UI** | 余额概览 + 模式设置 + 模型消费分布 + 调用历史 |
| 🛑 **硬拦截** | 额度耗尽 / 过期即时返回 402 |
| 🔌 **Hermes 接入** | OpenAI 兼容端点，一行配置即可接入 |
| 🐳 **Docker** | 一键部署，数据卷持久化 |

---

## 快速开始

### Conda 方式

```bash
conda create -n vertex-monitor python=3.11 -y
conda activate vertex-monitor
pip install -r requirements.txt
python proxy.py
```

### Docker 方式

```bash
docker compose up -d
```

启动后打开 <http://localhost:8899> 进入 Web UI。

---

## Web UI

Web UI 提供三个核心面板：

### 1. 本期概览
实时显示剩余额度、已消费、总预算、截止时间、状态徽章。

### 2. 计费模式设置
- **自动循环**：设置每月重置日 + 每月金额（如每月 1 号重置 $10）
- **手动设定**：自由设置余额 + 截止日期，随时修改
- **立即重置**按钮：手动归零本期消费

### 3. 消费统计
- **模型消费分布**：每个模型的调用次数、token 用量、消费金额
- **最近调用**：最近 20 条调用详单
- **累计统计**：历史总消费 & 总调用次数

---

## 接入前：查询当前消费

见下方「余额校正」——先查 GCP Billing 确认接入前的消费额，再通过 Web UI 调整。

### 方式一：GCP Billing Console（推荐）

1. <https://console.cloud.google.com/billing> → 报告
2. 筛选：本月至今 / SKU / Vertex AI
3. 查看总费用

### 方式二：开发者福利页面

<https://developers.google.com/program/my-benefits>

---

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | Web UI |
| `GET` | `/health` | 健康检查 + 模型列表 |
| `POST` | `/api/test` | 连通性测试（发送最小请求） |
| `GET` | `/usage` | 预算状态摘要 |
| `GET` | `/api/config` | 计费配置 + 完整状态 |
| `POST` | `/api/config` | 更新计费配置 |
| `POST` | `/api/reset` | 手动重置本期消费 |
| `GET` | `/api/stats` | 模型消费统计 |
| `GET` | `/api/history` | 最近 N 条调用历史 |
| `POST` | `/v1/chat/completions` | OpenAI 兼容聊天补全 |

### 更新计费配置

```bash
# 切换为自动循环模式：每月 1 号重置 $10
curl -X POST http://localhost:8899/api/config \
  -H "Content-Type: application/json" \
  -d '{"mode":"auto_recurring","auto_reset_day":1,"auto_monthly_amount":10.0}'

# 切换为手动模式：余额 $8.50，下月底到期
curl -X POST http://localhost:8899/api/config \
  -H "Content-Type: application/json" \
  -d '{"mode":"manual","manual_balance":8.50,"manual_expires_at":"2026-07-31"}'
```

### 查询统计

```bash
curl -s http://localhost:8899/api/stats | python3 -m json.tool
```

---

## 接入 Hermes

在 `~/.hermes/config.yaml` 的 `custom_providers` 中添加：

```yaml
custom_providers:
  - name: vertex-budget
    base_url: http://localhost:8899/v1
    api_key: noop
    model: gemini-3.1-flash-lite
    models:
      gemini-3.5-flash:
        context_length: 1048576
      gemini-3.1-flash-lite:
        context_length: 1048576
      gemini-3.1-pro-preview:
        context_length: 1048576
      gemini-3.1-pro-preview-customtools:
        context_length: 1048576
      gemini-3-flash:
        context_length: 1048576
      gemini-2.5-pro:
        context_length: 2097152
      gemini-2.5-flash:
        context_length: 1048576
      gemini-2.5-flash-lite:
        context_length: 1048576
      gemini-2.5-flash-live-api:
        context_length: 1048576
      gemini-2.0-flash:
        context_length: 1048576
      gemini-2.0-flash-lite:
        context_length: 1048576
      gemini-1.5-pro:
        context_length: 2097152
      gemini-1.5-flash:
        context_length: 1048576
```

`/model` 选中 `vertex-budget` 即可。在对话中可直接询问余额——Agent 调 `GET /usage` 获取。

---

## 获取 GCP 服务账号 Key（vertex-key.json）

项目需要 GCP **服务账号 JSON 密钥**才能调用 Vertex AI API。

### 步骤

1. 打开 [GCP Console → 服务账号](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. 选择你的项目（如 `ai-project-384207`）
3. 点击 **"创建服务账号"**（或选择一个已有的）
   - 角色选择：**Vertex AI User**（`roles/aiplatform.user`）
4. 进入该服务账号 → **密钥** 标签 → **添加密钥** → **创建新密钥**
5. 选择 **JSON** → 下载
6. 将下载的文件重命名为 `vertex-key.json`，放入项目根目录

### 已有账号直接下载密钥

如果你已有服务账号：

1. [IAM → 服务账号](https://console.cloud.google.com/iam-admin/serviceaccounts) → 找到账号
2. 点击账号邮箱 → **密钥** → **添加密钥** → **创建新密钥** → JSON

> ⚠️ `vertex-key.json` 已加入 `.gitignore`，不会被提交到 Git。

---

## Docker 部署

```bash
docker compose up -d        # 启动
docker compose logs -f      # 日志
docker compose down         # 停止
```

数据持久化在 `./data/`（store.json + store_history.jsonl）。Web UI 端口 8899。

---

## 支持模型

| 模型 | context_length | 状态 |
|------|---------------|------|
| `gemini-3.5-flash` | 1,048,576 | 推荐 |
| `gemini-3.1-flash-lite` | 1,048,576 | 推荐 |
| `gemini-3.1-pro-preview` | 1,048,576 | 预览 |
| `gemini-3.1-pro-preview-customtools` | 1,048,576 | 预览 |
| `gemini-3-flash` | 1,048,576 | 预览 |
| `gemini-2.5-pro` | 2,097,152 | 稳定 |
| `gemini-2.5-flash` | 1,048,576 | 稳定 |
| `gemini-2.5-flash-lite` | 1,048,576 | 稳定 |
| `gemini-2.5-flash-live-api` | 1,048,576 | 稳定 |
| `gemini-2.0-flash` | 1,048,576 | 旧版 |
| `gemini-2.0-flash-lite` | 1,048,576 | 旧版 |
| `gemini-1.5-pro` | 2,097,152 | 旧版 |
| `gemini-1.5-flash` | 1,048,576 | 旧版 |

---

## 文件结构

```
VertexMonitor/
├── proxy.py               # FastAPI 代理
├── store.py               # 双模式计费 + 统计
├── static/index.html      # Web UI
├── config.json            # 项目配置
├── requirements.txt       # Python 依赖
├── Dockerfile
├── docker-compose.yml
├── vertex-key.json         # GCP 服务账号密钥（需自行下载）
├── .dockerignore / .gitignore
├── data/                  # 持久化数据
└── README.md
```

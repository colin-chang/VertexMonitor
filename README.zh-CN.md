# Vertex Monitor

English | [中文文档](README.zh-CN.md)

Google Vertex AI Gemini 模型的轻量级**预算代理** —— 实时追踪消费、强制限额，通过简洁的 Web UI 管理一切。

> 🎯 专为 Google AI Pro 订阅用户打造，每月有 Vertex AI 额度，需要**确保绝不超支**。

---

## 为什么需要 Vertex Monitor？

**痛点**：Vertex AI 按 token 计费，但没有内置方式说"本月花满 $10 就停"。一个失控的 Agent 循环就能烧光你的全部预算。

**方案**：Vertex Monitor 位于你的应用和 Vertex AI 之间，逐次计算 token 和费用。预算耗尽时，请求直接返回 `402 Payment Required` —— GCP 账单不再有惊喜。

---

## 核心功能

| 功能 | 说明 |
|------|------|
| 🪙 **实时计费** | 每次调用按 Vertex AI 官方定价计算（通过 liteLLM），精确到 $0.00001 |
| ✋ **手动模式** | 自由设定余额和截止日期，随时修改 |
| 🔄 **自动循环** | 每月重置日 + 金额 —— 适合订阅额度场景 |
| 📊 **仪表盘** | 余额概览、消费占比图、模型统计、调用历史 |
| ⚙️ **设置页** | 浏览器内管理凭证、模型白名单、计费模式 |
| 🌐 **国际化** | 英文 + 简体中文，localStorage 持久化，无闪屏 |
| 🛑 **硬拦截** | 预算耗尽 → 即时 `402`，不会超支 |
| 🔌 **OpenAI 兼容** | 可直接接入 Hermes、Cursor 或任何 OpenAI 兼容客户端 |
| 🐳 **Docker** | 一键部署，数据卷持久化 |

---

## 快速开始

### 方式一：Docker（推荐）

```bash
# 克隆仓库
git clone https://github.com/colin-chang/VertexMonitor.git
cd VertexMonitor

# 复制示例配置，填入你的 GCP 项目 ID
cp config.example.json config.json

# 放置服务账号密钥
cp ~/Downloads/your-key.json vertex-key.json

# 启动
docker compose up -d
```

打开 http://localhost:8899 —— 开始使用。

### 方式二：Conda

```bash
conda create -n vertex-monitor python=3.11 -y
conda activate vertex-monitor
pip install -r requirements.txt

cp config.example.json config.json
# 编辑 config.json，填入你的 GCP 项目 ID
# 将 vertex-key.json 放在项目根目录

python proxy.py
```

---

## Web UI

### 仪表盘

主界面一目了然：

- **余额概览**：剩余、已消费、总预算、截止时间、状态徽章
- **消费占比图**：环形图展示各模型花费占比
- **Token 用量图**：堆叠柱状图展示 prompt vs. completion tokens
- **模型统计表**：每个模型的调用次数、token 数、费用
- **最近调用**：最近 20 条 API 请求的完整详情
- **累计统计**：历史总消费和总调用次数

### 设置页

无需编辑文件，直接在浏览器管理代理配置：

- **Vertex AI 凭证**：粘贴服务账号 JSON Key，状态指示器显示是否已配置
- **允许的模型列表**：每行一个模型名 —— 只有列表中的模型才能通过代理调用
- **计费模式**：切换自动循环（每月重置）和手动设定（自定义余额 + 截止日期）
- **测试连通性**：发送最小请求验证一切正常

---

## 获取 GCP 服务账号 Key

Vertex Monitor 需要 GCP 服务账号 JSON 密钥才能调用 Vertex AI API。

1. 打开 [GCP 控制台 → 服务账号](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. 选择你的项目
3. 点击**创建服务账号**
   - 角色：**Vertex AI User**（`roles/aiplatform.user`）
4. 进入该服务账号 → **密钥**标签 → **添加密钥** → **创建新密钥**
5. 选择 **JSON** → 下载文件
6. 重命名为 `vertex-key.json`，放在项目根目录

> ⚠️ `vertex-key.json` 已通过 `.gitignore` 排除，不会被提交到 Git。

---

## API 参考

### 代理端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/v1/chat/completions` | OpenAI 兼容聊天补全（代理到 Vertex AI） |

### 管理端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 仪表盘页面 |
| `GET` | `/settings` | 设置页面 |
| `GET` | `/health` | 健康检查 + 模型列表 |
| `GET` | `/usage` | 预算状态摘要 |
| `GET` | `/api/config` | 计费配置 + 完整状态 |
| `POST` | `/api/config` | 更新计费配置 |
| `POST` | `/api/reset` | 重置本期消费 |
| `GET` | `/api/stats` | 各模型消费统计 |
| `GET` | `/api/history` | 最近 API 调用历史 |
| `GET` | `/api/settings` | 获取凭证 + 模型白名单 |
| `POST` | `/api/settings` | 保存凭证 + 模型白名单 |
| `POST` | `/api/test` | 测试 Vertex AI 连通性 |

### 更新计费配置

```bash
# 自动循环：每月 1 号重置 $10
curl -X POST http://localhost:8899/api/config \
  -H "Content-Type: application/json" \
  -d '{"mode":"auto_recurring","auto_reset_day":1,"auto_monthly_amount":10.0}'

# 手动模式：余额 $8.50，下月底到期
curl -X POST http://localhost:8899/api/config \
  -H "Content-Type: application/json" \
  -d '{"mode":"manual","manual_balance":8.50,"manual_expires_at":"2026-07-31"}'
```

---

## 集成

### Hermes Agent

在 `~/.hermes/config.yaml` 中添加：

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
      gemini-2.5-pro:
        context_length: 2097152
      gemini-2.5-flash:
        context_length: 1048576
      gemini-2.5-flash-lite:
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

使用 `/model` 选择 `vertex-budget` 即可。

### 任何 OpenAI 兼容客户端

将客户端的 `base_url` 指向 `http://localhost:8899/v1`，API key 填任意非空字符串。

---

## 支持模型

| 模型 | 上下文长度 | 状态 |
|------|-----------|------|
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

## Docker 命令

```bash
docker compose up -d        # 启动
docker compose logs -f      # 查看日志
docker compose down         # 停止
```

数据持久化在 `./data/`（Docker 数据卷挂载）。端口 8899。

---

## 项目结构

```
VertexMonitor/
├── proxy.py                  # FastAPI 代理 + API 端点
├── store.py                  # 双模式计费引擎 + 统计
├── static/
│   ├── index.html            # 仪表盘页面
│   ├── settings.html         # 设置页面
│   └── i18n.js               # 翻译引擎（英文 / 简体中文）
├── config.example.json       # 示例配置（复制为 config.json）
├── requirements.txt          # Python 依赖
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── .dockerignore
├── LICENSE                   # MIT
├── SECURITY.md
├── PRIVACY.md
├── data/                     # 运行时数据（git 忽略）
│   └── .gitkeep
└── README.md
```

---

## 安全与隐私

- **凭证**仅存储在 Docker 容器内（`/app/data/`），不会进入 Git
- **无遥测** —— 数据始终留在你的机器上
- **无外部服务** —— 唯一的出站流量是你自己的 API 调用到 Google Vertex AI
- 详见 [SECURITY.md](SECURITY.md) 和 [PRIVACY.md](PRIVACY.md)

---

## 许可证

[MIT](LICENSE) © 2025 Colin Chang

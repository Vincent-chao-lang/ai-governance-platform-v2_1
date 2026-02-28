# AI 治理平台 V2.1

### 为什么企业需要 AI 治理？

随着 AI 技术的普及，企业面临以下挑战：

| 挑战           | 风险                              | 后果                             |
| -------------- | --------------------------------- | -------------------------------- |
| **数据泄露**   | 员工将敏感数据发送给外部 AI 服务  | 商业机密泄露、监管罚款、声誉损失 |
| **合规风险**   | 无法满足 GDPR、数据出境等法规要求 | 法律诉讼、业务停滞、巨额罚款     |
| **成本失控**   | AI 调用量难以追踪和分配           | 预算超支、资源浪费、无法优化成本 |
| **供应商锁定** | 业务系统深度绑定单一 AI Provider  | 切换成本高昂、议价能力弱         |
| **安全漏洞**   | 提示注入、密钥泄露等攻击          | 系统被入侵、数据被盗、服务中断   |
| **权责不清**   | 谁在用、用什么、用多少无记录      | 审计困难、事故难以追溯           |

### 核心价值

#### 1. 降低风险

```
无治理                          有治理
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
员工直接调用 OpenAI  →  平台检测敏感信息并拦截
API Key 硬编码在代码 →  集中管理，定期轮换
无法追踪谁用了什么  →  完整审计日志
攻击者利用提示注入  →  实时检测并拦截
```

#### 2. 节约成本

**某企业案例**：500 名员工使用 AI，月均 10 万次调用

| 项目              | 无治理       | 有治理         | 节省     |
| ----------------- | ------------ | -------------- | -------- |
| 高价模型滥用      | 全员 GPT-4   | 按需分配模型   | 40%      |
| 无限额调用        | 无控制       | 部门配额管理   | 25%      |
| Provider 切换成本 | 改代码重部署 | 切配置即可     | 无法量化 |
| **总计**          | **¥50万/月** | **¥22.5万/月** | **55%**  |

#### 3. 提升效率

- **开发效率**：统一的 OpenAI 兼容接口，业务系统无需改动
- **运维效率**：集中配置管理，支持热更新策略
- **审批效率**：异步工作流，不阻塞用户操作
- **故障恢复**：自动故障转移，保障业务连续性

#### 4. 增强可控性

```
策略配置示例（config/policy.yaml）：

研发部门：
  ✅ 可用模型：GPT-4, Claude-3
  ✅ 速率限制：1000 次/分钟
  ✅ 工具权限：Jira, GitHub
  ✅ 风险检测：开启

财务部门：
  ✅ 可用模型：GPT-3.5 仅
  ✅ 速率限制：100 次/分钟
  ✅ 工具权限：禁用
  ✅ 风险检测：严格模式（阻止任何 PII）
```

#### 5. 促进创新

- **降低试错成本**：Mock Provider 支持本地开发测试
- **快速接入新模型**：新增 Provider 无需改业务代码
- **工具生态开放**：可扩展自定义工具（如内部 API）
- **渐进式推广**：可先小范围试点，再逐步扩大

### 对比：有无治理的差异

| 维度       | 直接使用 AI 服务     | 使用本平台           |
| ---------- | -------------------- | -------------------- |
| 数据安全   | ❌ 无保护             | ✅ 自动检测拦截       |
| 合规审计   | ❌ 无法审计           | ✅ 完整日志           |
| 成本控制   | ❌ 按用量付费，无控制 | ✅ 配额管理，模型分级 |
| 供应商锁定 | ❌ 代码深度绑定       | ✅ 配置切换，零代码   |
| 故障恢复   | ❌ 单点故障           | ✅ 自动故障转移       |
| 工具调用   | ❌ 无法实现           | ✅ 支持企业系统集成   |
| 部门隔离   | ❌ 无法隔离           | ✅ 策略隔离，配额独立 |
| 审批流程   | ❌ 无法实现           | ✅ 写操作审批工作流   |

## 概述

一个治理优先的 AI 平台，为企业级 AI 模型使用提供全面控制，同时保持对多种 Provider 和工具的灵活性。



AI 治理平台 V2.1 是一个基于 Python 的 FastAPI 应用程序，为 AI 模型交互提供全面的治理和控制。架构采用模块化设计，职责清晰分离：

- **API 层**：聊天补全、工具执行和管理操作的 RESTful 端点
- **执行层**：多 Provider 路由和工具代理能力
- **治理层**：策略引擎、风险检测和审批工作流
- **数据层**：PostgreSQL 数据库与全面审计
- **工作层**：已批准工具操作的异步执行

## 应用场景

### 企业级 AI 治理与合规

**场景**：一家金融公司需要让员工使用 AI 能力提高工作效率，但必须确保符合监管要求（如 GDPR、数据出境安全等）。

**解决方案**：
- **数据防泄漏**：自动检测并阻止敏感信息（身份证号、银行卡号、API 密钥）发送给外部 AI 服务
- **审计追踪**：记录所有 AI 交互，满足合规审计要求
- **访问控制**：不同部门配置不同的模型和权限，如研发部可使用 GPT-4，客服部仅限 GPT-3.5

### 多 AI Provider 统一管理

**场景**：企业同时使用多个 AI 服务（内部 LLM 网关、Azure OpenAI、阿里云通义千问等），需要统一入口管理。

**解决方案**：
- **统一 API**：提供 OpenAI 兼容的统一接口，业务系统无需改动
- **智能路由**：根据请求类型自动路由到最合适的 Provider
- **故障转移**：主 Provider 不可用时自动切换备用服务，保障业务连续性

### AI 辅助开发与运维

**场景**：开发团队希望 AI 能执行实际操作（创建 Jira 工单、查询 ServiceNow、部署服务等），但需要严格的审批管控。

**解决方案**：
- **工具调用**：AI 可以调用企业内部系统的 API
- **写操作审批**：创建、修改等高风险操作需要管理员审批后执行
- **参数验证**：严格校验工具调用参数，防止恶意或错误操作
- **异步执行**：审批通过后后台执行，不阻塞用户操作

### 成本控制与资源管理

**场景**：多个部门共用 AI 服务，需要控制预算并合理分配资源。

**解决方案**：
- **部门级配额**：为每个部门设置不同的速率限制和模型权限
- **使用统计**：实时追踪各部门的 AI 调用量和成本
- **模型分级**：不同场景使用不同成本的模型（如内部测试用 Mock，生产用 GPT-4）

### 安全防护

**场景**：担心员工在使用 AI 时泄露公司机密或被提示注入攻击。

**解决方案**：
- **风险检测**：实时识别 PII、密钥泄露和提示注入攻击
- **请求拦截**：检测到风险时自动阻止并记录事件
- **策略引擎**：灵活配置安全规则，适应不同业务场景

## 典型用户

| 用户角色 | 核心需求 | 平台价值 |
|---------|---------|---------|
| **CTO/架构师** | 统一管理多个 AI Provider，降低供应商锁定风险 | 多 Provider 支持、故障转移、统一 API |
| **合规官** | 满足数据安全和隐私法规要求 | 风险检测、审计日志、访问控制 |
| **IT 管理员** | 控制成本、分配资源、监控使用情况 | 部门级配额、使用统计、速率限制 |
| **安全团队** | 防止数据泄露和恶意攻击 | PII/密钥检测、提示注入防护、参数验证 |
| **开发团队** | 快速集成 AI 能力，无需关注治理细节 | OpenAI 兼容接口、工具调用、审批工作流 |

## 功能特性

### 核心能力

- **AI 聊天补全 API**：标准的 OpenAI 兼容 `/v1/chat/completions` 端点
- **多 Provider 支持**：
  - Mock provider（默认，无外部调用）
  - OpenAI 兼容 provider（用于内部 LLM 网关）
  - OpenAI provider（直接调用 OpenAI API）
  - 故障转移路由支持

- **治理与安全**：
  - 基于策略的部门级访问控制
  - PII、密钥和提示注入风险检测
  - 部门级速率限制
  - 全面的审计日志

- **工具执行框架**：
  - 带参数验证的工具注册表
  - Jira 和 ServiceNow 集成能力
  - 写操作需要审批
  - 已批准工具的异步执行

- **管理界面**：
  - 管理端点的基本身份认证
  - 审批工作流管理
  - 系统监控和健康检查

## 项目结构

```
ai-governance-platform-v2_1/
├── app/                        # 主应用程序代码
│   ├── api/                   # API 端点
│   │   ├── __init__.py
│   │   ├── admin.py          # 管理端点（审批）
│   │   ├── chat.py           # 聊天补全端点
│   │   ├── health.py         # 健康检查
│   │   └── tools.py          # 工具执行端点
│   ├── execution/            # 执行引擎
│   │   ├── providers/       # AI Provider 实现
│   │   │   ├── __init__.py
│   │   │   ├── mock.py      # Mock Provider
│   │   │   ├── openai.py    # OpenAI Provider
│   │   │   └── openai_compat.py  # OpenAI 兼容 Provider
│   │   └── router.py        # Provider 路由逻辑
│   ├── governance/           # 治理层
│   │   ├── __init__.py
│   │   ├── approvals.py     # 审批工作流
│   │   ├── policy.py        # 策略引擎
│   │   ├── registry.py      # 工具注册表
│   │   └── risks.py         # 风险检测
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── ai_requests.py   # AI 请求跟踪
│   │   ├── approvals.py     # 审批模型
│   │   ├── base.py          # 基础模型
│   │   ├── policies.py      # 策略模型
│   │   └── tools.py         # 工具调用模型
│   ├── schemas/             # Pydantic 模式
│   ├── worker/              # 异步工作器
│   │   ├── __init__.py
│   │   └── executor.py      # 后台任务执行器
│   ├── config.py            # 应用程序配置
│   ├── db.py                # 数据库设置
│   └── main.py              # FastAPI 应用程序入口
├── config/                   # 配置文件
│   └── policy.example.yaml  # 示例策略配置
├── docker/                   # Docker 设置
│   └── init-db.sql          # 数据库初始化
├── migrations/              # 数据库迁移
├── .env.example             # 示例环境变量
├── docker-compose.yml       # Docker 服务
├── requirements.txt         # Python 依赖
└── README.md               # 本文件
```

## 技术栈

### 后端框架
- **FastAPI**：现代、快速的 Web 框架，用于构建具有自动验证功能的 API
- **Uvicorn**：运行应用程序的 ASGI 服务器

### 数据库
- **PostgreSQL**：持久化存储的主数据库
- **SQLAlchemy 2.0**：支持异步的数据库 ORM
- **psycopg**：Python 的 PostgreSQL 适配器

### 核心依赖
- **Pydantic**：使用 Python 类型注解的数据验证
- **PyYAML**：YAML 配置解析
- **httpx**：用于外部 API 调用的异步 HTTP 客户端
- **python-multipart**：文件上传支持
- **python-jose**：JWT 令牌处理

## API 端点

### 公开端点

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| `POST` | `/v1/chat/completions` | AI 聊天补全（OpenAI 兼容） |
| `POST` | `/v1/tools/execute` | 执行工具操作 |
| `GET` | `/health` | 健康检查端点 |

### 管理端点（需要基本认证）

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| `POST` | `/admin/approvals/{id}/approve` | 批准工具执行 |
| `POST` | `/admin/approvals/{id}/reject` | 拒绝工具执行 |
| `GET` | `/admin/approvals` | 列出所有审批 |
| `GET` | `/admin/approvals/{id}` | 获取审批详情 |

## 快速开始

### Docker（推荐）

```bash
# 构建并启动所有服务
docker compose up --build

# 服务访问地址：
# API: http://localhost:8000
# API 文档: http://localhost:8000/docs
# 管理界面: http://localhost:8000/admin (admin/admin123)
# PostgreSQL: localhost:5432
```

### 本地开发

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp .env.example .env
cp config/policy.example.yaml config/policy.yaml

# 启动应用程序
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 配置

### 环境变量 (.env)

```bash
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/ai_governance

# API 密钥
OPENAI_API_KEY=your_openai_api_key
OPENAI_COMPAT_API_KEY=your_internal_api_key

# Provider 配置
OPENAI_COMPAT_BASE_URL=https://your-internal-gateway.com/v1

# 管理员凭证
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# 应用程序设置
LOG_LEVEL=INFO
MAX_REQUESTS_PER_MINUTE=60
```

### 策略配置 (config/policy.yaml)

策略文件定义每个部门的治理规则：

```yaml
defaults:
  route:
    models_allowlist: ["gpt-4o-mini", "gpt-4o"]
    providers:
      - name: "mock"
        kind: "mock"
    risk_detection:
      enabled: true
      detectors: ["pii", "secrets", "prompt_injection"]

departments:
  engineering:
    route:
      models_allowlist: ["gpt-4o", "claude-3-opus"]
      providers:
        - name: "internal"
          kind: "openai_compat"
          base_url_env: "OPENAI_COMPAT_BASE_URL"
          api_key_env: "OPENAI_COMPAT_API_KEY"
        - name: "fallback"
          kind: "mock"
    tools:
      enabled: true
      allowlist: ["jira", "servicenow"]
      write_tools: ["jira:create", "servicenow:create"]
      approval:
        required_for_write: true
    rate_limit:
      requests_per_minute: 100
```

## 版本历史

### V2.1 - 多 Provider 抽象层
- Provider 抽象层与接口模式
- 多 Provider 支持（mock、openai_compat、openai）
- 主 + 故障转移路由
- 按部门配置 Provider

### V2.3 - 工具代理加固
- 使用 Pydantic 进行参数模式验证
- 写操作审批工作流
- 工具调用与 LLM 请求 ID 绑定
- 增强的审计日志

### V2.4 - 异步工作器执行
- 非阻塞审批工作流
- 已批准工具的后台任务执行
- 状态跟踪：pending → approved → processing → completed/failed
- 生产安全的执行模型

## 数据库架构

平台使用 5 个主要数据库表：

| 表 | 用途 |
|-------|---------|
| `ai_requests` | 跟踪所有 AI 聊天请求 |
| `ai_tool_calls` | 记录工具执行尝试 |
| `risk_events` | 记录安全违规 |
| `policy_versions` | 管理策略版本控制 |
| `tool_approvals` | 存储审批工作流状态 |

## 开发状态

### 已实现功能
- ✅ 多 Provider 路由与故障转移
- ✅ 基于策略的访问控制
- ✅ 风险检测（PII、密钥、提示注入）
- ✅ 带参数验证的工具执行
- ✅ 写操作审批工作流
- ✅ 后台执行的异步工作器
- ✅ 全面的审计日志

### 待实现 / TODO
- ⏳ 工具代理集成（Jira、ServiceNow 实现）
- ⏳ RAG 适配器实现
- ⏳ 高级分析仪表板

### 生产环境建议
1. 使用 Redis 替换内存速率限制器
2. 添加 Alembic 数据库迁移
3. 集成 SSO/IAM 进行身份认证
4. 添加全面的监控和告警
5. 实现适当的密钥管理（如 Vault）

## 故障排除

### 数据库连接问题
```bash
# 检查 PostgreSQL 状态
docker compose ps postgres

# 查看数据库日志
docker compose logs postgres

# 重置数据库
docker compose down -v
docker compose up -d
```

### Provider 配置
- 验证 `OPENAI_COMPAT_BASE_URL` 从容器可访问
- 检查 API 密钥在 `.env` 中正确设置
- 检查 policy.yaml 中的 Provider 配置

### 权限问题
- 确保 `config/policy.yaml` 具有正确的文件权限
- 验证数据库用户具有必要的权限

## 贡献

欢迎贡献！请确保：
1. 代码遵循 PEP 8 风格指南
2. 所有新功能都包含测试
3. 相应更新文档
4. 维护安全最佳实践

## 许可证

[在此添加您的许可证信息]

## 支持

如有问题和疑问，请在项目仓库上提交 issue。

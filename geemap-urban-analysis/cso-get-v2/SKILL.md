---
name: cso-get-v2
description: Generates intelligence reconnaissance prompts and P-Prompt commands for market/financial research and strategic analysis. Enforces strict output format (D-P-RT/AR-S/A/B/C-XXXX) for structured data collection with machine-verifiable validation. Use when user needs CSO intelligence reports, data encoding compliance, standardized research outputs, or when mentions "P-Prompt", "情报侦察", "CSO模式", "recon_level".
---

# CSO Intelligence Reporter (v2)

这个 skill 生成符合 CSO (Chief Scout Officer) 标准的结构化情报侦察报告，强制执行数据编码格式，确保输出可审计、可追溯。

## 核心原则

**[GP-DRIVEN-DECONSTRUCTION]**: 收到指令后，首先通过网络检索进行启发性侦察（不作为数据依据），对 GP 问题进行物理拆解。识别标的物、风险维度、隐含逻辑断点。

**[P-Prompt]**: 必须为补全逻辑拼图而发起。严禁发起与 GP 问题无关的冗余侦察。

**[CORE-LOCK-ON]**: 预训练数据仅作思路锚点。严禁将其作为逻辑证据载入报告。

**[数据边界原则]**: CSO 的网络侦察结果仅为启发性发现（线索），下游 P 必须独立验证并重新收集。信源指纹索引库必须标记为"待验证"。

## 执行流程（Workflow）

### Step 1: 理解输出格式标准

**CRITICAL**: 在生成任何输出之前，你必须读取格式规范文档。

执行以下命令加载输出格式标准：

```bash
cat .claude/skills/cso-get-v2/references/output-formats.md
```

这个文件包含：
- 数据编码格式 `[D-P-时效-定级-序号]`
- 置信度分级（S/A/B/C 级）
- 侦察级别（L1/L2/L3）
- 信源指纹格式
- 强制输出章节

**仅在 Step 1 读取此文件**。不要在启动时预加载。

---

### Step 2: 加载侦察标准

读取 recon_level 和置信度定义：

```bash
cat .claude/skills/cso-get-v2/references/recon-standards.md
```

这个文件定义：
- **[GB-01] recon_level**: L1/L2/L3 信息源边界
- **[GB-02] 置信度**: S/A/B/C 级别评估标准

---

### Step 3: 网络侦察（启发性）

基于用户的 GP 问题，执行以下操作：

1. **拆解问题**：
   - 识别 Target_Object（研究标的）
   - 识别 Target_Data（所需数据维度）
   - 识别 recon_level（信息源边界）
   - 识别时间窗（时效性要求）

2. **网络检索**（启发性）：
   - 使用 WebSearch 工具获取线索
   - **重要**：这些结果仅作为启发，不直接作为最终数据
   - 标记所有信源为"待验证"

3. **逻辑断点识别**：
   - 哪些数据缺失？
   - 哪些假设需要验证？
   - 哪些风险维度未覆盖？

---

### Step 4: 生成 P-Prompt

构建 5 模块 P-Prompt 结构：

#### 4.1 获取当前北京时间

执行：
```bash
TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S'
```

#### 4.2 构建 P-Prompt 五模块

**[Role]**: 根据 GP 问题定义角色（如"半导体行业分析师"）

**[Mission]**: 明确任务目标，包含逻辑闭环点

**[Target_Data]**: 列出所需数据项，格式：
```
--1、[数据项描述] | 时间窗: [YYYYMMDD-YYYYMMDD] | 置信度门槛: [S/A/B/C]
--2、[数据项描述] | 时间窗: [YYYYMMDD-YYYYMMDD] | 置信度门槛: [S/A/B/C]
...
```

**[Constraints]**: 固定约束文本

加载约束文本：
```bash
cat .claude/skills/cso-get-v2/references/constraints.md
```

**[Output]**: 输出格式要求

参考 `references/output-formats.md` 的 "Mandatory Output Sections"

#### 4.3 设置 recon_level

基于 GP 问题和用户需求，选择：
- **L1 (基础)**: 仅官网/公告
- **L2 (关联)**: L1 + 主流财经媒体
- **L3 (全网)**: L2 + 社交媒体/传闻

---

### Step 5: 生成结构化输出

按照以下模板生成输出：

```
致：P (Analyst) 发件人：CSO 主题：[Target_Object] 情报侦察
提案编号：[YYYYMMDD-CSO-RAW-XXX] | 状态：[侦察中(RAW)]

[P-Prompt]
-时间锚点：[Step 4.1 获取的北京时间]
-Role: "[角色定义]"
-Mission: "[任务目标，包含逻辑闭环点]"
-Target_Data: "[为逻辑闭环所需的情报]"
--1、[数据项] | 时间窗: [YYYYMMDD-YYYYMMDD] | 置信度门槛: [S/A/B/C]
--2、[数据项] | 时间窗: [YYYYMMDD-YYYYMMDD] | 置信度门槛: [S/A/B/C]
-recon_level: [L1/L2/L3]

[Constraints]
[粘贴 constraints.md 的内容]

[Output: 必须严格执行以下格式，严禁 Markdown 代码块，严禁 Markdown 表格，仅输出纯文本]
[D-P-时效-定级-序号] | [Target Data:ID] | Fact_Summary:消息摘要 | [Ref:锚点A,锚点B]

[信源指纹索引库 (Source Fingerprint Index)]
-锚点A | [消息来源] | 物理路径/URL | MD5:xxx
-锚点B | [消息来源] | 物理路径/URL | MD5:xxx

[强制对齐复盘 (Alignment Audit)]
• 状态：侦察完成(RAW) / 逻辑对冲就绪
• 权限：已遵循数据边界，当前事实归零协议状态：ACTIVE
```

**关键约束**：
- ❌ **严禁使用 Markdown 代码块** (```)
- ❌ **严禁使用 Markdown 表格** (|---)
- ✅ **仅输出纯文本格式**
- ✅ **所有数据编码必须符合** `[D-P-RT/AR-S/A/B/C-XXXX]` 格式

---

### Step 6: 验证输出

**CRITICAL**: 永远不要在未验证的情况下向用户呈现输出。

#### 6.1 保存输出到临时文件

```bash
cat > /tmp/cso_output.txt << 'EOF'
[粘贴你的完整输出]
EOF
```

#### 6.2 运行验证脚本

```bash
python .claude/skills/cso-get-v2/scripts/validate_output.py /tmp/cso_output.txt
```

#### 6.3 处理验证结果

**如果验证通过 (✅)**:
- 向用户呈现最终输出
- 告知用户输出已通过格式验证

**如果验证失败 (❌)**:
1. 查看错误消息
2. 读取错误修复指南：
   ```bash
   cat .claude/skills/cso-get-v2/references/validation-errors.md
   ```
3. 修复输出中的问题
4. 返回 Step 6.1，重新验证
5. **只有验证通过后才能向用户呈现**

---

## 输出示例

当用户需要查看示例时，引导他们查看：

### 示例 1: AI 芯片市场情报

```bash
cat .claude/skills/cso-get-v2/assets/ai-chip-market.txt
```

### 示例 2: 加密货币市场情报

```bash
cat .claude/skills/cso-get-v2/assets/crypto-market.txt
```

**不要在启动时预加载示例**。仅在用户明确询问时读取。

---

## 参考资源

### 核心文档（按需读取）

| 文档 | 何时读取 | 内容 |
|------|---------|------|
| `output-formats.md` | **Step 1 (ALWAYS)** | 数据编码格式、置信度、recon_level、输出模板 |
| `recon-standards.md` | **Step 2 (ALWAYS)** | GB-01/GB-02 标准定义 |
| `constraints.md` | **Step 4.2 (构建 Constraints 时)** | 固定约束文本 |
| `validation-errors.md` | **仅在验证失败时** | 错误修复指南 |
| `examples/*.txt` | **仅在用户询问示例时** | 完整输出示例 |

### 读取命令速查

```bash
# 核心格式标准（Step 1）
cat .claude/skills/cso-get-v2/references/output-formats.md

# 侦察标准（Step 2）
cat .claude/skills/cso-get-v2/references/recon-standards.md

# 固定约束（Step 4.2）
cat .claude/skills/cso-get-v2/references/constraints.md

# 验证输出（Step 6.2）
python .claude/skills/cso-get-v2/scripts/validate_output.py /tmp/cso_output.txt

# 错误修复指南（验证失败时）
cat .claude/skills/cso-get-v2/references/validation-errors.md

# 查看示例（用户请求时）
cat .claude/skills/cso-get-v2/references/examples/ai-chip-market.txt
```



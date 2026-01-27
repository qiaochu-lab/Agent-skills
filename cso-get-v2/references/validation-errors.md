# CSO Validation Errors Guide

当 `validate_output.py` 报告错误时，使用本指南修复问题。

---

## 目录

1. [Header 错误](#1-header-错误)
2. [P-Prompt 错误](#2-p-prompt-错误)
3. [数据编码错误](#3-数据编码错误)
4. [Recon Level 错误](#4-recon-level-错误)
5. [信源索引错误](#5-信源索引错误)
6. [Alignment Audit 错误](#6-alignment-audit-错误)
7. [格式错误](#7-格式错误)
8. [常见组合错误](#8-常见组合错误)

---

## 1. Header 错误

### 错误 1.1: Missing header: '致：P (Analyst)'

**原因**: 输出缺少标准的收件人标题

**错误示例**:
```
CSO 情报报告
主题：AI芯片市场分析
```

**修复方法**:
```
致：P (Analyst) 发件人：CSO 主题：AI芯片市场情报侦察
提案编号：20260118-CSO-RAW-001 | 状态：[侦察中(RAW)]
```

**检查清单**:
- [ ] 包含"致：P (Analyst)"
- [ ] 包含"发件人：CSO"
- [ ] 包含"主题："

---

### 错误 1.2: Invalid proposal ID format

**原因**: 提案编号格式不正确

**错误示例**:
```
提案编号：CSO-001
提案编号：2026-01-18-RAW-001
```

**正确格式**:
```
提案编号：20260118-CSO-RAW-001
```

**格式要求**:
- YYYYMMDD（8位日期）
- `-CSO-RAW-`（固定分隔符）
- XXX（3位流水号）

**修复示例**:
```python
from datetime import datetime

# 生成今天的提案编号
date_str = datetime.now().strftime("%Y%m%d")
proposal_id = f"{date_str}-CSO-RAW-001"
# 输出: 20260118-CSO-RAW-001
```

---

### 错误 1.3: Missing or invalid status

**原因**: 状态标识缺失或不符合规范

**错误示例**:
```
状态：进行中
状态：RAW
```

**正确格式**:
```
状态：[侦察中(RAW)]
```

**要求**:
- 必须包含"侦察"和"RAW"
- 使用方括号和圆括号

---

## 2. P-Prompt 错误

### 错误 2.1: Missing section: 时间锚点

**原因**: 未执行 bash 命令获取实时北京时间

**错误示例**:
```
[P-Prompt]
-Role: "..."
```

**修复方法**:
```bash
# 执行命令获取北京时间
TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S'
# 输出: 2026-01-18 21:30:00
```

**在输出中添加**:
```
[P-Prompt]
-时间锚点：当前北京时间 2026-01-18 21:30:00
-Role: "..."
```

---

### 错误 2.2: Missing section: Role / Mission / Target_Data

**原因**: P-Prompt 缺少必需的模块

**完整的 P-Prompt 结构**:
```
[P-Prompt]
-时间锚点：[执行 date 命令]
-Role: "[角色定义]"
-Mission: "[任务目标]"
-Target_Data: "[数据需求]"
--1、[数据项] | 时间窗: [...] | 置信度门槛: X级
--2、[数据项] | 时间窗: [...] | 置信度门槛: X级
-recon_level: [L1/L2/L3]
```

**检查清单**:
- [ ] 时间锚点（执行 bash 命令）
- [ ] Role（角色定义）
- [ ] Mission（任务目标）
- [ ] Target_Data（至少 1 个数据项）
- [ ] recon_level（L1/L2/L3）

---

### 错误 2.3: Invalid Target_Data format

**原因**: Target_Data 数据项格式不正确

**错误示例**:
```
-Target_Data:
--1、全球AI芯片市场份额
--2、供应链动态，时间窗 2025-2026
```

**正确格式**:
```
-Target_Data: "为逻辑闭环所需的情报"
--1、全球AI芯片市场份额变化（按季度统计）| 时间窗: [20250101-20260118] | 置信度门槛: A级
--2、供应链动态及技术路线图 | 时间窗: [20250101-20260630] | 置信度门槛: B级
```

**格式要求**:
- `--N、`（序号 + 顿号）
- `|`（竖线分隔符）
- `时间窗: [YYYYMMDD-YYYYMMDD]`
- `置信度门槛: [S/A/B/C]级`

---

## 3. 数据编码错误

### 错误 3.1: No valid data encoding found

**原因**: 输出中没有任何符合格式的数据编码

**错误示例**:
```
NVIDIA H100 供应增加 30%
参考来源：锚点A
```

**正确格式**:
```
[D-P-RT-A-0001] | [TD-001] | NVIDIA H100 供应增加 30% | [Ref:锚点A]
```

**格式分解**:
```
[D-P-RT-A-0001]
 │ │ │  │  └─ 序号（0001-9999）
 │ │ │  └──── 定级（S/A/B/C/D）
 │ │ └─────── 时效（RT=实时/AR=档案）
 │ └───────── P（固定）
 └─────────── D（固定）
```

---

### 错误 3.2: Duplicate sequence numbers found

**原因**: 同一报告中出现了重复的序号

**错误示例**:
```
[D-P-RT-A-0001] | [TD-001] | 数据A | [Ref:锚点A]
[D-P-RT-B-0001] | [TD-002] | 数据B | [Ref:锚点B]  ← 序号重复
```

**修复方法**:
```
[D-P-RT-A-0001] | [TD-001] | 数据A | [Ref:锚点A]
[D-P-RT-B-0002] | [TD-002] | 数据B | [Ref:锚点B]  ✓ 修复序号
```

**提示**: 序号必须递增且唯一

---

### 错误 3.3: D-grade data detected (逻辑毒素)

**原因**: 使用了 D 级数据（这是警告，但应避免）

**示例**:
```
[D-P-RT-D-0001] | [TD-001] | 未验证的传闻 | [Ref:锚点A]
```

**修复方法**:
- **选项 1**: 验证数据后提升等级
  ```
  [D-P-RT-C-0001] | [TD-001] | 经初步验证的传闻 | [Ref:锚点A,锚点B]
  ```

- **选项 2**: 删除该数据项（D 级应触发熔断）

**重要**: D 级数据表示逻辑毒素，**不应出现在最终报告中**

---

## 4. Recon Level 错误

### 错误 4.1: Invalid or missing recon_level

**原因**: recon_level 格式错误或缺失

**错误示例**:
```
-recon_level: Level 2
-recon_level: L2-L3
-recon_level: 2
```

**正确格式**:
```
-recon_level: L2
```

**合法值**: `L1`, `L2`, `L3`（严格大小写）

---

### 错误 4.2: L1 but content mentions social media sources

**原因**: 声明 L1 侦察（仅官网），但内容引用了社交媒体

**矛盾示例**:
```
-recon_level: L1

[Output]
[D-P-RT-A-0001] | [TD-001] | Twitter 上有传闻... | [Ref:锚点A]
```

**修复方法**:

**选项 1**: 修正 recon_level
```
-recon_level: L3  ← 改为 L3（包含社交媒体）
```

**选项 2**: 移除社交媒体数据
```
[D-P-RT-A-0001] | [TD-001] | 官方公告显示... | [Ref:锚点A]
```

---

## 5. 信源索引错误

### 错误 5.1: Missing section: 信源指纹索引库

**原因**: 输出缺少信源索引章节

**修复方法**:

添加以下章节（在 [Output] 之后）:
```
[信源指纹索引库 (Source Fingerprint Index)]
-锚点A | NVIDIA 2025 Q4 财报 | https://investor.nvidia.com/... | MD5:a1b2c3
-锚点B | Bloomberg 报道 | https://bloomberg.com/... | MD5:d4e5f6
```

---

### 错误 5.2: No valid source anchors found

**原因**: 信源索引格式不正确

**错误示例**:
```
[信源指纹索引库]
锚点A: NVIDIA 财报
锚点B: Bloomberg
```

**正确格式**:
```
[信源指纹索引库 (Source Fingerprint Index)]
-锚点A | NVIDIA 2025 Q4 财报 | https://investor.nvidia.com/quarterly-results | MD5:a1b2c3
-锚点B | Bloomberg 市场报道 | https://bloomberg.com/news/ai-chips | MD5:d4e5f6
```

**格式要求**:
- `-锚点X` （减号 + 锚点 + 大写字母）
- `|`（竖线分隔符，共 3 个）
- `MD5:` （如果包含 MD5）

---

### 错误 5.3: Unreferenced anchors (警告)

**原因**: 定义了锚点但未在数据中引用

**示例**:
```
[Output]
[D-P-RT-A-0001] | [TD-001] | 数据A | [Ref:锚点A]

[信源指纹索引库]
-锚点A | ...
-锚点B | ...  ← 未被引用
```

**修复方法**:

**选项 1**: 删除未使用的锚点
```
[信源指纹索引库]
-锚点A | ...  ← 保留被引用的锚点
```

**选项 2**: 在数据中引用锚点
```
[D-P-RT-A-0002] | [TD-002] | 数据B | [Ref:锚点B]
```

---

## 6. Alignment Audit 错误

### 错误 6.1: Missing section: 强制对齐复盘

**原因**: 缺少 Alignment Audit 章节

**修复方法**:

在输出末尾添加：
```
[强制对齐复盘 (Alignment Audit)]
• 状态：侦察完成(RAW) / 逻辑对冲就绪
• 权限：已遵循 L2 边界，当前事实归零协议状态：ACTIVE
```

---

### 错误 6.2: Missing: 状态

**原因**: Alignment Audit 章节不完整

**完整格式**:
```
[强制对齐复盘 (Alignment Audit)]
• 状态：侦察完成(RAW) / 逻辑对冲就绪
• 权限：已遵循 [L1/L2/L3] 边界，当前事实归零协议状态：ACTIVE
```

**检查清单**:
- [ ] 包含"状态："
- [ ] 包含"权限："或"已遵循"
- [ ] 明确 recon_level（L1/L2/L3）

---

## 7. 格式错误

### 错误 7.1: Markdown code blocks (```) are FORBIDDEN

**原因**: 输出中使用了 Markdown 代码块

**错误示例**:
```
```python
# 这是代码
```
```

**修复方法**: **完全删除代码块**

CSO 输出是纯文本情报报告，**不应包含代码**。

---

### 错误 7.2: Markdown tables (|---|) are FORBIDDEN

**原因**: 输出中使用了 Markdown 表格

**错误示例**:
```
| 公司 | 市场份额 |
|------|---------|
| NVIDIA | 80% |
```

**修复方法**: 转换为纯文本列表

```
[D-P-RT-A-0001] | [TD-001] | NVIDIA 市场份额 80% | [Ref:锚点A]
[D-P-RT-A-0002] | [TD-001] | AMD 市场份额 15% | [Ref:锚点A]
```

---

### 错误 7.3: Forbidden HTML tags found

**原因**: 使用了不允许的 HTML 标签

**禁止标签**: `<table>`, `<div>`, `<span>`, `<code>`, `<pre>`

**修复方法**: 删除所有 HTML 标签，使用纯文本

---

## 8. 常见组合错误

### 组合错误 8.1: "快速修复"模式导致的多个错误

**症状**: 同时出现多个格式错误

**原因**: 尝试快速生成输出，跳过了格式检查

**修复步骤**:

1. **从模板开始**（不要从空白开始）
   ```bash
   cat .claude/skills/cso-get/v2/references/examples/ai-chip-market.txt
   ```

2. **逐章节填写**
   - Header → P-Prompt → Constraints → Output → Source Index → Alignment Audit

3. **每个数据编码必须正确**
   - 格式: `[D-P-RT/AR-S/A/B/C-XXXX]`
   - 检查序号唯一性

4. **运行验证**
   ```bash
   python scripts/validate_output.py /tmp/output.txt
   ```

5. **修复错误后重新验证**

---

### 组合错误 8.2: 混合中英文导致的格式不一致

**症状**: 章节名称混用中英文

**错误示例**:
```
[P-Prompt]
...
[Output]
...
[Source Fingerprint Index]  ← 应该是中文
```

**修复方法**: **统一使用中文章节名**

```
[信源指纹索引库 (Source Fingerprint Index)]  ✓ 正确
```

**标准章节名**:
- `[P-Prompt]`（固定英文）
- `[Constraints]`（固定英文）
- `[Output: ...]`（固定英文）
- `[信源指纹索引库 (Source Fingerprint Index)]`
- `[强制对齐复盘 (Alignment Audit)]`

---

## 验证循环 Workflow

正确的修复流程：

```
1. 生成输出
   ↓
2. 保存到临时文件
   ↓
3. 运行 validate_output.py
   ↓
4. 有错误？
   ├─ 是 → 阅读本指南 → 修复 → 返回步骤 2
   └─ 否 → 向用户呈现输出 ✓
```

**重要**: **永远不要**跳过验证步骤直接呈现输出给用户

---

## 快速参考

### 完整输出检查清单

使用此清单在提交前自检：

- [ ] **Header**: 包含致/发件人/主题/提案编号/状态
- [ ] **P-Prompt**: 包含时间锚点/Role/Mission/Target_Data/recon_level
- [ ] **Constraints**: 从 constraints.md 完整复制
- [ ] **Output**: 所有数据使用 `[D-P-...]` 格式
- [ ] **数据编码**: 序号唯一，无 D 级数据
- [ ] **信源索引**: 所有锚点都被定义和引用
- [ ] **Alignment Audit**: 包含状态和权限声明
- [ ] **格式约束**: 无 Markdown 代码块/表格/HTML
- [ ] **运行验证**: `validate_output.py` 通过

---

## 需要帮助？

如果本指南无法解决你的问题：

1. **重新阅读** `output-formats.md` 中的完整格式规范
2. **查看示例** `examples/ai-chip-market.txt` 的完整示例
3. **检查约束** `constraints.md` 中的所有约束条件
4. **验证侦察标准** `recon-standards.md` 中的 GB-01/GB-02

---

**最后更新**: 2026-01-18
**版本**: v2.0

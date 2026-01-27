# Agent-Skills（智能体技能）

一个用于构建、管理和进化 Claude Code Skills 的工具包 — 通过两种互补方法实现。

## 两种技能开发方法

本仓库展示了创建和管理 Claude Code Skills 的**两种不同方式**：

| 方法 | 技能 | 目的 |
|----------|--------|---------|
| **手动编写** | [skill-creator](./skill-creator/) + [cso-get-v2](./cso-get-v2/) | 遵循官方规范从零开始编写技能，通过脚本强制输出验证 |
| **GitHub 导入生态系统** | [github-to-skills](./github-to-skills/) + [skill-manager](./skill-manager/) + [skill-evolution-manager](./skill-evolution-manager/) + [geemap-urban-analysis](./geemap-urban-analysis/) | 从 GitHub 仓库导入技能，然后自动管理和进化它们 |

---

## 第一部分：手动编写技能

### 技能目录标准

每个结构良好的技能都遵循以下布局：

```
skill-name/
├── SKILL.md              # 入口点 — YAML 前置数据 + 指令
├── scripts/              # 执行确定性任务的可执行脚本
├── references/           # 补充文档，按需加载
└── assets/               # 模板、示例数据、样板文件
```

关键设计原则：**保持 `SKILL.md` 精简**（< 500 行）。详细内容放入 `references/`；可重复的逻辑放入 `scripts/`。

---

### skill-creator

**官方技能编写指南，本身就打包成一个技能。**

基于 Claude 的文档，`skill-creator` 编纂了从零开始编写技能的规范和最佳实践。它提供：

- **6 步创建工作流**：理解 → 规划 → 初始化 → 编辑 → 打包 → 迭代
- **上下文效率原则** — 仅包含 Claude 尚不知道的内容
- **三种自由度级别**的指令：文本（高）、伪代码（中）、脚本（低）
- 脚手架和验证脚本

| 脚本 | 目的 |
|--------|---------|
| `init_skill.py` | 搭建新技能目录的脚手架 |
| `package_skill.py` | 打包技能用于分发 |
| `quick_validate.py` | 验证 `SKILL.md` 前置数据（名称格式、必需字段、字符限制） |

| 参考文档 | 内容 |
|-----------|---------|
| `output-patterns.md` | 输出格式化模式 |
| `workflows.md` | 工作流设计模式 |

```
/skill-creator
```

---

### cso-get-v2 — 手动编写示例

**一个结构化的情报侦察技能，按照 `skill-creator` 规范手工制作。**

CSO 情报报告器通过严格的 6 步工作流生成金融/市场研究报告，包含 GP 驱动的解构和 P-Prompt 构建。

**这个示例的重要性 — 脚本强制输出验证：**

这里展示的最强大技术是使用 `scripts/` 在**运行时强制输出合规性**。`validate_output.py` 脚本以编程方式检查每个生成的报告是否符合严格的格式规则：

- 验证数据编码格式：`[D-P-RT/AR-S/A/B/C-XXXX]`
- 确保所有 5 个必需部分存在（标题、P-Prompt、输出、来源索引、对齐审计）
- 拒绝禁止元素（Markdown 代码块、表格）
- 验证来源指纹引用
- 检测重复的编码序列
- **返回退出代码 0/1** — 智能体必须通过验证才能交付输出

这种模式 — **将格式强制委托给脚本而不是仅依赖提示指令** — 适用于任何需要结构化、可重复输出的技能。

```
cso-get-v2/
├── SKILL.md                                  # 核心工作流指令
├── scripts/
│   └── validate_output.py                    # 强制输出格式（退出 0 = 通过）
├── references/
│   ├── constraints.md                        # 操作约束
│   ├── output-formats.md                     # 格式规范
│   ├── recon-standards.md                    # 侦察等级定义
│   └── validation-errors.md                  # 错误代码参考
└── assets/
    ├── ai-chip-market-intelligence.txt       # 示例报告
    └── crypto-market-intelligence.txt        # 示例报告
```

---

## 第二部分：GitHub 导入生态系统

对于封装现有开源工具的技能，完全自动化的生命周期处理创建、维护和持续改进。

```
+------------------+     +----------------+     +------------------------+
| github-to-skills | --> | skill-manager  | --> | skill-evolution-manager|
+------------------+     +----------------+     +------------------------+
      导入                 维护和                   从用户反馈中
      仓库作为             跟踪上游                 进化和改进
      技能                 更改                    
```

---

### github-to-skills

**将任何 GitHub 仓库转换为标准化的技能包。**

获取仓库元数据（README、最新提交哈希），分析工具调用模式，并搭建完整的技能目录，包含生命周期跟踪的前置数据：

```yaml
github_url: <原始仓库地址>
github_hash: <最新提交哈希>
version: <标签或0.1.0>
```

这些元数据使 `skill-manager` 能够稍后检测上游更改。

| 脚本 | 目的 |
|--------|---------|
| `fetch_github_info.py` | 检索仓库元数据（描述、README、提交哈希） |
| `create_github_skill.py` | 协调技能生成 |

```
/github-to-skills <github_url>
```

---

### skill-manager

**生命周期管理器 — 审计、更新和清点您的技能库。**

扫描本地技能目录中基于 GitHub 的技能，将本地 `github_hash` 与远程 HEAD 进行比较，并报告哪些技能已过时。

| 功能 | 描述 |
|------------|-------------|
| **审计** | 扫描带有 `github_url` 元数据的技能 |
| **检查** | 通过 `git ls-remote` 比较本地哈希与远程哈希 |
| **报告** | 状态摘要：过时 / 当前 |
| **更新** | 获取新的 README，对比更改，重写 `SKILL.md` |
| **清单** | 列出所有已安装的技能，删除不需要的技能 |

| 脚本 | 目的 |
|--------|---------|
| `scan_and_check.py` | 扫描目录，解析前置数据，检查远程版本 |
| `update_helper.py` | 更新前备份文件 |
| `list_skills.py` | 列出已安装技能的类型和版本 |
| `delete_skill.py` | 永久删除技能文件夹 |

```
/skill-manager check              # 扫描上游更新
/skill-manager list               # 列出所有已安装的技能
/skill-manager delete <name>      # 删除技能
```

---

### skill-evolution-manager

**持续改进引擎 — 从对话中学习并保留最佳实践。**

使用技能后，进化管理器会审查哪些有效、哪些无效，将结构化反馈提取到 `evolution.json` 中，并将改进融入 `SKILL.md`。

重要提示：经验数据通过 `evolution.json` 流动，**而不是**直接编辑 `SKILL.md`。这在技能升级过程中保留了累积的知识。

| 阶段 | 操作 |
|-------|--------|
| **审查** | 分析对话中的满意点/痛点 |
| **提取** | 将发现存储为结构化 JSON |
| **缝合** | 将经验转换为更新的 Markdown 文档 |
| **重新对齐** | 上游更新后批量重新缝合所有技能 |

| 脚本 | 目的 |
|--------|---------|
| `merge_evolution.py` | 逐步将新经验数据合并到 `evolution.json` |
| `smart_stitch.py` | 在 `SKILL.md` 中生成/更新最佳实践部分 |
| `align_all.py` | 升级后批量重新缝合所有技能 |

```
/evolve
```
或者："将这个经验保存到技能中"

---

### geemap-urban-analysis — GitHub 导入示例

**通过 `github-to-skills` 创建的技能的工作示例。**

该技能使用 Google Earth Engine 和 geemap 进行城市环境分析，展示了导入的 GitHub 工具如何成为完全功能的 Claude 技能。

| 功能 | 数据源 | 输出 |
|------------|------------|--------|
| **城市绿化度（NDVI）** | Sentinel-2（夏季，<20% 云量） | NDVI 分数（优秀 → 差）+ 交互式地图 |
| **城市扩张时间推移** | Landsat（1984至今） | 显示数十年城市增长的动画 GIF |
| **水域面积变化（NDWI）** | Sentinel-2（两年比较） | 面积（平方公里）、百分比变化、增减地图 |

| 脚本 | 目的 |
|--------|---------|
| `city_ndvi_analysis.py` | 植被覆盖分析 |
| `city_timelapse.py` | 城市扩张动画 |
| `water_area_change.py` | 水体变化检测 |

触发关键词："城市绿化"、"NDVI"、"城市扩张"、"时间推移"、"水域面积变化"、"NDWI"

---

## 安装

1. 克隆此仓库：
```bash
git clone https://github.com/qiaochu-lab/Agent-skills.git
```

2. 将所需技能复制到您的 Claude 技能目录：
```bash
# macOS/Linux
cp -r Agent-skills/skill-creator ~/.claude/skills/
cp -r Agent-skills/cso-get-v2 ~/.claude/skills/

# Windows
xcopy /E Agent-skills\skill-creator %USERPROFILE%\.claude\skills\
```

3. 重启 Claude 以加载新技能。

## 要求

- Python 3.8+
- Git
- PyYAML (`pip install pyyaml`)
- 对于 geemap：需要 `geemap`、`earthengine-api`（需要 Earth Engine 身份验证）

## 许可证

Apache 2.0（skill-creator）/ MIT（生态系统技能）

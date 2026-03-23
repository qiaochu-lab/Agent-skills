# Agent-Skills（智能体技能）

基于大语言模型（LLM）的智能体技能工具包，包含用于构建 Claude Code Skills 的脚手架工具，以及一个结合专业遥感领域的实际应用案例。

本仓库目前包含两个核心技能：

| 技能 | 描述 |
|----------|---------|
| [**skill-creator**](./skill-creator/) | **技能创造器**：官方技能编写指南的具体实现，帮助开发者从零开始标准化地构建、测试和打包新的 Agent Skill。 |
| [**geemap-urban-analysis**](./geemap-urban-analysis/) | **地理空间分析专家**：基于开源项目 `geemap` 和 Google Earth Engine (GEE) 封装的专业级遥感技能，支持用自然语言直接生成地表变化动图。 |

---

## ⭐️ 核心技能介绍

### 1. geemap-urban-analysis (地理空间分析 Agent)

**这是一个将复杂的遥感代码封装为“大模型可用工具（Tool Calling）”的典型最佳实践项目。**

它利用 Google Earth Engine 和开源库 `geemap`，将海量地理空间数据的检索、处理与可视化功能转化为大语言模型可以理解并执行的标准动作。这让非 GIS 专业的用户，也能通过类似“**帮我看看北京过去10年城市扩张情况**”的**自然语言对话**，直接获取专业的遥感分析图表和延时拉伸动图（GIF）。

**核心能力与应用场景：**

| 功能 | 数据源 | 输出形态 | 触发场景示例 |
|------------|------------|--------|------------|
| **城市绿化度（NDVI）** | Sentinel-2 | 植被指数地图与覆盖度分级 | “分析一下上海市中心夏天的植被覆盖度有多高？” |
| **地表变化延时拉伸 (Timelapse)** | Landsat (1984至今) | **显示数十年生长的动态 GIF** | “帮我生成一份亚马逊雨林过去20年被砍伐过程的动图！” |
| **水域面积变化（NDWI）** | Sentinel-2 | 面积变化统计与增减对比图 | “对比2018年和2023年鄱阳湖水域面积的变化情况。” |

**技术亮点**：
- **能力解耦与封装**：从 `geemap` 庞大的复杂 API 中提炼出目标明确的颗粒度脚本（如 `city_timelapse.py`），去除了不必要的参数干扰。
- **自然语言到空间呈现**：Agent 负责从对话中提取空间参数（时间范围、地理坐标包围盒），执行脚本层负责调度资源与云端渲染，实现了真正意义上的端到端“零代码遥感可视化”。
- **自动化格式校验**：通过严格的工具输出结构控制与异常处理，保障了请求大体量卫星图期间的稳定性。

---

### 2. skill-creator (技能创造器)

**一个“教 Agent 怎么编写 Agent 工具”的元技能。**

`skill-creator` 编纂了开发高质量提示词和关联执行脚本的规范，为撰写符合格式的 `.claude/skills` 提供了一套标准化的脚手架机制。

- **创建工作流**：支持一键运行 `init_skill.py` 搭建标准目录结构（含 `SKILL.md`, `scripts/`, `references/`, `assets/`）。
- **结构验证**：通过内置的 `quick_validate.py` 在运行时校验 `SKILL.md` 的 YAML 前置数据、必填项与格式字符长度限制。

---

## 🛠 安装与使用

1. **克隆此仓库**：
```bash
git clone https://github.com/qiaochu-lab/Agent-skills.git
```

2. **将所需技能安装到 Claude 本地技能目录**：
```bash
# macOS/Linux
cp -r Agent-skills/skill-creator ~/.claude/skills/
cp -r Agent-skills/geemap-urban-analysis ~/.claude/skills/

# Windows
xcopy /E Agent-skills\skill-creator %USERPROFILE%\.claude\skills\
xcopy /E Agent-skills\geemap-urban-analysis %USERPROFILE%\.claude\skills\
```

3. **环境配置（针对 geemap 技能）**：
- 确保系统已安装 Python 3.8+
- 安装依赖库：`pip install pyyaml geemap earthengine-api`
- **重要**：你需要拥有 Google Earth Engine 开发者账号，并完成本地鉴权。可以在终端执行 `earthengine authenticate` 登录。

4. **重启 Claude 或者对应的大语言模型工作区**，技能即可自动加载，您可直接用自然语言触发。

## 📄 许可证

本项目使用 MIT / Apache 2.0 许可证开源。

<!-- SPDX-FileCopyrightText: 2026 HanYang06 -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# 约定与红线

> 本文是 [AGENTS.md](../../AGENTS.md) 红线的展开版，是 LNA 的**规范入口**：
> 设计规范、目录规范、术语规范三者在此收口。
> 设计事实源在 [docs/architecture/](../architecture/index.md)，做什么在[路线图](../roadmap/1.x.md)；
> 冲突时以设计、路线图与仓库配置（`pyproject.toml` / `.pre-commit-config.yaml`）为准。

## 0. 权威顺序

```text
路线图  >  设计  >  代码
```

- **路线图管「要什么」**：做什么、按哪套设计、落在哪个版本（[1.x.md](../roadmap/1.x.md)）。
- **设计管「是什么、为什么」**：口径与理由（[设计篇](../architecture/design.md)）。
- **代码管「现在是什么」**：它是现状的唯一证据。
- 三层不一致时**改下层**；推翻上层只有两种动作：**新增条目**，或**撤回条目的 `决策状态`**（`已定` → `待裁` / `已废弃`）。
  条目只增不减，版本号只增不减。
- **未实现的设计标为「预留 / 草案 / 待定」，不得写成已实现。**

## 1. 设计规范（硬约束）

1. **禁改外部模型**：加载的预训练权重一律冻结 + `eval()`，训练只发生在自建的小模型上；用测试断言守住。
   （全程禁止微调大模型。）
2. **词表全局唯一**：只有一个 `lexicon` 实例，是全体模型**共享的参照系**；增改只能 **append 且升版本号**，
   禁止改已有条目（基础部分死锁）。**「冻结」指固化后的版本**；方向是**双向奔赴**（模型与表互相塑造），具体由**梯度下降分析**检验。
3. **配置不硬编码**：超参一律进配置（hydra），代码里不出现魔法数；**语言参数**（向量维度、词表范围、`L_max` 等）同样进配置，先给起步值、实测再固化。
4. **可复现**：固定 seed，config + seed 一并写进实验记录（mlflow）。
5. **无检测不成结论**：任何训练结果必须附**坍缩检测**；没有检测的结果不算数。
6. **风格自动化**：ruff + mypy + pre-commit 强制；规范尽量落成**机器能查**的检查，不写成人肉约定。

## 2. 目录规范（已定）

分法**不看分层，看归属**：每个目录回答「这件事归谁」。顶层就是**驾驭架构的三支柱 + 一层横切**。

```text
LNA/
├── README.md              # 项目门面
├── AGENTS.md              # 给代理的索引与红线
├── docs/                  # 文档（architecture / roadmap / guides / reference）
├── configs/               # hydra 配置（按 hydra 自己的约定，放仓库根）
├── src/lna/
│   ├── models/            # 支柱① 模型：角色无关，只是"模型"
│   │   └── lexicon/       #   词表：ID + 冻结向量（所有模型共享的参照系）
│   ├── orchestrator/      # 支柱② 调度核心：声明 API（Python）→ JS / YML；加载模型 + 路由
│   ├── training/          # 支柱③ 训练：一套数据 → 批量训 N 个专家
│   │   ├── gates/         #   三重门控（长度 / 熵 / 组合性）
│   │   └── eval/          #   坍缩检测 / 泛化阈值
│   └── infra/             # 横切基础设施
│       ├── data/          #   数据加载
│       ├── monitor/       #   硬件监控
│       └── report/        #   训练报告
├── tests/                 # 镜像 src/lna
└── runs/                  # 实验产物（mlflow），gitignore
```

- **模型角色无关**：`models/` 下**不建** `a/` `c/` `experts/`——角色是调度核心**运行时分配**的，
  写进目录就等于写死，多模型编排无从谈起。
- **调度核心的生成物（JS / YML）落哪：待定**——JS 只给机器、YML 给人读，二者是否入库、是否进构建目录，待定。
- **只建当前 Phase 要用的目录，不预建空占位**（做一步看一步）。
- 占位模块只写许可头 + 模块 docstring，不写空壳代码。

## 3. 术语规范

- **一个概念只有一个名字**；术语**以中文为准**、按中文自然层级命名（见[术语表](../reference/glossary.md)），
  英文命名非必需。
- **新增概念先入表**，再进代码与设计；同义词、别名一律视为错，见到就改。
- 术语表只收「读了会误解」的词，不当字典用；定义以设计与代码为准。

## 4. 许可与许可头

- 仓库为 **Apache-2.0**，**禁止引入 GPL / AGPL 依赖**（传染红线）；第三方库先核实许可再采用。
- 每个源文件 / 文档顶部必须有：

  ```text
  SPDX-FileCopyrightText: 2026 HanYang06
  SPDX-License-Identifier: Apache-2.0
  ```

  `.py` 用 `#`、`.md` 用 `<!-- -->`。

## 5. 质量门禁

- `mypy strict`、`ruff select=ALL`（逐条有理由的 ignore）、`ruff format` 强制。
- **warning 零容忍**（pytest `filterwarnings = ["error"]`）；覆盖率达标门槛以 `pyproject.toml` 为准。
- 提交前一条命令跑完：`uv run pre-commit run --all-files`（需先 `uv run pre-commit install`）。
- **不要 `git commit --no-verify`**：跳过只是把问题推到后面。

## 6. 文档与提交

- 文档、注释、commit message 用**中文**；commit 用 Conventional Commits（`feat(lexicon): …`）。
- **同一事实只写一处**：路线图不写设计口径，设计篇只解释事实依据。
- 改了实现就回写设计与路线图那一行，不留与代码不符的文档。

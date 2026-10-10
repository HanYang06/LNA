<!-- SPDX-FileCopyrightText: 2026 HanYang06 -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# AGENTS.md —— 给编码代理的项目须知

> 本文件只做**索引与红线**，不放长规则；细则在各处文档，冲突时以文档与仓库配置
> （`pyproject.toml` / `.pre-commit-config.yaml`）为准。

## 1. 项目是什么

**LNA**（Latent Nexus Architecture）：**架构型工程**——不是单体大模型，而是由 **N 个独立小专家模型**
组成的联合网络。要探索的是模型之间那门**私有的、通用的语言**（见[术语表](docs/reference/glossary.md)）。
Python 3.14（`.python-version`；声明 `>=3.11,<3.15`），`uv` 管理。当前**构想 / 设计阶段，尚无实现**。

**权威顺序 `路线图 > 设计 > 代码`**：
- 要什么 → [docs/roadmap/1.x.md](docs/roadmap/1.x.md)（格式见 [docs/roadmap/index.md](docs/roadmap/index.md)）
- 是什么 / 为什么 → [docs/architecture/index.md](docs/architecture/index.md)（索引与权威顺序）+ [design.md](docs/architecture/design.md)
- 怎么写 → [docs/guides/conventions.md](docs/guides/conventions.md)

## 2. 开工前 SOP

1. **先看路线图**：本次任务命中哪个条目，摸清它落哪个版本。
2. **再看设计与术语**：读相关的设计小节与[术语表](docs/reference/glossary.md)，别造别名。
3. **再动手**；**改了实现就回写设计与路线图那一行**。

## 3. 常用命令

```bash
uv sync                                  # 同步依赖
uv run lna                               # 运行入口
uv run pytest                            # 测试
uv run ruff check --fix .                # lint
uv run ruff format .                     # 格式化
uv run mypy                              # 严格类型检查
uv run pre-commit install                # 装钩子（一次）
uv run pre-commit run --all-files        # 提交前全量门禁
```

**不要** `pip install`，不要绕过 `uv run` 去调 `.venv/Scripts/*.exe`——工具版本唯一来源是 `uv.lock`。

## 4. 硬性约定（索引）

完整口径见[约定与红线](docs/guides/conventions.md)，这里只列红线：

- **模型角色无关**：模型就是模型，A / B / C 由**调度核心运行时分配**；**不得**把角色写进模型代码或目录
  （写死就丧失多模型编排能力）。**模型是模型，架构是架构。**
- **禁改外部模型**：预训练权重一律冻结 + `eval()`，训练只发生在自建小模型上（**全程禁止微调大模型**）。
- **词表全局唯一**：一个 `lexicon` 实例，是全体模型**共享的参照系**；只能 append + 升版本号，禁止改已有条目。
  **固化后冻结**；方向是**双向奔赴**（模型与表互相塑造），由**梯度下降分析**检验。
- **无检测不成结论**：任何训练结果必须附**坍缩检测**，否则不算数。
- **配置不硬编码**：超参一律进 hydra 配置，代码里不出现魔法数。
- **一个概念只有一个名字**：术语以中文为准，先入[术语表](docs/reference/glossary.md)再用。
- **未实现标「预留 / 草案 / 待定」**，不得写成已实现。
- 每个文件顶部必须有 SPDX 头（`SPDX-FileCopyrightText: 2026 HanYang06` + `SPDX-License-Identifier: Apache-2.0`）。
- 文档、注释、commit message 用中文；commit 用 Conventional Commits（`feat(lexicon): …`）。
- **只有用户明确要求才 commit。**

## 5. 结构速查

```text
README.md            # 门面
docs/architecture/   # 设计事实源：index.md 索引 + design.md 正文
docs/roadmap/        # 路线图（权威）：index.md 格式 + 1.x.md 条目
docs/guides/         # 约定与红线
docs/reference/      # 术语表
src/lna/
  models/            # 支柱① 模型（角色无关）：lexicon/ 词表
  orchestrator/      # 支柱② 调度核心：加载模型 + 数据路由
  training/          # 支柱③ 训练：gates/ 门控 · eval/ 检测
  infra/             # 横切：data/ 数据 · monitor/ 硬件监控 · report/ 训练报告
tests/               # 镜像 src/lna
runs/                # 实验产物（mlflow），gitignore
```

**只建当前 Phase 要用的目录，不预建空占位**；目录口径见[约定与红线](docs/guides/conventions.md) §2。

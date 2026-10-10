# LNA

> Latent Nexus Architecture

**架构型工程：不是单体大模型，而是一套由 N 个独立小型专家模型组成的联合网络。**

LNA 要探索的，是模型与模型之间那门**私有的、通用的语言**。这门语言是整套框架成立的前提。

- **状态**：构想 / 设计阶段，尚无实现
- **设计文档**：[docs/architecture/index.md](docs/architecture/index.md)
- **路线图**：[docs/roadmap/1.x.md](docs/roadmap/1.x.md)
- **约定与红线**：[docs/guides/conventions.md](docs/guides/conventions.md)　**术语表**：[docs/reference/glossary.md](docs/reference/glossary.md)

## 快速开始

需要 Python 3.14+ 与 [uv](https://docs.astral.sh/uv/)。

```bash
uv run lna
```

## 依赖分组

均为可选依赖组，按需安装：`dev` / `test` / `docs` / `ml` / `comms`。

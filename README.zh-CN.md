# xone-cli

语言：[English](./README.md) | 中文

`xone-cli` 是 X-One Agent Evidence Loop 的统一本地入口。

它把分散的工具串成一条清晰路径：

```text
收集 PR 证据
-> 判断交接决策
-> 需要时生成失败包
-> 需要时附加 MCP 风险上下文
-> 运行安全本地训练场景
```

## 安装

```bash
python -m pip install xone-cli
xone --version
xone doctor
```

## 首次运行

```bash
xone doctor
xone doctor --install-plan
xone runbook --head HEAD --dry-run
```

`xone doctor --install-plan` 会输出按场景分组的安装命令、推荐的 X-One package 版本、适用时机和下一条可尝试的命令。

`xone runbook` 会自动探测本地仓库默认分支。当前还不直接接收远程 GitHub URL；请先 clone 仓库，再用 `--repo` 传本地路径。

如果要重复执行开源样本替代真实用户反馈评测，可以使用只读评测入口：

```bash
xone eval open-source --repos repos.txt --output evaluation.md --format markdown
```

当你希望 X-One shallow clone 公开仓库并只运行 X-One dry-run 命令时，增加 `--clone-root .xone-eval-clones`。它不会运行第三方安装脚本、测试、容器或项目命令。

`xone-cli` 编排这些 X-One 工具：

- `agent-pr-evidence`
- `agent-failure-packet`
- `mcp-risk-index`
- `ai-incident-lab`

当前推荐工具版本：

- `agent-pr-evidence 0.4.2`
- `agent-failure-packet 0.4.2`
- `mcp-risk-index 0.3.1`
- `ai-incident-lab 0.2.2`

## 边界

- 不替代底层工具。
- 不自动发布 GitHub 评论。
- 不自动修改仓库。
- 不做 runtime allow/deny enforcement。
- 不运行第三方项目脚本。
- `xone eval open-source` 只会在用户显式执行该命令时调用 GitHub API 和 `git clone --depth 1`。

## 文档

- [产品基础](./docs/product-foundation.md)
- [安装](./docs/install.md)
- [发布](./docs/release.md)
- [开源反馈 Ledger](./docs/feedback/open-source-feedback-ledger.md)

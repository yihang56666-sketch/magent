# 贡献指南

感谢你对 **magent — Codex 原生子智能体编排 Skill** 的关注。

## 如何跑测试

仓库契约测试无第三方依赖，Python 3 标准库即可：

```powershell
python -X utf8 -B -m unittest discover -s tests -v
```

（等价于 `python -m unittest discover -s tests -v`；`-X utf8` 仅用于 Windows 控制台编码。）

期望输出末尾为 `OK`，当前契约用例为 33 项。提交前请本地跑通；CI（`.github/workflows/ci.yml`）会再跑同一套检查。

## 如何改协议

协议主体在 `codex-native-subagent-orchestrator/`：

| 路径 | 内容 |
| --- | --- |
| `SKILL.md` | 运行时编排流程（保持精简、可执行） |
| `references/dispatch-contract.md` | 分派包与边界 |
| `references/role-catalog.md` | 角色目录 |
| `references/workflow-patterns.md` | 工作流模式 |
| `references/acceptance-cases.md` | 原生验收案例 |
| `examples/` | 完整分派示例 |

修改公开契约时必须同步：

1. 更新 `tests/test_skill_contract.py` 中对应的断言；
2. 保持子智能体**只读**、主智能体唯一写入的不变量；
3. 工具名以**实际会话 schema** 为准，不写死未暴露的工具；
4. 不要引入 CLI、仪表板、模型 API、遥测或提示词复制生命周期。

`AGENTS.md` 是仓库级约定，请与协议改动一并遵守。

## 如何提交

1. 在本地 `main` 上工作（先与 `origin/main` / `github-public-release` 对齐）。
2. 小步提交，信息用英文祈使句，例如：
   - `docs: clarify dispatch packet evidence rules`
   - `fix: keep subagent roles read-only in role catalog`
   - `test: cover acceptance negative paths`
3. 提交前跑通契约测试，必要时刷新 `output/readiness/skill-contract-green.log`。
4. 不要提交密钥、本机绝对路径、`.agents/reports/cache/`、工作树残留或 `__pycache__`。
5. 向维护者发起 PR；推送与发布由维护者决定，不在贡献流程中自动执行。

## 文档口径

对外标题统一为「**magent — Codex 原生子智能体编排 Skill**」。Skill 目录名 `codex-native-subagent-orchestrator` 是安装产物名，两者不要混用成多套产品名。

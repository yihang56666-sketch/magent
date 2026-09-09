# Project Portfolio Audit

| 项目 | 当前判断 | 已验证证据 | 仍需人工验收 |
| --- | --- | --- | --- |
| 子智能体 Skill | 契约完整，可作为方法论项目展示 | `python -m unittest discover -s tests -v`：33 tests、OK | 已在真实 Codex 会话完成一次原生协作演练（Erdos 审查 magent、Poincare 审查硬件 agent），见 `output/readiness/acceptance-2026-09-09.md` |

## 本次核对记录

- 2026-09-06：结构契约测试为 27 项；HR 指导书与 README 已按 27 项口径。
- 2026-09-06：一次执行只能证明相应情景，不能把结构测试说成端到端成功率。
- 2026-09-07：修复测试契约文件中的本机用户名自指泄漏后，结构契约测试刷新为 28 项（该口径已被 2026-09-09 的 33 项取代）。
- 2026-09-09：工具协议改为按实际会话 schema 发现，删除旧 `spawn_agent/send_input/close_agent` 术语；新增全目录隐私扫描、本地 `.claude` 危险权限否定断言、验收记录检查；结构契约测试刷新为 33 项。

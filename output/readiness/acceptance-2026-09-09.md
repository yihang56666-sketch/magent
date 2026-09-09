# 2026-09-09 真实原生协作验收记录

本次记录对应一次真实 Codex 会话，不是回放的 fixture，也不是结构测试的替身。
它只证明该次会话中发生过以下事实，**不证明**模型会无条件遵守 Skill 指令。

## 证据

- 日期：2026-09-09；任务：双选会项目深度完善，用户明确授权子智能体对抗审查。
- 会话实际暴露的原生子智能体工具：`create_thread`、`send_message_to_thread`、
  `wait_threads`、`read_thread`、`set_thread_archived`。旧文档中的
  `spawn_agent/send_input/close_agent` 在当前 schema 中不存在，已同步移除。
- 已创建并收集结果的子智能体：
  - Erdos（`01a0841a-5487-7680-93f5-59d2c525c37b`）：只读审查 magent 仓库，
    返回 P0/P1/P2 发现，未修改任何文件。
  - Poincare（`01a0841a-52cc-79c3-a10d-f75c5c10d0f9`）：只读审查硬件 agent
    仓库，线程最终状态为 completed/idle，但最终报告未保留在会话存储中，
    因此不引用其评分；硬件 agent 验收以主智能体实测为准：pytest
    1017 passed / 12 skipped，CLI 为 35 个扁平子命令。
  - Fermat（`01a0841a-57b7-7433-8005-2cc2eb5a69d0`）：博客审查子智能体因模型
    不支持 vision 而报错，作为真实失败观察记录，主智能体改用无图片的
    Playwright/DOM 验证。
- 工作区基线：审查前记录各仓库 `git status`；审查期间未授权子智能体写入，
  所有修改均由主智能体完成。

## 结论边界

本次记录是“真实发生过协作”的证据，不是“全部验收案例通过”的证据。剩余案例
仍需按 `references/acceptance-cases.md` 在 HR 演示时现场复跑并记录工具调用与
证据。

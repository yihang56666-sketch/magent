# Codex 原生子智能体编排 Skill HR 面试指导书

## 一句话介绍

这是一个面向 Codex 原生 `spawn_agent` 的编排 Skill：它把复杂任务拆成边界清晰、只读、可审计的证据生产任务，由主智能体统一决策、写入、验证和交付。

## 技术与架构

- `SKILL.md` 是短流程入口，负责判断是否分派、选择模式、建立分派包、收集结果和失败恢复。
- `references/` 分为 delegation rubric、role catalog、workflow patterns 和 dispatch contract，避免每次临时发明代理协议。
- 角色包括 Explorer、Domain analyst、Reviewer、Test analyst、Security reviewer、Documentation researcher 和 Architect。
- 共享工作区采用“先记录 Git 基线、代理只读、返回后核对 diff”的协作边界；主智能体是唯一写入者和最终验证者。
- 工作模式包括并行证据收集、critic loop、sequential handoff 和 supervisor-led analysis；团队规模默认 1 到 3 个。

## 可演示路径

```powershell
cd D:\一些有用的项目\子智能体
python -m unittest discover -s tests -v
```

当前仓库契约测试 20/20 通过，覆盖元数据、只读约束、共享工作区保护、并发容量检查、失败恢复和可移植验证说明。

## HR 常问与回答

**为什么不让多个代理直接改代码？** 共享目录下并行写入会引入冲突和不可归因变更；代理只产出证据，主智能体集中修改可以保留审计链和一致的验收标准。

**什么时候不应该分派？** 单文件小改动、强顺序调试、一次命令即可回答的问题不值得分派；技能明确要求比较分派成本和独立不确定性。

**代理失败怎么办？** 记录超时/空结果，继续独立工作；只有缺失结果会改变决策时，才允许一次更窄的替补分派，绝不无限等待。

**如何防止提示词范围膨胀？** 每个 dispatch packet 固定使命、允许范围、禁止操作、所需证据、冲突策略和停止条件。

**目前限制是什么？** 这是编排层，不是独立运行时；它依赖当前 Codex 会话提供原生子智能体能力，也不提供模型 API、遥测、仪表板或权限沙箱。

## 下一步

继续为常见缺陷、代码审查和研究场景补充可复用 dispatch 示例，并在支持原生代理的环境中做一次端到端协作演练。

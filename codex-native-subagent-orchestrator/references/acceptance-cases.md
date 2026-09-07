# Native Acceptance Cases

These are manual native-session acceptance cases, not a simulated runtime.
Contract tests check document structure and consistency; they are not proof of model behavior.
Use only tools actually exposed in the current session and record their schema/version context.

| Case | Input condition | Required decision and observable evidence |
| --- | --- | --- |
| NO-AUTH | A request asks for depth but no user or applicable instruction authorizes delegation. | Keep local; zero spawn calls. Loading this Skill is not sufficient authorization. |
| IMMEDIATE-BLOCKER | Delegation is authorized, but the question blocks the immediate local step and no independent work exists. | Main agent answers locally; zero spawn calls for that question. |
| ONE-CRITIQUE | One authorized, bounded independent critique can run alongside useful main-agent work. | One specialist, a complete packet, returned agent ID, and evidence of useful local work. Do not add a second reviewer for reassurance. |
| WAIT-TIMEOUT | A native wait expires or returns empty while the original handle remains live. | Keep it pending, observe the same handle later, and do not dispatch a replacement. Record the observation separately from task status. |
| DIRTY-CONTENT | A scoped tracked or existing untracked file changes content while its status text stays unchanged. | Detect the fingerprint/diff change and stop to attribute it. Do not automatically blame an agent, revert, or clean the user's work. |
| MISSING-EVIDENCE | A report gives a conclusion but lacks sources or reproductions. | Ask the original agent once through the native message tool, then verify locally, discard the claim, or report the gap. No second overlapping broad tour. |
| TERMINAL-FAILURE | An authoritative native result confirms a terminal error. | Account for the missing result. Resume the original when supported and context-dependent, or confirm its termination before at most one narrow replacement; otherwise resolve locally. |
| COMPLETED-CLOSE | A started agent has returned its findings and is no longer needed. | Collect its report by ID, request native close, and check capacity before another assignment. Do not interpret a close tool's previous-status return as the post-close state. |

## Evidence record

For a real exercise record the date, authorized task, relevant native tools,
scoped pre-dispatch content digests, packet, returned ID, local work performed,
wait/message/close observations, received evidence, independent main-agent
verification, and post-dispatch digests. Omit credentials and unrelated private
files. Distinguish completed tests from proposed tests and unavailable tools.

If a case was only inspected rather than executed, label it a reasoning check.
Do not label a replayed fixture, a structural unittest, or an imagined tool trace
as native end-to-end execution. Do not claim latency, cost, or quality gains
without comparative measurements.

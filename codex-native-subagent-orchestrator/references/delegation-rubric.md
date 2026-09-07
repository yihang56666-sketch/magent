# Delegation Rubric

Keep work local when it is an obvious answer, a narrow single-file edit, a
single sequential operation, or when an extra agent would need nearly all of
the main agent's context to help. Also keep an immediate next step local if
its result blocks the main agent and there is no useful independent local work.
Establish applicable authorization before applying the delegation criteria.

Delegate when at least one independent question can materially reduce risk or
uncertainty: unfamiliar code, a reproducible bug, a risky regression surface,
security boundaries, independent research, or a design choice with real
trade-offs. That question must be answerable alongside useful local work, not
by handing off the main agent's urgent blocker and immediately waiting.

Choose the smallest useful team:

| Signal | Team |
| --- | --- |
| One independent uncertainty or one needed critique | 1 specialist |
| Two concrete independent questions | 2 specialists |
| Three concrete independent questions in a broad or risky task | 3 specialists |
| Security-sensitive or clearly cross-domain task | A fourth only when it owns an independent question |

Do not add agents for reassurance. Every agent must answer a question whose
answer changes the main agent's next decision.

# Detailed Chinese GitHub Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recreate `yihang56666-sketch/magent` as a public GitHub repository whose default branch presents the current Codex native subagent orchestration Skill with a detailed Chinese README and repository description.

**Architecture:** Keep runtime instructions concise in `codex-native-subagent-orchestrator/SKILL.md`, while the root `README.md` carries user-facing explanation, installation, examples, comparison, safety boundaries, and FAQs. Extend the dependency-free contract tests so the public documentation cannot silently regress to the old runtime positioning. Create the remote through the authenticated GitHub web interface, then push the verified local history without rewriting it.

**Tech Stack:** Markdown, Python `unittest`, Git, GitHub web interface, Codex Skill format.

---

### Task 1: Define the Chinese README contract

**Files:**
- Modify: `tests/test_skill_contract.py`

- [ ] **Step 1: Add the failing documentation contract test**

Add this method to `SkillContractTests`:

```python
def test_readme_is_a_detailed_chinese_product_guide(self) -> None:
    text = README.read_text(encoding="utf-8")

    for phrase in (
        "Codex 原生子智能体编排",
        "原生子智能体与本 Skill",
        "什么时候适合使用",
        "什么时候不应该分派",
        "完整工作流程",
        "动态临时专家",
        "失败与超时",
        "安全边界",
        "使用示例",
        "常见问题",
    ):
        self.assertIn(phrase, text)
```

- [ ] **Step 2: Run the new test and verify RED**

Run:

```powershell
python -m unittest tests.test_skill_contract.SkillContractTests.test_readme_is_a_detailed_chinese_product_guide -v
```

Expected: `FAIL` because the current README is English and does not contain the required Chinese sections.

- [ ] **Step 3: Commit the failing contract**

```powershell
git add -- tests/test_skill_contract.py
git commit -m "test: require detailed Chinese project documentation"
```

### Task 2: Write the detailed Chinese README

**Files:**
- Modify: `README.md`
- Test: `tests/test_skill_contract.py`

- [ ] **Step 1: Replace the root README with the approved structure**

Write a Chinese-first README containing:

```markdown
# Codex 原生子智能体编排 Skill

一句话定位：原生子智能体工具（如 `create_thread`）是执行引擎，本 Skill 是判断、路由、安全、恢复与结果汇总层。

## 它解决什么问题
## 原生子智能体与本 Skill 有什么区别
## 核心优势
## 什么时候适合使用
## 什么时候不应该分派
## 完整工作流程
## 角色系统与动态临时专家
## 失败与超时处理
## 安全边界与只读约束
## 使用示例
## 安装
## 前置条件
## 仓库结构
## 验证
## 限制与非目标
## 常见问题
## License
```

Retain the existing safe Windows and macOS/Linux installation commands, the portable verification command, the current-session native subagent tool prerequisite, and the statement that read-only behavior is instruction plus worktree auditing rather than an independent permission sandbox.

- [ ] **Step 2: Run the focused test and verify GREEN**

Run:

```powershell
python -m unittest tests.test_skill_contract.SkillContractTests.test_readme_is_a_detailed_chinese_product_guide -v
```

Expected: `OK` with one passing test.

- [ ] **Step 3: Run the complete contract suite**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests pass with zero failures.

- [ ] **Step 4: Commit the documentation**

```powershell
git add -- README.md
git commit -m "docs: add detailed Chinese Skill guide"
```

### Task 3: Validate the public release artifact

**Files:**
- Verify: `README.md`
- Verify: `codex-native-subagent-orchestrator/`
- Verify: `.github/workflows/ci.yml`

- [ ] **Step 1: Run structural validation when available**

Locate the installed `skill-creator/scripts/quick_validate.py`. If present, run it against `codex-native-subagent-orchestrator/`; otherwise record that only the repository contract suite is available.

- [ ] **Step 2: Check repository hygiene**

Run:

```powershell
git diff --check
git status --short
rg -n "TO[D]O|TB[D]|C:\\Users\\" README.md codex-native-subagent-orchestrator tests .github
```

Expected: no whitespace errors, no private absolute paths, and only the two pre-existing untracked historical plan files remain outside the release.

- [ ] **Step 3: Review the release diff and history**

Run:

```powershell
git log --oneline --decorate -8
git diff --stat origin/main...HEAD
```

Expected: the branch retains history, removes the obsolete runtime, contains the pure Skill, and adds only the approved detailed documentation work.

### Task 4: Recreate and publish the GitHub repository

**Files:**
- No local file changes.

- [ ] **Step 1: Create the public repository**

Using the authenticated GitHub web interface, create:

```text
Owner: yihang56666-sketch
Repository name: magent
Visibility: Public
Initialize with README: No
Description: 通用 Codex 原生子智能体编排 Skill：智能判断任务是否值得分派，动态选择只读专家角色，处理失败与冲突，并由主智能体完成验证和结果汇总。
```

- [ ] **Step 2: Confirm the remote target before pushing**

Run:

```powershell
git remote -v
git ls-remote origin
```

Expected: `origin` targets `https://github.com/yihang56666-sketch/magent.git`; a newly created empty repository may return no refs.

- [ ] **Step 3: Publish the verified history as `main`**

Run:

```powershell
git push -u origin HEAD:main
```

Expected: a new remote `main` branch is created without force push.

- [ ] **Step 4: Verify the remote publication**

Run:

```powershell
git ls-remote --heads origin main
git rev-parse HEAD
```

Expected: both commands report the same commit SHA.

- [ ] **Step 5: Verify GitHub presentation**

Open `https://github.com/yihang56666-sketch/magent` and confirm that the repository is public, `main` is the default branch, the Chinese description is visible, and the detailed Chinese README renders on the landing page.

### Task 5: Final release report

**Files:**
- No file changes.

- [ ] **Step 1: Report evidence**

Report the repository URL, remote commit SHA, contract-test count, validator result, exact files committed, and the two intentionally untracked historical plan files.

- [ ] **Step 2: Keep local branch tracking aligned**

After the push succeeds, set the current branch to track `origin/main` only if Git did not configure tracking automatically. Do not delete local branches or rewrite history as part of this release.

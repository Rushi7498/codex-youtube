# Bringing in the upstream reference materials

Upstream project: https://github.com/AgriciDaniel/claude-youtube

The upstream README describes a Claude Code skill with 14 sub-skills, 9 reference guides, 9 channel templates and YouTube API helper scripts. This repository currently supplies a Codex instruction layer and workflow recipes; it does not yet bundle every upstream file.

## Windows PowerShell steps

From the parent folder where you want to keep the source checkout:

```powershell
git clone https://github.com/AgriciDaniel/claude-youtube.git upstream-claude-youtube
```

Review the upstream `LICENSE` and its current terms, then copy/adapt useful material into this repository. Keep the original notices where required. For example, you can copy reference and template directories into `upstream-reference/` for personal study, or selectively migrate the needed files into `docs/reference/` after adapting references to Codex paths.

Do not copy Claude-only configuration (such as `CLAUDE.md`, `.claude-plugin/`, or the Claude installation scripts) as though it configures Codex. Use `AGENTS.md` as this repository's project instruction file and ask Codex to open workflow prompt files when needed.

## Python integrations

When migrating scripts:
- Review all imports and dependencies before running.
- Replace hard-coded Claude-specific cache paths with a project-appropriate user cache path.
- Put credentials in environment variables or a local ignored `.env` file.
- Test API quota accounting and error behavior before relying on results.
- Keep private analytics behind authorized OAuth; an API key alone does not authorize private Studio data.
- Run scripts with small requests first to control API quota.

## Smoke test after migration

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Only install dependencies required by the scripts actually migrated. A fresh Python environment is optional if you use only the instruction files.

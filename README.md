# Codex YouTube Creator Toolkit

A Codex-friendly adaptation scaffold inspired by [AgriciDaniel/claude-youtube](https://github.com/AgriciDaniel/claude-youtube). It gives Codex project instructions and repeatable workflows for YouTube channel audits, SEO, scripts, hooks, thumbnails, strategy, calendars, Shorts, analytics, repurposing, monetization, competitor research, metadata, and ideation.

> This starter package is a Codex adaptation layer, not a verbatim copy of the upstream repository. Importing its reference guides and scripts is a separate step. Upstream is MIT-licensed; retain its license and notices when copying code or documentation.

## Get started on Windows

1. Create a new GitHub repository called `codex-youtube` (prefer Private initially).
2. Put these files in it, then clone it:
   ```powershell
   git clone https://github.com/YOUR-USERNAME/codex-youtube.git
   cd codex-youtube
   code .
   ```
3. Open the repository in VS Code and start Codex in the project.
4. Ask Codex: `Read AGENTS.md and help me set up the YouTube Creator Toolkit.`

## Example prompts

Use natural language; these prompt recipes are provided as files in `.codex/prompts/`:

- “Audit my YouTube channel: [channel URL]. Goal: grow views and subscribers.”
- “Create an SEO package for a video about [topic]. Audience: [audience].”
- “Write a 6-minute Marathi YouTube script about [topic], with a strong hook and a clear source-checking plan.”
- “Give me 3 YouTube thumbnail concepts for this video. Make each concept distinct.”
- “Plan 30 days of uploads for a Marathi news/commentary channel.”
- “Repurpose this script into 3 Shorts, an Instagram Reel caption, and an X thread.”
- “Generate upload-ready metadata from this transcript and title.”

## Optional live data

The toolkit works manually without API credentials. For public channel/video statistics, configure the YouTube Data API v3 using `YOUTUBE_API_KEY`. For private channel analytics, OAuth 2.0 credentials and YouTube Analytics API access are required. Never commit API keys, client secrets, or OAuth tokens.

Live keyword research can optionally use a search provider or DataForSEO MCP, if configured. Check provider pricing before calling paid endpoints. AI image-generation workflows depend on whichever image tool is available in your Codex setup; otherwise, the toolkit produces detailed text briefs.

## Repository layout

- `AGENTS.md`: persistent Codex project instructions.
- `.codex/prompts/`: reusable task recipes that you can ask Codex to follow.
- `docs/workflows.md`: command-to-workflow map.
- `docs/upstream-migration.md`: how to bring over the upstream reference materials and scripts responsibly.
- `.env.example`: names of optional environment variables only (no secrets).

## Important limitations

- Recommendations must not invent analytics, keyword volumes, CTR benchmarks, earnings, or algorithm facts.
- Clearly label measured data, estimates, assumptions, and unavailable data separately.
- Don't upload, delete, schedule, publish, or change channel settings unless the user explicitly asks and the available integration supports the action.
- Respect copyright and platform rules. Repurpose only media the user has rights to use.

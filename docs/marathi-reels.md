# Windows-first Marathi Reels pipeline

This is a local preview renderer for Marathi news/Reels. It uses Python, edge-tts for narration, its word-timing VTT output for captions, and FFmpeg for the 1080x1920 MP4.

**No publishing is implemented.** The manifest records publishing_approved=false and publishing_enabled=false. Review the preview, factual claims, and rights to footage yourself before uploading anywhere.

## Prerequisites

- Windows 10/11 and PowerShell
- Python 3.12 (the launcher checks the usual per-user Python 3.12 location)
- FFmpeg and FFprobe
- Internet for Edge TTS voice generation
- edge-tts installed in the same Python interpreter

    python -m pip install edge-tts

If the python command resolves to the Microsoft Store alias, use the full path:

    $python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    & $python -m pip install edge-tts

## Step 1 — create a project

From the repository root:

    .\scripts\render-marathi-reel.ps1 -Project aurangabad-news

On the first run it creates:
- projects\aurangabad-news\topic.txt
- projects\aurangabad-news\narration.txt

Edit both files in VS Code. Put one clear topic in topic.txt. Put the exact approved words to be spoken in narration.txt. The renderer does not invent facts or write a script from a topic by itself.

To draft the Marathi script with Codex, ask it to read .codex/prompts/script.md and produce a short Marathi Reel narration plus a fact-check checklist. Keep allegations attributed to the source making them, and do not describe allegations as proven facts without independent evidence. Verify names, dates, figures and right of reply before rendering.

## Step 2 — render voice, timed captions and preview

After saving the two text files:

    .\scripts\render-marathi-reel.ps1 -Project aurangabad-news

Default voice is mr-IN-ManoharNeural. To use the female Marathi voice:

    .\scripts\render-marathi-reel.ps1 -Project aurangabad-news -Voice mr-IN-AarohiNeural

Generated files are kept under the project folder:
- audio\narration.mp3 — generated voice-over
- captions\edge-timing.vtt — Edge TTS timing data
- captions\captions.srt — grouped subtitle captions
- manifest.json — inputs, duration, output path and approval flags
- render.log — FFmpeg log

Preview MP4:
output\preview\aurangabad-news-preview.mp4

The script uses timed caption metadata returned by Edge TTS, rather than assigning guessed timestamps to a few long subtitle cards. Caption line grouping is heuristic; always watch the preview and correct the narration/captions if needed.

## Step 3 — use your own footage (optional)

Copy a video you have permission to use into the project or assets folder, then pass its path. Example:

    .\scripts\render-marathi-reel.ps1 -Project aurangabad-news -Video "assets\videos\your-footage.mp4"

The source is looped if shorter than the narration and center-cropped to 9:16. This first milestone does not yet select different clips per sentence, create transitions, or generate AI images.

## Re-render safely

By default, the renderer refuses to overwrite generated files. To regenerate audio, captions and preview for the same project:

    .\scripts\render-marathi-reel.ps1 -Project aurangabad-news -Force

-Force only replaces generated outputs for that project. It never modifies or deletes source footage. Use a different project name if you want to keep the previous render.

## Known limits / next milestones

1. Topic-to-script drafting is a Codex-assisted step, not an unattended API call. No paid model API is required by the local renderer.
2. Captions use Edge TTS word timings, grouped into readable lines. Proofread Marathi spelling and proper names.
3. Background music, transitions, multiple scene selection, AI visuals and publishing integrations are not included yet.
4. Never present AI-generated illustrative visuals as real news footage.
5. Upload/publish remains a manual action outside this pipeline; the renderer cannot publish.

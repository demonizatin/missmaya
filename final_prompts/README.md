# Final Prompts in Production Use

This folder contains every prompt that ships in the live Maya stack as of this commit. Eight prompts total — no overrides, no experimental variants, no playground-only stuff. These are the canonical ones.

| File | What it does | When it fires |
| --- | --- | --- |
| 1_system_prompt.md | Maya persona + rules 1-28 (tone, corrections, output format) | Every chat turn (system role) |
| 2_extra_rules.md | Rules 29-37 (emotional thread, mood, cooldown, lore, etc.) | Every chat turn (spliced into system prompt) |
| 3_avatar_prompt.md | Mayas character description | Every chat turn (interpolated as {avatar_prompt}) |
| 4_first_message_returning_user.md | Opening turn wrapper for returning users | Session start, has memory |
| 5_first_message_new_user.md | Opening turn wrapper for brand-new users | Session start, no memory |
| 6_session_summary.md | Rolling-summary compression | Background, fires when history > WINDOW_SIZE |
| 7_librarian_memory_merge.md | Writes JSON patch to memory after each session | On /end_session |
| 8_output_judge.md | Reviews + rewrites every Maya reply | After every chat turn, before reply ships to user |

## Stack

All eight prompts run on Qwen 32B via AWS Bedrock (qwen.qwen3-32b-v1:0). No Anthropic models, no CLI fallback. The output judge replaces the 360-line regex guard layer that used to live in app.py.

## Updating

These files are extracted FROM app.py and judge_guard.py — the source of truth still lives in those files. Re-run  if you change a prompt and want to refresh this folder. The prompts here are the SAME strings, just split into one file each for easier reading.

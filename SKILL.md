---
name: cook-video-editor
description: Short-form cooking video editing workflow for turning cooking footage directories (.MOV/.MP4 plus optional images) into vertical recipe videos. Use when the user provides a dish name, cooking steps, step-aligned footage, or asks Codex to edit cooking videos with burned-in multilingual subtitles, cover image, and reusable project files.
---

# Cook Video Editor

## Overview

Create short vertical cooking tutorial videos from raw footage. Favor a repeatable, inspectable workflow: analyze footage, create a step-to-clip plan, render a no-subtitle base video, burn subtitles, export cover and project files.

## Output Style

Use this default style unless the user provides another sample or explicit requirements:

- Export vertical `1080x1920`, `60fps`, H.264 `.mp4` with AAC audio.
- Convert horizontal `1920x1080` footage by scaling to height `1920` and center-cropping width `1080`.
- Keep pacing fast: usually `1-3s` per cooking operation, longer only for key transformations.
- Use one cooking action per subtitle segment.
- Start with a title over a plated dish, ingredient shot, or attractive finished-food shot.
- Follow the cooking sequence: ingredients, prep, blanch/fry/cook, season, plate, final display.
- End with plated dish plus a short subscribe/follow prompt when appropriate.
- Burn white subtitles with black stroke into the video.
- Generate Chinese-primary multilingual `.srt`, Japanese-only `jp.srt`, and a cover `.jpg`.

## Subscribe Ding Sound

When the final subtitle contains a subscribe/follow prompt, add one clear ding reminder:

- Trigger the ding `1.5s` after the subscribe subtitle appears.
- Extend the final subscribe clip if needed so the full ding tail is not cut off.
- Duck original audio to `30%` from `0.1s` before the ding until `0.2s` after it ends.
- Use a single-ding design: `2800Hz` main tone for `2.0s`, plus a `5600Hz` bright attack for `0.25s`.
- Fade in quickly, then fade out the main tone from `0.35s` over `1.65s`.
- Do not use echo delays that create a second audible ding.
- Verify the final filter graph has one ding event and the subscribe subtitle/tail are not truncated.

## Workflow

1. Inspect the directory with `rg --files`, `find`, and `ffprobe`.
2. Confirm available source files and existing outputs. Do not modify raw source footage.
3. If footage is not step-named, generate contact sheets:
   - middle frame for all clips;
   - `15%` and `85%` frames for all clips;
   - denser storyboards for long or ambiguous clips.
4. Build `project/clip_plan.tsv` with one row per subtitle/action segment:
   `idx, src, start, duration, zh, en, jp, pos`.
5. Use `scripts/scaffold_cook_project.py` to create the output directory and reusable project scripts.
6. Run the generated `project/build_video.sh`.
7. Quality-check early, middle, and final contact sheets against the subtitles. If a subtitle/action mismatch appears, adjust `clip_plan.tsv` and rerun.
8. Extract or refresh the cover from a strong finished-food frame.

## Clip Planning Rules

- Prefer user-provided step names and file names over visual guessing.
- If files are named like `01_准备食材.MOV`, bind that clip directly to the matching step.
- If a step has no action footage, use the best completion-state shot and make the subtitle truthful, e.g. "调味完成，腌制20分钟".
- For long clips containing multiple actions, split into multiple rows with different `start` values.
- Keep `idx` zero-padded and monotonic.
- Use `pos` values:
  - `title` for opening title
  - `normal` for ordinary steps
  - `ending` for finished dish and subscribe prompt

## Useful Commands

Probe all clips:

```bash
for f in *.MOV *.MP4; do
  [ -e "$f" ] || continue
  printf '%s\t' "$f"
  ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height,r_frame_rate,duration \
    -of csv=p=0 "$f"
done
```

Create middle-frame contact sheets with `ffmpeg` `tile`. If `drawtext` is unavailable, create unlabelled sheets and rely on filename ordering.

## Resources

- `scripts/scaffold_cook_project.py`: creates the dish output folder and writes reusable rendering scripts.
- `references/naming.md`: recommended source-material naming conventions and plan examples.

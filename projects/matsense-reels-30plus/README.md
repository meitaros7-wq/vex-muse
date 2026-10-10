# Matsense Reels: five ads for 30+ white / blue / purple belts (v1, 2026-10-10)

- **Scripts:** `narrator-script.txt` (English narration, ~50-60 words each); plan in `storyboard.md`.
- **Voice:** Meitar ran out of voice credits, so the narration is a local, free model:
  Kokoro-82M, voice `am_michael`, speed 0.95, one line at a time with designed pauses
  (`tools/vo.py`). Every take was transcribed back and matched the script word for word.
  It can be swapped for a human narrator later: replace `audio/vo_adN.wav` and re-run the mix
  (line timings in `audio/vo_lines.json` drive captions and cues).
- **Footage:** the two matches in the Matsense staging app (gi "Meitar Vs Amit", 23 Sep; no-gi
  "Meitar vs Amit", 1 Oct). The gi match is cropped to 9:16 with an athlete tracker
  (`tools/track.py`, `tools/clips.py`); the no-gi phone video is used as it was filmed.
- **App screens:** rebuilt in code from the Glow design system (`motion/reels/assets/kit.css`,
  `kit.js`), filled with the matches' real detected events. Demo values: the months on ad 5's
  three panels, "Masters Open" in 21 days, the private lesson on Thursday at 19:00.
- **Sound:** a generated D-minor pulse bed (`tools/mix.py`), ducked under the voice, plus
  Pixabay-licensed SFX bundled with HyperFrames (`audio/sfx/CREDITS.md`); -14 LUFS.
- **Build:** one HyperFrames project per ad (`motion/adN/index.html`, shared `motion/reels/assets`).
  `tools/render_all.sh` renders all five to `renders/`. Media is not in git; `tools/` rebuilds it.
- **Spend:** $0 (no paid generation).

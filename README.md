# UpOn 2.1 Website

The beta website and macOS download page for UpOn 2.1 by Mejalism Corp.

The editorial redesign includes the MEJALISM CORP wordmark, an app vision, a documented company/product timeline, and founder Louis Enda Japar. Mejalism Corp was founded in January 2024 and is headquartered in Bintulu, Sarawak, Malaysia.

## Local preview

```sh
cd dist
python3 -m http.server 4173 --bind 127.0.0.1
```

Open `http://127.0.0.1:4173/`.

## Release artifact

- File: `dist/UpOn-2.1-Beta.dmg`
- Version: 2.1, build 12
- Architecture: Apple silicon (arm64)
- Minimum system: macOS 14 Sonoma
- SHA-256: `53a78e4b49444813099947f187ee8580916f6c2547cdda12fdfad403fab4ff48`
- Status: beta, ad-hoc signed, not yet Apple-notarized

The disk image contains `UpOn 2.1.app`, an Applications shortcut, and the beta installation and privacy `README.md`.

## Product film

- File: `dist/assets/upon-2.1-film-v2.mp4`
- Duration: 30 seconds
- Format: H.264 1080p at 30 fps with 48 kHz stereo AAC audio
- SHA-256: `f4e7aa9a18f1153d4550254ee33d6620198e40d933efc4cf2e4d8672e8d99f14`
- Renderer: `motion/render_upon_film_v2.py`
- Captions: `dist/assets/upon-film-v2.vtt`

The film uses real UpOn screens, slower motion and crossfades, and an original calm score of warm sustained chords and sparse piano-like notes. The illustrative trajectory is explicitly labelled as having no medical values. The website includes chapter seeking, play/pause, opt-in sound, captions, and a reduced-motion-friendly presentation. Representative preview frames and final encoded contact-sheet QA stay under the ignored `motion/work/` folder. The previous film is retained as an iteration archive, but is no longer embedded.

## Hosting

This is a static website. The entire deployable site lives in `dist/`. `vercel.json` selects that output directory for Vercel; `.openai/hosting.json` retains the earlier private Sites deployment.

## Verification

The browser smoke test is `tests/site-smoke.js`, run with `playwright-cli run-code --filename tests/site-smoke.js` against the local preview. It checks desktop/mobile overflow, tabs and keyboard controls, mobile navigation, film decoding and chapter seeking, sound and manual pause, and reduced-motion behavior. Screenshots are written to the ignored `output/playwright/` directory.

The final film was decoded and its encoded contact sheet visually checked. The DMG checksum, mounted README, and strict app signature were verified.

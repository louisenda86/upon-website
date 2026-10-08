# UpOn 2.1 Beta

UpOn is a private macOS health-intelligence workspace by Mejalism Corp. It imports health reports, extracts source-linked biomarkers locally, builds trends and timelines, and lets you choose when to connect an AI provider for deeper educational analysis.

## Install

1. Open `UpOn-2.1-Beta.dmg`.
2. Drag **UpOn 2.1** into the **Applications** shortcut.
3. Because this beta is not yet notarized, Control-click **UpOn 2.1** in Applications and choose **Open** on first launch.
4. Enter your own profile name. UpOn never creates a random identity.

## Requirements

- macOS 14 Sonoma or later
- Apple silicon Mac (arm64)
- Approximately 50 MB of free disk space
- Internet access only when you choose a cloud AI provider

## What it accepts

- PDF medical reports
- PNG, JPEG, HEIC, and TIFF report images
- CSV, TSV, JSON, XLSX, XLS, and spreadsheet exports
- Markdown and plain-text reports

## Private-first workflow

1. Import and encrypt the original on this Mac.
2. Extract text and biomarker candidates locally with Apple Vision OCR by default.
3. Review and correct detected values before they enter comparisons.
4. Optionally connect OpenAI, Claude, Gemini, Ollama, llama.cpp, or LM Studio.
5. Approve the exact provider and data boundary before each AI analysis.

Cloud AI requires that provider's API key. A ChatGPT or Claude website login is not captured or reused by UpOn. Local runtimes are restricted to loopback addresses on this Mac.

## Important beta notice

UpOn 2.1 is beta software. It is an educational organization and analysis tool—not a medical device, diagnosis, emergency service, or replacement for a qualified healthcare professional. Always verify extracted values against the original report and discuss health decisions with a clinician.

This beta is ad-hoc signed for controlled pilot use and is not yet Apple-notarized. Do not bypass macOS security warnings for a copy obtained from anywhere other than the official UpOn beta website.

## Privacy and support

Health records, profile information, and analysis results are stored in an AES-GCM encrypted local vault protected by macOS Keychain. API keys and optional local tokens are stored separately in Keychain. UpOn does not upload a record until you explicitly approve an AI request.

- Product: UpOn 2.1 beta, build 12
- Company: Mejalism Corp
- Founder: Louis Enda Japar
- Founded: January 2024
- Headquarters: Bintulu, Sarawak, Malaysia

For pilot feedback, retain the original report and note the UpOn version, but never send medical records or API keys through an unsecured support channel.

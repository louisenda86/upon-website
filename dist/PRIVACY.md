# UpOn 2.1 private-pilot privacy notice

Last updated: 11 September 2026

UpOn is a local macOS app for organizing and explaining medical reports. The client chooses each analysis engine and each transfer.

## Information kept on this Mac

UpOn stores the client-entered profile name, optional profile photo, imported PDFs, report images, Markdown/text reports and data sheets, user-entered measurements and notes, locally extracted OCR/text and biomarker rows, structured AI analyses, review state, and completed plan actions. The profile name, original files, profile photo, current library, and last-known-good library state are encrypted with AES-GCM using a Keychain-backed key. Cloud API keys and optional local-server tokens are stored as separate macOS Keychain items. Encrypted vault folders use owner-only filesystem permissions and are marked as excluded from ordinary backup handling. If the original key is unavailable, UpOn does not create a replacement over existing encrypted data.

Chats remain in process memory and clear when UpOn closes. UpOn has no analytics, advertising, tracking, cloud account, iCloud sync, or background health-data upload.

## Cloud analysis

Importing any supported record sends nothing. After the client selects OpenAI, Claude, or Gemini and gives explicit consent, UpOn sends a PDF document and constrained analysis instructions only to the selected provider over HTTPS. An original PDF is sent directly; a report image or Markdown/text report is converted to a temporary in-memory PDF for that request while the encrypted original remains unchanged. Provider terms, project settings, retention controls, billing, and any required health-data agreements apply. A second cloud analysis is a separate disclosure and consent.

Before connecting AI, UpOn automatically starts local extraction after import and also lets the client manually run **Scan with OCR** from Records. Embedded PDF text extraction, direct Markdown/text reading, Apple Vision OCR for images and scanned pages, strict date detection, and numeric-row detection happen on the Mac. The client may explicitly select locally installed Tesseract CLI, Python + pytesseract, or PaddleOCR. Tesseract and Python receive image bytes through standard input; PaddleOCR requires a protected temporary image that is deleted immediately after the process completes. External processes receive a minimal environment and bounded execution. If the selected engine is unavailable or fails, UpOn falls back to Apple Vision. CSV, TSV, JSON, and bounded XLSX parsing also happens on the Mac and does not connect to an AI provider. Encrypted local previews are not sent anywhere and do not interpret whether a value is healthy, abnormal, diagnostic, or urgent.

Local extraction candidates appear in Biomarkers and Trends before AI is connected. Imported sheets expose all extracted rows for review and correction. Missing or ambiguous dates stay missing and are excluded from longitudinal charts rather than being replaced by the import date. Excel archives are assembled in memory; Excel and PNG export require an explicit save action and write only to a user-selected location. Editing a source-linked value is a local correction workflow and clears the relevant reviewed state until the client reviews it again.

Exact-file duplicate detection uses a SHA-256 fingerprint computed locally from the selected file. The fingerprint is stored inside the encrypted library and is not sent to an AI provider.

Manual measurements are entered by the client and stored only in the encrypted local library. UpOn preserves the supplied name, value, unit, date, and optional note. It does not validate the measuring device, infer a missing unit, add a reference range, or classify the result.

OpenAI requests use `store: false`, which is not by itself a Zero Data Retention guarantee. UpOn likewise does not claim zero retention for Anthropic or Google unless the client's provider account has an applicable agreement and correctly provisioned controls.

## Local analysis

For Ollama, llama.cpp, or LM Studio, the encrypted original remains on the Mac. UpOn extracts text from the selected source and uses the configured local OCR path for report images, with Apple Vision as the fallback. It sends bounded, source-linked extracted text to the selected local process. The endpoint validator allows only `localhost`, `127.0.0.1`, or `::1`; LAN and public hosts are rejected.

The local runtime and model are controlled by the client. UpOn cannot guarantee what independently installed local-server software logs, retains, or transmits, so clients should use trusted builds and review their configuration.

Some Ollama entries may be cloud-hosted even though Ollama itself runs locally. UpOn labels provider-reported remote models and shows a different disclosure because extracted report text or chat context may leave the Mac through that runtime.

## Ask AI

Ask AI sends the typed question to the selected connected engine. The client explicitly chooses **No health data**, **Current report**, or **Verified history** before sending. Current-report context includes only the selected provider's user-reviewed structured summary. Verified-history context may include up to five user-reviewed summaries from that same provider. The original record is never attached to chat, and provider contexts are not reused across engines.

## Privacy Lock

Privacy Lock is optional and can be enabled only after a successful macOS device-owner authentication check, which may offer Touch ID or the current Mac login password. UpOn receives only success or failure from macOS and does not receive biometric data or the Mac password. The app locks when opened and after it has been left for two minutes. Locking cancels in-flight model, chat, analysis, and OCR work and unloads health records from workspace memory until successful re-authentication. Privacy Lock reduces shoulder-surfing and casual access; it does not protect an already unlocked, compromised Mac from sufficiently privileged software.

## Browser-account boundary

UpOn does not sign in to, embed, or impersonate consumer AI accounts and receives no browser password, cookie, session, chat, memory, OAuth token, or subscription entitlement. A manual account handoff opens the official site and copies a generic prompt containing no report values. Browser responses remain outside UpOn.

## Deletion

Deleting one report or data sheet removes its encrypted original and associated local metadata. Deleting a manual measurement removes that entry from the encrypted library. **Delete all data** removes encrypted reports, data sheets, manual measurements, analyses, profile name and photo, local metadata, completed actions, vault key, all saved provider secrets, and in-memory chats from this Mac. It does not delete data governed by separate cloud-provider accounts.

## Medical and public-release boundary

UpOn provides educational decision support and can be incomplete or wrong. It does not diagnose, prescribe, replace professional care, or replace emergency services. Public distribution requires a responsible legal entity, public privacy-policy URL and contact details, provider-specific health-data terms, launch-market legal review, and any required medical-device assessment.

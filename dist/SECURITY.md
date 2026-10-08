# UpOn security and release posture

## Current pilot mode

UpOn 2.1 is a single-user macOS private pilot with private OCR scanning, direct OpenAI, Anthropic, and Gemini API connections, plus loopback-only Ollama, llama.cpp, and LM Studio connections.

- App Sandbox is enabled.
- Record picker access is user-selected and read-only. Export save access is user-selected and read-write. Security-scoped URLs are released immediately after import or export.
- PDF, PNG, JPEG, HEIC, TIFF, Markdown, and text reports are limited to 20 MB. PDFs above 500 pages are rejected; image metadata is validated before decoding and images above 50 megapixels are rejected.
- Data-sheet picker access is also user-selected and released after import. CSV, TSV, JSON, and XLSX files are limited to 25 MB and parsed locally; XLSX ZIP archives are preflighted for traversal, entry-count, per-entry, and total-expanded-size limits before parsing. Workbook processing is bounded to 50 sheets, 20,000 rows per sheet, 200 columns, 4,000 characters per cell, and 20,000 extracted biomarker rows.
- Original PDFs, report images, Markdown/text files, data sheets, and the local analysis library are encrypted with AES-GCM.
- Vault folders are forced to owner-only `0700` permissions and encrypted vault files to owner-only `0600` permissions. The local vault directory is marked as excluded from ordinary backup handling.
- The 256-bit vault key is stored as a `WhenUnlockedThisDeviceOnly` macOS Keychain item.
- Vault-key access is checked at launch. If encrypted data exists and the original key is missing, UpOn refuses to create a replacement key or overwrite the library. State saves keep an encrypted last-known-good copy for local recovery, and a recovered library is visibly reported.
- Library updates are committed before destructive file deletion. Failed saves roll visible state back to the last durable snapshot; failed imports remove their newly created encrypted orphan.
- Cloud API keys and optional local-server tokens are stored as separate Keychain items. They are never displayed again, logged, written to source, placed in UserDefaults, or included in the encrypted analysis library.
- A new key is tested with a health-data-free request against the same API and model used by the app. A successful key is marked connected. A key that authenticated far enough to receive a billing, quota, permissions, or rate-limit response may remain encrypted in Keychain as **repair required**, but it is never marked connected.
- Connection verification is stored separately from credential presence. Restarting UpOn cannot turn a blocked saved key into a falsely connected state.
- New OpenAI connections default to `gpt-5.6-sol`. GPT-5.6 requests explicitly preserve the previous GPT-5.4 effective reasoning baseline (`none`) during migration; the model picker retains Sol, Terra, Luna, and the previous compatible model rather than collapsing different cost and latency roles.
- Provider error bodies are reduced to a bounded provider message, error class, request ID, and `retry-after` value. API keys and request health data are never included in diagnostics.
- Network requests use an ephemeral URL session with no cookies, URL cache, or credential store.
- OpenAI requests go only to `https://api.openai.com/v1/responses` over HTTPS.
- Claude requests go only to `https://api.anthropic.com/v1/messages` over HTTPS.
- Gemini requests go only to Google's `generativelanguage.googleapis.com` API over HTTPS.
- Ollama, llama.cpp, and LM Studio addresses are validated before every request. Only `localhost`, `127.0.0.1`, and `::1` are accepted; LAN and public endpoints are rejected.
- Local processing extracts embedded PDF text and Markdown/text content directly, and applies Apple Vision OCR to report images or PDF pages without useful text. External OCR must be selected explicitly. Tesseract and Python receive normalized PNG bytes through standard input; PaddleOCR receives a `0600` file inside a random `0700` temporary directory that is removed immediately afterward. Child processes inherit only a minimal scrubbed environment, are terminated after 90 seconds, and have bounded captured output. Extracted text is bounded to 120,000 characters and retains source-page separators.
- OCR scanning is independent of AI and starts automatically after report import, with queued processing for multi-file selection. Its extracted text and deterministic numeric candidates are stored only inside the encrypted local library. OCR candidates are labeled unverified and are not classified as normal or abnormal.
- Supported dropped and selected files receive a local SHA-256 fingerprint before storage. An exact matching fingerprint prevents a duplicate encrypted copy; the fingerprint itself remains inside the encrypted library.
- Data-sheet extraction is independent of AI. Every imported biomarker row is searchable and editable in a full review sheet. Rows remain excluded from reviewed history until the client acknowledges the complete sheet, require explicit dates and stated matching units for comparison, and never receive inferred dates, ranges, or clinical flags.
- Local runtime discovery is limited to loopback APIs. LM Studio's native model list filters non-chat embedding models; OpenAI-compatible fallback remains available for older versions.
- Ollama entries containing a provider-reported `remote_host` are labeled **REMOTE**. UpOn stores that boundary with the selected model and changes analysis/chat warnings accordingly.
- Cloud document requests use PDF Base64 content and do not create persistent provider file objects. Original PDFs are supplied directly after consent; images and Markdown/text records are converted to an in-memory PDF after consent while the encrypted original remains unchanged.
- Biomarker and trend exports are explicit user actions. Excel exports are assembled in memory rather than a plaintext temporary file; Excel and PNG output is written only to a user-selected destination, and canceling the Save panel reports no false success.
- The user chooses one provider and gives explicit consent immediately before every analysis. Every cloud transmission is independent; local consent names the loopback process and text/OCR boundary.
- OpenAI PDF and chat requests set `store: false`.
- Claude PDF analysis uses JSON-schema structured output. UpOn does not claim Zero Data Retention unless the Anthropic organization has that arrangement.
- Provider results and verification states are stored separately. Provider-controlled responses are bounded and structurally sanitized before persistence or display. Verifying one model never verifies another.
- Biomarkers and Trends can also show local OCR candidates before AI. Longitudinal History uses separated source modes: OCR preview, same-provider results that the client has verified, or data-sheet rows the client has reviewed. It requires matching units and a source-stated unambiguous date; missing dates never borrow the import timestamp. Trend lines use straight segments between real observations. Comparison labels only numeric direction and does not claim improvement, decline, causation, or treatment effect.
- Ask AI attaches no original record. It can attach only a verified summary generated for the same selected provider; cross-provider context reuse is blocked.
- Ask AI exposes three explicit scopes: no health data, the current same-provider reviewed report, or up to five same-provider reviewed historical summaries. A user can cancel an in-flight chat or analysis request.
- Chat messages are kept in process memory only and are not persisted by UpOn.
- Quick Chat and the full Coach use the same provider-isolated, memory-only conversation state.
- Account handoff copies a generic safety-constrained prompt containing no medical record data, then opens the official ChatGPT or Claude website. UpOn does not inspect the browser session or response.
- The original PDF, image, Markdown, or text record remains available in-app for source review.
- The optional profile photo is encrypted inside the local vault, limited to 5 MB, and never attached to an AI request.
- Manual measurements are treated as user statements, not validated clinical results. They keep the entered value, unit, date, and note, enter their own `manual` provenance channel, and receive no inferred range or medical classification.
- Optional Privacy Lock can be enabled only after macOS confirms device-owner authentication is available and succeeds. It locks at launch and after UpOn has remained away from the foreground for two minutes, cancels active analysis/chat/OCR/model operations, and unloads health data from process-visible workspace state until re-authentication. UpOn never receives biometric templates or the Mac account password.
- Startup vault and credential probes run away from the UI thread. A vault-key read that does not return within eight seconds moves the app to an explicit blocked state with a retry action; UpOn does not create a replacement key over existing ciphertext.
- Clinician-summary clipboard content auto-clears after 60 seconds when it has not already been replaced by the client.
- Deleting a report or data sheet removes its encrypted original and attached metadata. **Delete all data** first invalidates and cancels active work, then removes the local profile and photo, vault key, completed actions, every provider secret, and in-memory chats.
- There is no analytics, advertising, tracking, cloud account, background sync, care-team sharing, or product-improvement upload in this pilot.

## AI and medical safety controls

- Every imported report and chat context is treated as untrusted source data; prompt-like content is explicitly ignored.
- Every model is instructed to extract only visible source facts and never invent missing values, ranges, units, dates, prior results, trends, symptoms, or patient facts.
- Laboratory-provided flags remain separate from model interpretations.
- Generic medical reference ranges are not substituted for missing laboratory ranges.
- Snapshot graphs use only extracted numeric results and bounds printed in the report. History graphs use only verified numeric observations with matching units. UpOn does not fabricate time-series points.
- The structured response includes unknowns, urgency, confidence, limitations, and source page numbers.
- Models are instructed not to diagnose, prescribe, change medication, promise prevention, or replace emergency or professional care.
- Red is reserved for source-supported urgent health states, destructive actions, and actionable processing or connection failures—not ordinary out-of-range styling.
- Additional providers are presented as comparisons, not adjudicators. Agreement is not treated as correctness.
- Manual marker correction clears the provider-reviewed state until the corrected result is reviewed again. Clinician summary export and report-aware chat require user verification against the original record.

These controls reduce risk; they do not prove clinical correctness. The extraction and safety pipeline still requires clinician-reviewed benchmarks, adversarial PDF tests, multilingual and poor-scan testing, urgency evaluation, model-version regression gates, and documented release thresholds.

## Provider data boundaries

### OpenAI

`store: false` prevents Responses API application-state storage, but it does not by itself mean Zero Data Retention. OpenAI API abuse-monitoring retention and the data controls of the user's Platform organization still apply. A regulated health-data workflow must have the required agreements and an eligible, correctly provisioned configuration before transmitting protected data.

### Anthropic

Anthropic API terms, organization settings, and any applicable retention configuration govern Claude requests. UpOn does not enable citations with structured outputs and does not place patient data in JSON-schema property names. A regulated health-data workflow must confirm current Anthropic eligibility, retention, and contractual terms before transmitting protected data.

### Google Gemini

Google Gemini API terms, project controls, retention behavior, and any applicable contractual configuration govern Gemini requests. A consumer Gemini subscription is not API authorization. Regulated workflows must confirm current eligibility and required agreements before transmitting protected data.

### Local runtimes

Loopback validation prevents UpOn from targeting a LAN or public server, but independently installed local runtimes and models remain outside UpOn's trust boundary. Users must select trusted builds, review runtime logging and telemetry, protect model-server access, and avoid proxying the loopback port to another machine.

### Browser-account boundary

UpOn does not embed or impersonate ChatGPT or Claude consumer authentication and receives no browser passwords, cookies, sessions, chats, memories, OAuth tokens, or subscription entitlements. Provider consoles and consumer chat sites open externally only when the user chooses. Account handoff is visibly separate from native API connection and cannot populate UpOn results automatically.

## Known pilot risks

1. API keys in a desktop client can be recovered by the device owner or sufficiently privileged malware. Keychain reduces accidental exposure but is not a production substitute for server-side credential control or workload identity.
2. The pilot has optional local device-owner Privacy Lock but no cloud user account, remote revocation, audit service, tenant isolation, managed retention policy, or centralized consent ledger.
3. The local vault is encrypted and owner-permission restricted, but an unlocked, compromised Mac can expose decrypted content while UpOn is running.
4. The app does not include malware scanning, out-of-process PDF/image/XLSX parser isolation beyond App Sandbox and bounded preflight checks, a dedicated clinical model-output adjudicator, or automated clinical escalation tests.
5. User verification is a workflow control, not proof that every value was checked correctly.
6. Sending a report to multiple cloud providers creates multiple separately governed external copies.
7. In-memory chat content can still be visible to other software with sufficient process or screen access while the app is running.
8. Ad-hoc local builds can trigger Keychain re-authorization after code changes. Public distribution requires a stable Developer ID signature and notarization.
9. A provider spending or billing limit is external account state. UpOn can diagnose it and route the user to the correct controls, but cannot bypass it.
10. Local model quality varies widely. JSON conformance and successful parsing do not establish extraction accuracy or clinical safety.
11. XLSX import support is read-only and depends on the pinned Apache-2.0 CoreXLSX parser. Password-protected, legacy `.xls`, Numbers, OpenDocument, malformed, or unusual workbooks may be rejected and should be exported as CSV or a simple `.xlsx` file.
12. External OCR quality and logging behavior are governed by the user's local Tesseract, Python, or PaddleOCR installation. UpOn can invoke those tools locally but cannot audit third-party package telemetry or shell environment configuration.
13. User-entered measurements are not device-authenticated and can be mistyped. Their presence in charts does not establish clinical validity.

## Production release blockers

Before a public health-data launch:

1. Replace direct client credentials with a controlled backend or provider-supported production workload identity.
2. Add real user authentication, passkeys or Sign in with Apple where appropriate, MFA, secure recovery, session expiry, and device revocation.
3. Add consent records, privacy-policy versioning, access logs, export/correction/deletion workflows, retention controls, and revocable selected-record sharing.
4. Add tenant isolation, least-privilege service roles, provider-specific rate and spend limits, secret rotation, WAF/rate limiting, incident response, encrypted backups, and disaster-recovery tests.
5. Add file malware scanning, parser isolation, broader hostile-document fuzzing, prompt-injection evaluation, dependency/SBOM scanning, and independent penetration testing.
6. Establish clinical governance, evidence policy, escalation ownership, provider/model/prompt versioning, benchmark datasets, regression gates, human-review routes, and harm reporting.
7. Complete Malaysian PDPA review and assess Software as a Medical Device classification before making diagnostic, predictive, monitoring, or treatment claims.
8. Execute and correctly configure any required health-data agreements with every selected provider before transmitting regulated data.
9. Provide a legal-entity privacy policy URL and accurate App Store privacy disclosures.
10. Sign with Developer ID, notarize, staple the ticket, and verify Gatekeeper acceptance through `release-app.sh`.

## Release commands

Local QA:

```sh
./build-app.sh
open "dist/UpOn 2.1.app"
```

Distribution:

```sh
xcrun notarytool store-credentials "upon-notary" --apple-id "you@example.com" --team-id "TEAMID"

UPON_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAMID)" \
UPON_NOTARY_PROFILE="upon-notary" \
./release-app.sh
```

Never commit API keys, Developer ID credentials, notarization passwords, or App Store Connect private keys. The release script accepts only a Keychain profile name for notarization.

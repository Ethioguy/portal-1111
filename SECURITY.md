# Security

Portal 11 has no server, no account and no backend. That removes most of the usual attack surface, and concentrates what is left in three places.

## Threat model

**What this app protects:** everything you type and every photo you add. All of it is on your device only.

**What it cannot protect against:** anyone with access to the device or the browser profile. There is no password on the app, by design — a lock screen you can forget is worse than none when the data never leaves the machine. If the device is shared, use a separate browser profile.

**Where risk actually lives:**

1. **The published HTML.** A single page, served as a static file. The public build ships a strict Content-Security-Policy: no inline event handlers, no third-party scripts, no frames, and `connect-src` limited to the one search API. `tools/build_editions.py` asserts that the public build contains no AI connection code, no API-key handling and no third-party embeds, and the build fails if any appear.
2. **The two optional outbound calls.** Searching Openverse sends only your search words. Playing a publisher's track streams it from that publisher's server, which sees your IP as any website would. Both are off until you use them, and neither sends anything you have typed.
3. **Backups.** `Setup → Copy backup` puts your whole log on the clipboard in plain text. That file is as sensitive as a diary. Keep it somewhere private; it is gitignored here so it cannot be committed by accident.

## Not in this repository, ever

- The personal edition (`private/`), which can hold your own Anthropic API key
- Any backup, sync file, `.env`, key or certificate
- Any photo, audio file or personal text

`.gitignore` blocks these, and the build guard checks the published HTML for personal content before it is written. Run `git status` before committing.

## Reporting a vulnerability

Open a private security advisory on the repository, or raise an issue with no exploit detail and ask for a contact. Please do not open a public issue containing a working exploit.

Since there is no server, there is nothing to patch centrally: a fix ships as a new build, and users get it the next time their browser updates the service worker cache.

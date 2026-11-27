# Portal 11 · Hybrid Training & Life at Home

**Train for hybrid fitness racing at home, and keep the other ten areas of your life in the same place.** One HTML file. Works offline. No account, no server, no tracking — your data never leaves your device.

Hybrid racing rewards people who can run *and* push, pull, carry and lunge under fatigue. Most training apps handle the gym and ignore everything else. Portal 11 tracks the training and the eleven areas of a life that has to hold it up: health, career, money, family, friends, growth, spirit, home, giving, fun and adventure.

> I started this on 11.11.2026 at 11:11 PM as my own fresh start. I'm sharing it openly because I wish everyone their own 11:11 portal — a step through to the next chapter.

## Use it

Open the app, then add it to your home screen. That's the install — it then runs offline like a native app.

Nothing to sign up for. Everything you type stays in your browser's own storage on that device.

## What's in it

| Area | What it does |
|---|---|
| **Training** | Daily run and workout plan, logged in one tap. Animated figures for all 43 movements, drawn from anthropometric segment ratios and clinical range-of-motion limits, so the positions are actually achievable |
| **Command centre** | Streaks, miles, sessions and check-ins across every track, with medals and a shareable summary |
| **11 life areas** | Premise, vision, purpose and strategy per area, with a satisfaction rating and a check-in |
| **Living workbook** | A Sunday / monthly / quarterly visioning cadence, built on five published methods with sources cited in `ai/portal_ai/workbook.py` |
| **Personal book** | Your whole workbook as a print-ready PDF with a photo-collage cover, versioned and date-stamped on every download |
| **Vision board** | Your own pictures per area and sub-area, held in IndexedDB on your device |
| **Meditation & focus** | Guided sessions timed to your chosen length, your vision-board photos fading behind the words, with optional background music that repeats or stops when the session ends |
| **Recipes & nutrition** | Meals built around the training week |
| **Inbox** | Capture tasks and ideas in one line, by voice or text; area, day and person are inferred |
| **Watch import** | Runs and rides from Apple Health, Garmin or Strava, via a Shortcut or any JSON/CSV export. Swims, lifts and walks are skipped so they can't overwrite a training day |
| **Backup reminders** | Nothing syncs, by design — so the app asks on your own cadence, and offers clipboard, a dated file, or the PDF book |

## Privacy

This is the whole point, so it's worth being precise. See [PRIVACY.md](PRIVACY.md) for the detail.

- **No account, no server, no analytics.** There is no backend to send anything to.
- **Your entries** live in `localStorage`; **your photos and audio** in IndexedDB. Both are per-device and per-origin. Clearing site data erases them, so use **Setup → Copy backup** before you do.
- **Two network calls exist, both optional and both started by you:** searching Openverse for cover photos or music sends only your search words; playing a publisher's track streams it from that publisher's server. No audio or image is stored in this repository.
- **The strict Content-Security-Policy** in the published build blocks any other outbound connection. If a future change tried to phone home, the build would break.
- **Nothing syncs between your devices, deliberately.** There is no server to hold a copy, so backing up is yours to do. The app reminds you on a cadence you choose and gives you three ways out: clipboard, a dated file, or the printed book.

### Accessibility

Audited with axe-core across all five views: **zero violations**. Passes WCAG reflow at 320 CSS px, respects `prefers-reduced-motion`, every control is 44px or larger, visible focus throughout, and no nested interactive controls. What that does *not* mean: no one has yet driven this with VoiceOver, NVDA or a switch device, and automated tools catch perhaps a third of real barriers. Help with that is the contribution I'd most value.

## Make it yours

Nothing here is specific to hybrid racing or to eleven life areas. A gym, a club, a clinic or one person with different priorities changes `config.py` — the name, the sessions, the weekly plan, the areas — and rebuilds. `config_examples/gym.py` is a working alternative: a three-day strength block with six tracked areas and a different name.

```bash
cp config_examples/gym.py config.py
python3 tools/build_config.py && python3 tools/build_editions.py
```

Full guide, including what is *not* configurable yet: [docs/ADOPTING.md](docs/ADOPTING.md).

## Data and AI practice

Three claims, each enforced by something in this repository rather than promised here.

- **No account, no server, no analytics.** There is no backend. Loading the app makes exactly one network request: the page itself.
- **Your entries never leave your device.** They live in `localStorage`, your photos and audio in IndexedDB, both per-device and per-origin. Nothing is transmitted, so nothing can be breached, subpoenaed or sold at the author's end — there is no "author's end".
- **The public build contains no AI connection code at all.** `tools/build_editions.py` asserts it, so a change that added any would fail the build, and CI runs that build on every push. The one AI feature exists only in a personal edition kept off this repository, using the owner's own API key.

Two outbound calls exist. Both are optional, both start with a tap, and neither sends anything you have typed:

| Call | What leaves the device | When |
|---|---|---|
| Openverse search (`api.openverse.org`) | your search words | only when you search for a cover photo or music |
| Streaming a track | nothing but the request itself; the publisher's server sees your IP, as any website does | only when you choose a track and start a session |

**What this costs you, said plainly.** Nothing syncs between your devices, and there is no password reset, because there is no account to reset. Clearing site data erases the log. The app says this in the open, reminds you to back up on a cadence you choose, and offers three ways out: the clipboard, a dated file, and the printed book — which is readable in twenty years by anything, with or without this app.

**On "AI for good".** The claim here is narrow and checkable: data minimisation and user control achieved by architecture rather than by policy. There is no data on a server because there is no server. This project has not been assessed against any named AI governance framework, and says so rather than implying otherwise. It is MIT licensed, so you can verify every line above instead of trusting it.

## Build it yourself

```bash
git clone https://github.com/Ethioguy/portal-11
cd portal-11
python3 tools/build_config.py       # config.py  -> window.CFG + manifest
python3 tools/build_editions.py     # app.src.html -> index.html
```

`index.html` is a build artifact and is committed so the app can be served directly from the repo. CI fails if it does not match what `app.src.html` produces, so the published app and the source can't drift apart.

```bash
cd ai && pip install -e ".[dev]" && pytest -q tests    # 23 tests
python evals/run_evals.py                              # offline evals: retrieval, tool contracts, guardrails, MCP
```

## How it's put together

The content is generated by Python and injected into a single HTML page; the browser holds the UI and the data, and nothing else.

```
config.py             everything a fork changes: brand, sessions, weekly plan, areas
app.src.html          single source; builds into index.html (public) and a personal edition
tools/build_*.py      generators: config, exercise art, life areas, coaching, recipes,
                      meditation, workbook, vision review, inbox — each injects a window.* block
ai/portal_ai/         the Python layer: typed tools, guardrails, RAG, MCP server
ai/tests/             23 tests
ai/evals/             offline evals for retrieval, tool contracts, guardrails and MCP
```

Two editions build from the same source. The **public** edition is what ships here: strict CSP, no AI connection code, no third-party embeds. The **personal** edition adds an optional "bring your own Anthropic key" coach; it is gitignored and never published, because an edition that can call out is not an edition anyone should get from a stranger.

The Python layer exists so the same logic serves the app, an MCP client and an agent without being rewritten three times. Write tools preview first and commit only with `confirm=true`; every call is audit-logged.

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). To report something security-related, see [SECURITY.md](SECURITY.md).

## Licence

MIT — see [LICENSE](LICENSE). Do what you like with it; no warranty.

Not affiliated with, endorsed by, or connected to HYROX, Brahma Kumaris, or any other organisation named in this repository. Those names appear only to describe what the app works with.

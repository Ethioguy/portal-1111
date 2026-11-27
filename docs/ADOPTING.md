# Adopting this for your own use

Portal 11 is a training and life log that happens to be set up for hybrid racing at home and eleven life areas. Neither of those is baked in. A gym, a running club, a physio clinic, a coach or one person with different priorities can change what it tracks by editing one file.

MIT licence. Fork it, rename it, sell it if you want. No attribution required, though a link back is appreciated.

## Ten-minute version

```bash
git clone https://github.com/Ethioguy/portal-11 my-app
cd my-app
cp config_examples/gym.py config.py     # or edit config.py directly
python3 tools/build_config.py           # validates and injects your config
python3 tools/build_editions.py         # writes index.html
open index.html
```

That is the whole loop. `config.py` holds the name, the sessions, the weekly plan and the areas; everything else follows from it.

## What `config.py` controls

| Key | What changes |
|---|---|
| `BRAND["name"]` | The name in the header |
| `BRAND["tagline"]` | The small line under it |
| `BRAND["full_title"]` | Browser tab and the installed app's name |
| `BRAND["since"]` | The origin line. `""` hides it |
| `BRAND["story"]` | The "Why I created it" card. `""` removes the card |
| `BRAND["theme"]` | Browser chrome colour |
| `TRAINING["sessions"]` | Every session: name, minutes, exercise list, timer style |
| `TRAINING["week"]` | Which session runs on which day, and what kind of run goes with it |
| `TRAINING["warmup"]` / `["cooldown"]` | The movement lists either side of a session |
| `TRAINING["stations"]` | The circuit used by race-simulation days |
| `AREAS` | The life areas: id, display name, and the pair each is grouped with. Any number works |

`tools/build_config.py` validates before it writes. It will tell you if a day points at a session that does not exist, if two areas share an id, if a colour is not a hex value, or if an exercise is not a `[movement, prescription]` pair. It reads the app's own timer presets rather than keeping its own list, so the two cannot drift.

## Worked example

`config_examples/gym.py` is a real alternative, not a stub: a gym running a three-day strength block with conditioning and mobility, six tracked areas instead of eleven, and no founder's note. Copy it over `config.py`, build, and you get a different app from the same codebase.

Use it as the template for your own.

## What is not in the config yet

Being straight about the edges, so you don't lose an afternoon:

- **Progression rules.** `planFor()` in `app.src.html` applies set and round progressions to the stock session keys (`A`, `B`, `C`, `CIRC`, `SIM`). Your own keys render exactly as written in the config, which is usually what a gym wants. If you need progression, that function is 15 lines.
- **Area icons.** The hexagon icons come from `tools/build_life_areas.py`, which carries its own list of SVG paths. New areas fall back to a generic icon until you add one there. This duplication is a known wart.
- **Recipes, workbook methods, meditation sessions and inbox rules** live in `ai/portal_ai/*.py`, one module each, with sources cited. They are data, so changing them is the same kind of edit — just a different file.
- **Copy and help text.** The guide entries and the welcome tour are written for this app's purpose. Search `app.src.html` for the phrases you want to change.

## Keeping your fork current

```bash
git remote add upstream https://github.com/Ethioguy/portal-11
git fetch upstream && git merge upstream/main
```

`config.py` is the file most likely to conflict, and it is yours — take your version. `index.html` will also conflict, since it is generated; take either side and rebuild.

## Before you publish your fork

- Run `python3 tools/build_editions.py`. It fails if the public build contains AI connection code, API-key handling, third-party embeds or personal text.
- Run `cd ai && pytest -q tests`.
- Check `git status` for anything personal. `private/`, backups, `.env` and photos are gitignored; confirm nothing slipped past.
- Update `PRIVACY.md` if you change what leaves the device. The current text is accurate for the stock build; if you add a service, say so there.
- Change the name. Running a fork under this one helps nobody.

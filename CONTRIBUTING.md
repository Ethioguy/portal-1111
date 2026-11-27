# Contributing

Thanks for looking. This is a personal project kept deliberately simple, so a few things are worth knowing before you spend time on a change.

## Ground rules

- **One source file.** The app is built from `app.src.html`. Never edit `index.html` by hand — it is generated. Run `python3 tools/build_editions.py` and commit both.
- **No dependencies in the browser.** No frameworks, no CDNs, no build step beyond the Python generators. The app must keep working offline from a single file.
- **Content comes from Python.** Exercises, life areas, recipes, workbook methods, meditation sessions and inbox rules live in `ai/portal_ai/` and `tools/build_*.py`, not hand-written in the HTML. Add data there and re-run its generator.
- **Nothing phones home.** A change that adds an outbound request to the public edition will fail the build guard, and that guard stays.
- **Cite sources.** Anything presented as research — a method, a range-of-motion limit, a training claim — carries its source in the Python module that defines it.

## Before you open a pull request

```bash
python3 tools/build_editions.py          # must succeed and leave index.html in sync
cd ai && pytest -q tests                 # 23 tests must pass
python evals/run_evals.py                # offline evals must pass
```

Then check `git status` for anything personal (backups, photos, the personal edition) before committing.

## Accessibility

Tap targets stay at 44px or larger, every control keeps an accessible name, animation is pausable, and the app must be usable at 200% zoom and with a screen reader. A change that breaks one of those will be asked to fix it.

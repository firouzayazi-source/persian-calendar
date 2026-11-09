# تقویم فارسی استوک لند

A subscribable Persian (Jalali) calendar for iPhone and Android, plus its install page and marketing kit.

## Files
- `stock-land-persian-calendar.ics` — the published calendar (1405–1407). Generated; never edit by hand.
- `tools/build.py` — rebuilds the .ics from `tools/source.ics` (original occasion data) and `tools/tips.txt` (weekly iPhone tips, `title|body`). Run `python3 tools/build.py` (needs `pip install icalendar jdatetime`). Output is reproducible except `DTSTAMP`.
- `index.html` — RTL install page (Vazirmatn font, light/dark), links to the .ics and Instagram.
- `marketing/` — A4 poster with QR, Instagram story, reel script (`reel.md`); `node marketing/render.js` re-renders the PNGs with Playwright.

## Calendar format
- Two all-day events per day: `info` (occasion · weekday + icon) and `date` (season emoji or 🔴 on holidays + Jalali date). iOS sorts by title, so the weekday line sits above the date line.
- Persian digits everywhere; description has Jalali + Gregorian date, holiday flag, occasions, weekly tip (Sunday, with alarm and Instagram link) and days to Nowruz.
- Holidays: `SOLAR_HOLIDAYS` + lunar keyword list `LUNAR_HOLIDAY_KEYS` (minus `NOT_HOLIDAY`).
- Source fixes live in `build.py`: `ADD` / `DROP` per Jalali date, `SOLAR_NAMES` for solar holidays the source leaves unnamed; bare «جمعه» occasions are dropped.
- 1405/1406 data is curated (~110 occasions/yr); 1407 comes from a different source with ~550 birth/death trivia entries. The owner chose to keep those.

## Workflow
- Small repo, commits go straight to `main`; GitHub serves the .ics to subscribers, so a push to `main` publishes.
- Expected official-holiday counts after overlaps: 1405 → 26, 1406 → 27, 1407 → 25 (printed by `build.py`).

See `CHANGELOG.md` for history.

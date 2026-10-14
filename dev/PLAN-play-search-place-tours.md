# Plan: play, search, place history, guided tours (2026-10-12)

Owner's wishes: a play button; a search box whose dropdown narrows as you type, and choosing a result moves the
timeline and the atlas there; "What happened here?" combined with play (pick a place, time runs, pauses at nearby
events with a short note); guided story tours, e.g. following human migrations.
Work happens on branch `play-search` (worktree `.claude/worktrees/play-search`, test server :8766) because another
session edits `karahan-era.html` on master at the same time; merge into master when both are committed.

## Phase 1 — Play (S–M)
- Play/pause button + speed (½×, 1×, 2×) in a bar under the timeline; Space toggles when not typing.
- Adaptive speed: years per second ∝ age (time before today), floor near today, so the whole span takes ~2 min and
  recent history slows down. The timeline zoom follows the speed so the view stays readable.
- Stops at today; dragging the timeline or choosing an event pauses.
- Test: playing moves the year forward smoothly with no long tasks; pause/resume; stops at today.

## Phase 2 — Search (S–M)
- Box in the header; dropdown of matches that narrows with each letter (events, eras, migrations; accent- and case-
  insensitive; ranked: title starts with query > word starts > contains, then importance).
- Keyboard: ↑/↓, Enter, Esc. Touch: full-width list.
- Choosing: event → timeline animates to its year and the map centres on its place; era → whole era in view;
  migration → its time span in view and the map fitted to its route.
- Later: states (Cliopatria names index), towns (GeoNames cities15000, CC BY) for Phase 3.

## Phase 3 — What happened here? (M)
- Long-press / "Here" button on the map (or a searched town) pins a place.
- Place panel: land/sea, ice, biome and temperature through time (small strip chart from existing rasters),
  who ruled it (Cliopatria/peoples), nearest dated finds (C14), population, nearby events.
- "Play from here": playback with the map centred on the pin; when an event within ~X km (scaled to zoom) comes up,
  playback pauses ~3 s and a short note (title, one line, link) appears, then continues.

## Phase 4 — Guided tours (M; writing is the larger part)
- Story JSON: steps of {year, map view, layers, caption, optional event/migration id}; next/back, autoplay between
  steps, deep-linkable (`?tour=…&step=…`).
- First stories (facts checked against Wikipedia/papers): Out of Africa and the peopling of the world; the peopling of
  the Americas; Doggerland drowns; the spread of farming from the Near East; the Austronesian voyages; the Bantu
  expansion; steppe migrations (Yamnaya). Migration arrows animate in sync with the steps.

## Feedback log — "What happened here?" (user, 2026-10-12; parked, revisit later)
- The separate place card below the map feels odd as its own view; it should feel part of the map/timeline
  (e.g. a side panel or overlay tied to the pin) rather than a second page section.
- "Nearby" is too generous: events far from the place are listed (now 900 km for importance ≤ 2, 400 km otherwise).
  Tighten and/or scale with zoom; prefer events whose region contains the place.
- Missing: migrations that pass through or reach the place, and other changes (who ruled it — Cliopatria/peoples,
  coastline/river changes, population steps, eruptions nearby). Add these as stops and as rows in the strip.

## Phase 4 status (2026-10-12)
- Engine done: "Guided tours ▾" in the play bar (also found by search), panel at the bottom of the map with
  Back / Next / Auto / Read more and step dots; time and map fly together (log-age interpolation); arrow keys step,
  Esc closes; deep link `?tour=<id>&step=<n>`. Data: `dev/data/tours.json` → `dev/scripts/embed_tours.py` →
  `<script id="tours">`. Test: `dev/test/tours.py`.
- First tours (fact-checked against Wikipedia): Out of Africa (10 steps), Peopling of the Americas (9), Doggerland
  drowns (8). Contested points are worded as "debated" (Madjedbebe 65 ka, Mandrin, White Sands, Monte Verde after
  Surovell et al. 2026, Paisley Caves, Storegga's effect).

## Tour candidates (popularity check, `dev/data/reddit_tours.json`)
Reddit blocks automated search, so this ranking uses proxies (AskHistorians FAQ sections, press explainers, existing
viral animated maps), not vote counts. High: Bronze Age collapse & Sea Peoples; Mongol conquests; Black Death spread;
Vikings from the Rus to Vinland; Polynesian wayfinding; Columbian Exchange & the Great Dying; Indo-European spread as a
language story; Ice Age land bridges (Beringia, Sunda, Sahul, Doggerland). Medium: Green Sahara; Silk Roads; White Sands
/ first Americans; Göbekli Tepe & first monuments; whole history in two minutes; Alexander; Zheng He vs the Iberian
voyages. Still planned from before: spread of farming, Austronesian voyages, Bantu expansion.

## Five ice ages (2026-10-13, requested via the Migrations session)
- 15 steps, 480 ka → 4.2 ka (`ice-ages`), facts checked against Wikipedia + cited papers (scratch research by a subagent);
  debated: Dye 3 DNA age, Toba catastrophe, D-O cause, Sahara drying speed, 4.2 ka and Akkad. Younger Dryas impact idea left out.
- Tour cards show a picture when a step has `img` (a title in `atlas/pimg/index.json`); 10 new picks in
  `dev/data/popup_images_pick.json` (Stokkermans, Zsoldos paintings; photos where no free painting exists).
- Rebuild sprites with `build_popup_images.py --cultures` (without the flag ~100 culture pictures drop out).

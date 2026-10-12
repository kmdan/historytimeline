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

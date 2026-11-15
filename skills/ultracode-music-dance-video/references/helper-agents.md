# Helper agents: when, how many, and how to brief them

The earlier session started five helper teams (42 helper runs). Only 10 returned a result. Helpers accounted for
roughly nine tenths of the session's cache traffic, the session hit the usage limit twice, and its output was several times
that of a comparable single session at the same effort. The film still got made, mostly by the main session. Read this
before starting any helper.

## The five teams and what each taught

| Team | Helpers | Returned | Lesson |
|---|---|---|---|
| Concept panel: 5 pitches, then 3 judges | 8 | 8 of 8 | Cheap relative to value (about 9 % of cache creation). Its grafts and one caught risk (a font with no A-Z) changed the film |
| Scene authors, one per scene | 9, then 7 restarted after a limit stop | 2 of 16 | The brief and file ownership worked; the size did not. Eight of nine stopped together at the first limit |
| Notes round on two unfinished scenes | 2 | 0 of 2 | Eight or nine notes per helper with no time budget: 26-54 minutes before the first edit; killed |
| Independent review of the finished render | 7 | 0 of 7 | 2 h 36 min, about a fifth of all cache creation, nothing returned |
| Fix round | 9 | 0 of 9 | Started at the end with an empty review list; cut off |

## Rules

1. **Size to the allowance.** At most four or five helpers at once for this kind of work. Nine heavy helpers in parallel
   exhausted the limit in under two hours. Group scenes by dependency (scenes sharing a routine together), heavy sections
   first. Lower effort for polish passes than for the first build.
2. **Budget in every prompt:** minutes, images, rounds, and what to do when it runs out. The budget that was finally written
   (too late to test): "about 45 minutes. Every image you open stays in your working memory and makes each later step slower:
   open at most about 30 images in total; prefer one sheet of many small tiles over many single stills; never open the same
   image twice; at most three render-look-fix rounds, then the final check; contact sheets at --tile 480 with at most 16 tiles,
   frame strips at --tile 320 with at most 24 frames; if a note would need a rebuild of the scene, do the simplest change that
   makes the shot read, and say so."
3. **Images slow helpers down.** Authors opened 28-88 images each; context grew to 340-450K tokens; past about 350K, gaps of
   5-15 minutes between steps appeared. Reviewers made 73-87 calls each, 53-72 of them image reads, with reads 3-5 minutes
   apart. Plan from measured step cadence, not from the number of steps a prompt implies. If a team has returned nothing useful
   in 60 minutes, assume it will not; look at its files.
4. **Incremental output.** Each helper appends to `work/<id>/STATUS.md` (built, left, known issues) after every round, and a
   reviewer appends to `findings.md` after every confirmed finding. The structured return is a summary, never the only copy.
   The seven reviewers lost everything because the final structured answer was their only output channel.
5. **Freeze the kit before spawning.** Build the engine, a reference scene and the brief first. If the kit must change, add
   the change to `CHANGES.md` (newest first) and tell helpers to re-read it before every render. Helpers discovered a new font
   guard and removed fonts from render errors.
6. **One owner per file** (`<id>.js`, one `<id>_parts.js`, `dev/<id>_*.js`, `work/<id>/`), and an explicit list of files they
   may not touch (core, kit, main, scene index, build scripts, docs). Missing kit features go into a `kit_requests` field;
   read those as the engine's bug list (ten real fixes came from two reports).
7. **Report schema:** `summary` (as built, not as planned), `departures_from_brief`, `final_sheets`, `render_rounds`,
   `known_issues`, `kit_requests`, `self_score`. Add: "known_issues must be empty or say why it cannot be fixed in the time you
   have". Authors listed the same five weak spots the final film shipped with, and stopped after about seven rounds without
   fixing them.
8. **Stopped helpers' edits are untrusted.** Have helpers write `<id>.next.js` and swap it in only after their last render
   passes, or keep a backup and write a `VERIFIED` marker. Re-render a stopped scene's sheet before the final render. Two
   half-finished edits went into the earlier final render unseen.
9. **Blind judges.** Give pitchers and judges a clean read-only copy holding only the song data and the engine README, not
   the working folder. The earlier judges saw renders of the director's build and raised its feasibility "for that and for
   nothing else". Decide beforehand whether the panel picks the concept; if so, do not build until it returns. Let judges
   start when four of five pitches are in, or cap pitch time at 30 minutes (the slowest pitch took 46).
10. **Verify every "available" claim in a shared brief.** A brief listing fonts as available, before checking them, sent a
    false fact to eight helpers.

## Recovering from stops

- Background helpers can die silently. A helper ended by an API error was marked failed and **not** retried; helpers ended by
  the session limit were restarted automatically after the reset with the same prompt, re-read the whole brief and kit (9-15
  minutes each) and redid work. Check the job journal for `failed` rows and for `started` rows without a `result` at the start
  of every resumed session; re-launch failed ones yourself; tell restarted helpers what exists on disk.
- Real return values are in the job's `journal.jsonl` (`result` rows); the completion notice is truncated. Each helper's own
  log has a `.meta.json` with its label.
- **At the first usage-limit warning, stop every helper before anything else** (keep the stop tool loaded from the start;
  the earlier session spent seven minutes of grace loading it while eleven helpers kept spending), then write the resume note
  (job id, which helper owns which file, whether its last edit was verified), then deliver.
- The grace window after a limit warning is short. Render and verify the deliverable, write the report, stop.

## Review that would have finished

Pre-render the evidence once in the main session (bar sheets, signature-instance sheets, a cuts sheet, a frame grabber), so
reviewers never render. Two or three reviewers, one bar group each, a budget, a findings file, on lower effort because they
only look. The whole-film reviewer runs after the section reviewers, with their findings. Hand each scene's findings to its
author as soon as they exist, rather than one fix wave at the end. Six check axes worth keeping: sync on every named hit frame
and the signature switch; story against the brief; composition and legibility; continuity of recurring story state;
artifacts (one-frame pops, blown highlights); on-screen text. Tell reviewers which deliberate rules of the film are not bugs,
and ask them to name the three strongest moments so fixes do not break them.

## Notes rounds

A note names a time range, the visible problem in plain terms, a measured target and a place: "the hanging figure is at least
a third of the frame height", "background gain about 0.55-0.7 so he is the brightest, sharpest thing", "the first frame after
the spin must be a clean image: figure sharp, FULL not WIDE". Keep a list of what to protect and of deliberate rules that must
not be "fixed". Each note gets a status: fixed, refuted, partly, not done. Give one helper two or three notes and 20 minutes,
not eight notes and no limit.

# Engine: renderer, looks, rig, dance, camera, font guard

What an earlier session built in about an hour of wall time and what it learned using it. Values are the ones that
worked; tags say how sure: **[verified]** seen on rendered sheets or measured on the final file, **[unverified]** built
but never seen moving, **[mistake → fix]** a problem it hit.

The engine in one sentence: a headless-Chrome page (three.js + Canvas 2D) where every object is a flat sheet with a 2D
canvas on it, standing in 3D; each video frame averages 12 renders across the shutter, so one loop gives motion blur,
depth of field and anti-aliasing; every frame is a pure function of the song clock `t`.

## A. Renderer

**Page contract.** The page sets `window.__ready = true` (or `window.__error = "..."` so the renderer stops), defines
`window.renderAt(t)` that returns after two `requestAnimationFrame`s, and exposes
`window.__info = {mode, width, height, subframes, duration, fps, scenes}`. Query switches on one page: `?only=<scene>`,
`?dev=<sheet>`, `?sub=N`, `?guides=1` (burn in time, frame, bar.beat, thirds and a 5 % safe box on a separate 2D canvas).

**Pure function of t.** No counters, previous values, `Math.random()` or `Date`. Randomness from `hash(a,b,c)`,
`rng(seed)` (`.range .int .pick .sign .gauss`), `noise1`, `noise2`, `fbm1` (slow camera drift). Scenes are called 4-32 times
per frame with different sub-frame times and in any order. [verified for the parallel render]

**Reset before every update.** The host loop calls `stage.reset()` and `kit.reset()` before every scene update, putting
camera, post, mirror and every shared object (puppet, room, cards: position, rotation, scale, visibility, opacity, gain,
tint, face texture) back to neutral. [mistake → fix: scenes leaked tints, faces and scale into each other until this
went into the host loop; a brief rule alone did not hold]

**Hard cuts.** `stage.beforeFrame` picks the owning scene once per frame, then every sub-frame's time is clamped into that
scene's `[t0, t1)`, so a cut never blends two scenes.

**Sub-frame accumulation.** Per frame, N renders summed with weight `1/N` into a Float32 target with additive blending,
each sample clamped to 64 so one bad pixel cannot poison the average. Scene target half-float with 4x MSAA.
N: 12 final, 6 preview at 960x540, 4 quick sheets, 1 text audit.

**Forward shutter.** `shutter = 0.5` (180°); sub-frame k at `ts = t + ((k+0.5)/N) · (shutter/fps)`. Frame n shows
[n/30, n/30 + 1/60]. A change scheduled exactly at a hit is fully visible on that frame. [mistake → fix: the first
version centred the shutter, which half-blurred every impact into the frame before]

**Hold the hit frame sharp when it matters.** Start motion after the first frame's shutter closes
(`tq = max(0, t - T0 - 1/60)`), so the frame the viewer sees on the hit is crisp.

**Depth of field.** Keep the focal plane still; offset the camera on a Vogel (golden-angle) disc of radius `aperture`:
sample k at angle `k·2.399963 + rot`, radius `sqrt((k+0.5)/N)·aperture`, `rot = hash(frame,11)·2π`. Offset along the
camera's right/up vectors and shear the projection to keep focus registered: `p[8] += -p[0]·ox/f`, `p[9] += -p[5]·oy/f`,
`f = max(0.05, focus)`. Keep `aperture` 0.02-0.06 (with 12 samples a larger lens shows ghost discs).

**Anti-aliasing.** 4x MSAA plus per-sub-frame jitter `jx = ((k·0.618034)%1 - 0.5)·0.9`,
`jy = ((k·0.754878)%1 - 0.5)·0.9`, applied as `p[8] -= 2·jx/W`, `p[9] -= 2·jy/H`. Hard-edged cutout sheets use
`alphaToCoverage`.

**Bloom.** Bright pass with soft knee (threshold 0.95, knee 0.5; `soft = clamp(br - thr + knee, 0, 2knee)² / (4knee)`),
bright values clamped to 24, six half-resolution levels down and back up, added at `bloom/6 · 2.2` (default bloom 0.55).
Anything over 1 blooms: that is the lever for glow. [mistake: flashes near blown-out; cap the sum of boosts on a hit]

**Final pass, in this order.** Zoom and shake offset → chromatic aberration (`0.0012 · (0.4 + r²·2.2)`) → add bloom →
exposure → mix to a fade colour (`fade 0..1`, `fadeColor`) → soft clip above 0.82 (`1 - exp` shoulder) → saturation →
contrast pivoted on 0.18 → tint → vignette (`smoothstep(1.05, 0.25, r·1.15)`) → linear to sRGB → triangular-PDF grain
(0.045, stronger in shadows, seeded by `hash(frame,3)`) → letterbox to 2.39:1 (`0..1`). Render linear with no tone mapping
because the pass does the encode. Fields a scene may write: exposure, bloom, bloomThreshold, bloomKnee, vignette, grain,
aberration, saturation, contrast, tint, fade, fadeColor, letterbox, shakeX, shakeY, zoom.

**Clamp everything.** [mistake → fix: a blown speckle band came from filtering overshoot and NaN; clamp the straight
colour (`clamp(rgb/a, 0, 1)`), the soft-clip output, and each accumulated sub-frame]

## B. Sheets and looks

**Layer = a plane with its own canvas**, drawn in world units, origin at the centre, y up. Build layers in `init` and
redraw only when a cache key changes; every redraw uploads the canvas.

**fitToCamera.** For something that moves and must stay crisp in close-up, ask which part of the sheet the camera sees
(unproject 16 NDC points onto the plane, +8 % margin), shrink the canvas view to that rectangle at the canvas aspect, and
fall back to the whole sheet when edge-on. A 2048 px sheet then gives full resolution on a close-up of a hand.

**Draw after the camera is final.** `puppet.set(pose)` pushes a callback into `stage.preRender`; `renderFrame` runs the
callbacks after the scene update and before rendering, so scenes may set pose and camera in any order.

**Paper shader.** Upload canvases premultiplied and undecoded; un-premultiply and decode with `pow(c, 2.2)` in the shader so
soft edges never fringe. One directional light: `diff = mix(1, 0.42 + 0.72·ndl², lit)`. Rounded corners by a signed-distance
box with `fwidth` AA; darken the rim so a card reads as thick. Back side modes: mirrored front, separate texture, or back
image cut to the front silhouette. Blend modes: cutout (depth write), alpha (soft, no depth write), add (light).

**Foil by colour key.** Any pixel within `smoothstep(0.07, 0.20)` of one exact key colour becomes stamped foil:
`0.55 + 1.7·sheen + 2.4·spec + 2.5·sparkle` with `sheen = pow(0.5 + 0.5·sin(uv·(5.2,3.4) + tilt + t·0.8), 5)`,
`spec = pow(N·H, 40)`, `sparkle = step(0.9925, hash(floor(uv·260)))·band²`. Artists paint with the key colour and get glinting
foil that blooms. Never use near-key colours for anything else. A colour key must be re-derived for every colour transform
applied before the shader sees it.

**A second look in the shader.** A whole-world alternate look (the earlier film's cold negative: `1 - c`, 45 % desaturated,
multiplied by (0.62, 0.82, 1.12)) can be switched per pass by shared uniforms, so the same drawing appears in two worlds.

**Mirror floor.** Render `stage.world` twice per sub-frame: flipped through y = 0 (the reflection, dimmer, `gain 0.45`),
clear depth, then upright. Shared uniforms tell each material which pass it is in, so the reflection can be a different
drawing. Groups: `world` (mirrored), `fixed` (backdrop, drawn first, never mirrored), `front` (overlays, drawn last with
fresh depth). Layer numbers pick passes (only-upright, only-reflection, and per look). Everything in `world` stays at y ≥ 0;
things lying on the floor at y 0.002-0.004. Materials double-sided (covers the winding flip). A cheap upgrade the earlier run
did not make: fade or blur the reflection with distance from the floor.

**Crowds.** One `InstancedMesh` with per-instance atlas rectangle and (opacity, gain, look) attributes draws hundreds of
cards in one call; a clone of a puppet shares geometry and material (mirror with `scale.x = -1`). Clone shots must be
medium or wide because clones disable view fitting.

**Cheap dressing, all functions of t.** Dust: GPU points, `y = mod(y + t·(0.06 + r·0.16), boxH)`, twinkle
`0.55 + 0.45·sin(...)`, fade near floor, ceiling and camera, point size capped at 1.2 % of frame height (520 flecks in a
22 × 10 × 16 box). A light beam from 40 stacked gradients widening from 0.06 to 0.5 of the width. A line-art wall with reveal
parameters (0..1) repainted only when the rounded key changes. Kick ripples: each kick in the last 0.9 s adds a ring
`r = 0.5 + dt·6.2`, alpha `(1 - dt/0.9)²·(0.35 + 0.5·strength)`. Strings: unit cylinders oriented between two points.

**Procedural art.** Symbols as `Path2D` (never glyphs: keeps the font guard happy), a fibre-stroke tile for paper grain,
cards cached by `key@size`, an atlas for instancing.

## C. Rig and poses

**A frontal paper doll.** All limbs rotate in the picture plane, head in profile: no 3D skinning, reads in stills.
A pose is a flat object of numbers, so blending is a lerp: `x, y` (hip offset; y < 0 crouch with feet planted), `pelvis,
spine, head` (degrees), `face` (+1/-1; animating through 0 is a paper flip), `shrugL/R`, `aL/aR = [shoulder, elbow, wrist]`,
`hL/hR` (`open|flat|fist|point`), `fL/fR = [x, y, rot]`, `kL/kR` knee side, `turn`, `tilt`, `mouth`, `blink`, `stretch`.

**Conventions that prevent mistakes.** L = screen-left always. Shoulder 0 = arm down, 90 = out, 180 = up, negative = across
the body; elbow and wrist in the same sense. Figure about 2.0 tall: thigh 0.5, shin 0.5, upper arm 0.3, forearm 0.27, hand
0.15, head 0.27, shoulder half-width 0.225. Helpers: `fullPose`, `mixPose` (hand shape switches at 0.5), `mirrorPose`
(swap L/R, negate leans, flip face).

**IK.** Legs always two-bone by the law of cosines from the sole position and shoe pitch; clamp unreachable targets to
`thigh + shin - 1e-4`; knee side +1 out (plié), -1 in (Charleston). Arms forward kinematics for dancing, plus
`reach(pose, side, x, y, bend, handDeg)` to land the wrist exactly on a point (palms together, fingertip on a surface).
Unwrap the shoulder (`if (sh < -110) sh += 360`).

**Whole-figure transforms** as a canvas transform about the floor point: `rotate(tilt)`, `scale(cos(turn)/sqrt(stretch),
stretch)` with `|cos| ≥ 0.02`; `cos < 0` shows the back. `turn: 360` is one paper spin; `stretch` keeps area.

**Die-cut drawing.** One `piece(shape, print)` function per body part: stroke the outline in stock colour at twice the
margin with a soft shadow (contact shadow and die-cut margin in one call), fill, clip and print (flat colour, pattern,
darker underside), then a thin ink keyline. Draw order builds the layering. Hands: fist, flat blade, point, open mitten.
Path helpers: tapered capsule, rounded polygon, SVG-like command list. Skins swap colours and costume parts on one rig.

**Deterministic marks.** Cracks as seeded random walks inside each piece's clip (up to 3 polylines of 7 steps, revealed one
after another by a 0..1 parameter), identical every frame.

**Pose library.** About 45 named partial poses combined with `combine("plie", "goal", {head: 10})` (later wins): open/closed
jumps, tutting right angles with flat hands, gestures (pray, crown, akimbo, cross, shrug, points, reach), legs and weight
(plié y -0.24, squat y -0.62, knees-in, steps, kicks, knee-up, lunges), whole body (running man, bow, limp hang, slump, floor
touch y -0.86). Style: tutting right angles, flat hands, jumping-jack opens and closes, Charleston knees, hip-hop bounce, hard
freezes; moves arrive on the beat (fast, small overshoot) and hold. Choose between variants by drawing five candidates side by
side with letters.

## D. Musical time and dance

**Time helpers** shared by every scene: `at, barOf, tInBar, barPhase, beatPhase, s16Phase, frameOf`; hit helpers by binary
search: `since(list,t)`, `until`, `count` (steps on every hit: alternate left/right per hit), `strength`, and
`pulse(list, t, halfLife, floor) = (floor + (1-floor)·strength)·0.5^(dt/halfLife)` (jumps to about 1 on the hit; `floor`
makes weak hits show). Presets: kick 0.13 s / 0.65, snare 0.09 / 0.6, hat 0.045 / 0.7. Guard comparisons with `+1e-9` so a hit
on a float-inexact frame time counts as happened. Write the song form in the time module's header so every author reads the
same map. Easing set: quad/cubic/quart/expo, `outBack(x, s)`, `outElastic`, `outBounce`, `snap(x,k) = 1-(1-x)^(2k)` (the dance
hit), `sharp`, plus `decay`, `ring` (damped oscillator kick), spring step and bounce. `keys(t, [[t, v, ease], ...])` where the
ease belongs to the segment ending at that key.

**Sequencer.** `dance([{t, pose, in, ease}, ...])`: `t` = when the pose is reached (put it on a hit), `in` = travel time
before it (0.07-0.1 snaps on kicks, 0.15-0.2 normal, 0.4+ legato). Ease `hit` = `outBack(1.25)` for limbs, while body fields
(x, y, pelvis, knees, turn, tilt, stretch, feet) use non-overshooting `outCubic`, so hips and feet never bounce through the
floor. Hand shapes switch mid-travel. A foot travelling along the floor lifts in an arc `sin(π·k)·min(0.13, dx·0.45)`. Keep key
spacing ≥ `in`.

**Free follow-through.** Evaluate the dance at slightly earlier times for distal parts: root and legs at `t`, chest and shoulder
at `t - 0.022`, elbows `t - 0.045`, wrists, hand shape and head `t - 0.065`; the face direction is not delayed (the head must
already look the right way on the hit). Copy pose objects before mutating them.

**Groove while holding.** `beatDip(t) = (0.5 + 0.5·cos(2πt/BEAT))^2.2` is 1 on every beat: `y -= bounce·dip`,
`head -= nod·dip`, shoulders `+0.012·dip`, a slow breathing sine, optional sway. Bounce 0.05-0.06, nod 3-4 (0.03 subtle to 0.1
heavy); rate 2 for eighths; 0 to freeze for a stillness shot. "Between hits he holds the pose and grooves; he never drifts."

**Leap pattern (anticipation, take-off, hang, landing)** for a hit-to-hit air time of 0.6 s: crouch in the 0.2 s before
take-off (extra hip dip up to 0.2, in-out quad); take off ON the first hit; `u` 0..1 through the air:
`lift = h·(outCubic(u/0.3) - inCubic((u-0.72)/0.28)) + 0.04·sin(πu)` (h = 0.62): up in 0.18 s, hang about 0.25 s, down in
0.17 s; knees tuck `sin(clamp(u/0.92)·π)^0.7`; land ON the next hit with a squash of 0.24 decaying over 0.3 s; cap the crouch;
skip the squash for poses already at the floor. While airborne, hold everything around him at the top of its arc too.

**A bar of choreography (worked pattern).** Ten keys per 3.2 s bar at offsets 0.0, 0.4, 0.9, 1.4, 1.6, 1.8, 2.0, 2.4, 2.8, 3.0:
kick; an off-beat step that sets up the leap; the air pose; the landing pose on the kick (`in 0.08`); two quick ticks
alternating mirrored poses; kick; snare; kick; a drop or reset. Choose poses that illustrate the line sung there. A routine is a
function of its start time, so the same routine can be danced solo and by a crowd later.

**Secondary motion.** Blink: period 2.6 s, start `n·2.6 + 0.4 + hash(n, seed)·1.6`, 0.13 s long, different seeds per figure.
A plume or hair angle as the negative velocity of head + spine + pelvis over 0.09 s, clamped ±38°, plus small noise.
Time-offset copies of a dance (a late twin, a canon) cost nothing: `pose(t - lag)`.

## E. Camera

The camera is data written per sub-frame: `{pos, look, roll, fov, aperture, focus}`. At fov 34 with a 2.0-tall figure:
WIDE z 13-15, FULL z 8-10, MEDIUM z 5-6.5, CLOSE z 2.5-3.5. Always a small drift (`fbm1`, about distance × 0.012). Cut only on a
bar line, a kick or a snare; each scene starts on a clearly different shot from the last. Keep the whole silhouette in frame on
every pose hit unless deliberately tight. A level camera near the floor puts a mirror line across the middle so figure and
reflection are equal. A kick-linked move: slow orbit plus a small push `-0.25·kick(t)` and a bloom pulse `+0.5·kick(t)`.
[mistake: the performer was small in many wide shots; size wide shots to the performer, not the room]

**Lettering fitted to the final camera.** Lay out the whole phrase once, reveal words in place; after the update, shrink and
place the sheet inside the camera's frame (`scale = min(1, 0.9·frameWidth/13)`, about 6 % from the top).

## F. Dev sheets

One page runs test sheets through the same renderer (`?dev=<name>`): a flat 16 × 9 layer filling the frame
(`fov = 2·atan(4.5/10)` at distance 10), post effects off. Sheets that paid for themselves: a pose sheet (8 test poses), the
whole pose library with names (22 per page), a close-up of one figure, a card/asset sheet, a type specimen sheet (to pick
lettering), an engine soak test (many objects, a moving camera, the mirror), and a **dance sheet**: one figure per 0.2 s step,
8 columns, each labelled `t  b<bar>+<beat>`, with the leap's lift added so the air phase shows. A single dance sheet that takes
a module path is better than one copy per scene.

## G. Font guard

1. Patch the `CanvasRenderingContext2D` `font` setter: parse the family list and throw unless every family is in the allowed
   list (fail closed on anything it cannot parse).
2. Wrap `fillText`, `strokeText`, `measureText`: re-check the font and throw on any character outside printable ASCII (32-126),
   with a message to draw symbols as paths. Use the straight apostrophe.
3. Record every distinct string drawn with its family, first time and count in `window.__drawnText` for the text audit.
4. At start-up, for each family: load it, then measure an all-ASCII string with `"<family>", monospace` and
   `"<family>", serif`. If the widths differ, glyphs are missing and it fell back: throw.

[mistake → fix: two serif files copied from a game launcher folder held 9 glyphs and no A-Z; `document.fonts` said "loaded";
the canvas silently fell back. A judge agent caught it by parsing the character map.]

## H. Lessons about building it

- Build the engine first and document each core file in a header (coordinates, API, traps); then build scenes.
- Measured costs: a 200-card 1080p frame took 4.3 ms of GPU but 0.36 s end to end, so capture, not drawing, is the floor;
  finished scenes cost 98-550 ms per `renderAt` at 16 sub-frames.
- What paid off: one loop for blur, depth of field and AA; one idea that is also one rendering trick; colour-key materials;
  pure-function time; shared story state as functions; a word whitelist; the font guard; a fixed whole-frame sixteenth.
- What stayed risky: nobody saw it move; wide shots too small; a busy background; blown flashes; the dance feel at speed.

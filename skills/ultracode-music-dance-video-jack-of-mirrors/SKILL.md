---
name: ultracode-music-dance-video-jack-of-mirrors
description: The "Jack of Mirrors" concept for the "Mirror Mirror" song passage - a paper court-card Jack and his cold mirror twin dancing on a mirror floor in a world of playing cards, built on the song's per-bar drum drop-out. Gives the idea, cast, two-world look, story variables, scene plan, per-bar images, lettering, ending and the known weak spots to fix. Use together with ultracode-music-dance-video, which holds the craft (engine, sync, checks, rendering); this skill decides only the concept.
---

# Jack of Mirrors (concept)

This is the concept of an earlier finished film for this song passage. A reviewer of six versions called it the most
creative. Build it with the craft skill `ultracode-music-dance-video` (engine, frame clock, checks, rendering), which
must be read first. Scene-by-scene detail with hit times: `references/story-and-scenes.md`. The song's measured facts
(grid, the per-bar gap, lone hits): `ultracode-music-dance-video/references/song-facts.md`.

## 1. The idea

The song is a man questioning a mirror: who will rise, who will fall, don't lie to me. A court card is its own mirror: an
upright figure joined to an upside-down twin, so every half-turn swaps who is up and who is down. The lyric already talks
like a deck of cards (royalty falling, crowns traded, a big-money deal, a rigged game, a pivot, a loss, a young man). So the
performer is the **Jack of an invented fifth suit, Mirrors, whose pip is an eye**.

- He is a jointed **paper puppet** (frontal paper doll, die-cut pieces, gold brads at the joints, a red/blue split torso,
  a plume). Above the mirror line the world is warm: ivory card stock, gold foil, red, blue. Below it is his **twin**: the
  same figure as a cold negative (ivory → navy-black, ink → silver-white, red → cyan, gold → ice-white), cracked, dancing late.
- **The story is the gap between the two closing.** The twin is a whole beat late (0.8 s) in hook 1, half a beat (0.4 s) in
  the quiet verse, a sixteenth (0.2 s) after the drop, eases to 0 over the break, and dances in unison in the last hooks.
- **Cracks and gold.** The twin's cracks creep in during hook 1, then one more scar opens on every loud-verse downbeat
  (8 scars), and they fill with gold on the line about scars and learning. From hook 2 the Jack wears the gold seams himself.
- **Strings.** He dances on puppet strings until the break, where they snap on the two lone kicks and the frame pivots about
  a brass pin.
- **The signature: the gap.** In every loud bar the bass and drums vanish for 0.6 s (snare to next kick). In that hole the
  worlds swap (upright goes cold, reflection warm), he is in the air, and the words the voice sings alone appear as lettering.
  He lands on the kick, which is the bar's punch line.
- **The promise.** His fingertip and the twin's stop either side of the mirror line and never touch, three times; on the last
  kick they touch. The picture turns out to be the face of a card, flips to its back, and the title MIRROR stamps in on the
  last kick and holds.

## 2. Look rules (put them in the brief)

- **Gold = bass.** Foil dims whenever the bass rests and flares on bass notes; it drains when the bass leaves and slams back
  for the length of each lone low hit. A frozen frame should tell you whether the bass is playing.
- **Gold is a key colour.** Paint foil only with the one exact gold key; never use gold-ish colours for anything else (a
  separate flat dark gold for non-foil). A second magenta key becomes gold foil in both worlds (the twin's seams).
- **Ink on black** is invisible in the warm world and bright silver in the cold one: that is how the gap lettering appears
  only during the swap.
- **The mirror floor is the twin:** the world is drawn twice per sub-frame, flipped (cold look, own pose, own cracks) then
  upright; when he leaps, the reflection drops away below him.
- **The deck is the audience:** 56 cards in two blocks of 7 × 4 flanking the stage, dealt one per hi-hat tick in the quiet
  verse (the last on the last hat), face-down gold backs until the drop, flipping face-up over 3 frames on the drop's kick,
  hopping on kicks afterwards, clapping on hats. Special cards (Kings, Queens, Aces, sixes, the Mirrors suit) have fixed slots.
- **Cast from one rig:** Jack, King and Queen (the Queen of Mirrors, his mother) are skins of the same puppet: colours, robe
  length, collar (ruff, ermine, pearls) and head.

## 3. Scene plan

| Time | Scene | What happens |
|---|---|---|
| 0.0-12.8 | The card | The card on the wall: Jack above, twin below; a half-turn on the first line (who rises, who falls); the card towers with a ruler on the second line (standing tall); push into his eye; the small card in the void with lettering on the mirror line; two knocks on the first two drum hits; a gold flash on the last frame |
| 12.8-25.6 | The gold room | He dances on strings with the late twin while one card is dealt per hi-hat tick (56) and counted on the wall; the Queen of Mirrors flies in and bobs on the hats; the deck applauds; then 1.8 s of stillness (limp on slack strings, one cone of light) and four Kings marked in red, one per sixteenth |
| 25.6-32.0 | The drop | The deck flips face-up; Kings topple one per sixteenth and slam flat on the kick at 27.0; the Queens swap their crowns, spin and come round as sixes; six cards dealt away |
| 32.0-38.4 | Pray | He lands praying; the fallen Kings rise like lanterns; the wall of cards turns edge-on in the gap and nine tall cards slam down as a cage |
| 38.4-44.8 | The movie | Letterbox slams in, film strips of cards, a credit roll of card names rises and jams; crop brackets close in and he breaks out |
| 44.8-51.2 | Scars | A fan of spades turns upside down into false hearts; the low two-shot where the twin's cracks fill with gold; a giant J and its mirror image reading as L |
| 51.2-54.4 | The break | Dark and cold: a brass pin stabs the floor, the strings snap on the lone kicks, the whole frame pivots about the pin |
| 54.4-67.2 | Hook 2 | The duet: the four-bar hook routine, free of strings, in unison with the twin; the deck as corps de ballet; fingertips that almost touch; the giant eye |
| 67.2-79.17 | Hall of mirrors | Five, then nine Jacks in canon, a giant, back to one; the touch on the kick at 78.2; card face, flip to its back at 78.6; title MIRROR on the last kick at 78.8, then a dead hold of the last 11 frames |

**Lettering whitelist** (hard-coded per gap bar; nothing read from a transcript at render time): in each hook bar, the
two or three words the voice sings alone inside that bar's gap; one short phrase on the mirror line in bar 3; one key word
pair in bar 11 and in bar 14; the title MIRROR. This kit carries no lyric words, so take them from your own listening and
keep each phrase to a few words. Card indices, numerals, a counter, a ruler 1-10 and a credit list of card names are the
only other text. The uncertain first word of the fourth hook line is never shown.

## 4. The four-bar hook routine

One bar per hook line, ten keys per bar at bar offsets 0.0, 0.4, 0.9, 1.4, 1.6, 1.8, 2.0, 2.4, 2.8, 3.0: kick; an off-beat
step setting up the leap; the air pose; the landing on the kick; two quick ticks alternating mirrored poses; kick; snare;
kick; a drop or reset. Poses illustrate the line: running-man arms for the line about running from faults, a stretched tall pose
for the line about standing tall, a full paper spin in the air of bar 3, a floor touch with a pointing finger on the mirror at the landing. Danced as a
bust-only legato piece on the hero card in hook 1, a duet in hook 2, then by five, nine in canon (a second puppet a sixteenth
behind) and a giant in hook 3.

## 5. Fix what the earlier film shipped

1. **The Jack was small in wide shots** (the drop, bars 12 and 16, the troupe of nine). Keep a minimum figure height (about
   250 px of 1080) outside one designed pull-back; a medium solo on the landing kick every second bar; only the lead wears a
   red mark in crowds.
2. **The ivory card wall was busy behind an ivory dancer.** Dim or darken the wall at pose hits (deck gain about 0.4-0.7);
   reserve ivory for the hero card; give the Jack a dark keyline or lit rim; threshold a sheet to test his silhouette.
3. **The giant J and L and some landing flashes were near blown-out.** One boost per hit, capped.
4. **The crop sequence left the frame mostly black for 2.5 s.** Keep motion inside the matte and halve the black time.
5. **The four gap shots of the first loud hook looked alike.** One named composition per gap bar (low frontal; two-shot
   across the mirror line with words either side; three-quarter with words coming at the lens; top-down with words flat on
   the mirror), compared side by side as thumbnails.
6. **The opening 9 s were a small portrait card in an empty wall,** and the deck flashed its backs early, spoiling a reveal.

Also from its own review: the dead hold at the end was never checked frame by frame, and the twin's lag jumps at bar lines 4, 8
and 16 are hidden only because each coincides with a hard cut; keep those cuts.

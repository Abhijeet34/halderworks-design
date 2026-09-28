# Colour

Every colour here was solved to a contrast target. None was chosen and then checked.
The difference is not pedantry. Solving caught a `warning` at chroma 0.12 that falls outside sRGB at every light ground, and five dark-theme pairs that cleared AA against the darkest surface and failed against the lightest one.
Both would have shipped under an eyeball.

**108 text pairs, both themes, 0 below WCAG AA 4.5:1. 90 non-text pairs held to 3:1, 0 below it. 33 tokens, 0 outside the sRGB gamut.**
Those are the counts `tools/build.py` prints and writes into the header of `tokens/tokens.css`; every one is re-measured on the formatted strings before either file is written.
`tools/contrast.py` then re-derives all **198 certified pairs** from the CSS with a second converter that shares no code with the build, on the float value and on the 8-bit value a display receives.

The first pass certified 51 pairs. Re-running the matrix over the completed system, with the two
surfaces the interaction-state layer needed and the ink-on-quiet-fill pairs the rules already
assumed, found **three defects that had shipped**:

| defect | measured | now |
|---|---|---|
| `hw-accent` on `hw-accent-quiet`, dark, a pairing this file already instructed | 4.37:1, below AA | the fill re-solved; 4.60:1 |
| `hw-success` on `hw-success-quiet`, dark | 4.46:1, below AA | 4.61:1 |
| `hw-accent-ring` solved against the ground only | **2.56:1 on `hw-surface-raised`**, a focus ring inside a dialog | re-solved against the surface closest to it in lightness; 3.05:1 at its worst |

All three came from the same habit the solver exists to prevent: checking a pair against a
convenient ground rather than against the worst one it is permitted to sit on. The token build
now refuses to emit unless the whole matrix holds.

The third pass, specifying the form layer, found a **fourth** of the same family, and this one had
already been measured and printed by this system without being recognised:

| defect | measured | now |
|---|---|---|
| `hw-border-strong` as a control outline, its only stated job | **1.45:1 to 2.14:1**, against the 3:1 that WCAG 2.2 SC 1.4.11 holds a control boundary to | re-solved against the surface closest to it in lightness; **3.03:1** at its worst in both themes |

[15-color-combinations.md](15-color-combinations.md) already printed `1.64:1` for that token, as the
argument for never using it as an ink, and never asked whether it cleared the different bar it
actually had to meet. A number measured for one question does not answer another one.
That is the ring's lesson arriving through a different door, and it is why
[05-coverage.md](05-coverage.md) now exists: the hole was not in the measuring but in knowing which
questions the system owes an answer to.

## The contrast matrix

Read this as permission. A text token may sit on any surface whose column shows a ratio here, and on no other.
The full table, including the hover and active surfaces, is in
[15-color-combinations.md](15-color-combinations.md), which also says which inks may sit on a
quiet fill and what may never sit on what.

### Light

| foreground | on ground | on surface | on surface-sunken |
|---|---:|---:|---:|
| `hw-text` | 14.83 | 15.78 | 13.98 |
| `hw-text-secondary` | 6.37 | 6.78 | 6.00 |
| `hw-text-muted` | 4.88 | 5.20 | 4.60 |
| `hw-accent` | 5.09 | 5.42 | 4.80 |
| `hw-success` | 5.10 | 5.42 | 4.80 |
| `hw-warning` | 5.10 | 5.43 | 4.81 |
| `hw-danger` | 5.09 | 5.42 | 4.80 |
| `hw-ink-text` on `hw-ink` | 17.63 | | |

### Dark

| foreground | on ground | on surface | on surface-raised | on surface-sunken |
|---|---:|---:|---:|---:|
| `hw-text` | 16.38 | 15.23 | 14.02 | 16.98 |
| `hw-text-secondary` | 7.01 | 6.52 | 6.00 | 7.27 |
| `hw-text-muted` | 5.38 | 5.00 | 4.60 | 5.58 |
| `hw-accent` | 5.60 | 5.21 | 4.79 | 5.80 |
| `hw-success` | 5.61 | 5.22 | 4.80 | 5.82 |
| `hw-warning` | 5.61 | 5.22 | 4.80 | 5.82 |
| `hw-danger` | 5.61 | 5.22 | 4.80 | 5.82 |
| `hw-ink-text` on `hw-ink` | 17.36 | | | |

The focus ring is a non-text indicator, which WCAG 2.2 holds to 3:1 rather than 4.5:1.
`hw-accent-ring` is solved to that bar against the surface CLOSEST TO IT IN LIGHTNESS, not against
the ground: 3.05:1 on `hw-surface-sunken` in light and 3.05:1 on `hw-surface-raised` in dark, its
two worst cases, rising to 3.44:1 and 3.70:1 elsewhere. Solved against the ground alone, as the
first pass did, it measured 2.99:1 in dark on the ground and 2.56:1 on `hw-surface-raised`.

The six chart colours are fills rather than text, so they are held to the same 3:1 on all four surfaces a chart is drawn on: ground, surface, raised and sunken.
Against the light ground they measure 3.29, 8.13, 3.62, 8.41, 3.43, 7.55, and no pair falls below 3.10, which is `hw-chart-1` on `hw-surface-sunken`.
Against the dark ground they measure 8.54, 13.62, 7.84, 13.37, 8.18, 14.14, and no pair falls below 6.71, which is `hw-chart-3` on `hw-surface-raised`.
Adjacent series alternate in lightness, 0.20 apart in light and 0.15 in dark, and every chart colour sits at least 8.0 in oklab distance times 100 from each semantic.
That is the bar the accent was held to until [the three bars](#the-three-bars-the-accent-is-held-to) replaced it, and the charts keep it: a chart colour is an ink with no fill and no ring, and the house ramp comes as close as 8.7 in CIEDE2000 to a state, which the accent's 14 would refuse.
Their closest pair sits 15.4 apart in light and 10.2 in dark.

## Why the ground is neutral

Across 14 reference products, measured with `getComputedStyle` on the live pages rather than sampled from screenshots, 11 have a dominant painted ground within 2/255 of neutral grey.
The three that carry a cast are Superlist (12/255, hue 284), Railway (11/255, hue 292) and Arc (19/255, hue 98). The first two are casts on a *dark* ground.
Only Arc tints a light ground, and Arc is a consumer browser whose identity is deliberately playful.

This system's light ground is `oklch(0.978 0.003 198)`, which resolves to `#F6F8F8`: a channel spread of 2/255.
Its dark ground is `oklch(0.152 0.006 198)`, `#090C0C`, a spread of 3/255, sitting between Linear's `#08090A` and 21st.dev's `oklch(0.141 0.004 285.82)`.

The neutrals carry a trace of the accent hue rather than being flatly achromatic: chroma 0.003 in light, 0.006 in dark.
That is roughly a third of the chroma at which a cast becomes readable as a cast, and it exists so the accent looks native to the palette rather than pasted onto it.

## Why hue 198

The hue was chosen by measuring where the field already is, then staying out of it.
Sampling every chromatic colour those same 14 products actually paint, ranked by painted area, yields 29 accents above a 0.055 chroma floor.
Seventeen of them fall between hue 245 and 296, and so does the single highest-area chromatic colour on 8 of the 11 captures that paint one at all: Resend 245, Vercel 258, 21st.dev components 264, Superlist 264, Stripe 268, Arc 269, Linear 275, Railway 296. The three that sit elsewhere are 21st.dev's landing page at 36, rauno.me at 110 and Family at 147, and three more captures paint no chromatic colour at all.
That corridor is the most crowded place in colour space for a developer tool.

The bands outside it are mostly spoken for by meaning rather than by fashion. 20-90 is the warning family and also the warm-cream default this system is written against; 130-160 is success; 0-25 is danger.
That leaves 170-215 and 300-345. Both were built and rendered in full, in both themes, on a real product screen.

Two measurements settled it. The figures are oklab distance times 100 between the accent and the semantic it sits nearest:

| candidate | accent vs success | accent vs danger | verdict |
|---|---:|---:|---|
| 172, teal | 3.8 dark, 4.9 light | 21.2 | rejected. In the render the live badge and the passed badge read as one colour, which the number then confirmed |
| 318, magenta | 23.3 | 11.9 dark, 13.7 light | rejected. Closest to danger of the four, and it reads consumer rather than instrument |
| 240, azure | 16.2 | 23.1 | rejected on occupancy. It is the centre of the crowded corridor |
| **198, cyan-teal** | **8.2 dark, 8.9 light** | **20.7** | chosen. Every separation above 8, and outside the corridor |

That table is the choice, and it stands.
The bar the build then enforced from it, 8.0 in oklab distance, did not survive being tested, and [the next section](#the-three-bars-the-accent-is-held-to) replaces it.

### The three bars the accent is held to

The 8.0 bar had three faults, each measured by the constraint audit of 2026-09-21.
It was **bracketed by one rejection and one acceptance**, teal 172 at 3.8 and 198 at 8.2, so nothing between them had ever been looked at, and renders at 6.2 to 7.3 read as distinct.
It was **blind to lightness by construction**: every ink is solved to the same 4.5:1 floor, so every ink shares a lightness, and the one freedom that could separate a warm accent from the states, a deeper or lighter accent, never registered.
And it **measured one of the three things the accent paints**, the ink, while the first to collide is the selected-row fill: every quiet fill sits at L 0.94, C 0.035, so fills sit about a third as far apart as inks, and 198's own fill is 2.7 in oklab from `hw-success-quiet`.

So each element the brand paints is held apart, in CIEDE2000, the difference formula built to track how far apart two colours look, on the 8-bit value a display receives, in all four blocks, from the state drawn in the same form:

| element | held apart from | bar | why that state |
|---|---|---:|---|
| the primary fill, `hw-primary`, or `hw-ink` in a set with no vivid tier | `hw-danger` | 14 | a destructive confirm is the one state drawn as a filled button |
| the selected-row fill, `hw-select`, or `hw-accent-quiet` in a set with no vivid tier | each state's quiet fill | 5 | the selected row is the one accent element with no second channel, and it sits in a list beside status rows |
| the focus ring, `hw-accent-ring` | `hw-danger` | 17 | an error field is the one state drawn as a border around a control, where a focus ring also sits |

The numbers are the ones calibrated on renders: 14 between teal 172 at 10.5, where Live and Passed read as one family, and 186 at 14.3; 5 between a full-chroma 52 at 4.9, whose peach row reads as a status, and a rust 50 at 5.4; 17 between an oxblood at 14.7, whose ring reads as the error border, and the rust at 17.4.
They are the system owner's decisions of 2026-09-21, and the vivid tier, proposed by the scout of 2026-09-22 and built on 2026-09-28, moved the first of them without changing its number.

**The accent ink is no longer held to the states**, and `tools/contrast.py` reports its distance rather than refusing it.
The bar used to hold the ink 14 from all three state inks, and shipped products measure otherwise.
Two Mobbin screens read through a canvas on 2026-09-22 ([90-evidence.md](90-evidence.md#shipped-accents-on-state-hues)): Todoist paints its accent 2.5 CIEDE2000 from its own overdue red, with a selected row 5.5 from this system's danger fill, and Duolingo's primary button is 9.6 from its own success ink.
Nothing is confused, because every state carries a glyph and a word, which [15-color-combinations.md](15-color-combinations.md) already requires here, and macOS itself offers red, orange, yellow and green as the system accent while its alerts keep the system red.
Teal 172's render finding stands for the case it tested, and that case is now carried by the words.
The selected row keeps its bar because a wordless row beside a wordless state container is exactly where colour is the only channel; a neutral selection is exempt, because it is not a hue.

The house clears all three with room: primary 29.9, fill 8.2, ring 44.6 at its worst block, and its accent ink sits 18.7 from the nearest state ink, reported.
Every accent the audit rendered and judged, measured by `tools/contrast.py` at its worst of the four blocks; the old reading is the 8.0 bar's, light and dark only, and the ink column is now a reported distance:

| accent | old reading | ink, reported | fill | ring from danger | ring from border | as rendered | the build |
|---|---:|---:|---:|---:|---:|---|---|
| **198, the house** | 8.2 | 18.7 | 8.2 | 44.6 | 16.0 | chosen | builds |
| 186 | 6.2 | 14.1 | 6.0 | 46.2 | 16.6 | its own colour | builds |
| 116 | 6.3 | 14.2 | 6.5 | 37.3 | 15.9 | its own colour | builds |
| 350 | 6.7 | 16.0 | 6.5 | 20.0 | 16.7 | its own colour | builds |
| 172, teal | 3.8 | 8.1 | 3.3 | 47.0 | 16.7 | Live and Passed read as one family | refuses the fill |
| 152 | 1.4 | 1.8 | 0.0 | 45.8 | 16.8 | the selected row is a passed row | refuses the fill |
| 27 | 1.8 | 2.1 | 0.6 | 12.2 | 16.3 | the ring is the error border | refuses the fill and the ring |
| 52, full chroma | 4.7 | 11.8 | 4.9 | 16.4 | 15.9 | the peach row reads as a status | refuses the fill and the ring |
| 70 umber, deep, quiet | 13.7 | 14.3 | 6.9 | 22.4 | 9.7 | dark brown; selection a warm grey | builds with the accent or ink ring |
| 115 moss, deep | 9.4 | 15.1 | 7.1 | 35.2 | 13.5 | its own colour | builds with the accent or ink ring |
| 5 rose | 5.5 | 10.9 | 3.8 | 17.5 | 12.8 | the pink-grey row reads as a failed row | refuses the fill |
| 30 oxblood, deep | 12.2 | 12.0 | 0.9 | 14.2 | 13.7 | the ring reads as the error border | refuses the fill and the ring |

The umber is hue 70 at 0.6 times the house chroma, L 0.38 and 0.76, with its fill at 0.3; the moss is hue 115 at 0.8, L 0.44 and 0.70; the rose is hue 5 at 0.7 with its fill at 0.4; the oxblood is hue 30 at 0.8, L 0.38 and 0.76.
Every accent the render read as a state still refuses, on the fill or the ring; the ink half of teal's and 152's verdict is the one the words now carry.
The umber and the moss refuse only the ring's distance from a control's own edge, which [12-brand.md](12-brand.md#the-focus-ring) owns, and build with either of the rings it offers.

**What this opens is warm colour, and a second band.** The house set builds at 155 accent hues where it built at 127: 100 to 124, 184 to 219 and 265 to 358, against 113 to 115, 187 to 219 and 265 to 355 before, and `tests/hue_sweep.py` fails if that arc moves without this sentence moving with it.
A brand's vivid key is bound by none of the accent's arc: its one bar is the primary's 14 from `hw-danger`, and only when it is the primary.
quoth's Field identity keys on hue 100 over a slate accent at 255.
A warm accent at the house chroma is still bound by its fill: for hues 0 to 95 the fill tops out at 4.7 whatever the ink does.
**What stays closed with an accent selection is red and pink**, on the evidence of the renders rather than on principle.

Under simulated colour-vision deficiency the house already fails any bar like these, and survives on words: the shipped `hw-success` and `hw-danger` fills sit 0.9 apart under deuteranopia, three tan pills told apart by Passed, Retried and Failed.
That is the book's design ([15-color-combinations.md](15-color-combinations.md)), so the bars refuse on normal vision only.

A product's own colour is held to the ink bar, 14 CIEDE2000 from each state, and to a guard of 5.0 in hue and chroma with lightness left out, from the states and the accent; [95-extending.md](95-extending.md#how-a-product-colour-is-held-apart) says why it takes both, and why a dichromat's reading is reported for it too.

### The vivid tier

The accent is a text ink, solved to 4.5:1, and at the lightness that pins it butter, marigold, lime and pink do not exist: hue 113 at L 0.5 is olive.
A brand that wants a vivid colour takes it as a **fill with a solved label**, `hw-brand` and `hw-on-brand`, and as a large **field**, `hw-field`, never as text.
[12-brand.md](12-brand.md#the-vivid-tier) owns the tokens, their floors and the inputs that open them; [15-color-combinations.md](15-color-combinations.md#the-vivid-tier) the pairs.

## How colour is spent

The loudest control on any screen is `hw-primary`, and in the house set it is `hw-ink`: near-black in light theme, near-white in dark, and carrying no hue at all.
A brand may make it its own vivid fill with `primary: brand` ([12-brand.md](12-brand.md#the-vivid-tier)); the house does not.
The accent is spent on four things and nothing else - a link, a selected row, a live state, and the focus ring.
quoth's open microphone is the one live state that takes a colour of its own, `--quoth-live`, because there the accent would read as selection; [95-extending.md](95-extending.md#the-worked-example-quoths-live-colour) has the value and its derivation.

This is not restraint for its own sake, it is what the high-craft references measurably do.
Three of the fourteen (Radix Colors, emilkowal.ski, paco.me) paint no chromatic colour at all above the 0.055 floor on their landing surface.
Family's primary call to action is a black pill; Vercel's is a black button.
Where a whole page is one accent, the accent stops meaning anything.

Semantic colour is separate from the accent and always will be.
A green that also means "this is our brand" cannot also mean "this passed".
Nor can it mean "this step is finished": progress is neutral, and `hw-warning` appears only on a real problem, named in words. [68-page-patterns.md](68-page-patterns.md#first-run-and-setup) states it for the screen where both are most tempting.

## Two things you would otherwise rediscover

**`hw-warning` is dark amber, not yellow.** No yellow clears 4.5:1 against a light ground, and the in-gamut chroma ceiling at that lightness is what fixes the value. A yellow warning is a warning that readers with low vision cannot read.

**`hw-accent-quiet` carries exactly two inks and both are certified.** It is a fill, solved for a
visible step off its surface AND for the ink the system tells you to put on it. Those inks are
`hw-accent` and `hw-text`; nothing else. The first pass stated the first half of that rule and
never checked it, which is how a 4.37:1 pair shipped.

Solve the colour to the requirement; do not pick one and hope.


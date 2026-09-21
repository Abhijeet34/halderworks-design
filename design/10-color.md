# Colour

Every colour here was solved to a contrast target. None was chosen and then checked.
The difference is not pedantry. Solving caught a `warning` at chroma 0.12 that falls outside sRGB at every light ground, and five dark-theme pairs that cleared AA against the darkest surface and failed against the lightest one.
Both would have shipped under an eyeball.

**104 text pairs, both themes, 0 below WCAG AA 4.5:1. 54 non-text pairs held to 3:1, 0 below it. 33 tokens, 0 outside the sRGB gamut.**
Those are the counts `tools/build.py` prints and writes into the header of `tokens/tokens.css`; every one is re-measured on the formatted strings before either file is written.
`tools/contrast.py` then re-derives all **158 certified pairs** from the CSS with a second converter that shares no code with the build, on the float value and on the 8-bit value a display receives.

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

The six chart colours are fills rather than text, so they are held to the same 3:1 and clear it with room: 4.47, 4.74, 4.94, 4.92, 4.68, 4.42 against the light ground, 6.58, 6.23, 6.01, 6.03, 6.28, 6.57 against the dark one. Their closest pair sits 8.9 apart in oklab distance times 100, the same separation the accent keeps from success.

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

## How colour is spent

The loudest control on any screen is `hw-ink`: near-black in light theme, near-white in dark, and carrying no hue at all.
The accent is spent on four things and nothing else - a link, a selected row, a live state, and the focus ring.

This is not restraint for its own sake, it is what the high-craft references measurably do.
Three of the fourteen (Radix Colors, emilkowal.ski, paco.me) paint no chromatic colour at all above the 0.055 floor on their landing surface.
Family's primary call to action is a black pill; Vercel's is a black button.
Where a whole page is one accent, the accent stops meaning anything.

Semantic colour is separate from the accent and always will be.
A green that also means "this is our brand" cannot also mean "this passed".

## Two things you would otherwise rediscover

**`hw-warning` is dark amber, not yellow.** No yellow clears 4.5:1 against a light ground, and the in-gamut chroma ceiling at that lightness is what fixes the value. A yellow warning is a warning that readers with low vision cannot read.

**`hw-accent-quiet` carries exactly two inks and both are certified.** It is a fill, solved for a
visible step off its surface AND for the ink the system tells you to put on it. Those inks are
`hw-accent` and `hw-text`; nothing else. The first pass stated the first half of that rule and
never checked it, which is how a 4.37:1 pair shipped.

Solve the colour to the requirement; do not pick one and hope.


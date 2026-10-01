# Brand

A product's identity is a **brand seed**: twenty-three bounded inputs that `tools/build.py --brand` applies to a copy of the house seed and then solves with the same code as the house set.
Every brand ships the house's token names, clears the house's contrast floors, and is certified by the same second instrument.
A brand is a rebuild, never a hand-pick, and "never redefine an `hw-` token" does not change by a word.

## Why a brand is more than an accent hue

Until 2026-09-21 the rule was "the accent hue, and nothing else", and it could not carry the products this book serves.
Under the separation bar it used, only hues 198 to 342 built, at most three accents in that arc sat 8.0 apart, and six evenly spaced ones sat 3.8 apart, which is the distance at which [10-color.md](10-color.md#why-hue-198) rejected teal 172 because the live badge and the passed badge read as one colour.
Every product was the house with a different link colour.
The system's owner gave the direction the same day: each product needs its own distinction rather than a sampler hue.

The first brand tier, eleven inputs, still produced twins.
The product-identities scout of 2026-09-22 found five causes, and four were rules whose evidence did not hold: the accent was a text ink and only a text ink, so at the L 0.515 its floor pins, hue 113 is olive and butter, marigold, lime and pink do not exist; the loudest control was ink in every product; accent chroma was capped at 1.3 times the anchor, C 0.103, against a field median of C 0.194 measured across 87 systems; the three semantic bars closed half the wheel; and a neutral ceiling of 4.0 refused nothing the measured bar beside it did not already refuse.
The owner approved the amendment the same day, and [the vivid tier](#the-vivid-tier) is it.

What that rule got right survives whole.
A product stylesheet that sets `--hw-radius-md: 8px` is still a fork wearing the system's name, because nobody solved that value and nobody certified it.
The safe input was never "a hue". It was **an input to the solver**, and hue happened to be the only one wired up.

## Who chooses what, and when

| layer | who chooses | when | mechanism |
|---|---|---|---|
| foundations | the house | once | `tokens/tokens.seed.json`, and every refusal in `tools/build.py` and `tools/contrast.py` |
| brand | the product | once, at build time | a brand seed, solved by `tools/build.py --brand` into the same token names |
| overlay | the product | per surface | `data-overlay`: Instrument, Console, Editorial ([75-spec-sheet.md](75-spec-sheet.md#1-themes)) |
| viewer | the person | at run time | `data-theme`, `data-density`, `prefers-contrast`, `prefers-reduced-motion`, `forced-colors` |
| product namespace | the product | as a concept arises | `--quoth-live` and its kind, solved by `tools/build.py --extend` ([95-extending.md](95-extending.md#a-colour-of-the-products-own)) |

A product may pin a viewer setting where its surface has a convention, as pointback pins the dark theme for its lightbox, with `data-theme="dark"`.
The pin needs no tool: both themes are still solved and certified, and the pin chooses which one the product shows.
A product may also name a default overlay or a default density for a surface; the viewer's choice still wins where the screen is theirs.

## The inputs

Anything not in this table is not a brand input, and `tools/build.py` refuses a brand seed that names anything else, an `hw-` token included.
A brand that names none of the vivid tier's seven inputs, from `brandHue` to `darkCard`, emits exactly what it emitted before they existed, byte for byte; that is how the three example brands stayed unchanged when the vivid tier landed.
The four type inputs after them hold the same way: a brand that names none of them emits the bytes it did before, and the house set is unchanged by the roster that feeds them.
`sunkenDepth` holds it too, and a brand that names it at the house's own step, 0.020 and 0.034, emits the bytes a brand that does not name it emits.

| input | range | default | what it moves |
|---|---|---|---|
| `accentHue` | 0 to 359 | 198 | the accent family and the chart rotation |
| `accentChroma` | at least 0.3 times the house anchors | 1.0 | the chroma of `hw-accent`, `hw-accent-hover` and `hw-accent-ring` |
| `accentLightness` | a lightness per theme | 0.515 and 0.619 | `hw-accent` and `hw-accent-hover`, in all four blocks |
| `quietChroma` | 0.3 to 1.0 times the house anchor | 1.0 | `hw-accent-quiet`, the selected-row fill |
| `ring` | `accent` or `ink` | the house ring | `hw-accent-ring` |
| `neutralHue` | 0 to 359 | the accent hue | all sixteen neutrals together |
| `neutralChroma` | at least 0 times the house anchors | 1.0 | all sixteen neutrals together |
| `shape` | `crisp` 2/3/6px, `house` 4/6/10px, `moulded` 4/7/12px, `soft` 6/8/14px | `house` | `hw-radius-sm`, `-md`, `-lg` |
| `iconStroke` | `1.5px`, `1.75px`, `2px` | `1.5px` | `hw-icon-stroke` |
| `display` | a face in the roster | Newsreader | `--hw-font-display` |
| `text` | a face in the roster | Public Sans | `--hw-font-sans`, held to the house x-height |
| `brandHue` | 0 to 359 | the accent hue | the hue of the [vivid tier](#the-vivid-tier)'s fills |
| `brandLightness` | a lightness per theme | none: naming it opens the tier | `hw-brand` and `hw-field` |
| `brandChroma` | an absolute chroma above 0, clipped by the sRGB gamut | none: named with `brandLightness` | `hw-brand` and `hw-field` |
| `primary` | `ink` or `brand` | `ink` | `hw-primary` and its states and label |
| `selection` | `accent` or `neutral` | `accent` | `hw-select` |
| `groundLightness` | a lightness per theme, 0.92 to 0.985 light, 0.13 to 0.22 dark | the house ground | [every colour of that theme](#ground-lightness) |
| `darkCard` | `house` or `step` | `house` | [the dark card step](#the-dark-card-step) |
| `mono` | a monospaced face in the roster | IBM Plex Mono | `--hw-font-mono` |
| `quote` | a face in the roster | none | `--hw-font-quote` and the `.hw-quote` class, held to the house x-height |
| `displayFrom` | `display-2` or `title-1` | `display-2` | whether `title-1` is set in the display face |
| `displayScale` | `0.9`, `1.0` or `1.25` | `1.0` | the sizes of `display-1` and `display-2`, to whole px |
| `sunkenDepth` | a step of lightness per theme, 0.020 to 0.08 light, 0.034 to 0.13 dark | the house step, 0.020 and 0.034 | [`hw-surface-sunken`, and every colour darker than it](#sunken-depth) |

The numeric bounds are pinned in `tools/build.py` rather than in the seed, so an edit to the seed cannot widen one.
The registers, the stroke weights and the roster live in the seed's `brand` block, and `tools/contrast.py` declares the registers and the weights again on its own, so a hand-edited radius or stroke in an emitted file is refused by the second instrument too.

### Accent chroma

The sRGB gamut is the only ceiling on it now.
The 1.3 times it replaced kept a brand accent under `hw-danger`'s chroma in light, and its own text called that "a principle nothing has tested": in dark it never held, pointback's shipped pencil sat at 0.12 against `hw-danger`'s 0.11, and the field median is C 0.194, which Todoist's accent (C 0.20) and Duolingo's (C 0.24) sit either side of.
What stops a loud accent reading as a state is the separation bars in [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to), measured on each element it paints, not a multiplier on its chroma.
The lower bound is the quiet end: quoth's slate sits at 0.35, C 0.028, under the 0.055 floor this book uses to count a colour as chromatic.

### Accent lightness

The house solves its accent to the lightness its 4.5:1 floor allows and no further.
A brand may set its own, which is how the two products that already ship an accent keep theirs: papertrace's seal at `oklch(0.42 0.10 250)` and pointback's pencil at `oklch(0.78 0.12 230)` in dark.
Deeper than the floor in light and lighter in dark costs nothing in contrast, because the floor is a minimum.

The input moves the ink and its hover by the brand's offset from the house accent **in all four blocks**, the two `prefers-contrast: more` tiers included.
Moved in the default blocks alone, it does not survive the raised floors: every ink is re-solved toward the same 7:1 lightness, so a deep umber at hue 70 lands 10.1 from `hw-warning` under more contrast in dark while clearing it by 16.0 in the default dark theme.
Carried into the tier, the same umber keeps 14.3.

A lightness the floors would move is refused rather than re-solved, with the value the floor permits, because an input the build silently discards is a claim the file does not keep:

```text
FAIL  accentLightness light 0.6 does not clear hw-accent's floors at hue 250; the nearest
      lightness that does is 0.5234 (12-brand.md#accent-lightness)
```

### The focus ring

By default the ring is the house ring, solved to 3:1 against the surface closest to it, at the brand's accent chroma.
A quiet accent makes a quiet ring, and a quiet ring stops reading as focus: at 0.6 times the accent chroma, quoth's ring sits 7.4 from `hw-border-strong`, a control's own edge, in dark, and renders as a second grey outline.
So the ring is held **at least 14 CIEDE2000 from `hw-border-strong`**, and a brand whose ring cannot clear that takes one of two rings instead:

- **`ink`**, the text ink. The most visible ring measured, 36.6 from the border in light, and it leaves hue to the states. quoth takes it.
- **`accent`**, the accent ink itself. This is the ring a product draws when its one colour is its focus colour, and it is what pointback ships: its chrome sets `:focus-visible` to its pencil.

The bar costs the house's own chroma a band of the wheel: at the house anchors, hues 220 to 264 refuse on it, and a brand there takes more chroma, the accent ring or the ink ring.
The ring is also held 17 from `hw-danger`, the error border, which [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) owns with the other accent bars.

### Neutral hue and chroma

This is where a product's warmth or coolness lives, and it moves all sixteen neutrals together, so a warm ground never sits under cool text.
A tinted ground costs no contrast: the solver re-solves every ink against the ground it actually sits on, and all 198 certified pairs held at 1, 2, 4 and 6 times the house chroma at hue 75, and at 0 and 4 times across the brand corners `tests/hue_sweep.py` builds.
What a tinted ground does cost is its states. A warm ground swallows the warning fill first:

| neutral hue 75 at | light ground | warning fill from the ground | reads as |
|---|---|---:|---|
| 1 times | `#F9F7F6` | 9.8 | paper |
| 2 times | `#FAF7F3` | 8.5 | paper |
| 4 times | `#FDF7EF` | 6.7 | paper |
| 6 times | `#FEF7ED` | 5.9 | cream in light, brown in dark |

Every state's quiet fill is held **at least 6 CIEDE2000 from `hw-ground`** in every block, and that bar is the rule.
`neutralChroma` used to stop at 4.0 as well, and the ceiling refused nothing the bar did not: with it lifted and every other refusal untouched, a violet ground at 5.5 times built and certified, while papertrace's cream at 6.7 was still refused by the bar, its warning fill 5.0 from the ground.
So the ceiling is gone, and a state fill that a tinted ground has swallowed **takes chroma before the build refuses it**, at the lightness it already has, until it clears 6 with 0.2 to spare: papertrace's cream at 6.7 times lifts `hw-warning-quiet` from C 0.035 to 0.0413, and both instruments certify the set.
A fill that no chroma in gamut can lift is still refused.
`hw-surface` keeps chroma 0 in light at every multiplier, so data never sits on the tint.
[10-color.md](10-color.md#why-the-ground-is-neutral) says why the house's own ground stays neutral; a brand may warm or cool its ground, and the house does not.

### Shape and stroke

Four registers rather than a free number, because a 1px radius change is invisible and a free number invites one.
`crisp` is the 3px of Radix and the 4px of Vercel and Stripe; `soft` is the 8px input and 12px card the field clusters on ([30-space-radius-elevation.md](30-space-radius-elevation.md#radius)); `moulded`, 4/7/12, is a device's injection-moulded corner, the register quoth's Field identity asks for.
7px is off the 4px unit, and that is allowed: the unit governs space and size, and radius is outside its scope ([32-rhythm.md](32-rhythm.md)).
Every register keeps the two rules that give radius its job: three sizes bound to three roles, and a child never larger than its parent.
The stroke weights are the two the capture measured, 1.5px on 8 sites and 2px on 12, and the step between.

Neither moves a screen much: measured on a rendered product screen, a full register change moves its colour mass 0.03 CIEDE2000 at a glance and a stroke step 0.03, where moving the accent to 342 moves it 3.7 and warming the ground to twice the house chroma 2.0.
They are inputs because a product has a shape, and they carry no weight in telling two products apart.

### Faces

A face is a roster entry with its delivery, and [20-type.md](20-type.md#a-brands-faces) owns the roster, the delivery rule, the four roles a brand fills from it, and the x-height the text and quote faces are held to.

## The vivid tier

A brand that names `brandLightness` and `brandChroma` opens the vivid tier: twelve tokens the build appends to its copy of the seed and solves with everything else, and `tools/contrast.py` declares and certifies on its own.
"Vivid" is carried by fills, fields, grounds and art, none of which is text, so raising the text floors under `prefers-contrast: more` does not dull them.

| token | solved how | floor |
|---|---|---|
| `hw-brand` | the brand's fill at `brandHue`, `brandLightness` and `brandChroma`, clipped to sRGB | none of its own |
| `hw-brand-hover`, `hw-brand-active` | 0.03 and 0.06 of lightness toward the label | the label's floor holds on each |
| `hw-on-brand` | `hw-text` or `hw-ink-text`, whichever clears higher; if neither clears, `hw-brand` moves away from it | 4.5:1, 7:1 under more contrast |
| `hw-brand-quiet` | the brand hue at L 0.94 light, 0.27 dark, C 0.05 at most | `hw-text` at 7:1 on it |
| `hw-field`, `hw-on-field` | a large vivid area, solved as the brand fill with its own label | 4.5:1, 7:1 under more contrast |
| `hw-select` | the selected-row fill: a neutral step past `hw-surface-active` with `selection: neutral`, `hw-accent-quiet`'s value with `selection: accent` | `hw-text` at 7:1 on it |
| `hw-primary`, `hw-primary-hover`, `hw-primary-active`, `hw-on-primary` | copies of the ink family, or of the brand's, per `primary` | the label's 4.5:1 on each |

`hw-accent` stays what it was, the text-safe ink, and keeps its four jobs.
The fill has no floor of its own on purpose: a butter key is not text, and a label is what a reader reads.
When a label cannot clear, the fill moves rather than the label, because the fill is the brand's and the label is the reader's.
`tools/contrast.py` checks the forms as well as the ratios: a set that declares one of the twelve declares all twelve, each label is exactly `hw-text` or `hw-ink-text`, and the four primary tokens copy one family whole.

**A field is never under data.** It carries display copy and one action, or stages one of the product's own objects ([56-asset-placement.md](56-asset-placement.md#a-field-as-a-stage)), in `hw-on-field`, and no `hw-text-secondary` is ever placed on it.

**`primary: brand` makes the loudest control the brand's.** The key is then held 14 CIEDE2000 from `hw-danger`, in all four blocks, because a destructive confirm is the one state drawn as a filled button ([10-color.md](10-color.md#the-three-bars-the-accent-is-held-to)).
A coral at hue 30, L 0.72, C 0.16 as the primary sits 6.5 from the dark `hw-danger` and is refused; the same coral with `primary: ink` paints no button and builds.

**`selection: neutral` takes the selected row off the wheel.** The fill bar exists because the selected row is the one accent element with no second channel; a neutral row is not a hue, so it cannot read as a state, and the bar does not hold it.
Linear, Notion and Things select with a neutral fill.

### Ground lightness

`groundLightness` sets `hw-ground` per theme, and slides **every colour of that theme** by the ground's own offset before the solver runs, except the ink family, a control and its label solved to each other, and the vivid fills, whose lightness is the brand's input.
Sliding the ground alone was tried first and failed twice on quoth's Field identity: the inks re-solved by different amounts and the text ladder closed to 0.0587 against the 0.06 it keeps, and the semantics climbed onto the chart series, which do not re-solve, to 3.8 against their 8.0.
Slid together, every relationship the house measured is kept and the solver re-solves only the residue.

The bounds are the solver's own refusals, measured on Field's inputs: at 0.91 in light the raised-contrast chart ramp closes, two of its series falling under the 8.0 they keep, and 0.92 builds; at 0.12 in dark the text ladder closes, and 0.13 builds.
The light ceiling is the house surface's own white less the 0.015 that still reads as a step; the dark ceiling, 0.22, admits a ground the dark card step then refuses, because the step's own lift takes the chart ramp past white: with the step, Field builds at 0.17 and is refused at 0.18.
Each of quoth's two grounds builds on its own, its putty at 0.925 (D-039 in quoth's record) and its paper at 0.972.
D-055 asks for both at once, the paper pane inside the putty chassis, and the chassis is not a second ground: it is the sunken surface, which [sunken depth](#sunken-depth) sets.

### Sunken depth

`sunkenDepth` sets how far `hw-surface-sunken` sits under `hw-ground`, per theme, as a step of lightness.
It exists for a pane set in a deeper chassis: D-055 puts Field's content on paper at L 0.972 inside a putty chassis at L 0.925 that carries the rail and the window chrome, 1.151:1 under the pane.
Without it the deepest surface a brand has is the house's own step, 0.020 in light and 0.034 in dark, and Field's chassis sat at L 0.952, 1.061:1 under its pane.

The input moves the well, and **every colour darker than the well moves down with it**, for the reason [ground lightness](#ground-lightness) gives, except the ink family and the vivid fills.
Two narrower rules were tried first on Field, and both failed.
Moving the well alone re-solved `hw-text-muted` onto it and closed it on `hw-text-secondary` to 0.0487, against the 0.06 the ladder keeps, and left `hw-select` at L 0.924, 0.001 under the chassis: a selected rail row nobody could see.
Moving the well and the inks certified on it took `hw-text-muted` to 4.533:1 on `hw-border`, a pair the ruled ground refuses, because the rule stayed where it was.
Moved together, the selected row sits 1.090:1 and 2.0 CIEDE2000 under the chassis, and `hw-text-muted` on `hw-border` is 4.165:1, still refused.
In dark nothing is drawn darker than the well, so a deeper dark well moves nothing else.

The bounds are the solver's own refusals, measured on Field's inputs a thousandth at a time.
In light a well 0.080 deep builds, and at 0.081 the raised-contrast chart ramp closes, `hw-chart-4` falling under the 8.0 it keeps from `hw-chart-6`.
That is Field's ceiling, and the solver still refuses past its own on other grounds: under putty at 0.925 a well 0.030 deep builds and one 0.040 deep is refused on the same pair.
In dark every depth builds, down to a black well, so the ceiling is 0.13, the lowest dark ground, where every well the bound admits sits at or above L 0.
The floor is the house's own step, so the input only ever deepens a well.

Everything on the well is re-measured at the depth the file paints.
`tools/contrast.py` measures its 17 pairs, text and non-text, in all four blocks, and prints the well's step with its worst pair of each kind; on Field:

```text
the well light      L 0.9250, 1.151:1 under the ground; 17 pairs on it, worst text 4.805 --hw-text-muted, worst non-text 3.098 --hw-text-disabled
the well dark       L 0.1230, 1.059:1 under the ground; 17 pairs on it, worst text 7.110 --hw-text-muted, worst non-text 4.728 --hw-text-disabled
the well light-more L 0.9250, 1.151:1 under the ground; 17 pairs on it, worst text 7.074 --hw-text-muted, worst non-text 4.531 --hw-chart-1
the well dark-more  L 0.1230, 1.059:1 under the ground; 17 pairs on it, worst text 10.298 --hw-text-muted, worst non-text 5.915 --hw-text-disabled
```

The chart ramp moves down with the well, 0.027 in light, and is re-measured on the chassis: its six fills clear 3:1 on L 0.925 with 3.194 at worst, `hw-chart-5`, and 4.5:1 under more contrast with 4.531, `hw-chart-1`, and its closest pair sits 12.5 apart in light and 9.1 under more contrast, against the 8.0 it keeps.

**The dark chassis.**
D-055 left it to be measured against D-040's floor, and the floor cannot be met: a pane at L 0.17 sits 1.098:1 over pure black, under D-040's 1.2:1 at every chassis beneath it.
So Field's dark chassis takes the light chassis's own step of lightness, 0.047: L 0.123, `#070603` under the dark pane `#110F09`, 1.059:1 (1.058 at 8-bit) and 1.7 CIEDE2000, where the light chassis sits 3.2.
That value was accepted in review on 2026-09-29, with the rule that goes with it: **in dark the pane's edge is carried by a border, as D-040 carries a card's**, because the fill step alone cannot be.
`hw-border` sits 1.806:1 over the dark chassis and 1.705:1 over the dark pane, where in light it sits 1.154:1 over the chassis and 1.328:1 over the pane.

### The dark card step

`darkCard: step` is quoth's D-040 made a floor: in the dark theme a card is told from the page by a lighter surface and a visible border, never a shadow.
The build lifts `hw-surface`, and every surface and colour drawn above the ground with it, by the smallest amount that puts **`hw-surface` 1.2:1 over `hw-ground`**, then lifts `hw-border` until it sits **1.2:1 over the lifted surface**, each on the float value and at 8-bit.
1.2 is the smallest round step above every dark card step recorded as failing to separate, 1.094, 1.107, 1.111 and 1.116, and above the house's own raised step, 1.169.
The emitted header says `Dark cards: stepped`, and `tools/contrast.py` then holds both steps in both dark blocks against its own 1.2; `--check` refuses a header that drifts from what the seed builds.
The house's own dark cards keep their step, 1.076, with the border and no shadow, as [30-space-radius-elevation.md](30-space-radius-elevation.md) has them.

The step is narrow, and the accent decides where it builds.
On the house set its lift is 0.0547, and it slides the chart ramp's light series from L 0.88 to 0.935, where the gamut leaves most hues too little chroma to tell two series apart: at the house accent, 198, `hw-chart-2` sits 5.2 CIEDE2000 from `hw-chart-4` in dark, against the 8.0 they keep.
With the ink ring the step builds at accent hues 245 to 265, 21 of 360, and Field's 255 is inside that arc; under the house ring it builds at none, because the lifted `hw-border-strong` also closes on the accent ring.
`tests/hue_sweep.py` records that arc and fails if it moves.

### Identities are not one style

The owner's rule, recorded 2026-09-28: **an identity is not bound to fixed specifics.**
Mixing styles across products, and within one product, is allowed wherever it serves the experience, under the contrast floors.
A product may pair a grotesque with a hand, a flat fill with a drawn scribble, an engraving in its hero with in-house drawings of real controls on its setup steps.
Illustration and art styles may vary, and they are not one: [55-iconography.md](55-iconography.md#illustration) says what every style is still held to, and [56-asset-placement.md](56-asset-placement.md) where each may and may not go.
What does not vary is the floor: every colour a style brings is solved and certified, and every pair it puts text on clears its bar.

### quoth's Field identity, as the house solves it

`tests/fixtures/field/` is quoth's Field identity (D-039) as a brand seed, and the fixture every vivid-tier input is certified against on every change:

```json
{"accentHue": 255, "accentChroma": 0.35, "quietChroma": 0.4, "ring": "ink",
 "neutralHue": 95, "neutralChroma": 2.0, "shape": "moulded", "iconStroke": "1.5px",
 "brandHue": 100,
 "brandLightness": {"light": 0.8844, "dark": 0.8844}, "brandChroma": 0.1838,
 "primary": "brand", "selection": "neutral",
 "groundLightness": {"light": 0.972, "dark": 0.17}, "sunkenDepth": {"light": 0.047, "dark": 0.047},
 "darkCard": "step",
 "display": "Archivo Expanded", "text": "Archivo", "mono": "Martian Mono", "displayFrom": "title-1"}
```

It solves to the sports-yellow key `#F6DA02`, C 0.1836 where the seed asks 0.1838, because the gamut clips it, one blue step off the decided `#F6DA00`, with an ink label at 12.29:1 in light and 14.09:1 in dark; a paper pane `#F7F6F1` in a putty chassis `#E7E6E2`; a dark ground `#110F09` in a chassis `#070603`, with its cards at 1.23:1 over it; and every certified pair clears: `tools/contrast.py` checks 434 on it where it checks 398 on the house set, and the 36 more are the vivid tier's.
It is not quoth's shipped seed.
quoth owns that copy, adopts Field in its own task, and `examples/quoth/` takes the adopted seed then.
Its faces are D-039's: Archivo at 125% width for `title-1` and the display steps, Archivo at its normal width for text, and Martian Mono as its mono, which sets the spoken and typed lines, the labels in lowercase (D-054) and the numbers ([20-type.md](20-type.md#a-brands-faces)).
It names no `quote`, because the face its spoken line is set in is already its mono.

## The bars every brand is held to

Every brand is held to every house floor, in all four blocks, on the float value and at 8-bit.
On top of the floors, both instruments hold the painted distances below, in CIEDE2000 on the 8-bit value a display receives, in all four blocks:

| what | bar | owned by |
|---|---:|---|
| the primary fill, `hw-primary` or `hw-ink`, from `hw-danger` | 14 | [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) |
| the selected-row fill, `hw-select` or `hw-accent-quiet`, from each state's quiet fill, unless it is neutral | 5 | [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) |
| the focus ring from `hw-danger` | 17 | [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) |
| the focus ring from `hw-border-strong` | 14 | [the focus ring](#the-focus-ring) |
| each state's quiet fill from `hw-ground` | 6 | [neutral hue and chroma](#neutral-hue-and-chroma) |
| a vivid label on its fill | 4.5:1, 7:1 under more contrast | [the vivid tier](#the-vivid-tier) |
| `hw-surface` over `hw-ground`, and `hw-border` over `hw-surface`, in dark, with `darkCard: step` | 1.2:1 | [the dark card step](#the-dark-card-step) |

The accent ink is no longer held to the states; `tools/contrast.py` reports its distance and does not refuse it ([10-color.md](10-color.md#the-three-bars-the-accent-is-held-to)).

The chart ramp keeps its own bar, 8.0 in oklab distance times 100 from each semantic and between series, and a product's own colour keeps 14 CIEDE2000 from each state and 5.0 in hue and chroma from each state and the accent ([95-extending.md](95-extending.md#how-a-product-colour-is-held-apart)).

## Building a brand

```bash
python3 tools/build.py --brand examples/papertrace/brand.seed.json    # writes examples/papertrace/tokens/
python3 tools/contrast.py examples/papertrace/tokens/tokens.css         # certify it independently
python3 tools/export.py examples/papertrace                             # the five exports, per brand
python3 tools/build.py --brand examples/quoth/brand.seed.json --extend examples/quoth/quoth.seed.json
```

The build checks every input against its bound before anything is solved, then writes `tokens/tokens.css` and `tokens/tokens.json` beside the brand seed.
The header of the emitted file names the brand, `Brand: papertrace, from examples/papertrace/brand.seed.json.`, which is how `tools/contrast.py` tells the house file, whose ratios the book publishes, from a brand's, whose ratios it does not.
`--extend` composes with `--brand`: a product's own colour is solved against its brand's set, not the house's, because the surfaces and the accent it must stay clear of are its brand's.
CI builds, certifies and exports every `examples/*/brand.seed.json` on every change.

## Telling brands apart

`tools/distinct.py` reads two or more emitted files and reports, per pair, the CIEDE2000 between their grounds, accents, selected fills and rings in each theme, and whether their display and text faces differ:

```text
pair                            ground      accent        fill        ring   display  text   (CIEDE2000 light/dark)
papertrace / pointback       6.3/6.6     9.6/8.6     5.0/5.0    20.5/29.7    differ  differ
pointback / quoth            1.5/2.1    13.4/21.6    6.8/6.1    23.2/22.3    differ  differ
```

It is a report, and it refuses one case only: a pair whose every one of those colours sits under 2.3, the CIELAB just-noticeable difference, in both themes, with the same two faces, which is one brand built twice.

A weighted score with a pass bar was proposed and tested against rendered screens before this shipped, and it failed both ways.
It passed a pair with a different serif, crisp corners and a 2px stroke, which renders as the house with another serif, 0.64 CIEDE2000 from it at a glance.
It refused the house against accent 342 on a warm ground, which renders as the most different screen measured, 3.95 from it.
Shape and stroke together move 0.06 of a screen's colour mass, and the score weighted them as heavily as the accent.
The principle it was built on, that identity never rests on colour alone, needs no score: a product's name is on its screen.

Whether two brands read as two is a render looked at, not a number, so rendering the examples in a browser is a release step ([AGENTS.md](../AGENTS.md#releasing)).

## The three brands

Decided by the system's owner on 2026-09-21, as the constraint audit re-derived them.
Values are the emitted light and dark `hw-accent` and `hw-ground`; the bars are each product's worst over all four blocks, as `tools/contrast.py` reports them, the ink column now a reported distance rather than a bar.
None of the three names a vivid-tier input yet, so the vivid tier left every value here unchanged.

| brand | accent | ground | ink | fill | ring from danger | ring from border | fill from ground |
|---|---|---|---:|---:|---:|---:|---:|
| house | `#1D7578` / `#26979B` | `#F6F8F8` / `#090C0C` | 18.7 | 8.2 | 44.6 | 16.0 | 10.1 |
| quoth | `#5D6978` / `#7A899C` | `#F6F8FB` / `#090C0F` | 28.5 | 12.4 | 29.9 | 25.3 | 10.0 |
| papertrace | `#194F81` / `#7DBDFE` | `#FBF7F1` / `#0F0B04` | 34.1 | 14.8 | 39.1 | 25.7 | 7.7 |
| pointback | `#015E7D` / `#59C5F5` | `#F4F8FE` / `#070C13` | 30.8 | 14.1 | 42.0 | 22.5 | 11.0 |

### quoth

**The quiet instrument: monochrome, and the only colour it paints is the open microphone.**
Accent 255 at 0.35 times the house chroma, a slate ink; selected fill at 0.4; the ink focus ring; neutrals at 255 and 1.5 times; `soft`; Bricolage Grotesque for display and Instrument Sans for text, the face quoth already ships.
When the only colour on the screen means the microphone is open, colour performs quoth's privacy claim rather than decorating it.
Its ground is cool, because the owner rejected the brown and orange of its earlier palette.
`--quoth-live` is re-solved against this set, not the house's, and [95-extending.md](95-extending.md#the-worked-example-quoths-live-colour) has its values.

### papertrace

**Blue-black ink on warm paper.**
The seal keeps the blue it ships, hue 250 at its shipped depth, L 0.42 in light and 0.78 in dark, at 1.27 times the chroma; the paper turns warm, neutrals at 85 and 3.0 times, `#FBF7F1`; selected fill at 0.6; `crisp`, because paper has corners; the system serif for display and text, because the report is set as a document.
With a warm ground under it the seal no longer has to leave 250 to be told from quoth and pointback, so "a shared passage takes the seal's blue" keeps its colour.

### pointback

**The pencil in the margin, as it ships.**
Accent 230 at 1.25 times with its own lightness, `oklch(0.78 0.12 230)` in dark, which is also its focus ring; neutrals at 260 and 3.0 times; `house` corners; a 2px stroke, the weight of its pencil rule; the system stack for display and text; the dark theme pinned.
Its shipped text is warm on a cool ink, and one `neutralHue` cannot express that, so it stays cool: a known difference from what ships.

### Reserved: treadling, foliot and gates

None of the three has an interface today, so none has a brand seed.
A slot is reserved rather than built: when one of them gets a surface, its brand is decided then, and it must still clear every bar above against the brands that exist.

## What stays the house's

What makes two of these recognisably from one maker is everything a brand seed cannot reach, and the list is long on purpose:

- **The loudest control is ink by default**, and a brand makes it its own only through `primary: brand`, solved and held off `hw-danger`. Until the vivid tier every primary button in the fleet was the same near-black.
- **The accent does four jobs and no others**, and the three states are the same green, amber and red everywhere.
- **One mono face per product**, so every hash, run id and timestamp on a screen is set identically; the house's is IBM Plex Mono, and a brand may name another monospaced face from the roster where the mono is its identity, as Field's is.
- **One rhythm**: the 4px unit, the ten steps, the 44px row, the 32px control, the two densities.
- **One behaviour**: nine states, one focus geometry, one keyboard contract, one motion. Every product answers at 150ms on the same curve.
- **Border before shadow, one hairline, nothing floats that cannot be dismissed.**
- **One icon set and one alignment rule**, at whichever of three weights.
- **One voice**: sentence case, "Revoke key" then "Key revoked", numbers with their unit.
- **One proof.** Every brand is solved by the same build and certified by the same second instrument, and says so in its file header.

Put two products in greyscale with their names covered, and they should still differ in face and shape, and still obviously be siblings.

## Declined as inputs

| candidate | why not |
|---|---|
| motion | the house curves are identity: three alternative ease-outs differ from the house curve by at most 1.5px on an 8px move. Up to four named large moments may live in a product's namespace ([40-motion.md](40-motion.md#a-products-own-moments)) |
| the type scale below `title-1` | every size there is load-bearing for density, from the 44px row down |
| a ring chroma of its own | the accent and ink rings cover every brand that fails the border bar |
| elevation | 73 of 75 sampled elements carry no shadow; border-first is identity |
| surface texture | a product may have one, as a tier rather than an input: a signature ground is a product token held to the two-token pattern rule ([75-spec-sheet.md](75-spec-sheet.md)) |
| a figurative illustration set | brings its palette through the product's namespace, and its SVG carries no literal colour ([55-iconography.md](55-iconography.md#illustration)) |
| voice | the house rules are invariant; a product's register is its noun glossary ([25-content.md](25-content.md)) |
| a mark | a mark is a commission ([00-brand-book.md](00-brand-book.md#the-mark)) |

A brand is chosen once and solved every time.

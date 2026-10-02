# Brand

A product's identity is a **brand file**, `ramps/brands/<product>.json`: a neutral, five to eight named hues, and optionally a shape register, an icon stroke and a face per family.
`tools/ramps.py` builds it into twelve-step ramps with the same code as the house's own, `ramps/roles.css` names the same steps for every brand, and `tools/contrast.py` certifies the result as the second instrument.
Every brand ships the house's token names and clears the house's floors.
A brand is a rebuild, never a hand-pick, and "never redefine an `hw-` token" does not change by a word.

## Why a brand is more than an accent hue

Until 2026-09-21 the rule was "the accent hue, and nothing else", and it could not carry the products this book serves.
Every product was the house with a different link colour.
The system's owner gave the direction the same day: each product needs its own distinction rather than a sampler hue.

The first answer was a solver with eleven inputs, then twenty-three: accent chroma and lightness per theme, a quiet-fill multiplier, a ring choice, ground lightness, a sunken depth, a dark card step, a vivid tier of twelve tokens, and four type inputs.
Each input was bounded and certified, and the house design review of 2026-10-02 found the solver cost more than it returned: 1,978 lines solving each colour from 23 inputs, with bounds that lived in the code, and 205 of 360 accent hues refused, so "a product cannot take hue 150" held because the solver had no room rather than because a product needed it.
The ramps replaced it.
A brand now names hues and the build gives every hue the same twelve steps, so a role is a choice of step, never a new solve, and an input that only moved a step a few thousandths has nothing left to move.
Every one of the 360 hues builds; what `tools/contrast.py` still refuses is an accent whose selected-row fill reads as a state, 27 of every fifth hue's 72, from 0 to 85 and 130 to 170.

What the first rule got right survives whole.
A product stylesheet that sets `--hw-radius-md: 8px` is still a fork wearing the system's name, because nobody built that value and nobody certified it.
The safe input was never "a hue"; it is **an input to the build**.

## Who chooses what, and when

| layer | who chooses | when | mechanism |
|---|---|---|---|
| foundations | the house | once | `ramps/brands/house.json`, `ramps/roles.css`, `ramps/scales.css`, `ramps/roster.json`, and every refusal in `tools/ramps.py` and `tools/contrast.py` |
| brand | the product | once, at build time | a brand file, built by `tools/ramps.py` into the same token names |
| viewer | the person | at run time | `data-theme`, `data-density`, `data-text-size`, `prefers-contrast`, `prefers-reduced-motion`, `forced-colors` |
| product namespace | the product | as a concept arises | a hue of its own in the brand file, and `--quoth-live` and its kind naming its steps ([below](#a-colour-of-the-products-own)) |

A product may pin a viewer setting where its surface has a convention, as pointback pins the dark theme for its lightbox, with `data-theme="dark"`.
The pin needs no tool: both themes are still built and certified, and the pin chooses which one the product shows.
A product may also name a default density for a surface; the viewer's choice still wins where the screen is theirs.

## The inputs

Anything not in this table is not a brand input, and `tools/ramps.py` refuses a brand file that names anything else, an `hw-` token included.
An input is a hue or a top-level key other than `note`, and the house and the three example brands name eight or nine each.

| key | what it takes | default | what it moves |
|---|---|---|---|
| `neutral` | `{"hue", "chroma"}`, chroma 0 to 0.4 | none: every brand names it | the gray ramp: every ground, surface, line and text role |
| `accent`, under `hues` | `{"hue", "chroma"}`, and optionally `solid`, a lightness per theme for step 9 | none | links, the selected row, the focus ring and the accent solid |
| `mark`, under `hues` | the same | none | the highlighter, the house signature |
| `red`, `amber` and `green`, under `hues` | the same | none | the three states, and proof marks |
| any other name, up to eight hues in all | the same | none | a ramp of the product's own, such as quoth's `live` |
| `shape` | `crisp` 2/3/6px, `house` 4/6/10px, `moulded` 4/7/12px, `soft` 6/8/14px | `house` | `--hw-radius-sm`, `-md`, `-lg` |
| `iconStroke` | `1.5px`, `1.75px`, `2px` | `1.5px` | `--hw-icon-stroke` |
| `faces` | a roster face per family: `sans`, `display`, `read`, `mono` | Archivo, Archivo, Literata, IBM Plex Mono | `--hw-font-sans`, `--hw-font-display` and its width, `--hw-font-read`, `--hw-font-mono` |
| `note` | a sentence saying what the identity is and who decided it | none | nothing; it is the record |

The six chart series ramps (teal, blue, violet, pink, olive, sky) are the house's in every brand and are not inputs, so a chart reads the same series order in every product.
The registers, the strokes and the faces live in `ramps/roster.json`, which `tools/ramps.py` validates, and `tools/contrast.py` declares the registers, the strokes and the display widths again on its own, so a hand-edited radius, stroke or width in an emitted file is refused by the second instrument too.

Every hue gets the same twelve steps, each with its floor, which [10-color.md](10-color.md#ramps-steps-and-floors) owns.

### Shape and stroke

Four registers rather than a free number, because a 1px radius change is invisible and a free number invites one.
`crisp` is the 3px of Radix and the 4px of Vercel and Stripe; `soft`, 6/8/14, is the rounder register, an 8px input; `moulded`, 4/7/12, is a device's injection-moulded corner, the register quoth's Field identity asks for.
7px is off the 4px unit, and that is allowed: the unit governs space and size, and radius is outside its scope ([30-space.md](30-space.md#the-unit)).
Every register keeps the two rules that give radius its job: three sizes bound to three roles, and a child never larger than its parent.
The stroke weights are the two the capture measured, 1.5px on 8 sites and 2px on 12, and the step between.

Neither moves a screen much: measured on a rendered product screen, a full register change moves its colour mass 0.03 CIEDE2000 at a glance and a stroke step 0.03, where moving the accent to 342 moves it 3.7.
They are inputs because a product has a shape, and they carry no weight in telling two products apart.

### Faces

A face is a roster entry with its delivery, and [20-type.md](20-type.md#a-brands-faces) owns the roster, the delivery rule, the four families a brand fills from it, and the x-height a text face is held to.
A face's width is part of it: Archivo Expanded is Archivo at `font-stretch: 125%`, so the build writes the display face's width as `--hw-font-display-stretch` beside it, and a headline sets both.

### Neutral hue and chroma

This is where a product's warmth or coolness lives, and it moves the whole gray ramp together, so a warm ground never sits under cool text.
A tinted ground costs no contrast: steps 8, 11 and 12 are solved against the grounds they actually sit on.
What a tinted ground can cost is its states, so every state's quiet fill is held **at least 6 CIEDE2000 from `--hw-bg`** in every block; the four brands clear it with 9.29 at worst, quoth's warm putty in light.
`--hw-surface` stays white in light whatever the neutral, so data never sits on the tint.
[10-color.md](10-color.md#roles) says why the house's own ground stays near neutral; a brand may warm or cool its ground further, and the house does not.

### The focus ring

The ring is accent step 8, solved to 3:1 against every ground it can sit on.
A quiet accent makes a quiet ring, and a quiet ring stops reading as focus, so the ring is held **at least 14 CIEDE2000 from `--hw-line-strong`**, a control's own edge, and **17 from `--hw-danger`**, the error border, in every block.
Under `prefers-contrast: more` the ring becomes the text ink in light and accent step 11 in dark, the two that clear the raised bar.
The four brands clear the edge bar with 14.75 at worst, pointback's pencil in dark.

### The vivid tier

The solver's vivid tier, twelve tokens for a brand fill, a field and a brand primary, is retired.
What it existed for is a step-9 solid with a named lightness: quoth's sports-yellow key is accent step 9 at L 0.90 in light and 0.88 in dark, `#FCDF01` and `#F4D908`, with an ink label, and the house's mark is the same yellow.
**The loudest control is ink in every brand.**
`--hw-ink` is the primary, and no brand input moves it.
The tier's brand primary retired with it; quoth's vendored copy still carries `--hw-primary`, and its migration maps it onto the accent solid or onto ink.
The accent solid, `--hw-accent`, is the one place a brand's key fills a control: a brand button, a selected switch, a stage.

### The dark card step

quoth's D-040 asks for dark cards told from the page by a lighter surface at 1.2:1 and a visible border.
The roles are the same for every brand, and the dark surface is gray step 2 over step 1, 1.054:1, with the border at 1.526:1 over the surface carrying the edge, as [30-space.md](30-space.md#elevation) has it.
That is under D-040's step, and it is a stated gap rather than a refusal: a brand cannot yet move a role, and a per-brand surface step would be the first input that does.

### Sunken depth

D-055 puts Field's content on paper inside a deeper putty chassis.
The chassis is `--hw-bg-subtle`, gray step 2 in light and step 1 lowered 0.03 in dark, the same for every brand: 1.051:1 under the ground in light, where Field's decided chassis sat 1.151:1 under its pane.
The solver's `sunkenDepth` input is retired with the rest, so the deeper chassis is the same stated gap as the dark card step.

### Identities are not one style

The owner's rule, recorded 2026-09-28: **an identity is not bound to fixed specifics.**
Mixing styles across products, and within one product, is allowed wherever it serves the experience, under the contrast floors.
A product may pair a grotesque with a hand, a flat fill with a drawn scribble, an engraving in its hero with in-house drawings of real controls on its setup steps.
Illustration and art styles may vary, and they are not one: [00-brand-book.md](00-brand-book.md#icons-and-art) says what every style is still held to and where art may not go.
What does not vary is the floor: every colour a style brings is built and certified, and every pair it puts text on clears its bar.

## The bars every brand is held to

Every brand is held to every step floor and every role's floor, in light, dark and both under `prefers-contrast: more`, on the float value and at 8-bit.
On top of the floors, `tools/contrast.py` holds the painted distances below, in CIEDE2000 on the 8-bit value a display receives, in all four blocks:

| what | bar | the four brands at worst |
|---|---:|---:|
| the selected-row fill, `--hw-accent-fill`, from each state's fill | 5 | 10.29, quoth |
| the primary, `--hw-ink`, from `--hw-danger-solid` | 14 | 21.73, house |
| the focus ring from `--hw-danger` | 17 | 21.73, house |
| the focus ring from `--hw-line-strong` | 14 | 14.75, pointback |
| each state's fill from `--hw-bg` | 6 | 9.29, quoth |
| each status word, `--hw-danger`, `--hw-warning`, `--hw-success`, `--hw-delete` and `--hw-insert`, from `--hw-text` | 14 | 24.71, quoth |
| each chart series from every other series and from each state | 14 | 16.42 |

The accent text is not held to the states; `tools/contrast.py` reports its distance and does not refuse it, because every state carries a glyph and a word.
A hue of the brand's own is reported against the three state ramps and never refused: quoth's `live` sits 11.01 from amber at step 11, and [the worked example](#the-worked-example-quoths-live-colour) says what that costs.

## Building a brand

```bash
python3 tools/ramps.py                                       # every ramps/brands/*.json -> ramps/tokens/
python3 tools/contrast.py ramps/tokens/papertrace.tokens.css   # certify it independently
python3 tools/export.py examples/papertrace                    # the five exports, per brand
```

The build checks every key against its bound before anything is solved, then writes `ramps/tokens/<name>.tokens.css`: the brand's faces, width, radii and stroke first, then twelve steps per hue per theme.
`tools/export.py examples/<name>` composes that file with `ramps/roles.css` and `ramps/scales.css` into the brand's `exports/`.
CI builds, certifies and exports every brand on every change.

## Telling brands apart

`tools/distinct.py` reads the brands' ramps files and reports, per pair, the CIEDE2000 between their grounds, accent text, selected fills and rings in each theme, and whether their display and text faces differ:

```text
pair                            ground      accent        fill        ring   display  text   (CIEDE2000 light/dark)
house / papertrace           3.1/1.8     4.5/4.2     1.9/4.7     3.9/4.1     differ  differ
house / pointback            4.1/4.3    12.8/14.0    6.6/10.4   13.1/13.0    same    same
house / quoth                1.4/0.9    54.6/58.0   24.9/25.9   55.5/53.2    differ  same
papertrace / pointback       1.0/2.8     9.3/9.6     4.7/5.8     9.1/9.1     differ  differ
papertrace / quoth           4.6/2.5    54.2/58.8   24.5/23.7   55.9/53.0    differ  differ
pointback / quoth            5.6/5.2    44.6/51.5   23.2/21.1   49.1/45.9    differ  same
```

It is a report, and it refuses one case only: a pair whose every one of those colours sits under 2.3, the CIELAB just-noticeable difference, in both themes, with the same two faces, which is one brand built twice.
house and papertrace sit closest, both blue-accented on a near-neutral ground, and they differ in shape and in every face but the mono, IBM Plex Mono in both.
house and pointback share every face, Archivo and IBM Plex Mono, and are told apart by colour, the accent text 12.8 or more and the ring 13.0 or more in both themes, and by pointback's 2px stroke.

A weighted score with a pass bar was proposed and tested against rendered screens before this shipped, and it failed both ways.
It passed a pair with a different serif, crisp corners and a 2px stroke, which renders as the house with another serif, 0.64 CIEDE2000 from it at a glance.
It refused the house against accent 342 on a warm ground, which renders as the most different screen measured, 3.95 from it.
The principle it was built on, that identity never rests on colour alone, needs no score: a product's name is on its screen.

Whether two brands read as two is a render looked at, not a number, so rendering the examples in a browser is a release step ([AGENTS.md](../AGENTS.md#releasing)).

## The three brands

Each brand file's `note` records the identity and who decided it.
Values are the emitted light and dark accent text (step 11), accent solid (step 9) and ground.

| brand | accent text | accent solid | ground | inputs |
|---|---|---|---|---:|
| house | `#305EB7` / `#6294F2` | `#4474CF` | `#FBFAF7` / `#0F0E0C` | 8 |
| quoth | `#6E6100` / `#A99600` | `#FCDF01` / `#F4D908` | `#FCFAF4` / `#0F0E0A` | 9 |
| papertrace | `#2563A3` / `#5B99DC` | `#3C79BA` | `#F8FAFD` / `#0D0F10` | 8 |
| pointback | `#02698C` / `#2BA0CE` | `#59C5F5` | `#F7FAFF` / `#0B0E14` | 8 |

### quoth

**Field: a warm putty instrument whose key is a sports yellow.**
The neutral at hue 95, the accent and the mark both the yellow key at hue 100 with ink labels, the live microphone orange at 48 as a hue of its own, `moulded` corners, Archivo for text, Archivo Expanded for display and Martian Mono for labels and figures, as quoth's D-039 decided.
There is no slate accent: the earlier slate seed at hue 255 is retired (maintainer decision D-099), and the primary is ink.
quoth vendors its own copy of the tokens, built by the retired solver, until its migration replaces it with these exports.

### papertrace

**A report set as a document.**
The cool neutral at hue 250 it ships, a blue accent at 252, red at 25, `crisp` corners, and the system serif for interface, display and reading text, so the report loads no web font.

### pointback

**The pencil in the margin, as it ships.**
Its non-photo blue, `oklch(0.78 0.12 230)`, is the accent's named solid and carries ink; a cool neutral at 260; `house` corners; a 2px stroke, the weight of its pencil rule; Archivo for text and display and IBM Plex Mono for code and file names (maintainer decision C4 in pointback's record, 2026-10-02), from the house's vendored `fonts/`; the dark theme pinned.

### Reserved: treadling, foliot and gates

None of the three has an interface today, so none has a brand file.
A slot is reserved rather than built: when one of them gets a surface, its brand is decided then, and it must still clear every bar above.

## A colour of the product's own

A product sometimes needs a colour for a concept the house has no opinion about, and quoth's open microphone is the case that exists.
A composition of `hw-` roles is still the first answer.
When no house colour means the thing, the product names a hue of its own in its brand file, up to three beside the five the house's roles need, and the build gives it the same twelve steps and floors as every other hue.
The product then names the step its concept uses in its own namespace: `--quoth-live: var(--hw-live-8)` for a mark at 3:1 on every ground, step 11 for text at 4.5:1.

`tools/contrast.py` measures a brand's own hue at steps 8 and 11 against the same steps of the three state ramps, in both themes, and **reports** the closest in CIEDE2000, as "own hue from a state, reported"; it does not refuse it.
A reader holds that number to 14, the accent's old ink bar, decided by the maintainer on 2026-09-28 where teal 172 at 10.5 read as a state and 186 at 14.3 as its own colour.
It is reported rather than refused because a product's own record decides its colour, and the word beside the mark carries the state either way.

### The worked example, quoth's live colour

The accent already marks selection and focus, so a shared accent makes "the microphone is open" read as "this row is selected", and recording red sits on `--hw-danger`.
quoth's D-062 made it the orange of the open microphone, hue 48 at chroma 0.19 in `ramps/brands/quoth.json`.
A run of `tools/contrast.py` reports the lowest of steps 8 and 11, 11.01 from amber; the table is each step through the same `painted()`, step 9 included:

| step | light | dark | closest state, CIEDE2000, light / dark |
|---|---|---|---|
| 8, a mark at 3:1 | `#DC640C` | `#AD4C01` | amber 12.92 / 11.71 |
| 9, a solid | `#C25601` | `#C25601` | amber 12.31 / 12.31 |
| 11, text at 4.5:1 | `#A14600` | `#F36E01` | amber 11.01 / 13.41 |

Every step sits under the 14 from amber, by 3 at worst, and clears red by 15.02 or more and green by 49.41.
This is a finding, not a decision this file makes: either the orange moves off amber, which is quoth's to decide, or the bar is re-calibrated for ramps.
The live state is always the word `Recording`, in a house text colour, beside the mark, announced in a `role="status"` region; the mark does not pulse ([40-motion.md](40-motion.md#what-moves-on-its-own)).

## What stays the house's

What makes two of these recognisably from one maker is everything a brand file cannot reach, and the list is long on purpose:

- **The loudest control is ink**, in every brand.
- **The roles**: which step a link, a fill, a ring or a state names is `ramps/roles.css`'s, the same for every brand.
- **The accent does four jobs and no others**, and the three states are green, amber and red everywhere, at hues a brand may move only within the separation bars.
- **The chart series**, six ramps in one order.
- **One mono face per product**, so every hash, run id and timestamp on a screen is set identically; the house's is IBM Plex Mono, and a brand may name another monospaced face from the roster where the mono is its identity, as Field's is.
- **One rhythm**: the 4px unit, the space steps, the 44px row, the 32px control, the two densities, the five text sizes.
- **One behaviour**: the states each component's sheet lists, one focus geometry, one keyboard contract, one motion.
  Every product answers at 120ms on the same curve.
- **Border before shadow, one hairline, nothing floats that cannot be dismissed.**
- **One icon set**, at whichever of three stroke weights.
- **One voice**: sentence case, "Revoke key" then "Key revoked", numbers with their unit.
- **One proof.**
  Every brand is built by the same code and certified by the same second instrument.

Put two products in greyscale with their names covered, and they should still differ in face and shape, and still obviously be siblings.

## Declined as inputs

| candidate | why not |
|---|---|
| the solver's tuning inputs: accent chroma and lightness per theme, the quiet-fill multiplier, the ring choice, ground lightness, sunken depth, the dark card step | retired with the solver: a ramp step is chosen once for every brand, and each of these moved a step by a few thousandths against bars a brand could not see. The dark card step and the deeper chassis are the stated gaps above |
| a brand primary | the loudest control is ink in every brand, and the accent solid is where a key fills a control; the tier's `primary: brand` retired with the solver |
| the type scale, and which step the display face starts at | every size is load-bearing for density, from the 44px row down, and the stage sizes are the only ones the display face sets |
| a ring chroma of its own | the ring is accent step 8, held to its bars; a brand whose ring fails them changes its accent |
| motion | the house curve is identity: three alternative ease-outs differ from it by at most 1.5px on an 8px move. Up to four named moments may live in a product's namespace ([40-motion.md](40-motion.md#a-products-own-moments)) |
| elevation | 73 of 75 sampled elements carry no shadow; border-first is identity |
| surface texture | a product may have one in its own namespace, held to the pattern rule ([30-space.md](30-space.md#surfaces)) |
| a figurative illustration set | brings its palette through the product's namespace, and its SVG carries no literal colour ([00-brand-book.md](00-brand-book.md#icons-and-art)) |
| voice | the house rules are invariant; a product's register is its noun glossary ([00-brand-book.md](00-brand-book.md#words)) |
| a mark | a mark is a commission ([00-brand-book.md](00-brand-book.md#the-mark)) |

A brand is chosen once and built every time.

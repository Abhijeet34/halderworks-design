# Brand

A product's identity is a **brand seed**: eleven bounded inputs that `tools/build.py --brand` applies to a copy of the house seed and then solves with the same code as the house set.
Every brand ships the house's token names, clears the house's contrast floors, and is certified by the same second instrument.
A brand is a rebuild, never a hand-pick, and "never redefine an `hw-` token" does not change by a word.

## Why a brand is more than an accent hue

Until 2026-09-21 the rule was "the accent hue, and nothing else", and it could not carry the products this book serves.
Under the separation bar it used, only hues 198 to 342 built, at most three accents in that arc sat 8.0 apart, and six evenly spaced ones sat 3.8 apart, which is the distance at which [10-color.md](10-color.md#why-hue-198) rejected teal 172 because the live badge and the passed badge read as one colour.
Every product was the house with a different link colour.
The system's owner gave the direction the same day: each product needs its own distinction rather than a sampler hue.

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

## The eleven inputs

Anything not in this table is not a brand input, and `tools/build.py` refuses a brand seed that names anything else, an `hw-` token included.

| input | range | default | what it moves |
|---|---|---|---|
| `accentHue` | 0 to 359 | 198 | the accent family and the chart rotation |
| `accentChroma` | 0.3 to 1.3 times the house anchors | 1.0 | the chroma of `hw-accent`, `hw-accent-hover` and `hw-accent-ring` |
| `accentLightness` | a lightness per theme | 0.515 and 0.619 | `hw-accent` and `hw-accent-hover`, in all four blocks |
| `quietChroma` | 0.3 to 1.0 times the house anchor | 1.0 | `hw-accent-quiet`, the selected-row fill |
| `ring` | `accent` or `ink` | the house ring | `hw-accent-ring` |
| `neutralHue` | 0 to 359 | the accent hue | all sixteen neutrals together |
| `neutralChroma` | 0 to 4.0 times the house anchors | 1.0 | all sixteen neutrals together |
| `shape` | `crisp` 2/3/6px, `house` 4/6/10px, `soft` 6/8/14px | `house` | `hw-radius-sm`, `-md`, `-lg` |
| `iconStroke` | `1.5px`, `1.75px`, `2px` | `1.5px` | `hw-icon-stroke` |
| `display` | a face in the roster | Newsreader | `--hw-font-display` |
| `text` | a face in the roster | Public Sans | `--hw-font-sans`, held to the house x-height |

The numeric bounds are pinned in `tools/build.py` rather than in the seed, so an edit to the seed cannot widen one.
The registers, the stroke weights and the roster live in the seed's `brand` block, and `tools/contrast.py` declares the registers and the weights again on its own, so a hand-edited radius or stroke in an emitted file is refused by the second instrument too.

### Accent chroma

The upper bound keeps a brand accent under `hw-danger`'s chroma in light, 0.103 against 0.13, so no accent outshouts an error on the default theme.
In dark it does not hold: 1.3 times reaches 0.125 against `hw-danger`'s 0.11, and pointback's shipped pencil sits at 0.12.
That half of the bound is a principle nothing has tested, kept because nothing contradicts it and the one product above 0.11 ships there already.
The lower bound is the quiet end: quoth's slate sits at 0.35, C 0.028, under the 0.055 floor this book uses to count a colour as chromatic, which makes `--quoth-live` the only vivid thing quoth paints.

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
What a tinted ground does cost is its states. A warm ground swallows the warning fill first, and the bound is the point where that begins to show:

| neutral hue 75 at | light ground | warning fill from the ground | reads as |
|---|---|---:|---|
| 1 times | `#F9F7F6` | 9.8 | paper |
| 2 times | `#FAF7F3` | 8.5 | paper |
| 4 times | `#FDF7EF` | 6.7 | paper |
| 6 times | `#FEF7ED` | 5.9 | cream in light, brown in dark |

So `neutralChroma` stops at 4.0, and every state's quiet fill is held **at least 6 CIEDE2000 from `hw-ground`** in every block, which is the failure the bound prevents stated as a measurement.
`hw-surface` keeps chroma 0 in light at every multiplier, so data never sits on the tint.
[10-color.md](10-color.md#why-the-ground-is-neutral) says why the house's own ground stays neutral; a brand may warm or cool its ground within this bound, and the house does not.

### Shape and stroke

Three registers rather than a free number, because a 1px radius change is invisible and a free number invites one.
`crisp` is the 3px of Radix and the 4px of Vercel and Stripe; `soft` is the 8px input and 12px card the field clusters on ([30-space-radius-elevation.md](30-space-radius-elevation.md#radius)).
Every register keeps the two rules that give radius its job: three sizes bound to three roles, and a child never larger than its parent.
The stroke weights are the two the capture measured, 1.5px on 8 sites and 2px on 12, and the step between.

Neither moves a screen much: measured on a rendered product screen, a full register change moves its colour mass 0.03 CIEDE2000 at a glance and a stroke step 0.03, where moving the accent to 342 moves it 3.7 and warming the ground to twice the house chroma 2.0.
They are inputs because a product has a shape, and they carry no weight in telling two products apart.

### Faces

A face is a roster entry with its delivery, and [20-type.md](20-type.md#a-brands-faces) owns the roster, the delivery rule and the x-height the text face is held to.

## The bars every brand is held to

Every brand is held to every house floor, in all four blocks, on the float value and at 8-bit.
On top of the floors, both instruments hold the painted distances below, in CIEDE2000 on the 8-bit value a display receives, in all four blocks:

| what | bar | owned by |
|---|---:|---|
| the accent ink from each state ink | 14 | [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) |
| the selected-row fill from each state's quiet fill | 5 | [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) |
| the focus ring from `hw-danger` | 17 | [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) |
| the focus ring from `hw-border-strong` | 14 | [the focus ring](#the-focus-ring) |
| each state's quiet fill from `hw-ground` | 6 | [neutral hue and chroma](#neutral-hue-and-chroma) |

The chart ramp keeps its own bar, 8.0 in oklab distance times 100 from each semantic and between series, and a product's own colour keeps 8.0 in hue and chroma from each state and the accent ([95-extending.md](95-extending.md#why-the-separation-leaves-lightness-out)).

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
pair                          ground      accent        fill        ring   display  text
papertrace / pointback       6.3/6.6     9.6/8.6     5.0/5.0     9.5/8.1     differ  differ
pointback / quoth            1.5/2.1    13.4/21.6    6.8/6.1    33.2/26.8    differ  differ
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
Values are the emitted light and dark `hw-accent` and `hw-ground`; the bars are each product's worst over all four blocks, as `tools/contrast.py` reports them.

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

- **The loudest control is ink in every product.** `hw-ink` carries no hue, so every primary button is the same near-black or near-white.
- **The accent does four jobs and no others**, and the three states are the same green, amber and red everywhere.
- **One mono face**, so every hash, run id and timestamp is set identically.
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
| motion | the house curves are identity: three alternative ease-outs differ from the house curve by at most 1.5px on an 8px move. One named large transition may live in a product's namespace ([40-motion.md](40-motion.md#a-products-own-transition)) |
| the type scale below `title-1` | every size there is load-bearing for density, from the 44px row down |
| a display-size step | no product needs one, so the input was not built |
| a ring chroma of its own | the accent and ink rings cover every brand that fails the border bar |
| elevation | 73 of 75 sampled elements carry no shadow; border-first is identity |
| surface texture | a signature ground is a product token held to the two-token pattern rule ([75-spec-sheet.md](75-spec-sheet.md)), not a brand input |
| a figurative illustration set | brings its palette through the product's namespace, and its SVG carries no literal colour ([55-iconography.md](55-iconography.md#illustration-one-pictogram-set-and-no-figurative-drawing)) |
| voice | the house rules are invariant; a product's register is its noun glossary ([25-content.md](25-content.md)) |
| a mark | a mark is a commission ([00-brand-book.md](00-brand-book.md#the-mark)) |

A brand is chosen once and solved every time.

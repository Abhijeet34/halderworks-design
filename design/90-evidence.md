# Where the numbers come from

Every claim in this system traces to one of three places: a measurement taken off a live page, a solver run against a contrast target, or a licence file fetched from its repository.
Nothing here is a recalled fact about design.

## The two capture passes

**Pass one, 14 products**, rendered in a real browser at 1440x900 and measured with `getComputedStyle` on the DOM rather than sampled from screenshots.
For each one the capture recorded painted background colours ranked by area, every distinct font size, every distinct radius, the computed type of `h1`, `h2`, `p` and the first buttons, every `transition-duration` and `transition-timing-function`, every border width and colour, and the running-text measure.

21st.dev, Linear, Vercel Geist, Radix Colors, Stripe, rauno.me, emilkowal.ski, paco.me, Family, Superlist, Resend, Railway, Arc, and 21st.dev's component views.
Five documentation sites were measured separately for running-text measure: Stripe Docs, Tailwind, Radix Primitives, Vercel Docs, shadcn/ui.

**Pass two, 46 sites attempted and 44 captured**, for the layers pass one never measured: layout containers, the breakpoints declared in each site's own stylesheets, density, icon geometry, interaction-state selectors, surface texture, control-label casing and table anatomy.
A separate responsive pass re-measured 12 of them at 390, 768, 1024, 1440 and 1920px, and a third pass read the left offset of the first heading and first paragraph at four widths, which is the page margin with no centring to confuse it.

Screened by name, on their own merits, and grouped by what each was screened for:

| group | sites |
|---|---|
| **published design systems** | IBM Carbon, Shopify Polaris, GitHub Primer, Adobe Spectrum, Atlassian Design, Material Design 3, US Web Design System, GOV.UK Design System, Salesforce Lightning, Radix Themes, Nord Health, Base Web, Ant Design, Microsoft Fluent 2 |
| **products whose interface craft is the reference** | Linear, Stripe, Vercel, Raycast, Figma, Railway, Resend, Sentry, PlanetScale, Tailwind, shadcn/ui, GitHub, Datadog |
| **design-engineering writing** | rauno.me, Josh Comeau, Adam Argyle (nerdy.dev), Ahmad Shadeed, Matthew Strom, Refactoring UI, Emil Kowalski |
| **type foundries and specimen sites** | Klim, Commercial Type, Grilli Type, ABC Dinamo, Pangram Pangram, Fonts In Use |
| **icon sets** | Lucide, Phosphor, Tabler, Heroicons |

Two failed and are therefore cited nowhere: `height.app` returned `ERR_CONNECTION_RESET`, and `eightshapes.com` returned `ERR_NAME_NOT_RESOLVED`.
Three sites serve their stylesheets cross-origin, so their rule counts are absent rather than zero: Polaris, Base Web and Stripe.
Where a count below says "of 41", it is over the sites whose own stylesheets could be read; "of 44" is over every site captured.

**What these references were and were not used for.**
They set principles and they supply the numbers that principles are checked against.
No expression is carried across: not a palette, not a face, not a component's look.
The house decisions that came out of them are that a ground is neutral, that colour is scarce, that elevation is a border, that display type is set tight, that a type ramp has about nine steps, that 768 and 1024 are where the field agrees on structure, that hover is a fill, that focus is never removed, and that there is no texture. <!-- covered-by: Texture, grain, gradient, glass -->
Each is stated with the count that supports it.

## The headline counts from pass two

| reading | value |
|---|---|
| sites declaring a 768px min-width | 23 of 44, the most of any value |
| sites declaring a 1024px min-width | 18 of 44 |
| sites capping a container between 1100 and 1300px | 20 of 44 |
| median running-text measure, 30 sites carrying real paragraphs | 64ch, range 25 to 112 |
| median prose column width at 1440px, 12 sites | 721px |
| page margin at a 390px viewport | 16px on 6 of 12, 24px on 3 of 12 |
| most common measured button height | 32px on 14 sites, then 40px on 11 |
| most used rendered icon size | 16x16 on 21 sites, then 24x24 on 18, 20x20 on 15 |
| icon `stroke-linecap: round` | 868 uses across 16 sites, against 106 `butt` |
| sites declaring `:hover` and `:focus` | 41 of 41 |
| sites declaring `:focus-visible` | 32 of 41 |
| sites declaring `:disabled` | 31 of 41 |
| sites declaring a `readonly` rule | 6 of 41, the least-served state |
| `outline: none` declarations | 294 across 26 of 41 sites |
| real `outline-width` values | 2px 246 uses, 1px 75 uses |
| most common disabled opacity | 0.5 on 13 sites; `cursor: not-allowed` on 21 |
| hover carried by `background-color` | 39 of 41 sites |
| sites with a noise, grain or pattern image on a large element | **2 of 44** (Linear, Sentry) |
| sites using `backdrop-filter` | 8 of 44 |
| control labels in sentence case | 60.9% of 1211 labels; title case 11.0%, upper case 2.8% |
| table cells setting `tabular-nums` | **0 of 777**, across 15 sites |

The last row is the one place the house rule deliberately departs from measured practice, and [70-data-display.md](70-data-display.md) says why: those are documentation tables, which compare nothing.

## The solver

Colour was not chosen and then checked.
For each token the solver binary-searches lightness until the token hits its contrast target against the worst surface it is permitted to sit on, then clamps chroma to the in-gamut maximum at that lightness and hue.

Five defects it has caught that no eyeball would have, the first two in the first pass and the last three in this one:

1. A `warning` at chroma 0.12 falls outside sRGB at every light ground. The in-gamut ceiling at the required lightness is 0.101, and an out-of-gamut oklch triple is simply not the colour the token file claims.
2. "The worst surface" is the surface *closest in lightness to the foreground*, not the furthest. Solving dark-theme tokens against the darkest surface and light-theme tokens against white both feel right and both return the easiest ratio; each shipped sub-AA pairs before the rule was corrected. Six pairs in one direction, five in the other.
3. `hw-accent` on `hw-accent-quiet` measured 4.37:1 in dark theme, below AA, on a pairing [10-color.md](10-color.md) already instructed. The quiet fills had been solved for a visible step off their surface and never against the ink that sits on them.
4. `hw-success` on `hw-success-quiet` measured 4.46:1 in dark theme, the same cause.
5. `hw-accent-ring` was solved against the ground alone and measured **2.56:1 on `hw-surface-raised`** in dark theme: a keyboard focus ring inside a dialog, at roughly half the bar it is supposed to clear.

The final run: **108 text pairs across both themes, 0 below AA; 90 non-text pairs held to 3:1, 0 below it; 33 colour tokens, 0 outside sRGB.**
`tools/build.py` emits `tokens/tokens.json` and `tokens/tokens.css` from `tokens/tokens.seed.json`, re-measures every floor against the formatted strings before it writes them, and refuses to write either unless that holds.
Rebuilt at the shipped hue it re-solves three tokens, because the solver now targets the bar plus a margin rather than the bar: a value solved to land exactly on its floor is a value that rounding, a second converter or an 8-bit display can each take below it.
`tools/build.py --check` reproducing the two committed files byte for byte is the regression that proves the shipped set satisfies its own spec.
Rebuilt at hue 318 it re-solves five tokens and the matrix still holds, and a sweep of all 360 accent hues finds 145 buildable, all 145 accepted by `tools/contrast.py` and none carrying a pair below its bar on an exact reading.

## Measurements taken directly

Four more were measured in the third pass, in a headless browser with the faces loaded.

- **A field rendered 35.5px beside a 32px button.** The shipped `Input` anatomy of `7px 10px`
  padding on 13px text at 1.5 line-height is 19.5 of line box plus 14 of padding plus 2 of border.
  `--hw-control-h` is 32px and is defined as the input's outer height, so the token and the anatomy
  disagreed by 3.5px. After the box model in [66-forms.md](66-forms.md), input, select, button,
  stepper and segmented control all render exactly 32.0px.
- **1ch of `body-sm` Public Sans is 7.961px**, which is what `--hw-panel-w` is derived from.
- **`--hw-border-strong` ran 1.45:1 to 2.14:1** across the six surfaces it sits on, in both themes,
  against a 3:1 bar. Re-solved, its worst case is 3.03:1.
- **A floating panel loses its edge without a shadow in dark theme.** Rendered with the border and
  shadow removed, a dark panel over a `#0d1011` desktop and a light panel over `#f4f6f7` both read
  as text on the wallpaper. This is the measurement behind the one exception to the light-theme-only
  shadow rule.

Two numbers in the first two passes were measured rather than sampled or solved.

- **Lucide's painted stroke.** Rasterised at 8x and summed by alpha coverage: Lucide as shipped, a 2-unit stroke on a 24 grid, paints **1.313px** at a 16px render. `stroke-width="2.25"` paints **1.500px**. The arithmetic `1.5 x 24 / size` is therefore confirmed rather than assumed.
- **`vector-effect: non-scaling-stroke`**, tested as the one-line alternative, painted **0.187px** where 1.5px was asked for, tracking the raster scale rather than CSS pixels. The system does not rely on it.

## Published editorial accounts, screened for structure

Four published UI/UX accounts were screened on Instagram for structural devices this system had no
answer for: `janm_ux`, `ui.ux.jam`, `vectorayush` and `khushidotjpeg`.
They are cited here as sources, the same way the design systems above are.

**This section replaces a wrong conclusion, and the correction matters more than the original
claim.** An earlier pass read these accounts from their profile grids alone, without opening the
posts, and concluded that all four publish in the purple-gradient and display-serif register that
sits on this system's own anti-pattern list - and therefore confirmed the existing decisions
unchanged. Read properly, **one of the four matches that description and three do not.** The
earlier reading stated its limitation plainly and flagged it itself. The limitation was real and
the conclusion drawn from it was too narrow.

**Why a grid read was not enough**, which is the transferable part: `ui.ux.jam` keeps its older
gradient material **pinned**, so the three tiles at the top of the grid are the oldest work on the
account and the current work is below them. A reader who stops at the first screen of a grid is
reading a curated archive rather than a current register.

### Account by account

**`janm_ux` - the earlier reading holds.**
Every thumbnail is one construction: a presenter's face beside a monitor, a two-line headline
whose second line is set in a blue-violet gradient. "One Tool to Build **3D Websites**", "Don't
design **Boring AI Websites**", "6 Amazing UI **Color Combos**". This is the register the earlier
pass described, and for this account it is accurate.

**`ui.ux.jam` - the earlier reading is out of date.**
The current work carries a consistent editorial frame: a small `JAM` mark top left, a year stamp
reading `20-26` top right, an item number bottom left and a month abbreviation bottom right. Across
one reels grid the item numbers run 165, 192, 248, 333, 358, 361 and the months FEB, MAR, JUL, SEP -
a continuous sequence, which is what makes the frame read as a publication rather than as a
decoration repeated. Adjacent tiles in the post grid stamp `506` and `507`. Grounds are desaturated
photographs of real desks and screens, near achromatic; headlines are white and large; colour comes
from what is in the photograph rather than from a gradient.

**`khushidotjpeg` - nothing like the earlier reading, and the most useful of the four.**
Warm neutral and muted grounds, no gradients anywhere. The organising device is a very large
editorial numeral against a much smaller headline: `5` "UX things I was taught as 'best practice'
that I now think are wrong", `3` "sites that will fix your colour choices", `6` "Figma plugins I
use on every single project". Also carried: a display serif mixed with a grotesque inside one
headline, one accent only as a highlighter-yellow marker behind two words, small-caps eyebrows
("TIPS + TRICKS FOR DESIGNERS"), a hand-drawn asterisk, bracketed italic asides ("[ you should
try ]"), torn-paper collage over photography, a grid-paper ground, faux application chrome with
traffic-light dots and a footer rule, dotted leader lines from colour swatches into a photograph,
and translucent stacked pill labels.

**`vectorayush` - near-black with one accent, executed well.**
Near-black ground, amber and gold as the single accent, a grotesque first line over a display serif
second line, a small-caps eyebrow and a hairline rule as a footer.

### What this changed, and what it did not

**The anti-pattern entry for the dark ground was read and deliberately left unchanged.**
`vectorayush` is the honest test of it: the entry reads "Near-black with a lone acid-green or
vermilion pop", and its house rule opens "the dark ground exists". The tell names an acid pop and
the rule names the two real failures, colour spent with no other decision being made and an acid
chroma. Amber on near-black is neither, so the entry already forbids the failure rather than the
family, and it was left exactly as it stood. An unnecessary edit there would have been worse than
none.

**Eight structural devices were taken from the three non-gradient accounts and judged one by one.**
Seven are specified in [75-spec-sheet.md](75-spec-sheet.md), the high-contrast theme among them,
and one is declined outright with its reasoning. The accent hue, the faces and the scales are unchanged, and no entry introduced a colour.

**One standing decision did move**, and it is flagged here because a reader of an earlier version
would not expect it: [50-surface-texture.md](50-surface-texture.md)'s blanket refusal of texture is
re-scoped. The refusal's stated reason - that a contrast ratio is computed against one background
colour - is exactly true of grain, glass and photography and is **not** true of a deterministic
two-colour pattern, whose worst pixel is a named token. The ruled ground in the spec sheet is
certified against that worst pixel and the certification immediately earned its place:
`--hw-text-muted` measures **4.01:1 light and 3.89:1 dark** against `--hw-border` and is therefore
refused on that ground, while `--hw-text` at 12.17 and 11.84 and `--hw-text-secondary` at 5.23 and
5.06 are permitted. A ground whose pixels are not enumerable still carries no text at all.

**The caveat is kept rather than dropped once it stopped being convenient.**
These are feed thumbnails optimised to be clicked, which is a different job from an interface, and
none of these accounts claims otherwise. They are evidence about structure, not a verdict on the
designers. Four accounts are a sample, not a census of how the format is used.

### The captures, and why they are not in this repository

Five screenshots of those published pages were taken on 2026-09-21 and kept as working reference
material outside this repository: two post grids from each of two accounts, plus one reels grid.
They are study material.

**Nothing in them is reproduced here.** Every entry in [75-spec-sheet.md](75-spec-sheet.md) states
what principle was taken and what expression was deliberately left behind, and an entry that could
not fill the second line was declined rather than shipped. They are not redistributed with this
system, because a screenshot of somebody's published work is theirs and this repository ships only
what it can license.


## The fourth evidence pass: six more published systems, read from installed packages

The three passes above read live pages with `getComputedStyle`.
The fourth pass changed instrument: where a system ships an npm package, it was installed and read
from disk instead, because **a constant in shipped source is the author's own number, where a page
is an observer's reading of it.**

| system | package | version | read for |
|---|---|---|---|
| Atlassian | `@atlaskit/tokens` | 16.12.0 | per-token lifecycle metadata; a shipped increased-contrast theme |
| Fluent 2 | `@fluentui/tokens` | 1.0.0-alpha.24 | a 3x3 easing matrix; a high-contrast theme that collapses rather than diverges |
| Ant Design | `antd` | 6.6.3 | a seed-to-token algorithm, and density as a measured diff |
| Base Web | `baseui` | 18.2.0 | composite tokens on a non-motion property |
| USWDS | `@uswds/uswds` | 3.14.0 | contrast as integer arithmetic on the token name |
| Apple HIG | none published | read 2026-09-21 | input modality as a top-level axis |
| Toast, drawer, animation | `sonner@2.0.8`, `vaul@1.1.2`, `motion@13.2.0` | | shipped interaction constants |
| Pictograms | `@carbon/pictograms@12.84.0` | | an illustration-class asset set, Apache-2.0 |
| Keyboard | ARIA Authoring Practices Guide | read 2026-09-21 | 30 patterns, 381 enumerated bindings |

### What a theme may change: nine pairs, five vendors, zero tokens added or removed

[10-color.md](10-color.md) takes it as given that a theme changes values and never the token set.
That was one vendor's stated rule. It is now the field's measured practice:

| vendor | theme pair | tokens | added | removed | changed |
|---|---|---:|---:|---:|---:|
| Primer | light to light-high-contrast | 959 | 0 | 0 | 28.3% |
| Primer | dark to dark-high-contrast | 959 | 0 | 0 | 27.5% |
| Atlassian | light to light-increased-contrast | 463 | 0 | 0 | **54.0%** |
| Atlassian | dark to dark-increased-contrast | 463 | 0 | 0 | 39.3% |
| Fluent | teamsLight to teamsHighContrast | 459 | 0 | 0 | **78.4%** |
| Fluent | teamsDark to teamsHighContrast | 459 | 0 | 0 | 75.4% |
| Fluent | webLight to teamsLight, the product axis | 459 | 0 | 0 | **10.9%** |
| Base Web | light to dark | 1170 | 0 | 0 | 44.0% |
| Ant Design | default to dark algorithm | 443 | 0 | 0 | 81.9% |

**This corrects an inherited number.** An earlier pass, working from the Primer sample alone,
recommended expecting roughly a quarter of this system's 33 colour tokens to move in a
high-contrast theme. A quarter is the **low end of a 28 to 78% range**, not the expectation, and
[05-coverage.md](05-coverage.md)'s high-contrast row now says so.

Fluent's product-axis row is the control that makes the rest readable: changing product identity at
the same contrast level moves 10.9% of tokens, and changing the contrast level moves 78%.
Contrast is roughly seven times the move that identity is.

### The two high-contrast strategies are opposite, and each media query gets its own answer

| vendor | distinct values before | after | direction |
|---|---:|---:|---|
| Primer light | 454 | 466 | **up 12** - roles pushed apart |
| Atlassian light | 127 | 119 | down 8 |
| Fluent Teams, colour tokens only | **192** | **15** | **down 177** - roles collapsed together |

Fluent's high-contrast theme puts 366 colour tokens onto 15 distinct values, and five carry almost
all of them: `#ffffff` on 127 tokens, `#000000` on 104, `#1aebff` on 104 at 14.37:1 on black,
`#ffff00` on 12 at 19.56:1, `#3ff23f` on 7 at 13.98:1.
That is the Windows High Contrast system palette, and the collapse is the point: the theme is
surrendering the palette to the user agent rather than trying to be more readable itself.

**`prefers-contrast: more` and `forced-colors: active` are two questions, not one.**
The first asks for a stronger palette and a per-role re-solve answers it. The second means yours was
thrown away, and the one-line `outline: <width> solid transparent` rule answers it.
One theme cannot answer both, and this is the first time the distinction has been measured inside a
token file rather than inferred from a media query.
Both now ship: the per-role re-solve in `tokens/tokens.css`, specified in
[75-spec-sheet.md](75-spec-sheet.md#high-contrast-which-answers-prefers-contrast-more-and-nothing-else),
and the transparent border in [50-surface-texture.md](50-surface-texture.md#under-forced-colours).

### Two independent sources ship the exact reduced-motion error this system's rule was written against

[40-motion.md](40-motion.md) forbids blanket suppression, with its reason.
`sonner@2.0.8`, a widely used toast library, ships:

```css
@media (prefers-reduced-motion) {
  [data-sonner-toast], [data-sonner-toast] > *, .sonner-loading-bar {
    transition: none !important;
    animation: none !important;
  }
}
```

An earlier pass found a published design-reference skill committing the same error in its own
reduced-motion shortcut.
**Two unrelated, well-regarded sources shipping the same error moves the house rule from a
defensible opinion to a rule with two shipped counter-examples behind it**, which is the strongest
form the evidence for any rule in this system takes.

### The easing default, on one axis, so "out-biased" stops being an adjective

[40-motion.md](40-motion.md) says its default is out-biased on purpose and gave no number for it.
The number is the fraction of the change already done at the quarter point, `p(0.25)`:

| curve | p(0.25) | p(0.50) | p(0.75) |
|---|---:|---:|---:|
| Fluent `curveDecelerateMax` | 0.849 | 0.966 | 0.995 |
| Ant `motionEaseOutCirc` | 0.838 | 0.958 | 0.993 |
| Linear, and `vaul@1.1.2` | 0.779 | 0.955 | 0.992 |
| **house `--hw-ease-out`** | **0.765** | 0.961 | 0.997 |
| **Base Web `easeDecelerate`** | **0.765** | 0.961 | 0.997 |
| Fluent `curveDecelerateMid` | 0.691 | 0.890 | 0.976 |
| Stripe | 0.689 | 0.934 | 0.994 |
| Ant `motionEaseOut` | 0.600 | 0.875 | 0.976 |
| Carbon productive standard | 0.306 | 0.685 | 0.907 |
| Carbon expressive standard | 0.258 | 0.747 | 0.954 |
| linear (control) | 0.250 | 0.500 | 0.750 |
| **house `--hw-ease-standard`** | **0.237** | 0.776 | 0.959 |
| **Tailwind default `ease-in-out`** | **0.237** | 0.776 | 0.959 |
| house `--hw-ease-in` | 0.099 | 0.325 | 0.630 |

Three readings, none of which was available before:

- **`--hw-ease-out` is 76.5% done at a quarter of the way through**, fourth most out-biased of 17
  measured curves.
- **Base Web's `easeDecelerate` is `cubic-bezier(0.22, 1, 0.36, 1)`, byte-for-byte this system's
  `--hw-ease-out`**, arrived at independently by a published system. That is the strongest
  confirmation any single value here has.
- **`--hw-ease-standard` is byte-identical to Tailwind's default.** [40-motion.md](40-motion.md)
  says so of the curve while arguing against it, and then ships it under a house name. The
  token now records the inheritance in its own `usage` string, so a reader of
  `tokens/tokens.json` can tell the value is inherited rather than chosen.

### Shipped interaction constants, which this system had none of

`vaul@1.1.2` publishes its whole drawer contract as named constants:

```javascript
const TRANSITIONS = { DURATION: 0.5, EASE: [0.32, 0.72, 0, 1] };
const VELOCITY_THRESHOLD = 0.4;
const CLOSE_THRESHOLD = 0.25;
const NESTED_DISPLACEMENT = 16;
```

A drag closes the drawer if velocity clears 0.4 **or** distance clears 25% of the dimension - two
independent thresholds, either sufficient.
Its only easing, `cubic-bezier(0.32, 0.72, 0, 1)`, is the curve an earlier pass measured on Linear;
two unrelated sources shipping the identical four numbers is worth more than either sighting alone.

`sonner` supplies the toast stacking geometry: `--scale: var(--toasts-before) * 0.05 + 1`, so each
toast behind the front one is 5% smaller and one gap further back.
It also gives every property inside one transition its own duration, with `box-shadow` at half the
geometry's duration everywhere it appears.

[74-interaction-constants.md](74-interaction-constants.md) is what this system does with those.

### Ant Design: 47 seed tokens become 443, and density as a measured diff

```bash
node -e "const {theme}=require('antd');
  console.log(Object.keys(theme.defaultSeed).length,
              Object.keys(theme.defaultAlgorithm(theme.defaultSeed)).length)"
# 47 443
```

A 9.4x expansion from a published function, with dark and compact as alternative algorithms over the
same seed. That is the architecture `tools/build.py` now has, and [95-extending.md](95-extending.md)
describes.

`compactAlgorithm` on the same seed changes **exactly 30 of 443 tokens**, and every one is a font
size, a line height, a font height, a spacing step or a control height. No colour, no radius, no
border width, no shadow, no icon size - which is the same list [45-density.md](45-density.md) holds
fixed, arrived at independently.

The one place the two systems differ is type, and [45-density.md](45-density.md) now records it.

### USWDS: contrast as integer arithmetic on the token name

Every USWDS colour token carries a grade in its name - `blue-40v` is grade 40 - and contrast is
arithmetic on the grade:

```scss
@function magic-number($grade-1, $grade-2) { @return math.abs($grade-1 - $grade-2); }
$system-wcag-magic-numbers: ("AA": 50, "AAA": 70, "AA-large": 40);
```

Run against real WCAG ratios on 36 pairs of one published family:

```text
AA       (delta >= 50, real bar 4.5:1) -> 36/36 agree, 0 false pass, 0 false fail
AAA      (delta >= 70, real bar 7.0:1) -> 33/36 agree, 0 false pass, 3 false fail
AA-large (delta >= 40, real bar 3.0:1) -> 34/36 agree, 0 false pass, 2 false fail
```

**Zero false passes at every target.** The rule never approves a pair that fails; it only refuses
pairs that would have passed, which is the correct direction for a safety rule.

**The honest reading, which is why this system did not adopt it:** 36 pairs, one family, one
vendor's palette, and a palette built so the rule holds. That is evidence USWDS constructed its
ramps to satisfy the rule, not evidence that grade separation predicts contrast in general.
Adopting it would mean rebuilding every token name here to carry a grade, which
[10-color.md](10-color.md) and [15-color-combinations.md](15-color-combinations.md) do not.
[85-considered-and-declined.md](85-considered-and-declined.md) carries the decision.

### The keyboard hole, counted rather than characterised

Before [72-keyboard.md](72-keyboard.md) existed, run over the whole book:

```bash
grep -rni 'roving\|tabindex' .        # no output, exit 1
grep -rni 'activedescendant' .        # no output, exit 1
grep -rni 'arrow key\|Down Arrow' .   # 2 matches
```

`roving` and `tabindex` **0**, `activedescendant` **0**, arrow keys **2**, `aria-disabled` **2**,
both about a blocked submit button - across a book that claimed 107 answered surfaces.

The ARIA Authoring Practices Guide publishes **30 patterns, all 30 carrying a Keyboard Interaction
section, and 381 enumerated bindings across the 23 that have any**.
Five say "Not applicable", one defers to the dialog pattern, and `checkbox` states its rule in
prose; every zero was read before it was reported, and a first parser that returned 173 rows and
seven zeroes was wrong rather than the guide being silent.

Whole-corpus key frequency across all 30 patterns: Shift 36, Control 34, Down Arrow 25, Up Arrow 24,
Home 21, End 21, Space 19, Enter 15, Tab 15, Right Arrow 12, Left Arrow 11, Escape 8, Shift+Tab 6,
Page Down 6, Page Up 6, Delete 5, Alt 4, Backspace 2, F6 1.

Two readings: **Home and End appear 21 times each, more often than Enter**, which makes them the
most under-implemented pair in the field. And **Tab appears in only 15 of 381 rows**, because inside
a composite widget Tab is what you use to leave.

### Illustration, measured rather than argued

A reference image in the flat multi-colour register was measured over every pixel:

```text
size (430, 334); distinct values 80
  #fdf0d2 39.59%   #fafafc 17.55%   #82a0cb 14.45%   #20335c 14.20%   #c57f6a 11.79%
  top-5 share: 97.59%
```

**This corrects an inherited number:** an earlier note recorded five colours at 98.7%. Measured
independently, the figure is **97.59%**, and six values reach 98.24%. The difference changes
nothing and is recorded because an inherited number nobody re-ran is how a reference pack drifts.

Two descriptive corrections fall out of the same pixels: the cream is a **letterboxed band**, inset
58px at the top and 15px at the bottom with near-white above and below, not a strip over a fill; and
the sixth value is a two-pixel anti-aliased seam rather than a shadow, so the claim of no shadow
holds and now holds because it was checked.

Against the two construction models the field ships:

| | `@carbon/pictograms` | the flat multi-colour register |
|---|---|---|
| colours per asset | **1**, inherited from CSS | **5**, baked into the asset |
| palette cost | zero | a second palette to certify against every ground |
| measured | 1,575 assets, **1,575 of 1,575** on `viewBox="0 0 32 32"`, **0** carrying any colour literal, 1,559 a single path | - |
| governance | 44 categories, aliases on 1,574 of 1,575, deprecations naming their replacement | none |
| licence | Apache-2.0 | varies; see below |

**A pictogram is not an icon at a larger size, and there is a number for it.** Measured across 400
files, the repeated stroke magnitude is **0.72 on a 32 grid = 2.25%** of the frame, against Lucide's
2 on 24 = **8.33%**. The pictogram line is **3.7x finer relative to its frame**, which is what makes
it illustration-class and unreadable at this system's 16px icon size.
[55-iconography.md](55-iconography.md) rejects Carbon's *icon* set for being filled; that reason does
not reach this package, which is a different package and is drawn as outlines.

**One licence decides one option.** unDraw is the closest style match to the flat register and its
licence rules it out as a shipped set, quoted verbatim from its own page:

> This license does not include the right to compile assets, vectors or images from unDraw to
> replicate a similar or competing service, in any form or distribute the assets in packs or
> otherwise.

A design system that vendors unDraw SVGs into a repository and ships them to products is
distributing them. That fact is invisible in the drawings and decides the option.
Humaaans publishes CC0 and is the closer style match; Open Peeps also publishes CC0 but was read
through one channel only and should be treated as one confirmation rather than two.

**Where the flat register fails, and it is not craft:** five baked values have no dark-theme
counterpart. `#fdf0d2` at `oklch(0.9577 0.0416 87.36)` on this system's dark ground at
`oklch(0.152 0.006 198)` is a light rectangle in a dark screen, and none of the three libraries
solves it.

### The coverage cross-check, and the one leak it caught

[05-coverage.md](05-coverage.md) opened by claiming its list was derived from what a design system
has to answer rather than from what this one happens to contain, and cited no external taxonomy
anywhere. A list of what its authors thought of cannot prove that nothing is missing.

**The instance that proves it under-reported**, found by sweeping every refusal in the rule files
against the inventory: `35-layout.md` refuses a resizable splitter with a stated reason, the ARIA
APG carries `windowsplitter` as one of its 30 patterns, and the inventory had **no row for it**.
Seven of eight refusals stated in rule files reached the inventory and that one escaped.

Six external lists were then enumerated, five read from installed packages rather than from a page.
[05-coverage.md](05-coverage.md) names them, with their sizes and the date, as its cross-check
manifest. The audit returned **34 rows the inventory did not carry**: 13 genuine gaps, 18 to exclude
with a reason, and 3 already covered by composition.

**What the audit does not prove**, stated because the opposite is the easy claim to make: it proves
the inventory was missing at least 34 rows. It does not prove 34 is all of them, and it cannot.
Material 3, Spectrum, Polaris, Primer, Carbon and Atlassian all publish component lists and none was
enumerated for this purpose. The recurring fix is the fourth rule in `tools/check-coverage.py`, not
the 34 rows.


## The rhythm measurement, which this system could nearly prove and had never stated

A reader asked whether this system captures rhythm. It had a spacing scale, a type ramp and a
line-height for every step, and **no statement anywhere of how the three relate** - so "on the
grid" was a habit rather than a property, and nothing could be checked against it.

Counted over the four families the unit governs - spacing, layout, density, icon:

```text
35 space and size values on the 4px unit, 7 off it and all 7 declared with a reason.
```

Counted over the type ramp, every step's line box against the same unit:

| step | size x line-height | line box | on the unit |
|---|---|---:|:--:|
| `display-1` | 56 x 1.02 | 57.12px | no |
| `display-2` | 40 x 1.08 | 43.20px | no |
| `title-1` | 28 x 1.15 | 32.20px | no |
| `title-2` | 21 x 1.25 | 26.25px | no |
| `title-3` | 17 x 1.35 | 22.95px | no |
| `body-lg` | 17 x 1.60 | 27.20px | no |
| `body` | 15 x 1.55 | 23.25px | no |
| `body-sm` | 13 x 1.50 | 19.50px | no |
| `label` | 12 x 1.35 | 16.20px | no |
| `micro` | 11 x 1.20 | 13.20px | no |

**Zero of ten**, and none within half a pixel of one. That is the measurement behind
[32-rhythm.md](32-rhythm.md)'s rule that the unit governs the space *between* things and type
governs the space *inside* them, and behind its refusal of a baseline grid.

**Two defects the count found**, both of which had survived three rounds because nobody had
counted:

1. **`--hw-space-2` and `--hw-icon-gap` both claimed one job** - the gap between an icon and its
   own label - at 2px and 6px, with directly contradictory reasons attached: one recorded that 4px
   "already reads as separate", the other that 4px "reads as one object". The 6px token owns that
   gap; 2px now carries the badge inset it actually has in [65-components.md](65-components.md).
2. **"exactly two off-grid values in the system" was wrong.** Counted within the unit's scope there
   are **seven**, of which four are consequences of a height token rather than choices. All seven
   are now listed with the reason each cannot be on the unit, and `tools/build.py` refuses to emit
   an eighth that is not declared - and refuses a declared exception whose value has since moved
   back onto the unit, because a stale entry in that list is what makes the next drift look
   legitimate.

## The motion source, screened

Motion has been the measured weak point in every round: an earlier pass found **three systems of
91** mentioning any duration at all, and the round after it had to take its motion evidence from
two published systems because nothing else carried any.

Ripplix (`ripplix.com`), which calls itself the "World's Largest UI Animation & Micro Interaction
Library", was screened against that gap. It publishes, in its own words:

> 7,000+ curated UI animations from 1,000+ real apps across mobile, web, smartwatch and AR/VR
> platforms

Its taxonomy is by surface with counts - one surface category's page is headed `Pricing Animation
Inspiration - 146 Real Examples`. Access is gated: `Join Now`, `Login`, and `Get Pro 40% OFF
$5/month`.

**On the pages reachable without an account, an entry carries a title, an app name, a category tag
and a preview. No duration, no easing curve, no CSS and no downloadable specification appeared on
either page read.**

**The verdict, and it is decisive rather than dismissive.** The motion gap here is a gap in
*specifications*, and what that library holds is *recordings*. A video of an interaction is an
observer's reading of somebody else's number with a time axis added - one step further from the
author's own value than a page is, and the selection rule this evidence base already runs on
prefers shipped source precisely because a constant in source is the author's own number.

The comparison is not close. Five shipped libraries read from source in one round produced
`VELOCITY_THRESHOLD = 0.4`, `CLOSE_THRESHOLD = 0.25`, a 0.5s settle on a named curve, a 0.05 scale
step, nine curves and eight durations. Seven thousand recordings produce none of those without
somebody measuring each one frame by frame.

**What it is genuinely good for, stated because a decline should name what it gives up.** It is a
*census of what moves*, by surface - which interactions in the field are animated at all. That is a
question this book cannot currently answer and a library of recordings answers better than a
library of source. It is recorded as that in
[85-considered-and-declined.md](85-considered-and-declined.md) rather than adopted as a motion
source.

**The limit of this screen:** two pages, read without an account. If entries behind the login do
carry durations and curves, the verdict changes, and the entry says so.

**One thing the screen establishes about the field rather than about this book.** An earlier round
measured 3 of 91 published systems mentioning any duration. Ripplix
publishes 7,000 recordings and, on its open pages, not one duration. **The specification gap is the
field's, not this system's** - which is why [74-interaction-constants.md](74-interaction-constants.md)
had to be transcribed from three shipped libraries rather than found already written anywhere.

## A third independent instance of the four-corner frame

`figma.expert`, an account publishing Figma tutorials, was screened for its assets on 2026-09-21 and
yielded one measurable thing, which was its format rather than its content.

Its carousel cover carries the same four-corner frame already measured on two unrelated accounts,
with a different payload in each corner: a series label top left, a slide counter reading `01 / 06`
top right, a strapline bottom left and an attribution bottom right, around an oversized stacked
headline.

**That is a third independent instance**, and it is what moves the four-corner frame from a device
two accounts happen to share to a format with real support behind it. The
[slide sequence](75-spec-sheet.md#slide-sequence) is built on the three.

**Two facts about that source belong beside the finding.**

**Instagram labels the account `AI-generated profile`, in its own words directly beneath the
handle.** That is the platform's label rather than an inference, and it is recorded here because a
source's nature is part of its provenance. It does not weaken the format measurement - a frame is a
frame whoever drew it, and it is a third instance because it is independent of the other two.

**Every asset it advertises is behind a direct message.** Ten posts read, each offering a file -
icon sets, plugin sheets, portfolio templates, a colour palette - and every one gated behind
commenting a keyword. Nothing is published, so nothing was obtained and nothing from any of them
is in this system.

**And its headline claim is the input this book exists to refuse.** The colour post is titled `Most
Expensive Colour Pallet In Figma (2026)`. "Most expensive" is not a property a palette has, and no
source is given for it anywhere. [85-considered-and-declined.md](85-considered-and-declined.md)
carries the refusal. **Take the frame; take no colour.**

## Sources the owner supplied, one by one

The sources above were chosen by screening the field.
These were handed over directly by the system's owner, across four rounds: followed accounts, reels, a profile, an image and two reference libraries.
This is the ledger for them, so a reader can see what each one gave the system and what it did not.
A source that produced nothing says so here, because silence reads as never having looked.

| source | what was read | taken | left, and where that is recorded |
|---|---|---|---|
| Four followed accounts: `janm_ux`, `ui.ux.jam`, `vectorayush`, `khushidotjpeg` | post grids and opened posts, two passes, 2026-09-21 | eight structural devices, of which seven are entries in [75-spec-sheet.md](75-spec-sheet.md), the high-contrast theme among them, and one is declined; the four-corner frame's first two instances | every colour, face and look; and the accounts as a standing input, [85-considered-and-declined.md](85-considered-and-declined.md#further-screening-of-social-design-accounts) |
| The request to follow those accounts' links and comments | bios of three of the four, the captions and comment threads of the posts opened | **nothing.** Zero outbound links in any bio, caption or thread read; the only non-Instagram anchors are the platform's own footer. On `ui.ux.jam` 9 of 24 posts gate a link behind commenting a keyword, and the keywords name AI build tools (Replit, Relume, Dreamina, Buzzy, CapCut), none a design reference | nothing to record elsewhere: the resources these accounts name are drawn on video frames or sent by direct message, never written where they can be followed |
| Nine `ui.ux.jam` reels | four read frame by frame, 2026-09-21: `DdWwArCu2wL`, `DdB2dB5OvwC`, `Dc09UoeOz0x`, `DctRY7dt3I0` | ten tools named on the frames, none of them in any text on the page; each is judged in the table below | **Five reels were not extracted.** `DdJmu57IR6j` gates its link behind a comment, and nothing is ever posted from the account used to read it. The video of `Dcd0Q-stjjF`, `DcTl9qAN4Sk` and `DcQ5ySWNlwH` never loaded - `readyState` stayed 0 through a play call, a wait of up to 5 seconds and a click, after four clean loads - and `DcLw91ftPmM` was not attempted. Whatever those five name is not in this system |
| `figma.expert` | ten posts, 2026-09-14 to 2026-09-20 | the four-corner frame as its third independent instance, in the [slide sequence](75-spec-sheet.md#slide-sequence) | every colour: its `Most Expensive Colour Pallet` is refused, [85-considered-and-declined.md](85-considered-and-declined.md#an-unsourced-superlative-as-a-palette-source). All ten advertised files are behind a direct message and none was obtained. Instagram labels the profile `AI-generated profile` |
| An illustration reference image, 430x334 | every pixel, [above](#illustration-measured-rather-than-argued) | the five-value flat construction, measured at 97.59% of the image; its ground hue of 87.36 lands within one degree of the corpus's warm-ground median of 86.5, and its chroma ceiling of 0.0929 sits inside this system's restraint | its values as house colours: garment and ink at hues 257 and 264 sit 60 degrees from `--hw-accent`, and five baked values have no dark-theme answer. The pictogram set is named in [55-iconography.md](55-iconography.md#illustration-one-pictogram-set-and-no-figurative-drawing); figurative illustration stays excluded |
| Mobbin and Refero | the libraries themselves, [below](#what-still-cannot-be-reached) | two taxonomies, as coverage cross-checks only | every screen: one is capped at four apps on a free account, the other was read logged out |

### The ten tools named on the reels

| tool | the reel's own card | verdict | where |
|---|---|---|---|
| `ripplix.com` | "World's Largest UI Animation & Micro Interaction Library" | declined as a motion source, kept as a census of what moves: 7,000+ recordings, and on its open pages no duration, curve or CSS | [the screen](#the-motion-source-screened), [85](85-considered-and-declined.md#ripplix-as-a-motion-source) |
| `osmo.supply` | "the elements, techniques and code behind award-winning work" | **priced, not screened**: 25 euros a month for one seat, code behind the paywall, 20 resources in a free vault | [85](85-considered-and-declined.md#not-yet-screened-and-named-so-the-gap-is-visible) |
| `webzooo.com` | "Website inspiration organized by color" | declined as a design-time input | [85](85-considered-and-declined.md#a-gallery-indexed-by-colour-webzooocom) |
| `Coolors.co` | "for color palettes generations" | declined: a ramp with no contrast target | [85](85-considered-and-declined.md#palette-generators-that-produce-a-ramp-without-a-contrast-target) |
| `Colorkit.io` | "for scaling a color" | declined with `Coolors.co` | [85](85-considered-and-declined.md#palette-generators-that-produce-a-ramp-without-a-contrast-target) |
| `shaders.com` | "The component library for creative WebGPU effects in the browser" | declined by the non-enumerable-ground rule | [85](85-considered-and-declined.md#animated-and-shader-grounds) |
| `ShaderGradient.cc` | "for animated gradients" | declined with `shaders.com` | [85](85-considered-and-declined.md#animated-and-shader-grounds) |
| `jitter.video` | "Helps creative teams design and ship polished animations at scale" | declined as equipment: an editor that exports video, GIF and Lottie | [85](85-considered-and-declined.md#production-equipment-mockups-3d-templates-and-an-animation-editor) |
| `ls.graphics` | "High-end mockups for serious design work" | declined as equipment | [85](85-considered-and-declined.md#production-equipment-mockups-3d-templates-and-an-animation-editor) |
| `ContentCore.xyz` | "3D Mockups and 3D Motion Templates" | declined as equipment | [85](85-considered-and-declined.md#production-equipment-mockups-3d-templates-and-an-animation-editor) |

## Licences, fetched rather than recalled

Each file was fetched from its repository and its first line read.

| set | file | first line |
|---|---|---|
| Lucide | `lucide-icons/lucide/main/LICENSE`, 3208 bytes | `ISC License` |
| Phosphor | `phosphor-icons/core/main/LICENSE`, 1071 bytes | `MIT License` |
| Tabler | `tabler/tabler-icons/main/LICENSE`, 1073 bytes | `MIT License` |
| Heroicons | `tailwindlabs/heroicons/master/LICENSE`, 1071 bytes | `MIT License` |
| Feather | `feathericons/feather/main/LICENSE`, 1082 bytes | `The MIT License (MIT)` |
| Octicons | `primer/octicons/main/LICENSE`, 1068 bytes | `MIT License` |
| Radix Icons | `radix-ui/icons/master/LICENSE`, 1063 bytes | `MIT License` |
| Carbon | `carbon-design-system/carbon/main/LICENSE`, 11339 bytes | `Apache License` |

## What still cannot be reached

Four sources were asked for in the first capture pass and could not be rendered, so no measured value in this system is attributed to any of them.
Two later yielded a taxonomy, and a taxonomy is all this system takes from them.

- **Mobbin.** `mobbin.com/browse/ios/apps` redirects to a sign-in wall.
  A signed-in free account shows the four latest apps and redirects every deep URL back to them; its 23-name taxonomy of screens, elements and flows is used only as a coverage cross-check, in the [manifest](05-coverage.md#the-cross-check-manifest).
- **Refero.** `refero.design` serves its own marketing page logged out and `refero.design/web` returns its 404.
  Its 15-name page-type taxonomy is used the same way.
  Its logged-out page advertises a **Refero MCP** - 142,000+ screens, Pro only, at 999 rupees a quarter when read on 2026-09-21 - which would remove the browser dependency for design references; it is a subscription nobody has taken, so it has not been evaluated.
- **height.app**, which reset the connection on both attempts.
- **eightshapes.com**, whose name did not resolve.

They can be added.
Doing so would change the reference tables above and could change the accent hue, and that is a revision this system is built to take rather than a reason to have waited: hue is one argument to the token build, and the build re-verifies the whole matrix.

Solve to the requirement. Checking afterwards only tells you what you already shipped.

# Layout

A framework that cannot lay out a page is not one.
This section is the grid, the breakpoints, the container widths, the reading measure, and the two page shapes these products actually build.

Every number here was read off live pages rather than recalled.
The capture is 44 sites at 1440x900, described in [90-evidence.md](90-evidence.md); where a number comes from the breakpoints declared in a site's own stylesheets, the count is of sites, not of rules.

## The grid

**Twelve columns above `--hw-bp-lg`, six between `--hw-bp-md` and `--hw-bp-lg`, four below it.**
One gutter, `--hw-column-gap` at 24px, at every width.
Columns are fluid; the gutter is not.

Twelve is not a convention borrowed on faith.
Of the grids sampled in the capture, 58 declare twelve columns, more than any count above six; the counts below it are one column (150 grids) and two (107), which are what a twelve-column grid collapses to rather than a different system.
Twelve divides by 2, 3, 4 and 6, which is what makes a half, a third, a quarter and a sixth all expressible without a second grid.

The gutter is 24px because it is the largest common column-gap that stays on the 4px scale at every step: measured gaps in the capture run 8px (162 uses), 16px (149), 12px (101), 24px (93), 10px (83) and 20px (62).
The 10px and 20px values are off a 4px grid and are exactly the drift [30-space-radius-elevation.md](30-space-radius-elevation.md) exists to stop.

```css
.hw-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--hw-column-gap);
}
@media (min-width: 768px)  { .hw-grid { grid-template-columns: repeat(6,  minmax(0, 1fr)); } }
@media (min-width: 1024px) { .hw-grid { grid-template-columns: repeat(12, minmax(0, 1fr)); } }
```

`minmax(0, 1fr)` rather than `1fr` is load-bearing.
A bare `1fr` track has an automatic minimum of `min-content`, so one long unbroken string, a hash or a URL, silently widens its column and pushes the grid past the viewport.

## Breakpoints

Five, named for what they are rather than for a device.

| token | value | what changes at it | how many of 44 declare it |
|---|---:|---|---:|
| `--hw-bp-sm` | 600px | nothing structural. The floor below which a screen is one column and the rail is a sheet | 4 |
| `--hw-bp-md` | 768px | four columns become six. Page margin goes 16px to 24px. A two-pane screen may split | 23 |
| `--hw-bp-lg` | 1024px | six columns become twelve. The rail becomes permanent. Page margin goes 24px to 32px | 18 |
| `--hw-bp-xl` | 1280px | the content column stops growing and the margins take the rest | 12 |
| `--hw-bp-2xl` | 1600px | only a wide table or a three-pane shell uses the extra width. Prose never does | 3 |

768px and 1024px are the two most declared min-widths in the whole capture, by a clear margin: 23 sites and 18 sites of 44.
The next three are 640px (13), 1280px (12) and 480px (11).
The system takes 768 and 1024 as its two structural breakpoints because that is where the field agrees, and a product whose breakpoints agree with the field is one whose components survive being dropped into someone else's page.

Counting by band rather than by exact value says the same thing more strongly: 28 of 44 sites declare something between 700 and 860, and 27 declare something between 860 and 1100.

Three rules:

- **Breakpoints are min-width only.**
  Mixing `min-width` and `max-width` in one system produces a 767px-to-768px gap that nothing matches, and that gap is always found by a user rather than by a test.
- **A component never declares a breakpoint.**
  It declares a container query or it takes its layout from the grid it was placed in.
  A card that rearranges itself at 768px is wrong twice in a sidebar 320px wide.
- **Never add a sixth breakpoint to fix one screen.**
  That screen has a layout problem, and a sixth breakpoint moves it rather than fixing it.

## Page margin

| from | to | token | value |
|---|---|---|---:|
| 0 | `--hw-bp-md` | `--hw-gutter-sm` | 16px |
| `--hw-bp-md` | `--hw-bp-lg` | `--hw-gutter-md` | 24px |
| `--hw-bp-lg` | up | `--hw-gutter-lg` | 32px |

Measured at a 390px viewport, where nothing is centred and the number is unambiguous, the left offset of the first heading was 16px on 6 of 12 sites (Stripe, Carbon, GOV.UK at 15px, USWDS, joshwcomeau.com, Raycast), 24px on 3 (Linear at 23px, Vercel, shadcn/ui) and 33 to 36px on 2 (GitHub, Primer).
Tailwind's own site sets 0 and lets its content blocks carry the inset.

16px is the floor and it is a floor, not a preference: below it a thumb resting on the edge of a phone overlaps the first character of every line.

## Container widths

| token | value | for |
|---|---:|---|
| `--hw-container-app` | 1440px | the app shell. Past it the content pane stops and the window grows around it |
| `--hw-container-page` | 1200px | a marketing or documentation page |
| `--hw-container-prose` | 720px | a reading column standing on its own |

The 1100-1300 band is the most occupied in the capture: 20 of 44 sites cap a container inside it, against 10 in 1300-1500, 10 in 700-900 and 6 in 900-1100.
1280px alone is the single most common exact cap, on 7 sites.
1200px sits in the middle of that band and divides by 12 into a whole number of columns after gutters, which 1280px does not.

720px for prose is the measured median, not a round number.
Across the twelve sites measured at four viewport widths, the running-text column at 1440px landed at 566, 640, 686, 697, 720, 722, 768, 786, 838 and 856px: median 721px.

## Measure

Measure is stated in `ch` because a pixel width means nothing until the face is known.

| context | token | value |
|---|---|---:|
| running text inside product UI | `--hw-measure-ui` | 56ch |
| long-form: docs, release notes, reports | `--hw-measure-prose` | 68ch |

Measured as rendered paragraph width divided by the width of `0` in that paragraph's own font, across 30 sites that carry paragraphs over 120 characters, the medians run from 25ch to 112ch with a median of 64ch.
The tight end is docs-site body cells that are not really prose: Lightning 25ch, Primer 27ch, Material 3 28ch.
The loose end is a genuine defect: Ant Design at 112ch and Dinamo at 88ch are past the point where the eye reliably finds the next line.

68ch sits above the median and below the point where return sweeps start to fail.
56ch is tighter because product UI text is read in glances between controls, not in passes.

**A container width and a measure are not the same constraint and a page needs both.**
A 1200px container with no measure produces 140-character lines on a wide monitor; a 68ch measure with no container produces a 680px page on a 2560px screen with everything jammed left.

## The two shapes we build

### The app shell

A permanent rail and a content pane, which is what quoth, treadling, foliot and gates all are.

```text
>= 1024px                                  < 1024px
+--------+-----------------------------+   +-----------------------------+
| rail   | content pane                |   | header (rail is a sheet)    |
| 248px  | max 1440px, centred past it |   +-----------------------------+
|        | 32px margin                 |   | content pane                |
|        |                             |   | one column, 16px margin     |
+--------+-----------------------------+   +-----------------------------+
```

- The rail is `--hw-rail` at 248px on `--hw-surface-sunken`, with a single `--hw-border` hairline against the pane and no shadow.
  It is a well, not a floating panel: see [50-surface-texture.md](50-surface-texture.md).
- Below `--hw-bp-lg` the rail leaves the layout entirely and returns as a dismissible sheet at `--hw-z-rail`, which is the one time it earns a shadow.
- `--hw-rail-collapsed` at 56px is the only other rail state, and it shows icons with their labels in tooltips.
  There is no half-width rail and no resizable splitter: a splitter is a per-user layout the product then has to store, migrate and support.
  [05-coverage.md](05-coverage.md) carries the window splitter as an excluded row. It did not for
  three rounds, and that single escape is what `tools/check-coverage.py`'s fourth rule now exists
  to catch.
- The content pane carries the page margin, the rail does not.
  The rail's own inset is `--hw-space-8` because it is a list, not a page.
  What goes **inside** the rail - the item height, its current state, grouping, nesting depth and
  the skip link that lets a keyboard past it - is [37-navigation.md](37-navigation.md).
- A toolbar pinned to the top of the pane sits at `--hw-z-sticky` on `--hw-surface` with its bottom border, never transparent over scrolling content.
  Its height, item spacing, separator and overflow rule are in [37-navigation.md](37-navigation.md).

### The marketing or documentation page

```text
+---------------------------------------------+
| header, full width, content inset to 1200    |
+---------------------------------------------+
| section: content at 1200px, 12 columns       |
+---------------------------------------------+
| section: prose at 720px, left-aligned        |
+---------------------------------------------+
| section: full-bleed surface, content at 1200 |
+---------------------------------------------+
```

- Sections alternate their **ground**, never their alignment.
  A full-bleed `--hw-surface-sunken` band behind a 1200px content block is the only sanctioned way to mark a section change.
- Prose sits at `--hw-container-prose`, left-aligned within the 1200px container rather than centred in the viewport, so the eye keeps one left edge down the whole page.
- **Vertical rhythm varies and that is the point.**
  A section is `--hw-space-48`, `--hw-space-64` or `--hw-space-96` on its vertical padding depending on what it carries, and a page that uses one of those three for every section reads as generated.
  That failure has its own row in [80-anti-patterns.md](80-anti-patterns.md).
- A documentation page adds a third column, the on-page table of contents, only above `--hw-bp-xl`, and drops it rather than shrinking it below that.
  Its width, depth limit, active-section rule and scroll-spy behaviour are in
  [37-navigation.md](37-navigation.md); the header and footer of a page with no rail are there too.

## Layering

Seven layers, and a number that is not on this list is a layer nobody decided on.

| token | value | what sits there |
|---|---:|---|
| `--hw-z-base` | 0 | page content |
| `--hw-z-sticky` | 100 | a sticky table head, a pinned toolbar |
| `--hw-z-rail` | 200 | the rail when it overlays content below `--hw-bp-lg` |
| `--hw-z-dropdown` | 300 | menu, select, popover, tooltip |
| `--hw-z-scrim` | 400 | the dialog scrim |
| `--hw-z-dialog` | 500 | the dialog itself |
| `--hw-z-toast` | 600 | toasts, which must clear a dialog because they report what the dialog did |

The gaps are 100 so a product can slot one layer in without renumbering, and the fact that it had to is a gap to report.

Lay the page out on the grid, then let the content decide how tall it is.

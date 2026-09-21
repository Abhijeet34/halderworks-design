# Iconography

One licence-clean open set, one grid, one stroke weight, one alignment rule.

## The set: Lucide

**Lucide**, at <https://lucide.dev>, under the **ISC licence**.

The licence was verified by fetching the file rather than recalled: `raw.githubusercontent.com/lucide-icons/lucide/main/LICENSE` returns 3208 bytes beginning `ISC License`.
ISC is a permissive two-clause licence, functionally equivalent to MIT, and it permits use in a closed product with attribution kept in the source.

The alternatives were screened on the same basis, and their licences fetched the same way:

| set | licence | grid | why not |
|---|---|---|---|
| **Lucide** | ISC | 24, stroke 2, round caps and joins | **chosen** |
| Phosphor | MIT | 256 | a 256 grid means hinting decisions were made for a size we do not use, and the weight axis is five variants we would have to pick one of anyway |
| Tabler | MIT | 24, stroke 2 | a genuine alternative. Lucide is chosen on continuity: it is the Feather line, which is the drawing style closest to Public Sans' terminals |
| Heroicons | MIT | 24, stroke 1.5 | two sets, outline and solid, and its 20px "mini" set is a second grid |
| Feather | MIT | 24, stroke 2 | unmaintained since 2020. Lucide is its maintained fork |
| Octicons | MIT | 16 and 24 | drawn for GitHub's own vocabulary, which is not ours |
| Carbon | Apache-2.0 | 32, filled | filled rather than stroked, and a filled set beside a 400-weight text face reads heavier than the text |

**No mark is drawn here.**
There is no logomark and no wordmark, because a mark is a commission rather than something an agent invents. <!-- covered-by: Logomark and wordmark -->
That is unchanged from the first pass and is correct.

A set is a choice a system makes once.
Drawing our own icons is not on the table: an interface needs roughly 200 of them before it stops asking for one it lacks, and 200 icons drawn to a consistent optical weight is a body of work with no connection to what these products do.

## The grid and the sizes

| token | value | where |
|---|---:|---|
| `--hw-icon-sm` | 14px | inside a badge, or beside 12px `label` text |
| `--hw-icon` | 16px | the default |
| `--hw-icon-lg` | 20px | a toolbar or rail icon carrying its own hit target |

16px is the most widely used rendered icon size in the 44-site capture, on 21 sites; 24px follows on 18 and 20px on 15.
24px is not a size in this system: at 15px body text a 24px icon is a picture beside a sentence.

Every icon sits on a **16px box on the 4px grid**, whatever its rendered size, so an icon slot never shifts the baseline of the row it is in.

## Stroke weight, which is the part that is usually got wrong

**The painted stroke is 1.5px at every size.**

Lucide is drawn on a 24-unit grid with `stroke-width="2"`, which is confirmed by reading the files: all nine fetched icons carry `viewBox="0 0 24 24"`, `stroke-width="2"`, `stroke-linecap="round"`, `stroke-linejoin="round"`, `fill="none"` and `stroke="currentColor"`.

Rendered at 16px unchanged, that 2-unit stroke paints **1.31px**, measured by rasterising the icon at 8x and summing alpha coverage across the stroke.
That is thinner than the system wants beside 13px and 15px text.

So the stroke attribute is scaled to hold the painted weight constant:

```text
stroke-width = 1.5 x 24 / rendered-size

14px icon -> 2.571
16px icon -> 2.25      measured painted stroke: 1.500px
20px icon -> 1.8
```

```css
.hw-icon {
  width: var(--hw-icon); height: var(--hw-icon);
  stroke: currentColor; fill: none;
  stroke-width: calc(var(--hw-icon-stroke) * 24 / var(--hw-icon));
  stroke-linecap: round; stroke-linejoin: round;
}
```

A constant painted stroke across sizes is the optical rule, not a constant attribute.
An icon set rendered at three sizes with one `stroke-width` gives you three different line weights on one screen, and that is what makes an icon row look assembled rather than drawn.

`vector-effect: non-scaling-stroke` looks like the one-line answer and was tested: rasterised, it tracked the raster scale rather than CSS pixels and painted 0.187px where 1.5px was asked for, so the system does not rely on it.

## Corners and terminals

Round caps and round joins, which is Lucide's own drawing and the measured majority: `stroke-linecap: round` appears 868 times across 16 sites in the capture against 106 `butt`, and `stroke-linejoin: round` 866 times across 14 sites against 108 `miter`.

Do not restyle a Lucide icon's caps.
A round-capped set with square caps forced on is a set whose corner radii were drawn for a terminal that is no longer there.

## Colour

`stroke: currentColor`, always.
An icon inherits whatever text token it sits in, so an icon beside `hw-text-secondary` is secondary and an icon inside a `danger` badge is danger, with no icon-colour token anywhere in the system.

**An icon is never the only carrier of a state.**
That rule is in [15-color-combinations.md](15-color-combinations.md) for colour and it applies identically here.

## Alignment against text

This is the rule that makes icon rows look drawn rather than dropped in.

- **Align to the cap height, not to the line box.**
  `vertical-align: -0.125em` on a 16px icon beside 15px text puts the icon's optical centre on the text's optical centre.
  A `vertical-align: middle` icon sits visibly high, because `middle` is the x-height midpoint plus half the ex-height, not the cap-height midpoint.
- **Use `--hw-icon-gap` at 6px between an icon and its own label.**
  This is deliberately off the 4px unit: at 4px the pair reads as one object and the icon looks like a glyph, at 8px it reads as two objects.
  It is the **only value in this system chosen against two named bounds** rather than derived from a height or a scale.
  It was for three rounds described as the second of exactly two off-unit values; counted, there are **seven** across the families the unit governs, and [32-rhythm.md](32-rhythm.md) lists all seven with the reason each one cannot be on it.
- **An icon-only control needs an accessible name and a tooltip**, and it is only allowed in a toolbar or a rail.
  Everywhere else the icon sits beside a label.

An icon that needs a legend is a label that should have been written.

## What an icon may not be

- **Decorative.** An icon that repeats its own heading, a clipboard beside "Records" or a rocket beside "Get started", is noise with a colour.
  It has a row in [80-anti-patterns.md](80-anti-patterns.md).
- **An illustration.** An icon is never scaled up to stand in for a drawing. The one illustration
  set is a pictogram set with its own sizes and rule, in the section below.
- **An emoji.** Never, anywhere, in any product surface.

## Illustration: one pictogram set, and no figurative drawing

Four files in this book carried a rule about illustration, and three of them carried the same sentence:

> no illustration set exists and inventing one per empty state is how a product ends up with six
> unrelated drawings <!-- covered-by: Pictograms, the one illustration set -->

**Read as written, its first half is the gap restated and its second half argues for a coherent set
rather than against one.** The sentence forbids improvisation. It contains no argument against a
set, and it had been read as one for three rounds.

What the field ships was then measured rather than characterised, and it splits on one axis that
is not style: **whether an illustration carries colour of its own.**

| | a monochrome pictogram set | a flat multi-colour set |
|---|---|---|
| colours per asset | **1**, inherited from `currentColor` | **5**, baked into the asset |
| palette cost | **zero** | a five-value sub-palette certified against every ground it sits on |
| dark theme | free, by construction | no answer. A cream at `oklch(0.9577)` on this system's dark ground is a light rectangle |
| governance shipped | 44 categories, aliases on 1,574 of 1,575, deprecations naming their replacement | none in any of the three libraries screened |
| licence | Apache-2.0 | CC0, or - for the closest style match - a licence that forbids redistribution in packs |

**A pictogram is not an icon at a larger size**, which matters because this file already rejected
one vendor's *icon* set for being filled. Measured across 400 files, the pictogram line is 0.72 on
a 32 grid, **2.25% of its frame**, against Lucide's 2 on 24 at **8.33%** - 3.7x finer relative to
its frame. That is what makes it illustration-class, drawn for a 48 to 96px block, and what makes
it invisible at `--hw-icon` 16px. It is a different package and it does not compete with Lucide.

**The set is `@carbon/pictograms`**, Apache-2.0, measured at version 12.84.0 in
[90-evidence.md](90-evidence.md#illustration-measured-rather-than-argued).
It is named here the way the typefaces and Lucide are named, and it is not vendored: a product that
uses a pictogram installs the package itself, and this repository stays free of dependencies.

| what it fixes | value |
|---|---|
| size | `--hw-space-48` or `--hw-space-64`, which paint the 0.72 line at 1.08px and 1.44px |
| never | at `--hw-icon` 16px, where the same line paints 0.36px and disappears. A pictogram is never an icon |
| colour | `currentColor`, inherited from `--hw-text-secondary`, 6.37:1 light and 7.01:1 dark on `--hw-ground`. It takes the surrounding text colour by construction and brings no colour of its own |
| where | the **nothing yet** kind of [empty state](65-components.md#emptystate-the-three-kinds-which-are-not-interchangeable), and a section of a marketing page. Never in a control, a row, a table or a toast |
| how many | one per view, from this set only |
| markup | `aria-hidden="true"`, because the words beside it carry the meaning and the drawing repeats them |

That keeps the rule above standing for its own reason, which no set removes: one drawing per screen,
chosen from anywhere by whoever built the screen, is the failure, and a licensed set does not
prevent it. **A set plus a rule does**, and this is the set and the rule.

**Figurative illustration stays excluded.** A figurative set would carry its own colours, and the
only construction measured has five baked values and no dark-theme answer. If one is ever
commissioned it brings its palette through [a product's own namespace](95-extending.md#a-products-own-namespace),
never through an `hw-` token. Whether to commission one is an
[open decision](05-coverage.md#open-decisions).

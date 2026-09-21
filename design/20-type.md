# Type

Three faces with three jobs, each an open-licensed file a product hosts itself, so no screen waits on a font service.

| role | face | what it does |
|---|---|---|
| interface and text | **Public Sans** | every screen, every control, every paragraph of product copy |
| display | **Newsreader** | the two largest steps, on marketing, docs and release surfaces only |
| machine output | **IBM Plex Mono** | hashes, run ids, timestamps, durations, costs, CLI output, code |

## Why not Inter

Inter is the safe answer, and five of the fourteen reference products use it: Linear, Family, Railway, Superlist and Resend all set their body in it.
That is exactly why it is not the house face. A system whose type is the most common choice in its own category has spent nothing on identity.

Public Sans is a Libre Franklin derivative drawn for the US Web Design System, which means it was designed for dense public-information interfaces rather than for a marketing page.
None of the fourteen references use it.

It costs one adjustment, and here is the number. Measured in a real browser with the faces loaded, at 100px:

| face | x-height | cap height | x/cap | width of a 35-character line |
|---|---:|---:|---:|---:|
| Public Sans | 51.7 | 72.3 | 0.715 | 1563 |
| Inter | 54.6 | 72.8 | 0.750 | 1594 |
| Libre Franklin | 53.0 | 74.2 | 0.714 | 1561 |
| Newsreader | 44.0 | 67.6 | 0.651 | 1425 |
| IBM Plex Mono | 51.6 | 69.8 | 0.739 | 2100 |
| JetBrains Mono | 55.0 | 73.0 | 0.753 | 2100 |

Public Sans has a 5.3% smaller x-height than Inter, so it reads about half a step smaller at the same size.
That is why the product body step here is **15px, not 14px**, and the dense step is 13px rather than 12px.
Set Public Sans at Inter's sizes and it will look thin and slightly too small, and you will blame the face instead of the size.

## Why these fallbacks

The fallback stacks were chosen on measured metrics rather than on familiarity.

- **Public Sans falls back to Libre Franklin**, its own parent, which sets a 35-character line within 0.2% of it (1561 against 1563). A fallback flash barely reflows the page.
- **IBM Plex Mono falls back to JetBrains Mono**, which shares its 0.6em advance exactly (600 against 600 at 100px), so a column of digits keeps its width through the swap.
- **Newsreader falls back to Iowan Old Style and Source Serif 4**, both low-contrast reading serifs at similar proportions. It is display-only, so a few percent of drift costs nothing.

## Figures, which is the rule most often missed

Public Sans ships proportional figures by default, and the spread is large: at 100px, `1111111111` measures 407px while `0000000000` measures 606px. A `1` is a third narrower than a `0`.

A column of durations, costs, counts or timestamps set without `font-variant-numeric: tabular-nums` will visibly jitter row to row.

**Every number that sits in a column, or that a reader will compare against the number above it, gets `tabular-nums`.** Running prose keeps the proportional figures, which are better inside a sentence.

Newsreader's figures are already tabular (567 against 567), and a monospace face is tabular by construction.

## The scale

Nine distinct sizes. Both display steps use Newsreader; everything else uses Public Sans.
The one exception is [the mixed-face headline](75-spec-sheet.md#the-mixed-face-headline), a display step set in Public Sans around one Newsreader term.

| step | size | line-height | tracking | weight | where |
|---|---:|---:|---:|---:|---|
| `display-1` | 56px | 1.02 | -0.022em | 500 | one page-defining headline, marketing or release only |
| `display-2` | 40px | 1.08 | -0.020em | 500 | a section opener on a marketing surface |
| `title-1` | 28px | 1.15 | -0.018em | 600 | the screen's own name, one per screen |
| `title-2` | 21px | 1.25 | -0.012em | 600 | a section inside a screen |
| `title-3` | 17px | 1.35 | -0.006em | 600 | a card header or a form group |
| `body-lg` | 17px | 1.6 | 0 | 400 | long-form running text in docs and release notes |
| `body` | 15px | 1.55 | 0 | 400 | the default for product UI |
| `body-sm` | 13px | 1.5 | 0 | 400 | table cells, list rows, control labels, help text |
| `label` | 12px | 1.35 | 0.01em | 500 | a control's own label, a hint, a badge |
| `micro` | 11px | 1.2 | 0.06em | 600 | column heads and eyebrows, set uppercase |

17px appears twice on purpose: `title-3` and `body-lg` are the same size doing different jobs, separated by weight and line-height.
Nothing smaller than 11px exists. If 11px is too big for the space, the space is wrong.

The display tracking is not a taste call either. Measured across the reference set, display type is set between -0.010em and -0.060em with the cluster at -0.020em: Linear -0.022, 21st.dev -0.022, Family -0.020, Superlist -0.020, Stripe -0.020, Railway -0.036.
Display line-height in the same set runs 0.909 to 1.20. Both steps here sit inside those ranges.

## Measure

| context | measure | evidence |
|---|---|---|
| product UI text | **56ch** | reference product columns measure 29 to 45ch, which is too narrow for a settings description; 56ch is the top of comfortable and the bottom of long-form |
| long-form: docs, release notes, reports | **68ch** | measured on five documentation sites: Stripe 50ch, shadcn 64ch, Radix 67ch, Tailwind 76ch, Vercel 80ch, median 67ch |

Measure is a real `ch` measurement of the rendered paragraph divided by the width of `0` in its own font, not a character count, because a character count means nothing for a proportional face.

## A brand's faces

A brand may name its own display face and its own text face ([12-brand.md](12-brand.md#the-eleven-inputs)); the mono face is the house's in every product, so every hash and timestamp is set alike.
A face is an entry in the roster in `tokens/tokens.seed.json`, and an entry is a face **plus its delivery**:

- **self-hosted**: the product ships the file. The roster cites the upstream file by URL and pins its sha256, so the metrics below were read from a file a reader can fetch and check.
- **system**: a named stack that loads nothing, for a product that makes no network request and ships no font, which is what papertrace's report and pointback's chrome both promise.

| roster entry | delivery | x-height, read from the file | upstream file |
|---|---|---:|---|
| Public Sans | self-hosted | 0.517 | [PublicSans[wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/publicsans/PublicSans%5Bwght%5D.ttf) |
| Newsreader | self-hosted | 0.426 | [Newsreader[opsz,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/newsreader/Newsreader%5Bopsz,wght%5D.ttf) |
| Bricolage Grotesque | self-hosted | 0.528 | [BricolageGrotesque[opsz,wdth,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/bricolagegrotesque/BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf) |
| Instrument Sans | self-hosted | 0.510 | [InstrumentSans[wdth,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentsans/InstrumentSans%5Bwdth,wght%5D.ttf) |
| system serif | system | | `"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif` |
| system sans | system | | `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` |

All four files are under the SIL Open Font License 1.1, read from each family's `OFL.txt` upstream; the repository vendors none of them.
The x-heights are the fonts' own `OS/2` values at their default instance: Newsreader reads 0.426 from its file against 44.0 in the browser table above, a variable face whose optical-size axis the browser sets per size, and the build uses no x-height but Public Sans's.
Public Sans reads 0.517 from its file and 51.7 in the browser, the same number two ways, which is what makes the file reading trustworthy.

**A text face other than Public Sans is held to Public Sans's x-height.**
Every size in the scale above was derived from that x-height, so a text face with a smaller one would set every row half a step small.
A brand whose text face differs gets `font-size-adjust: 0.517` on every `.hw-*` type class of the text family in its `tokens.css`, which scales whatever face renders, a system face included, until its x-height is the house's.
A product that sets `--hw-font-sans` outside those classes sets the same declaration beside it.

```bash
python3 tools/faces.py --check PublicSans[wght].ttf    # the file's x-height and sha256 against its roster entry
```

The display face is a brand's to choose because it is the one face the brand is recognised by; the text face is a brand's too, because quoth already ships Instrument Sans as its interface and papertrace sets its report in a serif, and a tier that took either away would delete an identity each product already has.

## Rules

- **Weight carries hierarchy before size does.** 400 for text, 500 for a label or a control, 600 for a heading. 700 exists in the variable font and this system does not use it.
- **Uppercase is only for `micro`**, and only for a column head or an eyebrow. An uppercase button label is shouting.
- **Italic is for a term being defined or a quoted title**, never for emphasis. Emphasis is weight. In a mixed-face headline the face does the italic's job, and the term is not also italic.
- **Headings get `text-wrap: balance`.** Long body text does not; balancing a paragraph makes its last lines ragged.
- **Never letterspace lowercase text positively**, except `label` at 0.01em, which is there to keep 12px from closing up.

Set type to be read for an hour, not to be seen for a second.

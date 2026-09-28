# Type

Three faces with three jobs in the house set, each an open-licensed file a product hosts itself, so no screen waits on a font service; a brand fills the same roles, and an optional fourth, from [the roster](#a-brands-faces).

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

A brand fills four roles from the roster ([12-brand.md](12-brand.md#the-inputs)), and names any it leaves to the house:

| role | input | house face | what it sets |
|---|---|---|---|
| display | `display` | Newsreader | the display steps, from `display-2` up or, with `displayFrom: title-1`, from `title-1` up |
| text | `text` | Public Sans | every other step |
| mono | `mono` | IBM Plex Mono | machine output, and the numbers and labels of a brand whose mono is its identity; a monospaced face only |
| quote | `quote` | none | the words a person said or wrote, through `.hw-quote` inside a step class; optional |

The mono face is one per product, so every hash and timestamp on a screen is set alike; it stopped being one for the fleet when quoth's Field identity took Martian Mono as its voice (D-039 in quoth's record), and the roster refuses a proportional face in the role: an entry says `monospaced`, `tools/faces.py --check` holds that claim to the file's own `post.isFixedPitch`, and the build takes nothing else as `mono`.
`displayScale` multiplies `display-1` and `display-2` by 0.9, 1.0 or 1.25, to whole px, 70px and 50px at the top; every step below them was derived from the text face's x-height and does not move.

A face is an entry in the roster in `tokens/tokens.seed.json`, and an entry is a face **plus its delivery**:

- **self-hosted**: the product ships the file. The roster cites the upstream file by URL and pins its sha256, and cites the family's `OFL.txt` and pins that too, so the metrics below were read from a file a reader can fetch and check and the licence that ships beside it is the one the roster read.
- **system**: a named stack that loads nothing, for a product that makes no network request and ships no font, which is what papertrace's report and pointback's chrome both promise.

An entry may also carry a width or a style, which the build writes beside the family in every class that sets it: **Archivo Expanded** is Archivo's own file at `font-stretch: 125%`, the named instance at the end of its width axis, and **Instrument Serif Italic** sets `font-style: italic`.
Field's renders set its screen title at 110%, its welcome headline at 112% and, after the refresh that followed D-039, its site headline at 125%; the roster carries the one wide width, and a product that needs a narrower one for titles has found a gap, not a value to set by hand.

| roster entry | delivery | x-height, read from the file | upstream ships | upstream file | licence text | upstream repository |
|---|---|---:|---|---|---|---|
| Public Sans | self-hosted | 0.517 | ttf, otf | [PublicSans[wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/publicsans/PublicSans%5Bwght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/publicsans/OFL.txt) | [uswds/public-sans](https://github.com/uswds/public-sans) |
| Newsreader | self-hosted | 0.426 | ttf, woff, woff2 | [Newsreader[opsz,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/newsreader/Newsreader%5Bopsz,wght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/newsreader/OFL.txt) | [productiontype/Newsreader](https://github.com/productiontype/Newsreader) |
| IBM Plex Mono | self-hosted, monospaced | 0.516 | ttf, otf, woff, woff2 | [IBMPlexMono-Regular.ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/OFL.txt) | [IBM/plex](https://github.com/IBM/plex) |
| Bricolage Grotesque | self-hosted | 0.528 | ttf, otf, woff2 | [BricolageGrotesque[opsz,wdth,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/bricolagegrotesque/BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/bricolagegrotesque/OFL.txt) | [ateliertriay/bricolage](https://github.com/ateliertriay/bricolage) |
| Instrument Sans | self-hosted | 0.510 | ttf, otf, woff2 | [InstrumentSans[wdth,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentsans/InstrumentSans%5Bwdth,wght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentsans/OFL.txt) | [Instrument/instrument-sans](https://github.com/Instrument/instrument-sans) |
| Archivo | self-hosted | 0.526 | ttf, otf, woff2 | [Archivo[wdth,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth,wght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/OFL.txt) | [Omnibus-Type/Archivo](https://github.com/Omnibus-Type/Archivo) |
| Archivo Expanded | self-hosted, at 125% | 0.526 | ttf, otf, woff2 | the same file | the same, [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/OFL.txt) | the same, [Omnibus-Type/Archivo](https://github.com/Omnibus-Type/Archivo) |
| Figtree | self-hosted | 0.500 | ttf, otf, woff2 | [Figtree[wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/figtree/Figtree%5Bwght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/figtree/OFL.txt) | [erikdkennedy/figtree](https://github.com/erikdkennedy/figtree) |
| Atkinson Hyperlegible Next | self-hosted | 0.496 | ttf, otf, woff2 | [AtkinsonHyperlegibleNext[wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/atkinsonhyperlegiblenext/AtkinsonHyperlegibleNext%5Bwght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/atkinsonhyperlegiblenext/OFL.txt) | [googlefonts/atkinson-hyperlegible-next](https://github.com/googlefonts/atkinson-hyperlegible-next) |
| Shantell Sans | self-hosted | 0.485 | ttf, otf, woff2 | [ShantellSans[BNCE,INFM,SPAC,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/shantellsans/ShantellSans%5BBNCE,INFM,SPAC,wght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/shantellsans/OFL.txt) | [arrowtype/shantell-sans](https://github.com/arrowtype/shantell-sans) |
| Fraunces | self-hosted | 0.482 | ttf, otf, woff2 | [Fraunces[SOFT,WONK,opsz,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/OFL.txt) | [undercasetype/Fraunces](https://github.com/undercasetype/Fraunces) |
| Literata | self-hosted | 0.507 | ttf, woff2 | [Literata[opsz,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/literata/Literata%5Bopsz,wght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/literata/OFL.txt) | [googlefonts/literata](https://github.com/googlefonts/literata) |
| Instrument Serif Italic | self-hosted, italic | 0.510 | ttf, otf, woff2 | [InstrumentSerif-Italic.ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/InstrumentSerif-Italic.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/OFL.txt) | [Instrument/instrument-serif](https://github.com/Instrument/instrument-serif) |
| Martian Mono | self-hosted, monospaced | 0.600 | ttf, otf, woff2 | [MartianMono[wdth,wght].ttf](https://raw.githubusercontent.com/google/fonts/main/ofl/martianmono/MartianMono%5Bwdth,wght%5D.ttf) | [OFL.txt](https://raw.githubusercontent.com/google/fonts/main/ofl/martianmono/OFL.txt) | [evilmartians/mono](https://github.com/evilmartians/mono) |
| system serif | system | | | `"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, "Times New Roman", serif` | | |
| system sans | system | | | `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` | | |

"Upstream ships" is what each family's own repository, named in the entry's `upstream`, publishes, read from its file tree on 2026-09-28; the file the roster pins is always a TTF from `google/fonts`, because `tools/faces.py` reads metrics from an sfnt file and not from a compressed web font.
A native app takes the TTF or OTF: quoth's pill registers Martian Mono with CoreText, which the woff2 a webview loads does not serve, and the pinned `MartianMono[wdth,wght].ttf` is that file with both axes.
A webview or a site takes woff2, converted from the pinned file or taken from upstream, which the OFL permits for every face here with one exception, below.

The x-heights are the fonts' own `OS/2` values at their default instance, and eleven of the thirteen files draw their `x` to that height to three places; Instrument Serif Italic draws it at 0.516 and Shantell Sans at 0.497, an italic's and a hand's overshoot, and the roster keeps the header value the browser's `font-size-adjust` reads. Newsreader reads 0.426 from its file against 44.0 in the browser table above, a variable face whose optical-size axis the browser sets per size.
Public Sans reads 0.517 from its file and 51.7 in the browser, the same number two ways, which is what makes the file reading trustworthy.
Martian Mono's is the outlier, 0.600, with a 0.750em advance against Plex Mono's 0.600em, and its fallbacks are narrower: macOS's own files measure 0.618em for SF Mono and 0.602em for Menlo. A column of its digits reflows by a fifth if the file fails to load, so a product that sets Martian Mono self-hosts it rather than relying on the stack.

**A text face other than Public Sans is held to Public Sans's x-height.**
Every size in the scale above was derived from that x-height, so a text face with a smaller one would set every row half a step small.
A brand whose text face differs gets `font-size-adjust: 0.517` on every `.hw-*` type class of the text family in its `tokens.css`, which scales whatever face renders, a system face included, until its x-height is the house's.
The quote face is held the same way on `.hw-quote`, always, because it sits on a line beside the text face: Instrument Serif's 0.510 and Shantell Sans's 0.485 would otherwise set a spoken line visibly smaller than the typed one beside it.
A product that sets `--hw-font-sans` or `--hw-font-quote` outside those classes sets the same declaration beside it.

```bash
python3 tools/faces.py --check PublicSans[wght].ttf    # the file's x-height, pitch and sha256 against its roster entry
python3 tools/faces.py --check OFL.txt                 # the licence text's sha256 and Reserved Font Name
```

The display face is a brand's to choose because it is the one face the brand is recognised by; the text face is a brand's too, because quoth already ships Instrument Sans as its interface and papertrace sets its report in a serif, and a tier that took either away would delete an identity each product already has.

### The licence rule

**Every roster face is under the SIL Open Font License 1.1.**
`tools/build.py` refuses a roster entry whose `licence` is anything else, and one that pins no licence text, before it solves anything.
The reason is the product-identities scout's licensing survey of 2026-09-22, in [90-evidence.md](90-evidence.md#font-licensing-per-platform): of twelve licence sources read from their own pages, the OFL is the only one that lets the same file ship in a sold Mac app with woff2 in a WKWebView, on iOS, on Windows, on a self-hosted site and in static art, subset and converted, with no fee and no per-app licence.
Adobe Fonts forbids embedding and self-hosting outright, Grilli Type's app licence prohibits `@font-face`, and Apple's and Microsoft's system faces may be named in a stack and never shipped, which is what the two system entries do.
No face is bought: the one paid display face the scout weighed, Klim's, does not publish whether its App licence ships woff2 and forbids reformatting, so the WKWebView path needs the foundry's written answer before it could be considered.

**IBM Plex Mono carries a Reserved Font Name, "Plex", and it is the only roster face that does.**
Its `OFL.txt` opens `Copyright © 2017 IBM Corp. with Reserved Font Name "Plex"`, and the OFL forbids a Modified Version to use a Reserved Font Name without IBM's written permission.
A subset is a Modified Version, so a product that subsets Plex Mono renames the family, in the file's `name` table and in its `@font-face`, to a name without "Plex", and keeps "IBM Plex Mono" in the stack only for the unmodified file.
The roster records the name as `reservedName`, and `tools/faces.py --check OFL.txt` reads it from the licence's first paragraph and refuses a roster that disagrees, so a face that gains a Reserved Font Name upstream is caught when its licence is next checked.
The other twelve licence texts declare none, which `tools/faces.py` reports for each.

## Rules

- **Weight carries hierarchy before size does.** 400 for text, 500 for a label or a control, 600 for a heading. 700 exists in the variable font and this system does not use it.
- **Uppercase is only for `micro`**, and only for a column head or an eyebrow. An uppercase button label is shouting.
- **A mono `micro` is lowercase.** A brand whose mono is its identity may set `micro` in it, as Field's labels are, and then sets it in lowercase: mono capitals are one product's signature, 53.8% of Nothing's labels against 0% on eleven other sites measured for quoth's D-054, and mixed case keeps word shape at 11px.
- **Italic is for a term being defined or a quoted title**, never for emphasis. Emphasis is weight. In a mixed-face headline the face does the italic's job, and the term is not also italic.
- **Headings get `text-wrap: balance`.** Long body text does not; balancing a paragraph makes its last lines ragged.
- **Never letterspace lowercase text positively**, except `label` at 0.01em, which is there to keep 12px from closing up.

Set type to be read for an hour, not to be seen for a second.

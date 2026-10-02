# Type

Three faces with four jobs in the house set, each an open-licensed file vendored in `fonts/` and served from the product's own origin, so no screen waits on a font service; a brand fills the same four families from [the roster](#a-brands-faces).

| family | face | what it does |
|---|---|---|
| `sans`: interface and text | **Archivo** | every screen, every control, every paragraph of product copy |
| `display`: the stage voice | **Archivo** | the stage sizes, on marketing, docs, release surfaces and a stage |
| `read`: running prose | **Literata** | long-form reading text and quoted words |
| `mono`: machine output | **IBM Plex Mono** | hashes, run ids, timestamps, durations, costs, CLI output, code |

## Why Archivo and Literata

Public Sans and Newsreader were the house faces until 2026-10-02, when the maintainer approved the house design review's recommendation to replace them.
quoth already ships Archivo, and its width axis gives a condensed stage voice, the app voice and Archivo Expanded from one 90 KB WOFF2, so a product that sets all three loads one file.
Literata takes the reading job Newsreader held on docs and release surfaces, and IBM Plex Mono stays.

Inter is still not the house face, and for the same reason: five of the fourteen reference products set their body in it, Linear, Family, Railway, Superlist and Resend, and a system whose type is the most common choice in its own category has spent nothing on identity.

Archivo's x-height is 0.526, read from its file, against Inter's 0.546 and Public Sans's 0.517.
The scale was derived from Public Sans's x-height, which is why the product body step is **15px, not 14px**, and the dense step 13px rather than 12px; Archivo's x-height is 1.7% larger than the one the scale was built on, so it sets the same sizes a shade fuller and never smaller.

| face | x-height | cap height | `1111111111` at 100px | `0000000000` at 100px |
|---|---:|---:|---:|---:|
| Archivo | 0.526 | 0.686 | 521.3 | 572.7 |
| Archivo Expanded, at 125% | 0.526 | 0.686 | 642.0 | 739.5 |
| Literata | 0.507 | 0.700 | 407.0 | 602.0 |
| IBM Plex Mono | 0.516 | | 600.0 | 600.0 |

The heights are read by `tools/faces.py` from each roster entry's pinned TTF, whose sha256 matched on 2026-10-02.
The widths were measured the same day in headless Brave from the layout of a span in each vendored file, loaded through `fonts/fonts.css`.
Newsreader, the display face before them, measured a cap height of 0.676 and ten digits of 567px at 100px in the browser.

## Why these fallbacks

The faces are vendored and declared with `font-display: swap`, so a fallback shows only until the file arrives from the product's own origin.

- **Archivo falls back to the platform's interface sans**, `-apple-system`, `Segoe UI` or Roboto, which every product already draws its window chrome in.
- **Literata falls back to Iowan Old Style and Georgia**, both reading serifs at similar proportions.
- **IBM Plex Mono falls back to the platform mono**, SF Mono on macOS at a 0.618em advance and JetBrains Mono or Menlo at 0.600em, against Plex Mono's 0.600em, so a column of digits keeps its width within 3% through the swap.

## Figures

Archivo and Literata both ship proportional figures by default: at 100px a run of ten `1`s is 9% narrower than ten `0`s in Archivo, 521.3px against 572.7px, and a third narrower in Literata, 407px against 602px.
A column of durations, costs, counts or timestamps set without `font-variant-numeric: tabular-nums` visibly jitters row to row.

**Every number that sits in a column, or that a reader compares with the number above it, takes `tabular-nums`**, which the component layer's `.hw-num` class sets, and a numeric table cell is right-aligned as well.
Running prose keeps proportional figures, which read better inside a sentence, and a monospace face is tabular by construction.

## The ramp

Eight steps in rem, in `ramps/scales.css`, with the px each sets at the default text size M:

| step | px at M | for |
|---|---:|---|
| `--hw-text-xs` | 12 | labels, captions, column heads; `max(0.8rem, 11px)`, so never under 11px |
| `--hw-text-sm` | 13 | secondary lines and controls |
| `--hw-text-md` | 15 | content |
| `--hw-text-lg` | 17 | a lead, a row title in a reading view |
| `--hw-text-xl` | 21 | a section title |
| `--hw-text-2xl` | 28 | a page title |
| `--hw-text-3xl` | 36 to 54 | a stage headline, `clamp()`ed against the viewport |
| `--hw-text-4xl` | 48 to 112.5 | a stage poster, `clamp()`ed against the viewport |

Four leadings go with them: `--hw-leading-tight` 1.1 for a stage size and the page title, `--hw-leading-snug` 1.3 for a section heading and a subheading, `--hw-leading` 1.5 for interface text and `--hw-leading-read` 1.62 for running prose.
The two stage sizes are the display face's, and only a stage sets them.

**Nothing renders under 11px**, at any text size: `tests/exports.py` holds every step at S to XXL, and `tests/components.py` refuses text in the component layer smaller than 1em that is not held to 11px with `max()`.
If 11px is too big for the space, the space is wrong.

A screen takes a type style rather than a size and a weight: `components/components.css` sets `.hw-headline`, `.hw-title`, `.hw-heading`, `.hw-subheading`, `.hw-lead`, `.hw-body`, `.hw-small` and `.hw-label`, each a step, a leading, a weight and a tracking together, and its sheets name the style each component uses.
Weight carries hierarchy before size does, so a title is heavier before it is larger.

## The text-size setting

The reader chooses the text size, and everything moves with it.
`data-text-size` on `html` takes five values, and `ramps/scales.css` sets the root size for each as a percentage of the browser's default, so a reader who raised the browser's own default keeps that raise on top:

| `data-text-size` | root at the browser's default 16px |
|---|---:|
| `s` | 13px |
| `m`, the default | 15px |
| `l` | 17px |
| `xl` | 19px |
| `xxl` | 22px |

Type, space, control heights and every component's inner space are in rem or em, so a larger setting grows the box with its text rather than overflowing it.
Page gutters, breakpoints, container widths and the 44px touch floor stay in px, because the viewport decides those, not the text.
`tests/exports.py` holds the five roots and the type floor in every export.

WCAG 2.2's 1.4.4 asks that text resize to 200% without loss.
XXL is 1.47 times M, so XXL plus the browser's own zoom is the route past 200%, and a sixth step is open if a product needs one.
1.4.10, reflow at 320 CSS pixels, is the layout's intent ([30-space.md](30-space.md#layout)) and is certified by no tool here: a screen is looked at that wide before it ships.

## Measure

Running text inside product UI is held to `--hw-measure-ui`, 56ch, and long-form reading text to `--hw-measure-prose`, 68ch, both in `ramps/scales.css`; `.hw-body` and `.hw-lead` set the second.
A measure is in `ch` because a pixel width means nothing until the face is known, and a container width and a measure are separate constraints that a page needs both of.

## A brand's faces

A brand fills four families from the roster with `faces` in its brand file ([12-brand.md](12-brand.md#the-inputs)), and leaves any it does not name to the house:

| family | house face | what it sets |
|---|---|---|
| `sans` | Archivo | every screen, every control, every paragraph of product copy: `--hw-font-sans` |
| `display` | Archivo | the stage sizes: `--hw-font-display`, with its width in `--hw-font-display-stretch` |
| `read` | Literata | running prose and the words a person said or wrote: `--hw-font-read` |
| `mono` | IBM Plex Mono | machine output, and the numbers and labels of a brand whose mono is its identity; a monospaced face only: `--hw-font-mono` |

The mono face is one per product, so every hash and timestamp on a screen is set alike; it stopped being one for the fleet when quoth's Field identity took Martian Mono as its voice (D-039 in quoth's record), and the roster refuses a proportional face in the role: an entry says `monospaced`, `tools/faces.py --check` holds that claim to the file's own `post.isFixedPitch`, and `tools/ramps.py` takes nothing else as `mono`.
The solver's `displayFrom`, `displayScale` and `quote` inputs retired with it; the stage sizes are the house's in every brand, and the reading face carries quoted words.

A face is an entry in the roster in `ramps/roster.json`, and an entry is a face **plus its delivery**:

- **self-hosted**: the product ships the file.
  The roster cites the upstream file by URL and pins its sha256, and cites the family's `OFL.txt` and pins that too, so the metrics below were read from a file a reader can fetch and check and the licence that ships beside it is the one the roster read.
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

The x-heights are the fonts' own `OS/2` values at their default instance, and eleven of the thirteen files draw their `x` to that height to three places; Instrument Serif Italic draws it at 0.516 and Shantell Sans at 0.497, an italic's and a hand's overshoot, and the roster keeps the header value the browser's `font-size-adjust` reads.
Newsreader reads 0.426 from its file against 44.0 measured in a browser at 100px, a variable face whose optical-size axis the browser sets per size.
Public Sans, a roster face and the house's until 2026-10-02, reads 0.517 from its file and 51.7 in the browser, the same number two ways, which is what makes the file reading trustworthy.
Martian Mono's is the outlier, 0.600, with a 0.750em advance against Plex Mono's 0.600em, and its fallbacks are narrower: macOS's own files measure 0.618em for SF Mono and 0.602em for Menlo.
A column of its digits reflows by a fifth if the file fails to load, so a product that sets Martian Mono self-hosts it rather than relying on the stack.

**A sans other than Archivo is held to Archivo's x-height.**
Every size in the scale above was derived from the house face's x-height, so a text face with a smaller one would set every row half a step small.
A brand whose sans differs sets `font-size-adjust: 0.526` beside `--hw-font-sans`, which scales whatever face renders, a system face included, until its x-height is the house's; `tools/ramps.py` names the value in the description of the brand's `--hw-font-sans`.
No export carries it as a value of its own yet, and the type classes that once applied it retired with the solver, so it is a stated gap: a product sets the declaration itself.

```bash
python3 tools/faces.py --check Archivo[wdth,wght].ttf  # the file's x-height, pitch and sha256 against its roster entry
python3 tools/faces.py --check OFL.txt                 # the licence text's sha256 and Reserved Font Name
python3 tools/faces.py --vendored                      # fonts/ holds exactly the pinned files, and fonts.css loads only them
```

The display face is a brand's to choose because it is the one face the brand is recognised by; the sans is a brand's too, because papertrace sets its report in a serif and pointback its chrome in the system sans, and a rule that took either away would delete an identity each product already has.

### The faces the house ships

The three house faces are vendored in `fonts/` as WOFF2, the latin subsets Fontsource 5.3.0 publishes on npm, the same source quoth installs its Archivo from, each beside the `OFL.txt` the roster pins.
`fonts/fonts.css` declares them with `font-display: swap` and relative URLs, so a page loads them from its own origin and nowhere else.
Each roster entry's `vendored` list pins every file by sha256, and `tools/faces.py --vendored`, which CI runs, refuses a changed byte, a licence text off its pin, a file no entry accounts for, and a `fonts.css` that loads anything off its own origin.

### The licence rule

**Every roster face is under the SIL Open Font License 1.1.**
`tools/ramps.py` refuses a roster entry whose `licence` is anything else, and one that pins no licence text, before it builds anything.
The reason is the product-identities scout's licensing survey of 2026-09-22, recorded in [the evidence file as it stood on 2026-10-02](https://github.com/Abhijeet34/halderworks-design/blob/a95ed0fed0c544fc12483031a2066f3eecc6b535/design/90-evidence.md#font-licensing-per-platform): of twelve licence sources read from their own pages, the OFL is the only one that lets the same file ship in a sold Mac app with woff2 in a WKWebView, on iOS, on Windows, on a self-hosted site and in static art, subset and converted, with no fee and no per-app licence.
Adobe Fonts forbids embedding and self-hosting outright, Grilli Type's app licence prohibits `@font-face`, and Apple's and Microsoft's system faces may be named in a stack and never shipped, which is what the two system entries do.
No face is bought: the one paid display face the scout weighed, Klim's, does not publish whether its App licence ships woff2 and forbids reformatting, so the WKWebView path needs the foundry's written answer before it could be considered.

**IBM Plex Mono carries a Reserved Font Name, "Plex", and it is the only roster face that does.**
Its `OFL.txt` opens `Copyright © 2017 IBM Corp. with Reserved Font Name "Plex"`, and the OFL forbids a Modified Version to use a Reserved Font Name without IBM's written permission.
A subset is a Modified Version, so a product that subsets Plex Mono renames the family, in the file's `name` table and in its `@font-face`, to a name without "Plex", and keeps "IBM Plex Mono" in the stack only for the unmodified file.
The roster records the name as `reservedName`, and `tools/faces.py --check OFL.txt` reads it from the licence's first paragraph and refuses a roster that disagrees, so a face that gains a Reserved Font Name upstream is caught when its licence is next checked.
The other twelve licence texts declare none, which `tools/faces.py` reports for each.

## Rules

- **No style is set in capitals.**
  A column head and an eyebrow are `--hw-text-xs` in muted, in sentence case; an avatar's initials are the one uppercase transform in the layer, because initials are capitals.
- **A mono label is lowercase.**
  A brand whose mono is its identity may set labels in it, as Field's are, and sets them lowercase: mixed case keeps word shape at 11px.
- **Italic is for a term being defined or a quoted title**, never for emphasis.
  Emphasis is weight.
- **Titles balance.**
  `.hw-headline` and `.hw-title` set `text-wrap: balance`; body text takes `text-wrap: pretty` instead, because balancing a paragraph makes its last lines ragged.
- **Lowercase is never letterspaced positively**, except the label style at 0.01em, which keeps 12px from closing up.

Set type to be read for an hour, not to be seen for a second.

## Sources

| source | taken | left |
|---|---|---|
| [Omnibus-Type/Archivo](https://github.com/Omnibus-Type/Archivo), `OFL.txt`, SIL Open Font License 1.1, pinned by sha256 in `ramps/roster.json` | the variable TTF's x-height (0.526) and cap height (0.686), and its `wdth` axis for Archivo Expanded at 125% | the ttf and otf upstream ships; only the Fontsource woff2 subset is vendored |
| [googlefonts/literata](https://github.com/googlefonts/literata), `OFL.txt`, SIL Open Font License 1.1, pinned by sha256 in `ramps/roster.json` | the variable TTF's x-height (0.507) and cap height (0.700) | the ttf upstream ships; only the Fontsource woff2 subset is vendored |
| [IBM/plex](https://github.com/IBM/plex), `OFL.txt`, SIL Open Font License 1.1, pinned by sha256 in `ramps/roster.json` | `IBMPlexMono-Regular.ttf`'s x-height (0.516) and its Reserved Font Name, "Plex" | the otf, woff and woff2 upstream ships, and every weight but Regular; only the Fontsource woff2 subset is vendored |
| Fontsource 5.3.0 on npm | the latin subset WOFF2 vendored in `fonts/` for all three faces, the same source quoth installs its Archivo from | other language subsets and variable-font builds |
| [the product-identities scout's licensing survey of 2026-09-22](https://github.com/Abhijeet34/halderworks-design/blob/a95ed0fed0c544fc12483031a2066f3eecc6b535/design/90-evidence.md#font-licensing-per-platform) | the OFL as the only licence, of twelve surveyed, that clears self-hosting, woff2 in a WKWebView, and a sold Mac app, with no fee and no per-app licence | the eleven other licence sources it screened and declined |

# The spec sheet

A catalogue of named, fully specified assets that any Halderworks product can pull from without inventing anything.

It sits **inside** this system and is built entirely from tokens that already exist.
It adds no hue, no face and no scale step, and it never redefines an `hw-` token.
A project selects from it; it does not fork from it.

## How an entry is written

Every entry carries a name, its anatomy in tokens, the rule for when it applies and when it does not, its contrast obligation where it carries text, and two provenance lines:

- **Taken** - the principle, stated so that it could have been arrived at independently.
- **Left behind** - the expression that was deliberately not carried across.

That second line is the test, and it is a standing rule of this system rather than a formality: taking a reference and building our own asset is strictly our work, not somebody else's.
**An entry that cannot honestly fill the Left behind line is a copy and does not ship.**
One candidate failed exactly that way and is recorded under [What was declined, and why](#what-was-declined-and-why) rather than quietly dropped.

The sources are the accounts screened in [90-evidence.md](90-evidence.md), which is also where the account-by-account reading and the capture provenance live.

## 1. Themes

**A theme here is not a light or dark theme, and confusing the two is how this system gets forked by accident.**

- **Light and dark change the token values.** Same names, different numbers, chosen by the viewer or the operating system. [10-color.md](10-color.md) owns them.
- **A theme overlay changes which of those values a surface is allowed to reach for.** Same numbers, different permissions, chosen by the product and fixed for that surface.

The two compose: three overlays times two value themes is six real looks, and the contrast matrix already certifies every one of them, because an overlay introduces no pair.

An overlay is one attribute on an ancestor, exactly as density is: `<div data-overlay="console">`.
It may set only which type steps are permitted, which density applies, which measure running text takes, and which formats from section 3 are available.
**An overlay that sets a colour is not an overlay, it is a fork.**

### Instrument, the default

The product surface: a screen that reports state and takes action.

| what it fixes | value |
|---|---|
| largest permitted step | `title-1` |
| display face | none. Newsreader does not appear |
| density | comfortable |
| running measure | `--hw-measure-ui`, 56ch |
| formats available | none of section 3. A screen is not an issue of anything |
| colour scheme | Record (section 5) |

```css
[data-overlay="instrument"] { font-size: var(--hw-text-body); max-width: var(--hw-measure-ui); }
```

**Taken:** nothing external. This names the selection the system already made, so that the other two can be read as departures from something rather than as free choices.
**Left behind:** nothing. It is the existing default given a name.

### Console, the dense tool surface

A surface a person keeps open and scans: a run list, a log, a queue.

| what it fixes | value |
|---|---|
| largest permitted step | `title-3` |
| display face | none |
| density | compact, via `data-density="compact"` |
| identifiers | `--hw-font-mono` with `tabular-nums` for every id, duration, cost and timestamp |
| colour scheme | Well (section 5) |

```css
[data-overlay="console"] { font-size: var(--hw-text-body-sm); }
[data-overlay="console"] :is(h1, h2, h3) { font-size: var(--hw-text-title-3); font-weight: var(--hw-weight-title-3); }
```

**Taken:** a surface whose job is scanning should spend its vertical space on rows rather than on headings, so the heading ceiling drops rather than the type shrinking everywhere.
**Left behind:** nothing from the captures; this is derived from [45-density.md](45-density.md) and named here so a product stops re-deciding it per screen.

### Editorial, the reading surface

Marketing, documentation, release notes and dated reports.

| what it fixes | value |
|---|---|
| largest permitted step | `display-1` |
| display face | Newsreader at `display-1` and `display-2`, and nowhere else |
| density | comfortable |
| running measure | `--hw-measure-prose`, 68ch, at `body-lg` |
| formats available | all seven in section 3 |
| colour scheme | Page (section 5) |

```css
[data-overlay="editorial"] { font-size: var(--hw-text-body-lg); max-width: var(--hw-measure-prose); }
[data-overlay="editorial"] :is(h1, h2) { font-family: var(--hw-font-display); }
```

**Taken:** a reading surface and a working surface are different products of the same system, and the honest way to say so is a permission list rather than a second stylesheet.
**Left behind:** `ui.ux.jam`'s editorial register is carried by desaturated photography behind every headline. Ours is carried by measure, face and rhythm on a neutral ground, because [80-anti-patterns.md](80-anti-patterns.md) puts no photography in product surfaces and a photograph is a ground whose luminance is unknown.

### High contrast, which answers `prefers-contrast: more` and nothing else

Two published systems answer high contrast in **opposite** directions: one re-solves per role and its distinct-value count goes **up**, the other surrenders the palette to the user agent and collapses 192 values onto 15.
Those answer different media queries, and one block cannot answer both.
This one answers `prefers-contrast: more`, a reader asking for a stronger palette, with a per-role re-solve.

`tokens/tokens.css` carries it under `@media (prefers-contrast: more)`, solved by `tools/build.py` from the same seed as the default themes rather than chosen by eye.
Every 4.5:1 floor is raised to the 7:1 of WCAG 2.2 SC 1.4.6.
Every 3:1 floor is raised to 4.5:1, because SC 1.4.11 has no enhanced level and 4.5:1 is the next bar this system already holds.
The same 108 text pairs and 90 non-text pairs are certified at the raised bars by both instruments, on the float value and at 8-bit, with 0 below either: the worst text pair is 7.03:1 and the worst non-text pair 4.53:1.
27 of the 64 colour values move, 42.2%, inside the 28 to 78% [90-evidence.md](90-evidence.md) measured across five vendors: 18 re-solved by the raised floors and 9 set by the per-role targets below.
The grounds, the surfaces and the hairline border do not move at all.

**Raising the floors alone merged roles**, and the first build said so.
The solver keeps the lightness nearest each token's anchor, so two roles pushed toward one bar land on one value: `--hw-text-secondary` came out 0.033 from `--hw-text-muted` in light and 0.047 in dark, and three chart colours landed on the re-solved semantics.
The seed now gives those roles their own targets under `contrastMore`, and both instruments refuse a step between `--hw-text`, `--hw-text-secondary` and `--hw-text-muted` smaller than 0.06, the smallest step the default themes keep (0.062 light, 0.068 dark).
The chart and separation rules of [10-color.md](10-color.md) hold in this block unchanged.
`--hw-border-strong` and `--hw-text-disabled` share one lightness here, 0.5348 in light, and that is not a merge this block introduced: they share `oklch(0.6350 0.006 198)` in the default light theme too, because a boundary and a disabled glyph are different forms at one weight.

**What it does not answer.** `forced-colors: active` throws this palette away, and the answer there is the filled level's transparent border, which the user agent can repaint: [50-surface-texture.md](50-surface-texture.md#under-forced-colours).
The files in `exports/` carry the default themes only; `tokens/tokens.css` is the one file that carries this block.

## 2. Surface and texture styles

Texture was reported as a gap in this system before any of these accounts were screened, and the report was right: [50-surface-texture.md](50-surface-texture.md) had answered it with a blanket refusal.

**That refusal is now re-scoped rather than reversed**, and the distinction is one measurement.
The stated reason was that a contrast ratio is computed against one background colour, so a texture makes every certified number an approximation.
That is exactly true of grain, photography and glass, whose luminance at a given pixel is unknown.
It is **not** true of a deterministic two-colour pattern, whose worst pixel is a named token: you certify the ink against the darker of the two and the number is as real as any other in this system.

So the rule is now the one the evidence supports:

> A ground may carry a pattern only where every pixel of it is a token this system has solved, and any ink on it is certified against the **worst** of those tokens.
> A ground whose pixels are not enumerable carries no text at all, and must say so on its face.

Three styles, and no more.

### Ruled

A ground that says this is working material rather than a finished record.

```css
.hw-ground-ruled {
  background-color: var(--hw-ground);
  background-image:
    repeating-linear-gradient(to right,  var(--hw-border) 0 1px, transparent 1px var(--hw-space-24)),
    repeating-linear-gradient(to bottom, var(--hw-border) 0 1px, transparent 1px var(--hw-space-24));
}
@media (prefers-contrast: more) { .hw-ground-ruled { background-image: none; } }
```

**Contrast obligation, which is the whole entry.**
Ink on this ground can land on a rule, so every pair is certified against `--hw-border` and not against `--hw-ground`:

| ink on the ruled ground | light | dark | verdict |
|---|---:|---:|---|
| `--hw-text` | 12.17 | 11.84 | permitted |
| `--hw-text-secondary` | 5.23 | 5.06 | permitted |
| `--hw-text-muted` | **4.01** | **3.89** | **refused, below AA** |

`--hw-text-muted` is legible on the ground and illegible on the rule, and nothing on the screen tells a reader which one a given word landed on.
That pair is the reason this entry exists as a table rather than as a sentence.

**Cost:** two repeating gradients, no image, no request, no repaint on scroll.
**Rule:** the pitch is `--hw-space-24` and no other value; a ruled ground is one per view; it never sits under a data table, whose own rules are the grid there.
**Taken:** a ground can carry the same statement a heading would, that what sits on it is provisional.
**Left behind:** the blue-green graph paper, the tape, the paperclip and the hand-drawn asterisk that make `khushidotjpeg`'s version read as a sketchbook. Ours is this system's own spacing grid made visible in its own border token, which is a different claim made with our own materials.

### Grain

A ground for a large empty area that would otherwise read as a rendering failure.

```css
.hw-ground-grain {
  background-color: var(--hw-ground);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E");
}
@media (prefers-contrast: more), (prefers-reduced-transparency: reduce) {
  .hw-ground-grain { background-image: none; }
}
```

**Contrast obligation: none, because nothing may sit on it.**
That is not an omission, it is the entry.
A turbulence ground has no enumerable worst pixel, so **no text, no control, no icon and no data may appear on it, ever.**
It is permitted on exactly one thing: a full-bleed band on an editorial surface that carries nothing of its own.

**Cost:** one inline SVG data URI, roughly 300 bytes, no network request.
**Taken:** a very large flat area reads as unpainted rather than as calm, and a disturbance below the threshold of being seen fixes that without becoming a texture anyone notices.
**Left behind:** the torn paper, the collage edges, the drop shadows and the photograph underneath, which are the whole of what makes the reference version work and every one of which would put ink on an unknown luminance.

### Framed

Content that came from somewhere else, presented as a quotation of a surface rather than as the surface.

```css
.hw-frame { background: var(--hw-surface-sunken); border: 1px solid var(--hw-border);
            border-radius: var(--hw-radius-lg); padding: var(--hw-space-16); }
.hw-frame > figcaption { font-size: var(--hw-text-micro); letter-spacing: var(--hw-tracking-micro);
            font-weight: var(--hw-weight-micro); text-transform: uppercase;
            color: var(--hw-text-muted); margin-bottom: var(--hw-space-8); }
```

**Contrast:** `--hw-text` on `--hw-surface-sunken` is 13.98:1 light and 16.98:1 dark; the caption, `--hw-text-muted` on the same fill, is 4.60:1 and 5.58:1. Both are already in [15-color-combinations.md](15-color-combinations.md); the style adds no pair.

**Rule:** the caption names a real source and is never decorative. A frame with nothing to attribute is a card, and [80-anti-patterns.md](80-anti-patterns.md) has the rule for those.
**Taken:** a frame plus a source label is how you say "this is a document from somewhere", and that is information a reader uses.
**Left behind:** the traffic-light dots, the fake toolbar, the progress bar, the mouse pointer and the floating folder icons. Our products **are** applications, so window chrome drawn inside a window is a picture of the container it is already inside; in a social feed the same device carries real information because there the container is not an application. The dots are also three colours this system does not have, used as state with no word beside them.

## 3. Formats

Composition recipes: a layout in tokens, not a component and not a picture.
All seven are available on the Editorial overlay and none on Instrument.

### Masthead frame

A small persistent mark, an identifier and a sequence number, framing an item that belongs to a real series.

```text
QUOTH                                    2026-09-21     <- mark left, stamp right
───────────────────────────────────────────────────     <- one --hw-border rule

  Release notes for 4.2
  ...

  #507                                          SEP     <- optional foot, no rule
```

| part | token |
|---|---|
| the mark | `micro` (11px, 0.06em, 600, uppercase) in `--hw-text-muted` |
| the stamp and the sequence | `--hw-font-mono` at `label` (12px), `tabular-nums`, `--hw-text-secondary` |
| the rule | `1px solid var(--hw-border)`, exactly one |
| masthead to rule / rule to headline / content to foot | `--hw-space-8` / `--hw-space-24` / `--hw-space-32` |

**Contrast:** `--hw-text-muted` on `--hw-ground` is 4.88:1 light and 5.38:1 dark; `--hw-text-secondary` on `--hw-ground` is 6.37:1 and 7.01:1. Both already certified.

**When it applies.** All three must hold.

1. **A sibling exists now**, a previous issue a reader can open. Issue 1 of 1 is not a series and a masthead on it is a costume.
2. **The identifier resolves outside the page**: a release number matching a tag, a publication date, a sequence that increments with the feed. An identifier that appears nowhere but in its own stamp is ornament by construction.
3. **A reader would use it** to cite the item, to check they have the latest, or to find the one before.

**Rules.** Exactly one rule, because a second is a rule between rows, which is already refused.
The mark is one string and never changes; two mastheads in one product means the product thinks it is two.
No hue: a stamp is not a state.
Never on a product screen.
The sequence number is not the oversized ordinal, and they never appear at the same size.

**What the consumer provides:** the series itself - the identifier, the previous item's address, and the guarantee that the sequence increments. Semantically a `<header>` inside the item's `<article>`, a `<time datetime>` for the date, and a mark that is not a heading.

**Taken:** a frame that repeats across every item in a series turns a pile of posts into a publication, and the reader can then locate any one of them among its siblings.
**Left behind:** `ui.ux.jam`'s frame sits on desaturated photography, uses a drawn sun glyph as its mark and stamps a stylised `20-26` that is a year wearing a logotype. Ours is type on the ground, a wordmark that is just the product's name, and a date in the format [25-content.md](25-content.md) already fixes.

### Counted set

A numeral set two or more steps above the headline it counts.

| part | token |
|---|---|
| the numeral | `display-1` (56px Newsreader, 500) or `display-2` (40px) |
| the headline | `title-2` (21px) or `title-3` (17px), at least two steps below |
| the numeral's colour | `--hw-text`, or `--hw-text-muted` where the headline is primary. Never `--hw-accent` |
| the numeral's column | `--hw-space-64` at `display-1`, `--hw-space-48` at `display-2` |
| numeral to headline / item to item | `--hw-space-16` / `--hw-space-24` |

**Where the column width comes from.**
[20-type.md](20-type.md) records Newsreader's ten digits measuring 567px at 100px, so one digit advances 0.567em.
Two digits are 63.5px at 56px and 45.4px at 40px, which `--hw-space-64` and `--hw-space-48` hold with 0.5px and 2.6px to spare.
Three digits fit neither step, and that is the format's real ceiling rather than an accident: **a set of more than 99 does not take this format**, because a set nobody can hold in their head is a table.
This is derived from the recorded 567px measurement in [20-type.md](20-type.md) and was not re-measured when the format was written, because the faces could not be loaded in the environment it was written in. Re-measuring it needs one browser with Newsreader loaded.

**When it applies.** Three tests, all of which must pass. The boundary is in [4. Typography treatments](#4-typography-treatments), under the oversized ordinal, because the failure is a type failure.

**Rules.**
A count is a word in the sentence and goes in the heading text inside a `<span>`; a position is list structure and comes from an `<ol>` with `::marker` or a counter, never typed into the content, because a typed number and the DOM order can disagree and then one of them is lying.
The numerals are a column: `tabular-nums`, right-aligned, so 9 and 10 share an edge. A set whose numerals do not line up has not been made into a set.
One numeral per item and one set per view.

**What the consumer provides:** whether the number is a count or a position, and therefore which markup applies. The system cannot tell them apart and the answer decides the accessibility of the whole set.

**Taken:** where the count is part of the sentence, setting it at the size of the information it carries is structure encoding content rather than decorating it.
**Left behind:** `khushidotjpeg` sets the numeral in a warm tan or amber that appears nowhere else in the piece, and pairs it with a highlighter marker and a hand-drawn asterisk. Ours carries no hue at all, because a count is not a state and this system spends colour on four things.

### Spec card

A value shown beside the thing it describes.

| part | token |
|---|---|
| the specimen | a `--hw-space-48` fixed column: a swatch, a glyph, a numeral or a thumbnail |
| the name | `body-sm` in `--hw-text` |
| the value | `--hw-font-mono` at `label`, `tabular-nums`, `--hw-text-secondary` |
| row rhythm | `--hw-space-12` between rows, one `--hw-border` under the group and not between rows |

**Rule:** the specimen and its value sit on one row and one baseline, at every viewport, with no connector drawn between them.
**Taken:** a value is only checkable when it is adjacent to the thing it measures.
**Left behind:** the dotted leader lines that connect `khushidotjpeg`'s swatches to points inside a photograph. A leader is fixed geometry between two points, so it must be re-authored at every breakpoint, and choosing breakpoints per screen has its own entry on the anti-pattern list. [70-data-display.md](70-data-display.md) already settles the same question for charts: a line carries a direct label at its end, and a legend a reader must look back and forth to is a chart that needed labels.

### Comparison pair

Two things the reader is being asked to weigh against each other.

| part | token |
|---|---|
| each side | `--hw-surface`, `1px solid var(--hw-border)`, `--hw-radius-lg`, `--hw-space-16` padding |
| each label | `micro` uppercase in `--hw-text-muted` |
| the gap | `--hw-space-24`, and below `--hw-bp-md` the pair stacks |

**Rule:** the two sides share one inner padding and one first baseline, and **they do not share a height**. Stretching them to match is the entry [80-anti-patterns.md](80-anti-patterns.md) already carries; let the content set the height.
Two sides only. Three is a table.
**Taken:** a comparison is legible when the two things are aligned on the axis being compared and on nothing else.
**Left behind:** nothing from the captures. This format is derived from the system's own card and layout rules and is named here because a comparison assembled from scratch is how two-column blocks acquire equal heights.

### Quotation block

Someone else's words, attributed.

| part | token |
|---|---|
| the quotation | `body-lg` (17px) in `--hw-font-display` on the Editorial overlay, `--hw-text` |
| the left rule | `1px solid var(--hw-border)` with `--hw-space-16` of inset |
| the attribution | `micro` uppercase in `--hw-text-muted`, `--hw-space-8` below |

**Rule, and it is the hard one:** the quotation is real and the attribution is checkable.
[80-anti-patterns.md](80-anti-patterns.md) refuses invented quotes, invented logos and invented metrics without exception, and a quotation block is the shape that most invites all three.
A block with nothing real to put in it does not get placeholder text; it gets deleted.
The rule is `--hw-border` and never `--hw-accent`, because a coloured rail on a block is an accent edge.

**Taken:** attribution belongs in the same visual object as the words it attributes, not in a caption under it.
**Left behind:** `khushidotjpeg`'s quotation tiles set the quotation across a mixed serif and grotesque line over a grid-paper ground. Ours is one face, one rule and a neutral ground.

### Link-preview card

The Open Graph image: the one picture every product ships that is designed by nobody, seen by
everybody, and presented at a size somebody else chose.

**Measured.** On `recent.design/og-images`, 12 of 12 rendered cards measure aspect 1.91, carrying
nine distinct compositions in the one frame. Six cards read from the sites themselves on
2026-09-21 put the frame at 1200 x 630, **1.905**, for four of the six (`railway.com`,
`resend.com`, `vercel.com/pricing`, `notion.com`, at 1200 to 2400px wide), while `stripe.com`
serves 2.000 and `github.com` a 1200 x 1200 square that every large-card consumer crops. A band
read of the `railway.com` card at its native size gives the composition below.

**Every dimension is a fraction of the frame height `H`, never a pixel**, because the pixel width
is whatever the site rendered - 1200, 1920, 2048 or 2400 in that sample - and the presented width
is whatever the consumer chose.

| part | value | at 1200 x 630 | derivation |
|---|---|---:|---|
| the frame | aspect 1.905, at 1200 x 630 or a multiple of it | | four of six cards |
| inset, all four sides | `0.10 H` for everything that must be read | 63px | Railway's 10.2% above and 11.1% below |
| the mark | the product name in `--hw-font-sans` at 600, band height `0.076 H`, top left at the inset | 48px | Railway's wordmark band, 7.6%; the mark is a name, per [00-brand-book.md](00-brand-book.md#the-mark) |
| the headline | `display-1`'s face, weight and tracking, **cap height `0.084 H`**, so a size of `0.124 H` in Newsreader, whose cap height is 0.676em ([20-type.md](20-type.md#why-not-inter)) | 53px cap, 78px size | Railway's three headline lines, each 8.4% |
| line pitch | `1.5` times the cap height, `0.126 H` | 80px | Railway's 80px on a 53px cap. It is 1.02 of the size, which is `display-1`'s own line-height |
| lines | at most three, the last one above the bottom inset | | Railway's three |
| ground and ink | `--hw-text` on `--hw-ground`, one theme's pair, chosen per product | | |

A headline at `0.084 H` is about 22px tall when a feed presents the card 500px wide, which is the
number the fractions exist to protect.

**Contrast:** `--hw-text` on `--hw-ground`, already certified in both themes in
[10-color.md](10-color.md#the-contrast-matrix). The card is a raster with no theme switch, so it
carries one theme's pair and never mixes the two.

**Rules.**
The frame is 1.905 and says so: `og:image:width` and `og:image:height` are declared, and a square
card is refused, because a card the consumer must crop has been designed by the consumer.
Nothing that must be read reaches the frame edge; a recipe that runs type to the edge loses its
first and last letters to the first consumer that crops.
Type on the ground only: no photograph, render or screenshot behind text, because a picture is a
ground whose luminance is unknown.
`og:title` and `og:description` are written, not truncated by the consumer: the four sites
measured stay within 54 and 148 characters, which is recorded as an observation of four, not as a
limit.

**What the consumer provides:** the headline for each page, the frame rendered at build time, and
the `og:` and `twitter:card` meta tags that point at it.

**Taken:** a fixed frame specified in fractions of itself, so it holds at whatever pixel size a site
renders it and whatever width a consumer presents it.
**Left behind:** eight of the nine compositions `recent.design` indexes in the same frame - a
swatch row, a product photograph, an oversized wordmark cropped by the edge, a 3D gradient render, a
framed screenshot, a collage of interface chips, a portrait with overlaid text, and a mono headline
beside an illustration - and Railway's art, which bleeds to all four edges. Ours is the ninth, a
wordmark with one line under it, reduced to the product's name and a headline on a solved ground.

### Slide sequence

The carousel: a set of 4:5 slides read one after another, which is the outward-facing format a
product's announcements take on a social feed.

**Measured on three independent accounts.** `khushidotjpeg` and `ui.ux.jam` carry the same
four-corner frame, and `figma.expert` carries it a third time with a different payload in each
corner ([90-evidence.md](90-evidence.md#a-third-independent-instance-of-the-four-corner-frame)).
Instagram labels that third account `AI-generated profile`. Its frame counts as an instance,
because a frame is a frame whoever drew it; its colour claims are not evidence and contribute
nothing here ([85-considered-and-declined.md](85-considered-and-declined.md#an-unsourced-superlative-as-a-palette-source)).
The proportions below were read on `khushidotjpeg`'s 1080 x 1350 slides.

Every dimension is a fraction of the frame, as in the link-preview card, because the pixel size is
whatever the export chose.

| part | value | at 1080 x 1350 | derivation |
|---|---|---:|---|
| the frame | aspect 0.800, 4:5 | | both measured carousels; the feed's portrait frame |
| margin, four sides | one inset at `0.104` of the short side | 112px | measured 110 to 117px |
| corner labels | `micro`'s treatment - uppercase, 0.06em, 600 - at a glyph height of `0.017 H`, one size for all four | 23px | head and foot measured identical |
| cover ordinal | the **count of the set**, Newsreader at a glyph height of `0.156 H`, `--hw-text` | 211px | measured 15.63% |
| cover headline | `display-1`'s face, weight and tracking, line pitch `0.070 H` | 94px | measured 6.96% |
| body ordinal | the **index of the item** on this slide, Newsreader at `0.102 H`, `--hw-text-muted` | 137px | measured 10.15% |
| advance mark | Lucide `arrow-right` at `0.014 H`, in the ink of the text beside it | 19px | measured 1.41% |

**Contrast:** `--hw-text` and `--hw-text-muted` on `--hw-ground`, 14.83:1 and 4.88:1 light, 16.38:1
and 5.38:1 dark, already certified. Like the link-preview card, each slide is a raster with no
theme switch, so a sequence carries one theme's pairs and never mixes the two.

**Rules.**
The frame holds still: the margin, the ground, the ink, the label size and the mark are the same
on every slide, and only what sits inside the margin changes. A slide that changes any of those has
left the sequence.
The cover states the size of the set; every body slide states the position of its own item. Those
are two numbers with two jobs, and they are never set at one size.
Each corner carries a fact that is true of this slide or this sequence - the mark, the series, the
position, the advance mark - and a corner with nothing true to carry stays empty.
Every ordinal passes the three tests under [the oversized ordinal](#the-oversized-ordinal), so a
position reads `2 / 6` and never `02 / 06`.
The advance mark depicts only what the surface does. An arrow is honest on a feed that swipes; a
drawn control that does nothing when tapped is not.

**What the consumer provides:** the content of each slide, the export at 1080 x 1350 or a multiple
of it, and alt text on every slide carrying its words, because a slide's text is otherwise in
pixels only.

**Taken:** a sequence reads as one object when its frame holds still and only the inside of the
margin changes, and the cover and the body carry different numbers because they answer different
questions.
**Left behind:** `khushidotjpeg`'s pastiche selection toolbar at 1.13:1 against its ground, its body
ordinal at 1.41:1, and the brown of its cover ordinal; `ui.ux.jam`'s cover photograph; and every
colour `figma.expert` publishes, together with the `01 / 06` leading zero on its counter. Ours is
the frame alone, on a solved ground, with the product's name in one corner.

## 4. Typography treatments

Five treatments beyond the ramp in [20-type.md](20-type.md).
For each, the boundary that separates it from the decorative-marker entries in [80-anti-patterns.md](80-anti-patterns.md) is the load-bearing half.

### The oversized ordinal

The type half of the counted set in section 3. Anatomy is there; the boundary is here.

**When the numeral is information.** All three must pass.

1. **The delete test.** Remove the numeral and read what is left. `5` over "UX things I was taught as best practice that I now think are wrong" loses its subject and stops being a sentence. `02` over "Fast by default" loses nothing, because the headline never referred to it.
2. **The reorder test.** Swap two items. If their numbers must change and that change is wrong, the set is ordered. If the numbers simply follow the items around, the set was never ordered and the numbers were labels.
3. **The true-value test.** The numeral is the actual count or position, never padded and never picked to fill the slot. `01` in a set of three encodes a set size that does not exist; a leading zero below ten is decoration wearing a number's clothes.

A numeral that fails any of them is the failure this system already names three times over: an emoji as a section marker, a decorative icon that repeats the heading, a coloured dot with no word beside it.
It is a glyph carrying no information, set large.

**Taken / Left behind:** as the counted set in section 3.

### The small-caps eyebrow

A `micro` uppercase line naming the category a heading belongs to.

`micro` (11px, 1.2, 0.06em, 600) uppercase in `--hw-text-muted`, `--hw-space-8` above the heading.
**Contrast:** 4.88:1 light and 5.38:1 dark on `--hw-ground`, already certified.

**The boundary.** An eyebrow names a category that **has other members**. "Release notes" above a release note is an eyebrow, because there are other release notes and there are also other kinds of page. "Fast and reliable" above "Fast and reliable" is the decorative-icon failure rendered in type: a second element carrying the first element's information at a smaller size.
One eyebrow, never two. Never on a product screen, where a section is marked by its heading.
This is the only uppercase in the system, which is the constraint that keeps it meaning something.

**Taken:** a heading can say what a thing is without also having to say what kind of thing it is, if a category line carries the second job.
**Left behind:** `khushidotjpeg` runs two eyebrows on one tile, one per top corner, the second of which is a call to action rather than a category. Ours is one, it is a category, and it never asks for anything.

### The marker highlight

Emphasis carried by the ground rather than by the ink.

```css
.hw-mark { background: var(--hw-surface-sunken); padding: 0 var(--hw-space-4);
           border-radius: var(--hw-radius-sm); box-decoration-break: clone; }
```

**Contrast:** `--hw-text` on `--hw-surface-sunken` is 13.98:1 light and 16.98:1 dark, already certified. The treatment adds no pair and introduces no colour.

**The boundary.** At most one mark per headline, and never in running body text: [20-type.md](20-type.md) settles that emphasis in prose is weight, and a page with three marks on it has marked nothing.
The marked words must be the ones a reader would repeat back. A mark on a whole line is a line with a different background, not emphasis.

**Taken:** a mark on the ground is a second channel for emphasis that does not spend a colour and does not compete with weight.
**Left behind:** the highlighter yellow itself, and the hand-drawn skew and overshoot that make it read as a pen stroke. A yellow marker needs a fifth colour that is neither a semantic nor the accent, and this system has no fifth colour to spend. `tools/build.py` could solve one now; what it cannot do is decide that a fifth colour should exist, and nothing here argues that it should. <!-- covered-by: Colour palette, and how each value was arrived at -->

### The bracketed aside

A scope note attached to a headline without a second sentence.

`body-sm` in `--hw-text-muted`, inside literal square brackets, on the same line as the headline or directly below it.
**Contrast:** 4.88:1 light and 5.38:1 dark on `--hw-ground`.

**The boundary, and it is one test:** the bracketed text must survive being read aloud as part of the sentence. "Six Figma plugins [ that survive a handoff ]" passes. "Six Figma plugins [ you should try ]" does not, because it addresses the reader rather than qualifying the noun, and an aside that addresses the reader is a tone of voice, not information.
One aside per headline. Never in a control label, an error or a table header.

**Taken:** a qualification that is genuinely subordinate should be set as subordinate rather than promoted to its own sentence.
**Left behind:** the hand-lettered italic brackets, and the conversational register of the reference text.

### The mixed-face headline

One display headline set in Public Sans with a single term in Newsreader.
The span marks **the term the headline names**, never emphasis.

That is what makes it specifiable without touching either standing rule.
[20-type.md](20-type.md) fixes that emphasis is weight and gives one other job to a change of style, marking a term being defined, which italic does in running text.
In this headline the face does that job instead, so the face still carries a role rather than a tone and emphasis is still weight.

| part | token |
|---|---|
| the headline | `display-1` or `display-2` size, line-height, tracking and weight, in `--hw-font-sans` |
| the term | the same size, weight and tracking in `--hw-font-display`, roman and never also italic |
| both | `--hw-text` on `--hw-ground`, 14.83:1 light and 16.38:1 dark, already certified |

```css
[data-overlay="editorial"] .hw-headline-mixed { font-family: var(--hw-font-sans); }
[data-overlay="editorial"] .hw-headline-mixed > .hw-term { font-family: var(--hw-font-display); }
```

**The term test.** The span's words are the name of the thing the page is about, and the body uses the same words again, unmarked. A span on a verb, an adjective or an intensifier is emphasis set in a second face and is refused.

**Rules.** One span per headline and one mixed-face headline per view. Editorial overlay only, which is already the only place Newsreader appears; never on Instrument or Console and never in product UI. No hue on the span and no marker highlight in the same headline, because two marks in one line have marked nothing.
The two faces are set at one size and not optically matched. Newsreader's cap height is 0.676em ([20-type.md](20-type.md#why-not-inter)) and Public Sans's was not re-measured, because the faces could not be loaded where this entry was written; checking it needs one browser with both faces loaded.

**Taken:** two faces in one line can carry information, that these words are a name, when the second face is reserved for that one job.
**Left behind:** the second face as the carrier of the headline's voice, spent on whichever word the line leans on. That is emphasis by face, which is the reading `khushidotjpeg`'s and `ui.ux.jam`'s headlines invite and the one [20-type.md](20-type.md) refuses.

## 5. Colour schemes

The palette does not change and [15-color-combinations.md](15-color-combinations.md) remains the permission list.
**A scheme selects from that table. It never adds a pair, and a pair not in that table is not available to a scheme.**
What a scheme fixes is which four colours a surface actually uses, so a project picks one instead of assembling one.

| scheme | the page | what holds content | ink | where the accent may appear | the overlay it pairs with |
|---|---|---|---|---|---|
| **Record** | `--hw-ground` | `--hw-surface` with `--hw-border` | `--hw-text`, `--hw-text-secondary` | only where a state is reported | Instrument |
| **Well** | `--hw-surface-sunken` | `--hw-surface` with `--hw-border` | `--hw-text`, `--hw-text-secondary` | only where a state is reported | Console |
| **Page** | `--hw-ground` throughout, no surfaces | `--hw-border` rules only | `--hw-text`, `--hw-text-secondary` | links only | Editorial |

`--hw-ink` is the one action in every scheme, and it carries no hue in any of them.

**Why Page has no surfaces.** A documentation page whose every section is a card is a page of cards with one paragraph in each, which [80-anti-patterns.md](80-anti-patterns.md) already calls a list row that grew a border by accident. On Page, sections are separated by rhythm and a rule.

**Why Well inverts Record rather than darkening it.** `--hw-surface-sunken` recedes and `--hw-surface` comes forward ([50-surface-texture.md](50-surface-texture.md)), so a tool surface where content floats in a frame reads correctly in both value themes without either one changing a token.

**A screen with no state on it has no hue on it**, in all three schemes. That is a check rather than a coincidence, and it is the same sentence [15-color-combinations.md](15-color-combinations.md) closes on.

**Taken:** nothing external. The schemes are named selections from a table this system already certified.
**Left behind:** every one of the four accounts spends colour as identity - a gradient, an amber, a highlighter, a tinted photograph. None of that is carried, and naming the schemes is what makes the refusal concrete rather than merely stated.

## 6. Exports

**The requirement is that this book is usable irrespective of which model reads it.**
A system that exists only as prose is a system every agent re-interprets, so the book emits itself in the four forms agents actually consume.

`tools/export.py` reads `tokens/tokens.json` and writes all four into `exports/`:

| file | what it is | for |
|---|---|---|
| `DESIGN.md` | every token with its role, plus the eleven rules that are not negotiable | an agent with room for the long brief |
| `DESIGN.compact.md` | the same rules, colours and type ramp; every other family as one line per scale | a context window that cannot take the long one |
| `theme.css` | a Tailwind v4 `@theme` block, mapped to Tailwind's own namespaces so utilities generate | a Tailwind product |
| `variables.css` | plain CSS custom properties, both themes, compact density and reduced motion | anything else |
| `exports/design-tokens.json` | W3C DTCG, with `$value`, `$type` and `$description` on every token | a design tool or a token pipeline |

**This is not `tools/build.py`.**
That one solves colour against a contrast target and emits both token files; this one only re-expresses values it has already solved.
The exporter only re-expresses values that are already solved, so it cannot invent one, and it proves that twice on every run: it re-derives all 33 colour tokens against `tokens/tokens.css` before it writes anything, and after writing it compares all 180 custom properties the export declares against the ones `tokens/tokens.css` declares and exits non-zero on any divergence.

That second check is not decoration.
It found three real omissions the first time it ran: the per-step `--hw-leading-*`, `--hw-tracking-*` and `--hw-weight-*` properties, the `prefers-reduced-motion` block, and the `[data-density="compact"]` block.
Each would have handed an agent reading the export a quietly different system from the one a browser loads - in the second case, one that had dropped an accessibility accommodation.

**`tokens/tokens.json` was also not the single source it claimed to be.**
Four durations and three easings shipped in `tokens/tokens.css` and appeared nowhere in `tokens/tokens.json`, so any export built from the stated source would have had no motion values at all.
They are now families in `tokens/tokens.json` with roles, named `duration` and `easing` rather than `motion` because the artifact page's token reader rejects a family under that name.

### Every token carries its role

A token with a value and no role gets misused on the first screen that needs a border.
The role names the job and enumerates the surfaces:

> `--hw-border` - The 1px hairline: card and panel edges, table and cell borders, the tab baseline, chart axes and gridlines, the masthead rule, a framed quotation. Separates a container from its ground without being read as an edge.

All 112 entries in `tokens/tokens.json` carry one, and `exports/design-tokens.json` emits each as `$description`.
**The premise that ours largely lacked roles turned out to be wrong and is recorded here rather than quietly acted on:** all 105 entries already had a `usage` field, median 67 characters. Ten were thin enough to be worth enriching - `hw-border`, `hw-ink`, the three semantics, four of the six chart series, and `hw-cell-pad-y-compact` - and were rewritten to name their surfaces. The other 95 were already roles and were left alone.

**Taken:** an export format and a role discipline. A design system that ships a DESIGN.md and a W3C token file is one an agent can consume without a human translating it, and a role per token is what stops the consuming agent guessing.
**Left behind:** every value. The source that demonstrated this makes copying a palette one click, which is exactly why the line is drawn loudly: its colours are its own, and nothing in `exports/` came from it. What was taken is the shape of the file and the discipline of describing a token by its job.

## What was declined, and why

Eight devices were screened. Seven became entries above, the high-contrast theme among them, and one is declined outright.

**The stacked-label overlay** - translucent pills layered over a photograph, each carrying one clause of a sentence - **does not ship, and it is the entry that failed the Left behind test.**

Its refusals are already certified: a translucent surface takes its luminance from whatever is behind it, so its contrast against its own text is not a number, which [80-anti-patterns.md](80-anti-patterns.md) refuses twice and [15-color-combinations.md](15-color-combinations.md) refuses again for any text on `--hw-scrim`. A sentence split across stacked pills is also a sentence turned into badges, against one badge per row.

The honest part is what happens when those are removed.
Take away the translucency and the photograph and what is left is stacked opaque text on a surface, which is a paragraph.
The Left behind line would have to say "the translucency and the image", and the Taken line would then have nothing in it, because the translucency and the image **were** the device.
By the rule at the top of this file that makes it a copy rather than a derivation, so it is recorded here instead of specified.

The remaining rejections are inside their entries, where the thing that replaced them is: the dotted leader lines under Spec card, the faux window chrome under Framed, the torn-paper collage under Grain, the graph paper under Ruled, and the highlighter yellow under The marker highlight.

Take the structure or take nothing. A device that has to bring a colour with it was not a structural device.

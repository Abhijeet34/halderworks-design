# Considered and declined

A design system that only records what it took cannot tell a later reader whether a question was
answered or never asked.
This file is the second half: what was screened, what was refused, and the reason, so that the next
round does not rediscover the question and arrive at a different answer by accident.

Three rules govern an entry here:

- **It was actually examined.** A name with no measurement beside it is padding, and there is a
  separate section below for things that were named and not reached.
- **The reason is the reason.** Not "it did not fit the aesthetic".
- **A decline is reversible.** Every entry says what would change the answer.

Device-level refusals live where the thing that replaced them lives:
[75-spec-sheet.md](75-spec-sheet.md#what-was-declined-and-why) carries the stacked-label overlay and
the five expression refusals inside their own entries, and
[36-form-factors.md](36-form-factors.md#deliberately-out-of-scope) carries the form factors.
[05-coverage.md](05-coverage.md) carries the excluded surfaces. This file is for everything else.

## A second easing axis

**Declined, and both candidates are named so the question is not reopened blind.**

This system ships three curves on one axis: direction. Two published systems ship a second axis and
**they are not the same axis**:

| system | set | the second axis | what it asks |
|---|---|---|---|
| this system | 3 | none | is it entering, leaving, or moving on screen? |
| Carbon | 6, as 2x3 | **register** | is this a productive product or an expressive one? |
| Fluent 2 | 9, as 3x3 plus linear | **intensity** | how emphatic is this particular move? |

Both are defensible. Acquiring one by accident because it was the first one read would be the
failure, and acquiring both would be nine curves for a system whose whole argument is that a value
needs a reason.

Register is already answered here without a curve: the theme overlays in
[75-spec-sheet.md](75-spec-sheet.md#1-themes) are exactly that decision, made once per surface
rather than once per transition. Intensity is not answered and is not a question these products ask
- an instrument of record has no emphatic move.

**What would change it:** a product surface where two moves of the same direction genuinely need
different emphasis, with the pair named. That has not happened.

## Contrast as integer arithmetic on the token name

**Declined on transferability, not on correctness.**

USWDS gives every colour token a grade in its name and computes contrast as
`magic-number(g1, g2) = |g1 - g2|`, with AA at 50, AAA at 70 and AA-large at 40. Measured against
real WCAG ratios on 36 pairs of one published family, it agreed 36 of 36 at AA with **zero false
passes at every target** ([90-evidence.md](90-evidence.md) has the run).

Zero false passes is the correct direction for a safety rule and the result is real.
It is also 36 pairs of one family of one vendor's palette - and a palette built so that the rule
holds. It is evidence that USWDS constructed its ramps to satisfy the rule, not evidence that grade
separation predicts contrast in general.

Adopting it would mean rebuilding every token name here to carry a grade, which
[10-color.md](10-color.md) and [15-color-combinations.md](15-color-combinations.md) do not, in
exchange for replacing a solver that already runs in milliseconds.
`tools/build.py` computes the real ratio, so this system pays nothing for the exact answer.

**What would change it:** an author-time context where the real ratio genuinely cannot be computed.
There is none here.

## unDraw as a shipped illustration set

**Declined on its licence, not on its craft**, which is the most decision-changing fact in the
illustration screen and would not have been found by looking at the drawings.

Quoted verbatim from `undraw.co/license`:

> This license does not include the right to compile assets, vectors or images from unDraw to
> replicate a similar or competing service, in any form or distribute the assets in packs or
> otherwise.

"or otherwise" is the operative phrase. A design system that vendors a folder of unDraw SVGs into a
repository and ships it to products **is distributing them**, and the licence does not grant that.

It remains available for one-off use inside a single product surface. It cannot be the house set.

**What would change it:** a licence change, or a per-product arrangement. Neither is this system's
to make.

## Palette generators that produce a ramp without a contrast target

**Declined as a step backwards from what this system already has.**

`Coolors.co` and `Colorkit.io` generate palettes and scale colours by eye. This system's whole
authority is that every ink is solved to a stated contrast ratio against a stated ground, and that
the build refuses to emit when the matrix does not hold - a discipline that caught five defects no
eyeball found ([90-evidence.md](90-evidence.md#the-solver)).

A generator that returns a pleasant ramp with no contrast target hands back the problem the solver
exists to remove. The reel that recommended both tools demonstrates it on its own swatches:
`#4927B3`, `#824EBE`, `#9B75C9`, `#B49CD4` measure `oklch(0.4170 0.2029 284.51)` to
`oklch(0.7334 0.0835 303.99)`, so the hue drifts 19.5 degrees across four steps of what is presented
as one colour, and the base sits at 284.5, inside the 245-296 corridor
[10-color.md](10-color.md#why-hue-198) measured as the most crowded in the field.
`tools/build.py` holds a token's hue and solves only its lightness.
`@adobe/leonardo-contrast-colors` is the comparison that settles it: it solves a colour **to a stated ratio**, measured at 20 of 20 values within 0.08 of the ratio asked for, and
it is what [95-extending.md](95-extending.md) points at for a colour this system does not have.

**What would change it:** a generator that takes a target ratio and a ground as inputs. That is
Leonardo, and it is already the recommendation.

## Animated and shader grounds

**Declined by a rule this system already holds, and the rule has a number behind it.**

`shaders.com` and `ShaderGradient.cc` produce animated, non-enumerable grounds.
[50-surface-texture.md](50-surface-texture.md) rules that a ground whose pixels are not enumerable
carries no text at all, and [90-evidence.md](90-evidence.md) records why: on a mid-tone ground the
contrast approximation moves by up to 82%.

An animated shader is that failure with a time axis added - the worst pixel under a given word is
not merely unknown, it is different on the next frame.

They are not candidates for a product surface. A marketing-page band that carries nothing of its own
is the one place a non-enumerable ground is permitted, and
[75-spec-sheet.md](75-spec-sheet.md#grain) already specifies that case at roughly 300 bytes with no
network request and no animation.

**What would change it:** nothing, for a surface carrying text. The rule is not about shaders.

## Production equipment: mockups, 3D templates and an animation editor

**Declined as design-system material; noted as presentation equipment.**

`ls.graphics` and `ContentCore.xyz` sell device mockups and 3D motion templates. `jitter.video` is
an animation editor - "a collaborative motion design tool" in its own words, 2026-09-21 - that
exports video, GIF and Lottie. Nothing in any of the three is a rule, a value or a structure a
design system can be specified from: Jitter makes a motion, and this system's gap is the
specification a motion is made to.

They are legitimately useful for the outward-facing formats in
[75-spec-sheet.md](75-spec-sheet.md#3-formats) - a presentation asset is not a design decision. They
are recorded here so that "we looked at these and they are equipment" is on the record rather than
being rediscovered as a candidate.

## Award and showcase galleries as a standing input

**Declined as a trigger; kept as calibration.**

The measurable artefact on an award gallery is not the winning sites, it is the **published rubric**,
because that is the field stating what it weighs. Awwwards publishes:

```text
Design: 40%   Usability: 30%   Creativity: 20%   Content: 10%
```

with an Honourable Mention at 6.5 and a Developer Award above 7.

Read honestly, **60% of that score is appearance and invention and 40% is whether it works and says
anything.** That is the only numeric definition of high craft found published anywhere in four
rounds of screening, and it is worth knowing. It is also the reason a gallery is not a design-time
input for an instrument of record: this system's own weighting is the other way round.

**What would change it:** a gallery that indexes by a question an agent asks mid-screen. The one
close call is a gallery organised by colour, declined below.

## Further screening of social design accounts

**Declined after two passes.**

Two independent passes measured the same four published accounts, and
[90-evidence.md](90-evidence.md) carries both the measurements and the correction the second made to
the first. Eight structural devices were extracted, of which five became entries and one was
declined.

The return on a third pass is low: these are feed thumbnails optimised to be clicked, which is a
different job from an interface, and the structural vocabulary they carry has now been harvested.
The devices were worth taking once. The accounts are not a standing input.

## Ripplix, as a motion source

**Declined as a motion source; kept as a census of what moves.**

Motion is the measured weak point of this system and has been in every round, so `ripplix.com`,
which calls itself the "World's Largest UI Animation & Micro Interaction Library", was screened
against it directly on 2026-09-21. It publishes
**7,000+ animations from 1,000+ real apps**, organised by surface with counts, behind a login at
$5 a month.

**On the pages reachable without an account, an entry carries a title, an app name, a category tag
and a preview - and no duration, no easing curve, no CSS and no downloadable specification.**

The gap this system has is a gap in **specifications**. What that library holds is **recordings**.
A video of an interaction is an observer's reading of somebody else's number with a time axis
added, which is one step further from the author's own value than a documentation page is - and the
rule this evidence base runs on prefers shipped source precisely because a constant in source is
the author's own number.

The comparison settles it. Five shipped libraries read from source in a single round produced a
velocity threshold, a distance threshold, a settle duration on a named curve, a stack scale step,
nine curves and eight durations, every one of which is now in
[74-interaction-constants.md](74-interaction-constants.md). Seven thousand recordings produce none
of those without somebody measuring each one frame by frame.

**What declining it gives up, named rather than glossed.** It is a genuine **census of what moves**,
by surface: which interactions in the field are animated at all. This book cannot answer that today
and a library of recordings answers it better than a library of source ever will. If the question
is ever "should this surface move", that is where to look - and it is browsing, not a design-time
input.

**The limit of this screen, and what would change it:** two pages, read without an account. If
entries behind the login carry durations and curves, this becomes the first real motion source
found in four rounds and the verdict reverses. Somebody with an account should check one entry.

## A gallery indexed by colour: webzooo.com

**Declined as a design-time input; the reason is what a colour query is for here.**

`webzooo.com` describes itself as "a curated website inspiration gallery where designs are organized
by color, palette and hex code": 4,000+ sites across 33 industries, free, read on 2026-09-21.
It was the one gallery indexed by a question rather than by taste, which is why the award-gallery
entry above left it open.

**What an entry actually carries**, read from the served page of one,
`webzooo.com/site/tailride`: an industry (`FinTech & Banking`), one face name (`Inter`) and a
sentence of description. The hex palette the site advertises is not in the served page; it may
render in the browser and was not rendered here, so the palette claim is the site's and not a
measurement.

**Why it is declined even if the palette is there.** A colour query answers "what do sites at this
hue look like", and this system asks a colour question once per product, when a product takes its
own accent. That question is already answered by measurement - the hue corridor in
[10-color.md](10-color.md#why-hue-198) - and by `tools/build.py --accent-hue`, which refuses a hue too
close to a semantic colour. A screenshot at the same hue adds a look to copy, which is the input
[75-spec-sheet.md](75-spec-sheet.md) refuses to take.

**What would change it:** palettes published as data that can be read in bulk. 4,000 sites with
their painted colours would extend the hue measurement from 14 products to a corpus, and that is
worth having.

## An unsourced superlative as a palette source

**Refused, and this one is worth stating plainly because it is the exact input this system exists
to prevent.**

`figma.expert`, an account Instagram labels `AI-generated profile`, publishes a carousel titled
`Most Expensive Colour Pallet In Figma (2026)`.

"Most expensive" is not a property a palette has. No source is given for it anywhere in the post,
and none could be: there is no measurement that would establish it, which is what separates it from
every other claim in this book.

This system's whole authority is that a value is traceable to something measured - a contrast ratio
solved against a stated ground, a hue chosen by measuring where the field already is, a duration
read out of shipped source. **Adopting a palette on the strength of an unsourced aesthetic
superlative would undo the thing the system is for**, and it would do it invisibly, because the
resulting colours would look exactly as plausible as the solved ones.

The account's *format* is measured and used: its four-corner frame is the third independent
instance of that device and [90-evidence.md](90-evidence.md) records it. **Take the frame; take no
colour.**

That is the general rule and it is not about this account: a source can be good evidence for one
thing and no evidence at all for another, and saying which is which is the work.

## Not yet screened, and named so the gap is visible

These are not declines. They are candidates with a measured reason for not having been reached, and
naming them without measuring them would be the padding the rules above forbid.

| candidate | why it is interesting | why it has not been screened |
|---|---|---|
| **osmo.supply** | publishes the code behind award-winning work, and code is measurable where a screenshot is not; it lists CSS and GSAP easings and 100 buttons, which touch the motion gap | priced on 2026-09-21 at 25 euros a month for one seat, code behind the paywall. Its free vault of 20 resources is the next cheap step: one easing with a stated curve and duration would make it a motion source |
| **A curation site aimed at empty states specifically** | empty states are this system's weakest evidence area - **zero examples** in the 91-system corpus, against a component this book specifies in three kinds | searched for and **not found**. A landing-page gallery was screened instead and does not answer it |
| **Flow libraries** such as `pageflows.com` | multi-screen flows, which no source screened so far carries | subscription-gated at the point where the content starts |
| **A published system shipping a figurative illustration set with stated construction rules** | the whole figurative case currently rests on two CC0 asset libraries with no governance rather than on a system | none found. Carbon's pictograms are the monochrome case; the figurative case has no published system behind it |
| **Six more component taxonomies** - Material 3, Spectrum, Polaris, Primer, Carbon, Atlassian | each publishes a component list that would extend the coverage cross-check | the six lists already used returned 34 rows, and a seventh yielding nothing would not have been reportable as evidence of completeness. [05-coverage.md](05-coverage.md) states the limit this leaves |

A decline with a reason is coverage. A decline nobody wrote down is a question that gets asked again.

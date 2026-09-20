# How this repository was assembled, and what was verified

Moved here from the repository root on 2026-09-21: it is the maintainer's record of the first publication, and a visitor's first file after the README should say how to use the system rather than how it was scrubbed.

This is the first commit of a system that existed for three rounds as private working material.
It records what was carried across, what was deliberately not, and what was checked before it was
published - so that a reader can tell which claims in this repository were re-verified here and
which were inherited.

It is a one-off record of the publication, not a changelog.
[design/90-evidence.md](../design/90-evidence.md) is where the system's own numbers live, and it is
maintained; this file is not.

## 1. The scrub

The private material this book grew out of carried internal working paths, an internal role noun
used fifteen times, and one provenance sentence naming where evidence had been captured from.
None of that belongs in a public repository, and no later commit removes something from a history
that already carries it - which is why this repository begins at one finished commit rather than at
an iterative series.

Ten probes, each over **every file git will publish**, each required to return nothing:

```text
46 tracked files in the tree

clean absolute home-directory paths
clean any absolute home path
clean internal task directories
clean an internal role noun
clean internal tooling vocabulary
clean a personal device or account
clean build-environment leakage
clean private document links
clean private-material markers
clean an agent co-author trailer

ALL PROBES CLEAN
```

**That run reported clean once before it was true**, and it is recorded because the failure mode
is the one worth knowing. The first version built its file list with `mapfile`, which does not
exist in the shell it ran in, so every probe searched an empty list and every probe reported clean.
A scan that finds nothing because it looked at nothing is indistinguishable in its output from a
scan that found nothing. The script now asserts its file list is non-empty before it searches, and
that assertion was itself demonstrated failing against a deliberately empty list.

The measured leak surface before the scrub, for the record: **0** absolute home-directory paths, **15**
uses of the internal role noun across 7 files, and **1** internal working directory cited as
evidence provenance - 16 hits across 7 files. `halderworks` appears 56 times and stays; it is the
brand.

**Two changes were rewrites rather than deletions**, because the rules they carried are real:

- The internal role noun is replaced with public language throughout rather than deleted, because
  every rule it carried is real. The sentence about the wordmark, for one, used to attribute the
  commission to an internal role and now reads "a mark is a commission rather than something an
  agent invents" - the same rule, legible to somebody who has never seen the private material.
- **`design/90-evidence.md`'s capture provenance is rewritten, not repointed.** It used to cite
  screenshots taken from a browser session that was signed in, held in an internal directory. Rewriting
  the path would have left the sentence still recording whose account the evidence came from. The
  measurement is kept in full - five screenshots, what they were for, the date - and the
  provenance now says they are of published pages, held outside this repository and not
  redistributed, because a screenshot of somebody's published work is theirs.

Nothing in this repository names an individual's account, the accounts they subscribe to,
anything they bookmarked, or any private browsing. The four published accounts screened for structural devices are cited as sources, the
same way the design systems are.

## 2. The coverage checker, including the rule that had to be seen to fail

```text
142 surfaces checked: 106 covered, 10 partial, 26 excluded.
23 refusals swept across the rule files, 23 resolved to a row.
6 external taxonomies named in the cross-check manifest.
381 internal links and anchors checked.
0 unbacked.
```

`tools/check-coverage.py` exits 0.

**The fourth rule was demonstrated RED before it was trusted**, against the exact state it exists
for: the window-splitter refusal that sat in `design/35-layout.md` for three rounds with no
inventory row. Deleting that row from a throwaway copy:

```text
FAIL  35-layout.md:130  refuses 'half-width rail' and no row in 05-coverage.md carries a
      distinctive word from it. Rows carrying each word: {'half-width': 0, 'rail': 5}; a word
      needs 1 to 3.
FAIL  35-layout.md:130  refuses 'resizable splitter' and no row in 05-coverage.md carries a
      distinctive word from it. Rows carrying each word: {'resizable': 0, 'splitter': 0}; a
      word needs 1 to 3.

140 surfaces checked: 105 covered, 10 partial, 25 excluded.
22 refusals swept across the rule files, 20 resolved to a row.
2 unbacked.
```

Putting the row back and changing nothing else returns it to 0 unbacked.

**The first version of that rule did not fail**, and that is worth recording because it is the
whole reason the rule is shaped the way it is. It accepted any content-word match, so `rail` -
which appears in five unrelated rows - resolved the splitter refusal and the sweep still reported
22 of 22 with the row deleted. The check built to catch that leak did not catch it. Two changes
fixed it: a sentence refusing two things is **two** refusals, and a word resolves only if it is
**distinctive**, present in 1 to 3 of 142 rows.

Two further findings came out of running it, both real:

- Two sentences in the book were drawing instructions written in refusal grammar - "there is no
  horizontal gridline where the bars already start from a baseline", "there is no connector". Both
  were reworded, which is the check teaching the prose to keep a refusal and an instruction apart.
- Three inventory rows contained an escaped pipe inside a note, which splits the row into five
  cells so it **silently stops being a row**. Only the counts line caught it, and only because the
  header had been written before the table. The checker now refuses a line that carries a status
  and does not parse as a four-column row.

## 3. The build tool, which makes a published promise true

Three documents instructed a reader to run `tools/build.py`, and
[design/95-extending.md](../design/95-extending.md) told a product to regenerate the palette with it
to adopt its own accent. **It did not exist.** A published instruction nobody can run is a false
statement, and it could not ship that way.

It exists now, and the output files it had to reproduce were the contract:

```text
=== rebuild both token files from the seed ===
accent hue 198; 33 colour tokens solved across 2 themes, 0 re-solved.
104 pairs held to WCAG AA 4.5:1 and 54 to 3:1, 0 below bar. 0 outside sRGB.

=== git diff of the regenerated files ===
git diff --exit-code returned 0  (0 means byte-identical)

=== the independent instrument, on the rebuilt files ===
pass 1: 20 published ratios re-derived, 0 mismatched
pass 2: 112 form-layer pairs checked against AA 4.5:1 and non-text 3.0:1
0 failures
```

**Zero tokens re-solved at the shipped hue is the point of that run**, not an absence of work: it
is the regression proving the committed set already satisfies the floors the seed records for it.
The same code path does real work on a different hue:

```text
solved  hw-border-strong (dark): re-solved L 0.5160 -> 0.5162 at hue 318
solved  hw-accent (dark):        re-solved L 0.6190 -> 0.6296 at hue 318
solved  hw-accent-ring (dark):   re-solved L 0.5120 -> 0.5236 at hue 318
accent hue 318; 33 colour tokens solved across 2 themes, 3 re-solved.

shipped   223 property declarations,  145 distinct
hue 318   223 property declarations,  145 distinct
colour tokens: shipped 33, hue 318 33, names identical: True
values that changed: 26 of 33

pass 1: skipped. This set is built at accent hue 318; the published ratios were measured at
        198 and do not describe it.
pass 2: 112 form-layer pairs checked ... 0 failures
```

And the book's claim that a product cannot take hue 150 is now executable rather than written:

```text
FAIL  accent hue 150 sits 4.4 from hw-success in light theme, below the 8.0 this system
      requires (10-color.md#why-hue-198)
FAIL  accent hue 150 sits 1.4 from hw-success in dark theme, below the 8.0 this system
      requires (10-color.md#why-hue-198)

refusing to write: 2 colour(s) do not hold their floor
```

**The architecture, and why it is not a replay.** `tokens/tokens.seed.json` is the source: one
accent hue, per-token lightness and chroma anchors, and the contrast floor each token must hold.
The build resolves hues from the seed, clamps chroma into sRGB, re-solves lightness where a floor
fails, and refuses to write if one still fails. At hue 198 the clamp and the solve are no-ops
because the shipped values already hold; every other hue exercises them.

**Two instruments, deliberately.** `build.py` solves against the seed's floors. `tools/contrast.py`
knows nothing about the seed and re-derives the ratios from the CSS a browser loads. A build that
passes while a contrast run fails would mean the seed is wrong, and one instrument checking itself
can never report that.

**The chart ramp turned out to be derivable.** Its six hues are the accent hue plus a fixed
rotation of 0, 70, 130, 190, 250 and 310 degrees, which reproduces the committed 198, 268, 328, 28,
88 and 148 exactly. That was measured rather than assumed, and it is why a new accent rotates the
whole ramp coherently instead of leaving five colours behind.

**Value equality against the source material**, checked separately from the byte-identity above:
180 CSS custom properties and 102 token values compared, **0 differences**.

## 4. The secret scan

```text
gitleaks 8.30.1

=== the shared configuration ===
INF scanned ~619777 bytes (619.78 KB) in 184ms
INF no leaks found
gitleaks exit=0

=== and gitleaks' own default rule set, as a second opinion ===
INF scanned ~635931 bytes (635.93 KB) in 174ms
INF no leaks found
gitleaks exit=0
```

Two rule sets rather than one, because a shared configuration carries allowances that a default
set does not.

Every Markdown file also passes a structural validator - 29 files, 0 errors - after four
order-dependent duplicate anchors and one untagged code fence were fixed.

## 5. What each round contributed, and what was left out

Four rounds of measured evidence fed this book. Everything below is what was carried and what was
not, with the reason.

### The most recent round: six systems read from installed packages

| absorbed | where it landed |
|---|---|
| The ARIA Authoring Practices Guide - 30 patterns, 381 bindings, and the practice page whose sections are the missing artefact | [design/72-keyboard.md](../design/72-keyboard.md), a new file, plus a one-line keyboard field on each interactive component card |
| Input modality as a peer axis of form factor, from Apple's HIG | the split stated at the top of [design/36-form-factors.md](../design/36-form-factors.md) |
| Nine theme pairs across five vendors, zero tokens added or removed | [design/90-evidence.md](../design/90-evidence.md), and it **corrects an inherited number**: expect 28 to 78% of colour tokens to move in a high-contrast theme, not "roughly a quarter" |
| The two opposite high-contrast strategies | the high-contrast row's note and the open decision in [design/05-coverage.md](../design/05-coverage.md) |
| A seed-to-token algorithm as the architecture for the missing build | `tools/build.py` |
| Contrast as integer arithmetic on the token name | screened and **declined**, in [design/85-considered-and-declined.md](../design/85-considered-and-declined.md), on transferability rather than correctness |
| Shipped dismissal and stacking constants | [design/74-interaction-constants.md](../design/74-interaction-constants.md), a new file, with this system's own durations substituted and the difference stated |
| Two independent sources shipping the reduced-motion error this book's rule was written against | [design/40-motion.md](../design/40-motion.md), which now has two shipped counter-examples behind it |
| The easing quarter-point axis | [design/90-evidence.md](../design/90-evidence.md), and `--hw-ease-standard` now records in its own usage string that it is Tailwind's default |
| A density counter-example: shrink the glyph and raise the leading ratio | [design/45-density.md](../design/45-density.md), recorded as a choice rather than an oversight |
| The 34-row coverage cross-check | 13 surfaces built, 18 written down as excluded, 3 named as compositions, and the manifest in [design/05-coverage.md](../design/05-coverage.md) |
| A 14-name marketing-section catalogue | a checklist in [design/36-form-factors.md](../design/36-form-factors.md), **not** 14 inventory rows |
| The illustration measurements, and one licence that decides an option | [design/55-iconography.md](../design/55-iconography.md) and the open decisions |

**Left out of that round, with the reason:**

- **The carousel format.** Fully measured - a 4:5 frame, a ~10.4% margin, four corner labels at
  1.70% of frame height, a cover ordinal at 15.6% stating the size of the set against a body
  ordinal at 10.2% stating its own position. It is **not** specified as a sixth format, because
  whether outward-facing slide sequences are in scope is an open owner decision and building it
  would decide that by default. The measurement is recorded in the open-decisions table so it is
  not lost.
- **A pictogram set as a dependency.** Measured at zero palette cost, Apache-2.0, 1,575 assets. Not
  adopted, for the same reason: it is a registered open decision.
- **The 14 sections as inventory rows.** They are one composition row. This is the one place where
  adding rows would be the bloat the system is explicitly built against.
- **Two named candidates that were never opened** - a micro-interaction library and a paid
  design-engineering resource. They are recorded as unscreened with what makes each interesting, in
  [design/85-considered-and-declined.md](../design/85-considered-and-declined.md), rather than listed
  as if they had been evaluated.
- **A correction about the outbound links on three account profiles.** Genuine, and not carried, because the
  book never made that claim and repeating it would reintroduce private screening detail for no
  gain.

### The round before it: platform design systems, motion, states, validation

Its findings were already in the book and are unchanged here, except where the most recent round
supersedes them: the high-contrast magnitude above, and the ranking of standing inputs, which the
most recent round re-ordered on the stated criterion of what an agent can consult **while
designing a screen**.

### The two earliest rounds: a 91-system corpus and a 44-site capture

The measured base of the book - breakpoints, container widths, measure, control heights, icon
geometry, interaction-state selectors, the hue study. Carried whole and unchanged. Every count in
[design/90-evidence.md](../design/90-evidence.md) that names a number of sites comes from these.

### Two inherited numbers, corrected

- **107, not 114.** The inventory's row count was inherited as 114 in working notes. Counted, it
  was 107, and the file's own header sentence agreed. It was 141 at publication, 142 once the rhythm row landed,
  and the script verifies the header against the table so the two cannot drift.
- **97.59%, not 98.7%.** The top-five colour share of a measured illustration reference. Re-measured
  independently over every pixel. The difference changes nothing and is recorded because an
  inherited number nobody re-ran is how a reference pack drifts.

### Applied only in part, and stated as such

**A prohibition sentence on every token** - what a token is *not* for - was recommended and is
**not** applied across the set. The two lifecycle fields beside it, `state` and `introduced`, are:
every token now carries both, with `introduced` sourced from the token file's own comment recording
which families arrived in the second pass rather than from a guess. The prohibition is not applied
wholesale because writing 112 of them would mean inventing 112 prohibitions, which is exactly what
this system exists to prevent. Where the book already states a prohibition, it is in the token's
role string.

## 5b. A late round: rhythm, the motion source, and a third carousel instance

Three additions arrived after the tree was first complete, against a stated quality bar - that the
system capture essence, style, rhythm and motion, and that each of those be **answerable rather
than aspirational**. What follows is what each turned into.

### Rhythm, which the book could nearly prove and had never stated

The book had a spacing scale, a type ramp and a line-height for every step, and **no statement
anywhere of how the three relate**. "On the grid" was a habit rather than a property.

Measured rather than asserted:

```text
35 space and size values on the 4px unit, 7 off it and all 7 declared with a reason.
```

and, over the type ramp, **0 of 10 line boxes land on the unit** - none within half a pixel.
[design/32-rhythm.md](../design/32-rhythm.md) is the answer: the unit governs the space *between*
things, type governs the space *inside* them, a baseline grid is refused with the two leading
values it would have forced, and a worked screen is measured gap by gap.

**It is enforced rather than described.** `tokens/tokens.seed.json` carries a `grid` block - the
unit, its scope, and each exception with its reason - and `tools/build.py` refuses to emit in both
directions: an undeclared off-unit value, and a declared exception whose value has moved back onto
the unit. Both refusals were demonstrated failing before they were trusted:

```text
FAIL  hw-space-12 is 13px, off the 4px unit, and is not a declared exception. Put it on the
      unit or name it in grid.exceptions with the reason it cannot be
FAIL  hw-icon-gap is a declared grid exception at 8px, which is on the 4px unit. Remove the
      exception rather than leaving a line that excuses the next drift
```

**Two defects the count found**, both of which had survived three rounds because nobody had
counted. `--hw-space-2` and `--hw-icon-gap` both claimed the icon-to-label gap, at 2px and 6px,
with directly contradictory reasons - one recording that 4px "already reads as separate" and the
other that 4px "reads as one object". And the book's claim of "exactly two off-grid values in the
system" was wrong: within the unit's scope there are seven, four of them consequences of a height
token rather than choices. Both are corrected and both corrections carry the measurement.

### Motion: the field's largest animation library, screened

Motion has been the measured weak point in every round, and the largest curated UI-animation
library in the field was named as the first real candidate found in four. It was screened before
the interaction rules were finalised rather than after.

It publishes **7,000+ animations from 1,000+ real apps**, by surface with counts, behind a login at
$5/month. **On the pages reachable without an account, an entry carries a title, an app name, a
category tag and a preview - and no duration, no easing curve, no CSS and no downloadable
specification.**

**Declined as a motion source, and the reason is structural rather than a matter of quality:** the
gap is in *specifications* and what it holds is *recordings*. Five shipped libraries read from
source in one round produced a velocity threshold, a distance threshold, a settle duration on a
named curve, a stack scale step, nine curves and eight durations. Seven thousand recordings produce
none of those without somebody measuring each one frame by frame.

It is kept for the one question it answers better than source does - a census of *which*
interactions in the field move at all. The limit is stated in the entry: two pages, no account, and
if entries behind the login carry durations the verdict reverses.

**One finding about the field rather than about this book:** an earlier round measured 3 of 91
published systems mentioning any duration; the field's largest animation library publishes 7,000
recordings and, on its open pages, not one. The specification gap is the field's.

### A third instance of the four-corner frame, and a refusal

A screened account's carousel cover carries the same four-corner frame already measured on two
unrelated accounts, with a different payload in each corner. **That is a third independent
instance**, which moves it from a device two accounts share to a format with support - and the open
decision on carousel scope now records it.

Two things go with that finding. **The platform labels that account `AI-generated profile`**, in
its own words beneath the handle; that is recorded as provenance, and it does not weaken the format
measurement, because a frame is a frame whoever drew it. And **every asset it advertises is behind
a direct message**, so nothing was obtained and nothing from any of them is in this system.

**Its headline claim is refused, and it is worth naming as the clearest case in the repository of
what this system is for.** The colour post is titled `Most Expensive Colour Pallet In Figma (2026)`.
"Most expensive" is not a property a palette has and no source is given, because none could be.
Adopting it would undo the thing the system exists to do, invisibly, because the resulting colours
would look exactly as plausible as the solved ones. **The frame was taken and no colour was.**

### Conviction, essence and style

The bar named four words. Rhythm and motion became the two sections above.

**Conviction** is the outcome and is stated once, in [README.md](../README.md): a reader should be
able to tell from a screen built with this that somebody decided. Its corollary is the working
rule - a rule with no reason attached is itself a default, and adding rules does not add conviction
- which is how "master design system" and "not bloat" turn out to be one requirement.

**Essence and style** cannot be measured directly, and the honest proxy was already in the book.
[design/80-anti-patterns.md](../design/80-anti-patterns.md) now says plainly what its thirty-question
checklist does and does not do: a screen that fails one item is reliably generic, and a screen that
answers all thirty is not automatically good. The list removes failures; it does not supply
judgement. Claiming otherwise would have been the same kind of unsourced superlative the repository
refuses one section earlier.

## 6. The open decisions

[design/05-coverage.md](../design/05-coverage.md#open-decisions) holds them, and it is maintained where this file is not.
Six were open at publication, and two further things that are not decisions: right-to-left and localisation have no coverage row, and there is no logomark or wordmark.

## 7. What was not done here, so nobody assumes it was

- **Nothing was rendered.** No screen in this repository has been rasterised during this pass. Every
  contrast number is computed; every layout rule is on paper. A rule that is correct arithmetically
  and wrong in a browser would pass everything above.
- **The field was not re-screened.** The cross-check manifest names six external taxonomies and the
  date. Six more are named as never checked at all.
- **The weekly workflow has not run on a real runner.** Its YAML parses, all three of its shell
  steps pass `bash -n`, and both of its jobs were executed locally against this tree: the
  consistency job exits 0 with an empty summary, and the source job extracted and checked 21 cited
  sources, of which the 8 its host was permitted to reach returned 200. Its first real run
  will be its first run on a hosted runner.
- **The Apache licence text was not fetched from its canonical URL**, which the machine it was
  assembled on was not permitted to reach. It was taken from a locally installed copy, cross-checked against a
  second independent local copy - identical but for `http` against `https` on one line - and its
  section 9 was compared word for word against the canonical text retrieved separately. The `http`
  form matches the canonical.

# Coverage

This is the third round of an outside reader finding holes in this system that nobody working
inside it had reported.
The cause is structural rather than careless: the system had no statement of what a complete design
system contains, so its holes were invisible until somebody went looking for one specific thing.

This file is that statement.
Every surface a design system of this kind must answer is listed below, whether or not this system
answers it, and each is marked `covered`, `partial` or `excluded`.

**The list is derived from what a design system has to answer, not from what this one happens to
contain.**
That is the only way it can report a gap.

**And that claim used to have no citation**, which is the second thing a reader should know.
The inventory named no external taxonomy anywhere, so it listed what its authors thought of, and a
list of what its authors thought of cannot prove that nothing is missing. It was then audited
against six external lists and **34 rows came back that it had never named**.

The proof that it under-reported is one line of this book.
[35-layout.md](35-layout.md) refuses a resizable splitter, with a stated reason, and **there was no
row for it** - while an external pattern set carries `windowsplitter` as one of its thirty patterns.
Swept across the whole book, seven of eight refusals stated in rule files reached this inventory and
that one escaped, into exactly the class of gap this file exists to report.

`tools/check-coverage.py` is what stops that recurring. It reads this file and fails when a
`covered` row names a file or a section that does not exist, when a `partial` row does not say what
is missing, when an `excluded` row gives no reason, **when a refusal stated in a rule file does not
name the inventory row that carries it**, **when a sentence claiming a surface already has an entry
resolves to no covered or partial row here**, when the manifest below names no lists or carries no
date, and when any internal link or anchor in the book does not resolve.
A row is a claim, and the script is what makes it a checkable one.

Counts, which are what a reader should look at first, and which the script verifies against the
table so they cannot drift:
**149 surfaces, 114 covered, 9 partial, 26 excluded.**

## The cross-check manifest

The external taxonomies this inventory has been proved against, with their sizes and the date, so
the next reader re-runs the check rather than trusting it. Five of the six were read from installed
packages rather than from a page, because a list in shipped source is the author's own and a page is
an observer's reading of it.

| external list | size | how it was read | on | what it returned |
|---|---:|---|---|---|
| ARIA Authoring Practices Guide patterns | 30 | `w3.org/WAI/ARIA/apg/patterns/`, parsed | 2026-09-21 | `link`, `accordion`, `disclosure`, `toolbar`, `windowsplitter`, `treeview`, `treegrid`, `meter`, `slider-multithumb`, `feed` |
| USWDS components | 75 | `@uswds/uswds@3.14.0`, `packages/usa-*` | 2026-09-21 | `usa-skipnav`, `usa-nav`, `usa-sidenav`, `usa-header`, `usa-footer`, `usa-summary-box`, `usa-in-page-navigation`, `usa-collection`, `usa-step-indicator`, `usa-input-mask` |
| Ant Design components | 69 | `antd@6.6.3`, capitalised exports | 2026-09-21 | `Descriptions`, `Popconfirm`, `Anchor`, `Splitter`, `Tree`, `Timeline`, `Cascader`, `Transfer`, `Mentions`, `Tour`, `Steps`, `Drawer`, `Image` |
| Base Web components | 89 directories | `baseui@18.2.0` | 2026-09-21 | `side-navigation`, `app-nav-bar`, `data-table` bulk selection, `tree-view`, `notification`, `progress-steps`, `dnd-list`, `payment-card`, `phone-input`, `pin-code`, `aspect-ratio-box` |
| A landing-page gallery's page types and sections | 13 + 14 | `land-book.com` | 2026-09-21 | `Sign Up`, `Footer`, `Product listing`, `Product page`, and the 14-name section catalogue |
| Mobbin's and Refero's public taxonomies | 23 + 15 | captured in an earlier round and re-used | 2026-09-21 | `Log In`, `Resetting Password`, `Settings & Preferences`, `My Account & Profile`, `Notifications`, `Setting Up`, `Dashboard`, `Catalog Page`, `Product Details` |

**What this manifest proves and what it does not**, stated because the opposite is the easy claim.
It proves the inventory was missing at least 34 rows. **It does not prove 34 is all of them, and it
cannot.** Material 3, Spectrum, Polaris, Primer, Carbon and Atlassian all publish component lists
and none was enumerated for this purpose, because the six above already returned 34 and a seventh
list yielding nothing would not have been reportable as evidence of completeness.
[85-considered-and-declined.md](85-considered-and-declined.md) carries those six as named,
unscreened candidates.

**And one row since came from neither list.** `Vertical rhythm` above was found by a reader
asking whether this system captures rhythm - a question no component taxonomy asks, because it is
a property of a system rather than a surface it ships. That is the clearest available evidence for
the paragraph above: six external lists returned 34 rows and a seventh kind of reader returned a
thirty-fifth that none of the six would ever have carried.

**Only rows with no answer were reported.** An external row already answered under another name -
`listbox` by Select, `spinbutton` by Numeric stepper, `grid` by Data table, `alert` by Banner and
inline alert - produced nothing, which is how the audit stayed short.

## Foundations

| surface | status | where | note |
|---|---|---|---|
| Colour palette, and how each value was arrived at | covered | `10-color.md#why-hue-198` | 33 tokens per theme, and the palette is closed at that size. There is no fifth colour beyond the ink, the accent and the three semantics: a treatment that needs one is asking for a colour with no meaning to carry, and `75-spec-sheet.md` refuses the one candidate on exactly that ground |
| Which colours may sit on which | covered | `15-color-combinations.md#ink-on-ground` | |
| Light and dark theming | covered | `10-color.md#the-contrast-matrix` | both tables certified; `tokens/tokens.css` carries the attribute and the media query |
| Contrast verification as a process, not a claim | covered | `90-evidence.md#the-solver` | |
| Typeface choice and fallbacks | covered | `20-type.md#why-not-inter` | |
| Type scale, line-height, tracking, weight | covered | `20-type.md#the-scale` | |
| Reading measure | covered | `20-type.md#measure` | |
| Numerals and tabular figures | covered | `20-type.md#figures-which-is-the-rule-most-often-missed` | |
| Spacing scale | covered | `30-space-radius-elevation.md#space` | |
| Vertical rhythm, and how the spacing scale relates to the type ramp | covered | `32-rhythm.md#the-unit-and-exactly-what-it-governs` | **this row was not found by the cross-check; it was found by a reader asking whether the system captures rhythm, which is the inventory working rather than a hole in it.** The system had a spacing scale, a type ramp and a line-height set and no statement of how the three relate, so being on the grid was a habit rather than a checkable property. `tools/build.py` now refuses to emit an off-unit space or size value that is not declared with a reason |
| Corner radius and nesting | covered | `30-space-radius-elevation.md#radius` | |
| Elevation and shadow | covered | `30-space-radius-elevation.md#elevation` | the panel exception is in `36-form-factors.md` |
| How a surface separates from the one behind it | covered | `50-surface-texture.md#the-four-ways-a-surface-may-separate` | |
| Forced colours, and which separation survives them | covered | `50-surface-texture.md#under-forced-colours` | forced colours drops fills and shadows and repaints borders, so the filled level is the one that loses its edge, and it carries a transparent border for the user agent to repaint. No tool reads the book's CSS snippets, so the rule is checked by review |
| Texture, grain, gradient, glass | covered | `75-spec-sheet.md#2-surface-and-texture-styles` | the fourth pass re-scoped the blanket refusal in `50-surface-texture.md`, which still owns the decision: a ground may carry a pattern only where every pixel is a solved token and the ink is certified against the worst of them, and a ground whose pixels are not enumerable carries no text. Three styles are specified with their permission lists; gradients behind text and `backdrop-filter` remain refused |
| Borders | covered | `50-surface-texture.md#borders` | |
| Scrim | covered | `50-surface-texture.md#the-scrim` | |
| Motion: durations, easings, what may animate | covered | `40-motion.md#easing` | the three curves are now measured against fourteen others on one axis in `90-evidence.md`. What makes a movement start and stop - the dismissal thresholds and the one case where two properties in a transition take different durations - is `74-interaction-constants.md` |
| Reduced motion | covered | `40-motion.md#reduced-motion` | |
| Density | covered | `45-density.md#what-changes` | two settings and one attribute. A third density setting is refused there with its reason, and a published system's opposite answer - shrink the glyph and raise the leading ratio - is recorded beside it as a choice rather than an oversight |
| Iconography: set, grid, stroke, alignment | covered | `55-iconography.md#stroke-weight-which-is-the-part-that-is-usually-got-wrong` | |
| Pictograms, the one illustration set | covered | `55-iconography.md#illustration-one-pictogram-set-and-no-figurative-drawing` | `@carbon/pictograms`, Apache-2.0, named and not vendored: `currentColor`, at 48 or 64px and never at the 16px icon size, one per view, in the nothing-yet empty state or a marketing section. The sentence four files carried, that inventing one drawing per empty state ends in six unrelated drawings, argued for one set rather than none |
| Figurative illustration | excluded | `55-iconography.md#illustration-one-pictogram-set-and-no-figurative-drawing` | the only figurative construction measured bakes five values into each asset and has no dark-theme answer. Whether one is ever commissioned is an [open decision](#open-decisions) |
| Photography | excluded | `80-anti-patterns.md#imagery-and-icons` | no photography in product surfaces |
| Logomark and wordmark | excluded | `00-brand-book.md#the-mark` | a mark is a commission rather than something an agent invents |
| Sound and haptics | excluded | `05-coverage.md#foundations` | no product uses non-speech audio or haptics as an interface signal. quoth records audio as content, which is not the same thing. Adding one needs a decision about what a failure is allowed to sound like, and nothing here covers it |
| Layout grid and columns | covered | `35-layout.md#the-grid` | |
| Breakpoints | covered | `35-layout.md#breakpoints` | |
| Container widths and page margin | covered | `35-layout.md#container-widths` | |
| Layering and z-index | covered | `35-layout.md#layering` | |
| Content, tone, casing, error shape | covered | `25-content.md#errors` | |
| Interaction states, all nine | covered | `60-states.md#the-matrix` | |
| Focus | covered | `60-states.md#focus-visible-never-focus-and-never-removed` | |
| Right-to-left text inside a left-to-right product | covered | `35-layout.md#direction-and-text-in-another-script` | `dir="auto"` on every element showing text the product did not write, `<bdi>` around user text inside a product sentence, `text-align: start`, and logical inline-axis properties in the book's CSS. quoth's transcripts can arrive in Arabic, Hebrew or Urdu, so this half was live rather than hypothetical |
| A localised, mirrored build | partial | `35-layout.md#direction-and-text-in-another-script` | **no decision is recorded.** Nothing mirrors today and no product has a non-English interface. The logical properties are in, so a mirrored build would add rules rather than rewrite them; whether any product ships one is an [open decision](#open-decisions) |
| Accessibility beyond contrast: landmarks, focus order, keyboard maps | covered | `72-keyboard.md#the-map` | closed by the keyboard file. It carries the tab-sequence convention, the roving `tabindex` and `aria-activedescendant` split, the disabled-in-composite rule, the platform key table, and one row per component - which is the single page a reviewer checks a screen against. The `Input modality and keyboard` section below carries the parts as rows |

## Form controls

| surface | status | where | note |
|---|---|---|---|
| The shared control box model | covered | `66-forms.md#the-box-model-every-control-shares` | |
| Text input | covered | `66-forms.md#text-input` | anatomy in `65-components.md`; the box model here replaces its padding line |
| Textarea | covered | `66-forms.md#textarea` | |
| Select, native against custom | covered | `66-forms.md#select-and-native-against-custom` | |
| Combobox with type-ahead | covered | `66-forms.md#combobox-with-type-ahead` | |
| Checkbox and radio | covered | `66-forms.md#checkbox-and-radio` | |
| Switch, and which of switch and checkbox a case takes | covered | `66-forms.md#switch` | |
| Slider | covered | `66-forms.md#slider` | |
| Numeric stepper | covered | `66-forms.md#numeric-stepper` | |
| Date and time | covered | `66-forms.md#date-and-time` | |
| File upload, drop target and chosen files | covered | `66-forms.md#file-upload` | |
| Search with its clear affordance | covered | `66-forms.md#search` | |
| Segmented control | covered | `66-forms.md#segmented-control` | |
| Rich text and code editing | excluded | `05-coverage.md#form-controls` | no product takes formatted input. A code or transcript editor is a component with its own selection model, syntax colouring and undo story, and it would need a seventh chart-style palette for tokens. quoth's transcript is displayed rather than edited |
| Colour, rating, and tag or token input | excluded | `05-coverage.md#form-controls` | no product has a use. An instrument of record takes hashes, ids, durations and choices; none of these three appears in any product's input surface, and the brief for this system says not to invent a control we have no use for |

## Form furniture and validation

| surface | status | where | note |
|---|---|---|---|
| Label, and why a placeholder is not one | covered | `66-forms.md#label` | |
| Required and optional marking | covered | `66-forms.md#required-and-optional` | |
| Helper text | covered | `66-forms.md#helper-text` | |
| Character count | covered | `66-forms.md#character-count` | |
| Field group and legend | covered | `66-forms.md#field-group-and-legend` | |
| Form layout at each breakpoint | covered | `66-forms.md#form-layout-by-breakpoint` | |
| Label above against label beside | covered | `66-forms.md#form-layout-by-breakpoint` | |
| The action row and where the primary action sits | covered | `66-forms.md#the-action-row` | |
| Disabled against read-only | covered | `66-forms.md#disabled-against-read-only-which-are-not-the-same-control` | |
| When validation fires | covered | `67-validation.md#when-validation-fires` | |
| Where the error sits, and its colour on every surface | covered | `67-validation.md#the-error-colour-on-every-surface-it-can-appear-on` | |
| Binding the error to the field for a screen reader | covered | `67-validation.md#binding-the-error-to-the-field` | |
| Form-level error summary | covered | `67-validation.md#the-form-level-error-summary` | |
| Success and pending states | covered | `67-validation.md#success-and-pending` | a green tick on every valid field is refused there, with its reason: a form that congratulates the reader on each field has made the error state harder to find |

## Other components

| surface | status | where | note |
|---|---|---|---|
| Button | covered | `65-components.md#button` | |
| Card | covered | `65-components.md#card` | |
| List row | covered | `65-components.md#list-row` | |
| Data table | covered | `65-components.md#data-table` | |
| Badge | covered | `65-components.md#badge` | |
| Tabs | covered | `65-components.md#tabs` | |
| Dialog | covered | `65-components.md#dialog` | |
| Toast | covered | `65-components.md#toast` | the stack was a count with no geometry, so two implementations of it would not have looked alike. `74-interaction-constants.md#toast-stack-geometry` fixes the scale step and the offset |
| Empty state, and its three kinds | covered | `65-components.md#empty-state` | |
| Link | covered | `65-components.md#link` | the accent's first job, spent on "a link" that this book never specified. `visited` and `external link` both returned 0. There is no visited style and the row says why |
| Accordion and disclosure | covered | `65-components.md#accordion-and-disclosure` | three matches before this entry, all of them one token's `usage` string and its two export copies |
| Callout or summary box | covered | `65-components.md#callout` | 0 as a component, in a book that covers documentation pages. A neutral callout is the Framed style rather than a second component |
| Key-value pair list | covered | `65-components.md#key-value-pair-list` | a sweep for description list, key-value and definition list returned 0. An instrument of record displays a single record's fields constantly |
| Inline destructive confirm | covered | `65-components.md#inline-destructive-confirm` | 13 matches for `confirm` and none a pattern, which made the dialog the only place a confirmation could live and therefore made every delete a modal |
| Data display, alignment, numeric formatting, dates | covered | `70-data-display.md#numeric-formatting` | |
| The five states of a data container | covered | `70-data-display.md#the-five-states-of-a-data-container` | |
| Charts | covered | `70-data-display.md#charts` | |
| Bulk selection and select-all | covered | `70-data-display.md#bulk-selection-and-select-all` | a sweep for bulk, select all and multi-select returned 0, while this file requires a table to handle hundreds of rows |
| Skeleton and loading | covered | `60-states.md#loading-holds-the-width` | |
| Menu, dropdown and context menu | partial | `35-layout.md#layering` | `--hw-z-dropdown` names "menu, select, popover, tooltip" and only the select and the two form popovers in `66-forms.md` have an anatomy. A menu has none: no item height, no separator, no submenu rule, no destructive item treatment |
| Tooltip | partial | `55-iconography.md#alignment-against-text` | required by the icon-only control rule and by the truncation rule in `25-content.md`, and specified nowhere: no delay, no placement, no max width, no touch behaviour |
| Popover | partial | `66-forms.md#combobox-with-type-ahead` | the combobox and calendar popovers now fix the surface, border, radius, shadow and layer, which is the first popover anatomy in the system. A general popover still has no placement, flip or arrow rule |
| Banner and inline alert | partial | `67-validation.md#the-form-level-error-summary` | the form error summary is specified, and `70-data-display.md` requires a banner for a partial load, which has no anatomy: no dismissibility rule, no placement, no relation to the toast |
| Breadcrumb, pagination, command palette | partial | `05-coverage.md#other-components` | none is specified. Pagination is the one that bites first, because `70-data-display.md` requires a table to handle hundreds of rows and says nothing about how a reader moves through them |
| Avatar | partial | `30-space-radius-elevation.md#radius` | `--hw-radius-full` is reserved for "avatars and count pills", so the radius is decided and nothing else is: no sizes, no fallback initials, no group or stacking rule |
| Progress indicator | partial | `40-motion.md#what-may-animate` | a determinate indicator is the only thing in the system allowed to loop, which is a permission rather than a specification: no height, no track colour, no indeterminate fallback, and `66-forms.md` needs one for upload |

## Form factors

| surface | status | where | note |
|---|---|---|---|
| Desktop application shell | covered | `36-form-factors.md#1-the-desktop-application-shell` | the shell itself is in `35-layout.md#the-app-shell` |
| Menu-bar utility and its floating panel | covered | `36-form-factors.md#2-the-menu-bar-utility-and-its-floating-panel` | |
| Marketing and documentation page | covered | `36-form-factors.md#3-the-marketing-or-documentation-page` | the form factor was covered while naming no sections within it, so an agent had five typographic devices and no idea what a marketing page is made of. The fourteen-name checklist is there now |
| Small viewports and the coarse pointer | covered | `36-form-factors.md#4-small-viewports-and-the-coarse-pointer-that-usually-comes-with-one` | the section was named for two axes and now owns the viewport half. The pointer is one rebind and the keyboard is `72-keyboard.md` |
| Native mobile, email, print, terminal, and the rest | excluded | `36-form-factors.md#deliberately-out-of-scope` | each is listed there with its reason and what adding it would cost |

## Governance

| surface | status | where | note |
|---|---|---|---|
| How to extend the system without forking it | covered | `95-extending.md#the-decision-in-order` | |
| Product namespacing | covered | `95-extending.md#a-products-own-namespace` | |
| Adding a component or a token | covered | `95-extending.md#adding-a-token` | |
| Reporting a gap | covered | `95-extending.md#reporting-a-gap` | |
| Where every number came from | covered | `90-evidence.md#the-two-capture-passes` | |
| Anti-patterns, by surface | covered | `80-anti-patterns.md#colour` | |
| A ship checklist | covered | `80-anti-patterns.md#the-checklist` | |
| This coverage inventory | covered | `05-coverage.md#foundations` | checked by `tools/check-coverage.py` |
| The token build and its verification | covered | `95-extending.md#the-one-thing-a-product-may-change` | `tools/build.py` exists and both halves are closed. It reads `tokens/tokens.seed.json`, resolves every hue from one accent seed, clamps chroma into sRGB, re-solves lightness for any token whose floor no longer holds, and refuses to write if one still fails. It also refuses an accent hue that sits closer than 8 in oklab distance to a semantic, which is what makes this book's claim that a product cannot take hue 150 true rather than merely written. `tools/contrast.py` remains the second, independent instrument |
| A shipped component library | excluded | `95-extending.md#loading-the-system-in-a-product` | there is no build step and no runtime by design: the system is a token file, a set of rules, and the discipline to report a gap rather than invent a value |

## The spec sheet

| surface | status | where | note |
|---|---|---|---|
| Named theme overlays, and how they differ from light and dark | covered | `75-spec-sheet.md#1-themes` | Instrument, Console and Editorial. An overlay fixes which values a surface may reach for; light and dark change the values themselves |
| A high-contrast theme | partial | `05-coverage.md#the-spec-sheet` | **nothing is specified and deliberately nothing is sketched.** The blocker has moved: `tools/build.py` now exists and can emit a re-solved set, so what is missing is the decision rather than the tool. Two opposite strategies are measured - a per-role re-solve pushes distinct values up, surrendering the palette collapses them down by an order of magnitude - and they answer different media queries. The [open decision](#open-decisions) names which is which |
| Surface and texture styles, as CSS that ships | covered | `75-spec-sheet.md#2-surface-and-texture-styles` | Ruled, Grain and Framed, each with its cost, its `prefers-contrast` and `prefers-reduced-transparency` behaviour, and its certified permission list |
| Named composition formats | covered | `75-spec-sheet.md#3-formats` | masthead frame, counted set, spec card, comparison pair, quotation block, and the link-preview card and the slide sequence, which have their own rows below |
| Link-preview card, the Open Graph image | covered | `75-spec-sheet.md#link-preview-card` | **this row did not exist while this file claimed the card had been admitted**, from the first public commit until the change that added it. A sweep for link preview, Open Graph, `og:image` and `og:title` returned no entry and no row. The entry is specified in fractions of its own frame, measured on 12 cards on `recent.design` and six read from the sites: aspect 1.905, headline cap height 8.4% of frame height at a 1.5 line pitch, a 10% inset |
| Slide sequence, the carousel | covered | `75-spec-sheet.md#slide-sequence` | a 4:5 frame specified in fractions of itself, from the four-corner frame measured on three independent accounts. The third, `figma.expert`, is one Instagram labels `AI-generated profile`: its frame is evidence and its colour claims contribute nothing. No new token |
| Typography treatments beyond the ramp | covered | `75-spec-sheet.md#4-typography-treatments` | the oversized ordinal, the small-caps eyebrow, the marker highlight, the bracketed aside, each with the boundary that separates it from the decorative-marker entries in `80-anti-patterns.md` |
| The mixed-face headline | covered | `75-spec-sheet.md#the-mixed-face-headline` | one display headline in Public Sans with one Newsreader span marking the term it names, on the Editorial overlay only. The face never carries emphasis, so the rule that emphasis is weight stands |
| Named colour schemes | covered | `75-spec-sheet.md#5-colour-schemes` | Record, Well and Page. A scheme selects from the permission table in `15-color-combinations.md` and never adds a pair |
| What was taken from a reference and what was left behind | covered | `75-spec-sheet.md#how-an-entry-is-written` | every entry carries both lines, and the one candidate that could not fill the second is recorded as declined rather than shipped |
| Export formats an agent can consume | covered | `75-spec-sheet.md#6-exports` | `tools/export.py` emits DESIGN.md compact and extended, a Tailwind v4 `@theme` block, plain CSS variables and W3C DTCG JSON, and exits non-zero unless all 180 custom properties it writes match `tokens/tokens.css` |
| A role description on every token | covered | `75-spec-sheet.md#every-token-carries-its-role` | all 112 entries carry a `usage` naming the job and its surfaces, and `exports/design-tokens.json` emits each as `$description`. Each now also carries a lifecycle `state` and the version it was `introduced` in, which is what lets a migration reason about a token rather than guess |
| A single machine-readable source for every value | covered | `90-evidence.md#the-solver` | `tokens/tokens.seed.json` is the source and both token files are generated from it, so there is no second place a value can live. It carries the four durations and three easings that once shipped only in the CSS, plus a `state` and an `introduced` version on every token |

## Navigation

Six surfaces, every one carried by at least one external component library and none of them
answered until the cross-check found them. [37-navigation.md](37-navigation.md) owns all six.

| surface | status | where | note |
|---|---|---|---|
| Skip link | covered | `37-navigation.md#skip-link` | the first tab stop on any shell with a permanent rail. It was absent from a book whose shell puts a rail in front of the content |
| Navigation item, its states, grouping and nesting | covered | `37-navigation.md#the-navigation-item` | `35-layout.md` gave the rail a width and its items nothing: no height, no current state, no grouping, no nesting depth |
| Toolbar anatomy | covered | `37-navigation.md#toolbar` | `35-layout.md` placed a toolbar and specified nothing inside it: no item spacing, no separator, no overflow rule, no roving focus |
| Site header and footer | covered | `37-navigation.md#site-header` | the app shell had a rail; the marketing and documentation form factor had neither. The footer is the section after it |
| In-page table of contents | covered | `37-navigation.md#in-page-table-of-contents` | `35-layout.md` allotted it a third column and no anatomy: no active-section rule, no depth limit, no scroll-spy behaviour |

## Page patterns

| surface | status | where | note |
|---|---|---|---|
| Log in, sign up, reset password | covered | `68-page-patterns.md#the-way-in-sign-in-sign-up-reset-password` | a sweep for log in, login, sign in, sign up and authenticate returned one match, a casing example. Every product with a rail has a way in |
| Settings and preferences page | covered | `68-page-patterns.md#the-settings-page` | one match, an aside in `45-density.md` that presumed a settings page this book never specified |
| 404 page, and the status it returns | covered | `68-page-patterns.md#the-404-page` | **this file claimed an entry for it from the first public commit and there was none.** A sweep for `404` returned HTTP statuses and nothing that specified the page. Two of the four sites measured answer 200 at an address that does not exist, which is why the entry mandates the status code |
| Pricing page | covered | `68-page-patterns.md#the-pricing-page` | **`36-form-factors.md` claimed an entry for it from the first public commit and there was none.** A sweep for `pricing` and `paywall` returned the checklist word and other sites' prices. Two pages measured differ in one value, the price at 17px against 56px, and the entry decides it on this book's own type rules |

## Ruled out, with the reason

Eighteen rows the field carries that nothing here needs.
**An exclusion that is written down is coverage and an exclusion that lives in someone's head is a
gap** - which is the whole lesson of the splitter, and the reason these cost one line each rather
than being left out.

Whether any one of them is a surface a product is about to need is not pending: the one product
read against them forbids the riskiest, a modal setup wizard, in its own source, and has no
notification centre and no tree view. An exclusion is one reversible line, and a product that
needs one reports the gap.

| surface | status | where | note |
|---|---|---|---|
| Window splitter | excluded | `35-layout.md#the-two-shapes-we-build` | neither a half-width rail nor a resizable splitter: a splitter is a per-user layout the product then has to store, migrate and support, and a half-width rail is a splitter with one position. The reason already existed in the rule file for three rounds and had no row here, which is the leak this inventory was audited to find |
| Tree view | excluded | `05-coverage.md#ruled-out-with-the-reason` | no product displays a hierarchy. A flat list plus a filter is the house answer, and `65-components.md#accordion-and-disclosure` refuses nesting for the same reason |
| Treegrid | excluded | `05-coverage.md#ruled-out-with-the-reason` | a tree crossed with a grid is the most expensive widget in the external pattern set at 43 keyboard rows, and nothing here needs one |
| Meter | excluded | `05-coverage.md#ruled-out-with-the-reason` | distinct from a progress indicator: a static measurement rather than a task, and no product measures one |
| Range slider with two thumbs | excluded | `05-coverage.md#ruled-out-with-the-reason` | one thumb is specified in `66-forms.md#slider`; a second is a different interaction and no product filters a range |
| Feed and infinite scroll | excluded | `05-coverage.md#ruled-out-with-the-reason` | pagination is the house answer once the breadcrumb and pagination row is finished. Infinite scroll loses the footer and loses the reader's position |
| Notification centre | excluded | `05-coverage.md#ruled-out-with-the-reason` | a toast is transient and a centre is durable state a product must store, expire and mark read. No product has an inbox |
| Step indicator and multi-step form | excluded | `05-coverage.md#ruled-out-with-the-reason` | `66-forms.md` specifies a single-screen form and no product splits one. The one multi-screen flow here is the password reset, which is three addresses rather than three steps |
| Timeline and activity log | excluded | `05-coverage.md#ruled-out-with-the-reason` | a log is a table here, and `70-data-display.md` owns it |
| Input mask, prefix and suffix | excluded | `05-coverage.md#ruled-out-with-the-reason` | the inputs this system takes are hashes, ids and durations, which a mask fights rather than helps |
| Specialised payment inputs | excluded | `05-coverage.md#ruled-out-with-the-reason` | nothing here takes a payment, a phone number or a one-time code |
| Multi-level select and transfer list | excluded | `05-coverage.md#ruled-out-with-the-reason` | a combobox with a filter is the house answer to both, and it is specified in `66-forms.md#combobox-with-type-ahead` |
| Image lightbox and media viewer | excluded | `05-coverage.md#ruled-out-with-the-reason` | photography in product surfaces is already excluded above, and this is its component |
| Mentions | excluded | `05-coverage.md#ruled-out-with-the-reason` | these are single-operator instruments with no second user to mention |
| Account and profile page | excluded | `05-coverage.md#ruled-out-with-the-reason` | single-operator instruments with no account model. The settings page above is the surface that would otherwise absorb this |
| Onboarding and product tour | excluded | `05-coverage.md#ruled-out-with-the-reason` | a coachmark layer is a product decision none of these has taken, and `65-components.md#empty-state` is the house answer to a first-run screen |
| Drag-to-reorder list | excluded | `05-coverage.md#ruled-out-with-the-reason` | `66-forms.md` already rules that drag is never the only route, and no product orders anything by hand |
| Sheet or drawer as a general surface | excluded | `05-coverage.md#ruled-out-with-the-reason` | the one sheet in this system is the rail below `--hw-bp-lg`, specified in `36-form-factors.md`. A general drawer is a dialog that slides |

## Covered by composition

Three surfaces the field names that this system already answers by composing things it has.
**Naming the composition is the whole row**; adding a component would be the bloat.

| surface | status | where | note |
|---|---|---|---|
| Dashboard | covered | `35-layout.md#the-app-shell` | the app shell plus `70-data-display.md#charts` plus the data table. One row saying so stops a later round rediscovering it as a gap |
| Catalog, product list, product detail | covered | `65-components.md#list-row` | list row and data table. These are commerce surfaces and no product here sells; the composition is named rather than the surface excluded, because the components genuinely answer it |
| The fourteen marketing-page sections | covered | `36-form-factors.md#what-a-marketing-page-is-made-of` | a checklist inside the marketing form factor, not fourteen component rows. **This is the one place where adding rows would be the bloat this inventory is built against**, and the checklist is what an agent building a marketing page actually needs |

## Open decisions

These are not gaps and they are not exclusions. They are questions where the measurement is done and
the answer belongs to whoever owns this system, recorded here so they stay visible rather than
living in one reader's memory.

The tables below are deliberately not in the inventory's own format, because a decision is not a
surface and should not be counted as one.
That also means `tools/check-coverage.py` does not count them, so the count here and the one in the
README are kept by hand.

**Three are open**, each with a recommendation the owner only has to not object to or overrule.
Two more are open and belong outside this book: whether to pay for Refero's reference-screen corpus,
which is a spending decision, and whether the ship checklist becomes a merge gate in every
repository that ships a screen, which is a fleet process and is not ripe until real reviews record
which of its 30 questions a tool could answer.

| decision | what is already measured | the recommendation on the evidence | what would change it | who answers it |
|---|---|---|---|---|
| **Whether quoth's live-microphone state gets its own hue** | a product-specific concept takes a product namespace, [95-extending.md](95-extending.md#a-products-own-namespace). The conventional recording red would sit at hue 27, which is `--hw-danger`'s hue in both themes | **its own hue, as `--quoth-live`**, solved by the house tools and held to the bar the accent is held to: at least 8.0 from `--hw-success`, `--hw-warning`, `--hw-danger` and `--hw-accent`, and 3:1 on every surface it sits on. That rules out recording red | no hue clears 8.0 from all four at a lightness that holds 3:1 everywhere, in which case the state shares the accent and is carried by a word and a shape | the system's owner |
| **Whether any product ships a localised, mirrored build** | the content half is written: right-to-left text inside a left-to-right product is [specified](35-layout.md#direction-and-text-in-another-script), with logical inline-axis properties in the book's CSS | **no**, recorded as excluded with that reason. It is reversible at no cost, because the logical properties are already in | a product brief naming a non-English market | the system's owner |
| **Whether a figurative illustration set is commissioned** | the monochrome pictogram set is [named](55-iconography.md#illustration-one-pictogram-set-and-no-figurative-drawing). The only figurative construction measured bakes five values into each asset and has no dark-theme answer. **The pictogram set does not look like the reference image the owner supplied**, which is a flat five-value figurative drawing, where the set is a single-colour line | **no**: figurative illustration stays excluded until a commission comes with a dark-theme answer, and its palette then comes through a product namespace, never an `hw-` token | a budget for a commission | the system's owner |

### Settled, with the reason

Each of these was once filed as open. Some are answered by an entry, some were never decisions, and
three rested on a premise the book does not support; those three are retitled here.

| decision | settled | why |
|---|---|---|
| Whether Illustration moves off the excluded row | split: the [pictogram set](55-iconography.md#illustration-one-pictogram-set-and-no-figurative-drawing) is named, figurative illustration stays excluded | naming an Apache-2.0 set is what this book already does for its typefaces and its icon set |
| Whether an illustration set inherits the accent hue or carries its own | dissolved | a `currentColor` set takes the surrounding text colour, and a figurative one would bring its own through a product namespace |
| **Slide sequences are in scope because the owner asked for them**, retitled from "yes, on the precedent of the 404 page and the link-preview card" | yes, [specified](75-spec-sheet.md#slide-sequence) | the old ground cited two entries that did not exist when it was written. The real one is the owner's request for carousel art, and the frame is measured on three independent accounts |
| **The eighteen exclusions are not waiting on a roadmap**, retitled from "which, if any, is about to be needed" | not pending | all eighteen are written down, and the one product read forbids the riskiest in its own source. [The section above](#ruled-out-with-the-reason) says so |
| **The high-contrast theme waits on role separation, not on a tool or a decision**, retitled from "which question the high-contrast theme answers" | an author's work; the inventory row stays partial until it ships | the two questions are already separate: `forced-colors: active` is [the filled level's transparent border](50-surface-texture.md#under-forced-colours), and `prefers-contrast: more` is a per-role re-solve. `tools/build.py` run with every 4.5 floor raised to 7.0 and every 3.0 to 4.5 exits 0 with 20 of 66 values re-solved and none below bar, and puts `--hw-text-secondary` and `--hw-text-muted` on one value, L 0.4343 light and 0.7299 dark. What is missing is a minimum separation between roles |
| **The mixed-face headline marks a term, not emphasis**, retitled from "whether face may carry emphasis within a line" | [specified](75-spec-sheet.md#the-mixed-face-headline) | the collision was with "emphasis is weight", and a span naming a term does the job [20-type.md](20-type.md#rules) already gives italic, so both rules stand |
| Right-to-left text inside a product | [specified](35-layout.md#direction-and-text-in-another-script) | a correctness rule: quoth's transcripts can arrive in a right-to-left script today |
| Forced colours | [specified](50-surface-texture.md#under-forced-colours) | no separation level draws its edge with a shadow, so the exposure is the filled level, which forced colours flattens |
| Whether a patterned ground is allowed where every pixel is a solved token | already published as settled, [50-surface-texture.md](50-surface-texture.md#there-is-no-texture-and-that-is-a-decision) | the rule is certified against the worst pixel, which a two-colour pattern has and grain does not |
| Whether text may sit on grain in the light theme | no | the measurement offered was of a PNG tile at opacity 0.25, where this book's grain is a turbulence filter at 0.035, and no instrument here rasterises the filter |
| Display letter spacing | not a decision | [20-type.md](20-type.md#the-scale) states -0.022em and -0.020em, with six measured references |
| How large a price is set | [decided](68-page-patterns.md#the-pricing-page) by the type rules | a price is data, and `display-1` is one page-defining headline |
| Whether the chart series stop sharing one lightness | an author's defect fix; the owner reviews the rendered result | `--hw-chart-4`, `-5` and `-6` sit 1.6, 2.5 and 3.7 from `--hw-danger`, `--hw-warning` and `--hw-success` in light, against the 8.0 the accent is held to, so they move regardless |

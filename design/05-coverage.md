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
is missing, when an `excluded` row gives no reason, **when a refusal stated in a rule file resolves
to no row here**, when the manifest below names no lists or carries no date, and when any internal
link or anchor in the book does not resolve.
A row is a claim, and the script is what makes it a checkable one.

Counts, which are what a reader should look at first, and which the script verifies against the
table so they cannot drift:
**142 surfaces, 106 covered, 10 partial, 26 excluded.**

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
| Texture, grain, gradient, glass | covered | `75-spec-sheet.md#2-surface-and-texture-styles` | the fourth pass re-scoped the blanket refusal in `50-surface-texture.md`, which still owns the decision: a ground may carry a pattern only where every pixel is a solved token and the ink is certified against the worst of them, and a ground whose pixels are not enumerable carries no text. Three styles are specified with their permission lists; gradients behind text and `backdrop-filter` remain refused |
| Borders | covered | `50-surface-texture.md#borders` | |
| Scrim | covered | `50-surface-texture.md#the-scrim` | |
| Motion: durations, easings, what may animate | covered | `40-motion.md#easing` | the three curves are now measured against fourteen others on one axis in `90-evidence.md`. What makes a movement start and stop - the dismissal thresholds and the one case where two properties in a transition take different durations - is `74-interaction-constants.md` |
| Reduced motion | covered | `40-motion.md#reduced-motion` | |
| Density | covered | `45-density.md#what-changes` | two settings and one attribute. A third density setting is refused there with its reason, and a published system's opposite answer - shrink the glyph and raise the leading ratio - is recorded beside it as a choice rather than an oversight |
| Iconography: set, grid, stroke, alignment | covered | `55-iconography.md#stroke-weight-which-is-the-part-that-is-usually-got-wrong` | |
| Illustration | excluded | `55-iconography.md#illustration-which-is-an-open-decision-rather-than-a-closed-refusal` | no illustration set exists and inventing one per empty state is how a product ends up with six unrelated drawings. **The second half of that sentence argues for a coherent set rather than against one**, and it had been read as an argument against one for three rounds. Both construction models are now measured and the row is an [open decision](#open-decisions) rather than a settled refusal |
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
| Right-to-left and localisation | partial | `05-coverage.md#foundations` | **nothing is written and no decision is recorded.** This is the one row in this table that is neither answered nor deliberately set aside, and it is here so that it stops being invisible. Closing it means logical properties throughout, a re-check of every directional rule in layout, icons and data alignment, and a decision about whether any product will ship a localised build |
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
| Named composition formats | covered | `75-spec-sheet.md#3-formats` | masthead frame, counted set, spec card, comparison pair, quotation block |
| Typography treatments beyond the ramp | covered | `75-spec-sheet.md#4-typography-treatments` | the oversized ordinal, the small-caps eyebrow, the marker highlight, the bracketed aside, each with the boundary that separates it from the decorative-marker entries in `80-anti-patterns.md` |
| The mixed-face headline | partial | `05-coverage.md#the-spec-sheet` | **not specified, and it is a decision rather than a measurement.** Splitting one headline across Newsreader and Public Sans collides with two standing rules: `20-type.md` fixes that emphasis is weight, and the two faces carry roles rather than tones, so mixing them inside a line removes the only cue that says which face means what. Closing it means the system's owner deciding that face may carry emphasis within a line, and on which surfaces |
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

## Ruled out, with the reason

Eighteen rows the field carries that nothing here needs.
**An exclusion that is written down is coverage and an exclusion that lives in someone's head is a
gap** - which is the whole lesson of the splitter, and the reason these cost one line each rather
than being left out.

The open question on this section is not whether to write them down; it is whether any one of them
is a surface a product is about to need. That is the one entry in
[Open decisions](#open-decisions) below that only a roadmap can answer.

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

The table below is deliberately not in the inventory's own format, because a decision is not a
surface and should not be counted as one.

| decision | what is already measured | what is blocked on it | the recommendation on the evidence | who answers it |
|---|---|---|---|---|
| **Whether Illustration moves off the excluded row** | a monochrome pictogram set at Apache-2.0, 1,575 assets, `currentColor`, **zero** palette cost, with categories, aliases and deprecations shipped; against a flat multi-colour register with five baked values and no dark-theme answer. [55-iconography.md](55-iconography.md#illustration-which-is-an-open-decision-rather-than-a-closed-refusal) and [90-evidence.md](90-evidence.md) carry both | the Illustration row above, the identical sentence in three other files, and whether an empty state may ever carry a drawing | **split the row and move half of it.** Adopt the monochrome set, whose palette cost is measured at zero, and keep figurative illustration excluded until it has a dark-theme answer. Do not adopt a set whose licence forbids redistribution in packs, at any scope that involves shipping it | the system's owner |
| **Whether an illustration set inherits the accent hue or carries its own** | a `currentColor` set inherits by construction. A figurative set's chroma ceiling of 0.0929 already sits inside this system's restraint, so the clash is hue and not saturation: its blues sit 60 degrees from `--hw-accent` | only the figurative case | **the question dissolves for a monochrome set and only arises for a figurative one.** A figurative set carries its own palette and goes through [95-extending.md](95-extending.md#a-products-own-namespace) | the system's owner |
| **Whether outward-facing slide sequences are in scope** | the format measured on **three** independent published accounts, the third screened after this table was first written: a 4:5 frame, a uniform margin at about 10.4% of the short side, four corner labels all at 1.70% of frame height, a cover ordinal at 15.6% that states the size of the set, and a body ordinal at 10.2% that states its own position. The third account carries the same four corners with different content in each - a series label, a slide counter, a strapline and an attribution - which is what moves this from a device two accounts share to a format with real support | whether [75-spec-sheet.md](75-spec-sheet.md#3-formats) gains a sixth format. The entry would cost **no new token** - it inherits the masthead frame's - and one line in the out-of-scope list | **yes, on the same argument that admitted the 404 page and the link-preview card**, now with a third instance behind it: every product has one and this book is silent. If the book should stay inward-facing, the measured values keep without it and nothing else changes | the system's owner |
| **Which, if any, of the eighteen exclusions is about to be needed** | each of the eighteen is an external row with a measured absence here and a stated reason | nothing today. Ruling one out is the expensive mistake, and only a roadmap can catch it | **write all eighteen down as excluded**, which is done above. The specific ones worth a second look against a roadmap are the multi-step form, the notification centre, the tree view and the product tour, because each is a surface a growing product acquires rather than plans | whoever holds the roadmap |
| **Which question the high-contrast theme answers** | two opposite strategies, measured in token files: a per-role re-solve pushes distinct values **up** (454 to 466 on one vendor), and surrendering the palette collapses them **down** (192 to 15 on another). 28 to 78% of tokens move, across five vendors | the high-contrast row above, and `75-spec-sheet.md#1-themes` | **treat it as two decisions, not one.** Answer `prefers-contrast: more` with a per-role re-solve, which `tools/build.py` can now emit, and answer `forced-colors: active` with a one-line transparent-outline rule. One theme cannot answer both | an author; no owner decision needed |
| **Whether face may carry emphasis within a line** | nothing to measure. It collides with two standing decisions: `20-type.md` fixes that emphasis is weight, and the two faces carry roles rather than tones | the mixed-face headline row above | none. This is a decision about what this system is, not a value to solve for, and the honest form is to leave it open rather than to settle it by default | the system's owner |

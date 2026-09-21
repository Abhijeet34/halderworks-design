# Components

Fifteen components. The first ten are what these products were already building; the five after
Empty state were found missing by the coverage cross-check in [90-evidence.md](90-evidence.md),
each carried by at least one external component library and most by three.

Each card is a rule plus the tokens it uses, not an implementation: the markup and the accessibility
wiring stay in the product.

Four layers are shared across every component and are not repeated per card:
[60-states.md](60-states.md) owns the nine interaction states,
[45-density.md](45-density.md) owns what compact changes,
[70-data-display.md](70-data-display.md) owns alignment, numeric formatting and the five states a
data container has, and [72-keyboard.md](72-keyboard.md) owns the keyboard map.
A card below states only what is specific to that component.

## Button

A button commits an action; everything else on the screen is a link or a control.

### Button: variants

| variant | when |
|---|---|
| `primary` | the one action this screen exists for. At most one per screen, and never two side by side |
| `secondary` | a real alternative to the primary action: Export beside New run, Cancel beside Save |
| `quiet` | a low-stakes action that should not compete: Clear, Dismiss, Show more |
| `danger` | an action that destroys or revokes. Outlined, never a filled red block, so it cannot be clicked by reflex |

The primary fill is `hw-ink`, not `hw-accent`. The loudest control on the screen carries no hue, which is what keeps the accent meaning something when it does appear.

### Button: sizes

`sm` 12px/4px 9px for a toolbar or a table row action, the default 13px/7px 13px, `lg` 15px/9px 17px for a single call to action on a marketing surface. Three sizes, no fourth.

### Button: rules

- The label says what happens: `Revoke key`, not `Confirm`. Sentence case, never uppercase.
- Radius is `hw-radius-md`. A pill button is not part of this system.
- No shadow, ever. A button that is not obviously clickable needs a border, not a shadow.
- Disabled takes `hw-text-disabled` on `hw-surface-sunken`, not an opacity: see [60-states.md](60-states.md). A button that is disabled for a reason should say the reason nearby rather than leaving the user to guess.
- Loading replaces the label with the verb in progress (`Revoking...`) and keeps the button's width, so the row does not reflow.

**Keys:** Enter or Space activates. Full map in [72-keyboard.md](72-keyboard.md).

### Button: what the consumer provides

The element, its `type`, its handler and its accessible name. This system provides the class and the tokens.

## Input

A single-line text field with its label, hint and error, which are one component and not three.

### Input: anatomy

Label at `label` (12px/500) above the field, 4px clear. Field at `body-sm` (13px) at `hw-control-h` outer height with `hw-field-pad-x` horizontal padding, `hw-radius-md`, a 1px `hw-border-strong` outline. Hint or error at `label` below, 4px clear.

The height is the token and the vertical padding is a consequence. The first two passes specified `7px 10px` of padding instead, which renders **35.5px** beside a 32px button; that was measured in a browser, not derived. [66-forms.md](66-forms.md) owns the box model every control shares, and the twelve other controls that were missing entirely.

### Input: states

| state | what changes |
|---|---|
| rest | `hw-border-strong` outline on `hw-surface` |
| hover | outline moves to `hw-text-muted` |
| focus-visible | 2px `hw-accent-ring` outline at 2px offset, on top of the border, never replacing it |
| error | border becomes `hw-danger`, and an error line appears below in `hw-danger` |
| disabled | `hw-text-disabled` on a `hw-surface-sunken` fill, `hw-border` outline |
| read-only | `hw-text` on `hw-surface-sunken`. Legible, selectable, copyable, and not the same as disabled |

### Input: rules

- **The error replaces the hint; it does not stack under it.** Two lines of guidance under one field is one line too many.
- The error names the problem and the fix: `That key expired on 12 March. Generate a new one in Settings, Keys.` Never `Invalid input`.
- A placeholder is an example of the format, never a substitute for the label. `sha256:77c2d4e...` is a placeholder; `Artifact hash` is a label.
- A field that holds machine output - a hash, an id, a path - is set in `var(--font-mono)`.
- Never turn the focus ring off. It is solved to 3:1 against the ground precisely so it can stay on.

**Keys:** the platform's text-editing keys, unchanged. A field that intercepts Home, End or the arrows has broken text editing to gain a shortcut. Full map in [72-keyboard.md](72-keyboard.md).

### Input: what the consumer provides

The `id` linking label to field, the `aria-describedby` pointing at the hint or error, and `aria-invalid` when it is in error.

The other thirteen form controls, the label, helper, required marker, character count, field group, form layout, action row and validation are in [66-forms.md](66-forms.md) and [67-validation.md](67-validation.md).

## Card

A card groups things that are read together and acted on together. If the contents do not share an action or a subject, they do not share a card.

### Card: anatomy

`hw-surface` on a `1px solid hw-border`, `hw-radius-lg`, 16px padding. A header at `title-3` with an optional status on its right, a body, and an optional footer on `hw-surface-sunken` carrying the actions.

### Card: rules

- **No shadow.** A card sits on the page; it does not float above it. Elevation is for things that can be dismissed.
- **No accent bar or coloured rail.** If the card is selected its whole fill becomes `hw-accent-quiet`; if it is in error its border becomes `hw-danger`. An edge stripe is on the anti-pattern list.
- Inner corners follow the nesting rule: a 10px card with 16px padding gives its children a square corner or `hw-radius-sm`, never another 10px.
- A card with one line of content in it is a list row that grew a border by accident.
- Cards in a row share edges, baselines and inner padding. Let the content set the height; do not stretch one card over dead space.

### Card: what the consumer provides

The heading level. A card's title is `title-3` by style, not by tag; the correct tag depends on where the card sits in the document.

## List row

A row in a scannable list, where the subject is a thing rather than a set of columns. Use a data table when the columns are the point; use list rows when the row is.

### ListRow: anatomy

12px vertical, 16px horizontal, a `1px hw-border` between rows and none after the last, a leading status mark, a title at `body-sm` in `hw-text`, a secondary line in `hw-text-secondary`, and trailing metadata set in `var(--font-mono)` with `tabular-nums`.

### ListRow: states

Hover fills `hw-surface-sunken`. Selected fills `hw-accent-quiet` and keeps its text in `hw-text`, not in the accent. Focus takes the 2px ring inside the row, not around it, so the ring is not clipped by the container.

### ListRow: rules

- The whole row is the hit target, not the title inside it.
- Trailing metadata is right-aligned and tabular, so the eye can compare down the column even without rules.
- A row action appears on hover and is also reachable by keyboard. An action that only appears on hover and has no keyboard path does not exist for a keyboard user.
- No more than one badge per row. Two badges means the row is carrying two subjects.

**Keys:** Up and Down Arrow move between rows and the list is one tab stop, Enter opens the row, and a row action is reached with Tab once the row has focus. Full map in [72-keyboard.md](72-keyboard.md).

### ListRow: what the consumer provides

The list semantics, the keyboard handling, and a stable key per row.

## Data table

Columns of values that are compared against each other, which is the only reason to use a table. If nobody compares column to column, this is a list.

### DataTable: anatomy

Column heads at `micro` (11px/600, 0.06em, uppercase) in `hw-text-muted`. Cells at `body-sm` (13px), 9px 16px. A `1px hw-border` under every row and under the head; none after the last row. No vertical rules at all - alignment does that work.

### DataTable: rules

- **Every numeric column is right-aligned and set with `font-variant-numeric: tabular-nums`.** In Public Sans a `1` is a third narrower than a `0`, so a column without it visibly jitters. This is the rule broken most often.
- Identifiers, hashes and timestamps are set in `var(--font-mono)` at 12px. They are read character by character, not as words.
- Zebra striping is not used. A 1px border per row is quieter and does the same job; striping adds a surface that means nothing.
- The head is sticky when the table scrolls, on `hw-surface` with its border, so it does not become transparent over the rows.
- A cell that can overflow wraps or truncates inside its own container with a title attribute. Clipped text with no way to read it is a bug.
- Sort state lives on the head: the active column's label goes to `hw-text` with a direction mark, the rest stay `hw-text-muted`.

**Keys:** a table nobody interacts with takes none. Where cells are interactive it is a grid: the four arrows move cell to cell, Home and End move within the row, Control+Home and Control+End move to the table's corners. Full map in [72-keyboard.md](72-keyboard.md).

### DataTable: what the consumer provides

The table semantics (`scope` on heads, a caption or `aria-label`), sorting, selection and virtualization.

## Badge

A short, non-interactive mark of state on the thing it belongs to. If it can be clicked it is a button or a filter chip, not a badge.

### Badge: variants

`neutral` for a count or a category, `accent` for live or selected, `success` for passed, verified, settled, `warning` for retried or degraded, `danger` for failed or revoked.

### Badge: rules

- **The colour never carries the meaning alone.** Every badge has a word. A row of coloured dots with no labels fails for the 8% of men with a colour vision deficiency, and it fails for anyone reading a screenshot.
- One badge per row or per card. Two badges means two subjects.
- `micro` sizing: 11px, weight 600, 2px 7px, `hw-radius-sm`. Never a pill; the pill radius is reserved for avatars and counts.
- The label is one word where one word will do. `Settled`, not `Successfully settled`.
- The optional leading dot is 6px at `hw-radius-sm` in `currentColor`, so it follows whatever variant the badge is.

### Badge: what the consumer provides

Nothing but the word. A badge that needs a tooltip to be understood needs a better word.

## Tabs

Switches between views of the same subject without leaving the screen. If the views are of different subjects, they are navigation, not tabs.

### Tabs: anatomy

A row of labels at `body-sm` (13px/500) with 8px 4px padding and 16px between them, sitting on a `1px hw-border` baseline that runs the full width. The active tab draws a 2px `hw-accent` rule over that baseline and takes `hw-text`; the rest are `hw-text-secondary`.

### Tabs: rules

- **The underline is the only accent in the component.** No pill background, no filled tab, no shadow.
- Three to six tabs. Past six, the set is a sidebar.
- Labels are nouns, not verbs: `Evidence`, not `View evidence`.
- A count belongs beside its label as a `neutral` badge, not inside the label as `Runs (4)`.
- Switching a tab never changes the page's scroll position or the screen's title.
- Keyboard: arrow keys move between tabs, Tab moves into the panel. That is the ARIA tabs pattern and it is not optional.

**Keys:** Left and Right Arrow move **and activate** - this system takes automatic activation and [72-keyboard.md](72-keyboard.md) says why - Home and End go to the first and last tab, and Tab moves into the panel. The tablist is one tab stop.

### Tabs: what the consumer provides

`role="tablist"`, `role="tab"`, `aria-selected`, the arrow-key handling, and the panel wiring.

## Dialog

Interrupts to ask for one decision that cannot be deferred. Anything the user could act on later belongs on the page, not in a dialog.

### Dialog: anatomy

`hw-surface-raised` on a `1px hw-border`, `hw-radius-lg`, `hw-shadow-dialog` in light theme only. 24px padding. Title at `title-2`, body at `body`, actions right-aligned in a row with 8px between them, the primary action last.

### Dialog: rules

- **One question per dialog.** A dialog with two decisions in it is a form that should be a page.
- The title states the decision, not the category: `Rotate the signing key?`, not `Confirm`.
- **The button says the verb.** `Rotate key` and `Cancel`, never `OK` and `Cancel`, because `OK` forces the user to re-read the title to know what they are agreeing to.
- A destructive dialog uses the `danger` button variant and names what will be lost, with the number: `47 builds signed with this key will no longer verify.`
- Escape closes, and closing is always the safe outcome. If closing would destroy something, the dialog is wrong.
- Focus moves into the dialog on open and returns to the trigger on close. The focus trap and the return are not optional.
- Enters at `duration-slow` with `ease-out`, on opacity and a small `translateY`. Under reduced motion the movement goes and the opacity stays.

**Keys:** Escape closes, and it is the only key the pattern names. Tab cycles inside the dialog and never leaves it. Full map in [72-keyboard.md](72-keyboard.md).

### Dialog: what the consumer provides

The focus trap, the return target, `role="dialog"` with `aria-modal`, the labelled title, and the scrim.

## Toast

Confirms that something finished, without taking the screen. A toast is for an outcome the user already expected; anything they need to act on belongs inline.

### Toast: anatomy

`hw-surface-raised` on a `1px hw-border`, `hw-radius-lg`, `hw-shadow-overlay` in light theme only. 12px 14px, a leading status mark, a line at `body-sm`, and an optional single action in the `quiet` variant.

### Toast: rules

- **One line.** If it needs two, it is a banner on the page.
- The wording is past tense and matches the button that caused it: `Rotate key` produces `Key rotated`.
- Success dismisses itself after 5 seconds. **An error toast never auto-dismisses**, because the one person who needed to read it is the one who looked away.
- At most one action, and it is the undo or the place to look: `Undo`, `View run`. Never `OK`.
- Toasts stack downward from one corner, newest nearest that corner, maximum three visible. The fourth replaces the oldest.
- Enters at `duration-base` with `ease-out` on opacity and translate; leaves at `duration-base` with `ease-in`.

**Keys:** none. A toast never takes focus, which is exactly why an action inside one must also exist on the page. Full map in [72-keyboard.md](72-keyboard.md).

### Toast: what the consumer provides

The live region (`role="status"` for success, `role="alert"` for error), the timer, and the stack.

## Empty state

What a container says when it has nothing in it, which is the first thing most users ever see of a feature. An empty state that only says "No data" has wasted that.

### EmptyState: anatomy

Centred in its container, 48px vertical padding. A title at `title-3`, one line of explanation at `body-sm` in `hw-text-secondary` at a measure of about 40ch, and at most one action.

This is the one place in the system where centring is correct, because there is a single element and nothing to align it to.

### EmptyState: the three kinds, which are not interchangeable

| kind | what it says | action |
|---|---|---|
| **nothing yet** | what will appear here and what makes it appear | the primary action that creates the first one |
| **nothing found** | what was searched and that the filter can be cleared | `Clear filters`, in the `quiet` variant |
| **nothing permitted** | which permission is missing and who grants it | none, or a link to the person who can |

Shipping "nothing yet" copy in a "nothing found" state is the most common failure here: the user who filtered to zero results gets told how to create their first run, which they already have four of.

### EmptyState: rules

- No illustration beyond one pictogram, in the **nothing yet** kind only, from the one set [55-iconography.md](55-iconography.md#illustration-one-pictogram-set-and-no-figurative-drawing) names. A drawing chosen per empty state from anywhere else is how a product ends up with six unrelated drawings.
- No emoji. That is on the anti-pattern list.
- The explanation is one sentence. If it needs three, the feature needs documentation and the empty state needs a link to it.

### EmptyState: what the consumer provides

Which of the three kinds applies. Only the consumer knows whether zero rows means new or filtered.

## Link

Text that goes somewhere. A button commits an action; a link changes where you are.
This is the first of the accent's four jobs, and before this card the accent was spent on "a link"
that the system never specified.

### Link: anatomy

`--hw-accent` ink on whatever ground the text sits on, with a 1px underline at the face's own
underline position. Hover takes `--hw-accent-hover` and thickens the underline to
`--hw-focus-w` 2px. Focus-visible takes the 2px `--hw-accent-ring` at `--hw-focus-offset`, and the
underline stays.

**Contrast:** `--hw-accent` is certified on every ground in
[15-color-combinations.md](15-color-combinations.md) - 5.09 to 5.42 light, 4.79 to 5.80 dark. The
card adds no pair.

### Link: rules

- **A link in running text is underlined.** Colour is not allowed to carry meaning alone anywhere
  else in this system ([15-color-combinations.md](15-color-combinations.md),
  [55-iconography.md](55-iconography.md)), and a link distinguished only by hue is exactly that
  failure. The underline is the second channel.
- **A link that is interface chrome is not underlined and is not accent-coloured**: a navigation
  item, a tab, a breadcrumb. Those are [37-navigation.md](37-navigation.md)'s, and they carry their
  state as a fill. Underlining them would put an underline on every row of the rail.
- **There is no visited style.** A fifth value would have to be solved against every ground, and the <!-- covered-by: Link -->
  accent already has four jobs. A product whose reader genuinely needs to track what they have read
  has a data problem - a read column in a list - rather than a colour problem.
- **A link opens in the same tab.** Where it genuinely leaves the product - a specification, a
  licence, an external record - it carries a trailing `--hw-icon-sm` external mark in
  `currentColor`, and its accessible name says so. A `target="_blank"` link takes `rel="noopener"`.
- **A link is never a control.** If it submits, deletes, toggles or opens a dialog, it is a button,
  whatever it looks like. The test is what the browser's back button does afterwards.
- **A link label is the destination, not the instruction.** `Signing key rotation` and not
  `click here` or `read more`, both of which are unusable as a list of links read on their own.
- An inline link has no minimum hit target of its own. A link that stands alone as a call to action
  is a button and takes `--hw-control-h`.

**Keys:** Enter activates. **Never Space** - Space scrolls the page, and a link that consumes it
breaks scrolling. Full map in [72-keyboard.md](72-keyboard.md).

### Link: what the consumer provides

A real `href`. A `<span>` with a click handler is not a link: it cannot be opened in a new tab,
copied, bookmarked or reached by a screen reader's link list.

## Accordion and disclosure

A **disclosure** is one header and one panel. An **accordion** is a set of them.
Use either when a reader needs to choose what to read; use tabs when they need to switch between
views of one subject.

### Accordion: anatomy

| part | token |
|---|---|
| header | a full-width `<button>` at `--hw-row-h`, `--hw-space-16` horizontal padding |
| header label | `body-sm` (13px/500) in `--hw-text` |
| the mark | `--hw-icon` 16px chevron, **leading**, at `--hw-icon-gap` before the label, rotating 90 degrees at `--hw-duration-fast` with `--hw-ease-out` |
| between items | `1px` of `--hw-border`, and none after the last |
| panel | `--hw-space-12` above and `--hw-space-16` below, its left edge aligned to the **label**, not to the chevron |
| hover, focus, current | the list-row states in [60-states.md](60-states.md), unchanged |

The chevron leads rather than trails so that a collapsed accordion reads as one list with one left
edge down the column, which is the same argument [35-layout.md](35-layout.md) makes for
left-aligning prose inside a container.

Opening animates `grid-template-rows` from `0fr` to `1fr` at `--hw-duration-base` with
`--hw-ease-out`, which is the one way [40-motion.md](40-motion.md) permits a height to animate.

### Accordion: rules

- **Panels open independently and stay open.** The reader opened each one. Closing a panel they did
  not touch is the product overriding a choice they made. A single-open variant needs a stated
  reason, and if the reason is that the panels are views of one subject, it is a tab set.
- **No nesting.** An accordion inside an accordion is a tree, and this system has no tree view <!-- covered-by: Tree view -->
  ([05-coverage.md](05-coverage.md) carries the row and its reason).
- **Nothing essential goes inside a collapsed panel.** A reader skips them. A required form field
  inside one produces an error message pointing at something invisible, which
  [67-validation.md](67-validation.md) cannot recover from.
- **The header is a sentence a reader can answer from.** `When a signature fails to verify` and not
  `More information`.
- **Never used to make a page look short.** A page of nine collapsed headers is a page that has
  hidden its own content from search, from print and from a reader scrolling for one word.
- Three to about ten items. Past that the set wants a filter or a list.

**Keys:** Enter or Space toggles the focused header. Each header is its own tab stop and the arrow
keys are not used, which is what separates an accordion from a tablist. Full map in
[72-keyboard.md](72-keyboard.md).

### Accordion: what the consumer provides

`aria-expanded` on the header button, `aria-controls` pointing at the panel, and a real `<button>`.
A `<div>` with a click handler is the most common implementation of this component and it is
unreachable by keyboard.

## Callout

A short block that carries a different kind of statement from the prose around it: a caveat, a
consequence, a requirement.

**A neutral callout is not a component.** It is the Framed style in
[75-spec-sheet.md](75-spec-sheet.md#framed), which already specifies `--hw-surface-sunken` on a
`--hw-border` with a `micro` caption. This card is only for the three that carry a state.

### Callout: anatomy

| part | token |
|---|---|
| fill | `--hw-{semantic}-quiet` |
| border | `1px` of `--hw-{semantic}`, on all four sides |
| radius, padding | `--hw-radius-md`, `--hw-space-16` |
| the mark | `--hw-icon` 16px in `currentColor`, leading, on the first line |
| the kind | one word at `label` (12px/500) in `--hw-{semantic}`: `Warning`, `Required`, `Destructive` |
| the body | `body-sm` in `--hw-text` |

**Contrast:** the semantic on its own quiet fill is 4.59 to 4.61 in both themes, and `--hw-text` on
any quiet fill is 13.37 to 13.45. Those are the only two inks a quiet fill takes
([15-color-combinations.md](15-color-combinations.md)) and both are already certified. The card adds
no pair.

### Callout: rules

- **A border on all four sides, never a left rail.** A coloured edge stripe is refused for the card
  ([65-components.md](65-components.md#card)) and for the quotation block
  ([75-spec-sheet.md](75-spec-sheet.md#quotation-block)) for the same reason: a rail is an accent
  spent on decoration, and a reader cannot tell a rail from a scrollbar at a glance.
- **The kind is a word.** A red box with no word is a semantic colour carrying meaning alone, which
  [15-color-combinations.md](15-color-combinations.md) refuses everywhere.
- **At most one per section, and never two in a row.** Two adjacent callouts have told the reader
  that nothing on the page is ordinary.
- **Never nested, and never inside a table cell.** A callout inside a cell is a cell the column
  cannot be compared down.
- **Three lines is the ceiling.** Longer is a section with a heading.
- **It never carries the only copy of something the reader must act on.** Readers skip coloured
  boxes; that is measurable behaviour and it is why a callout is an emphasis of something the prose
  already says.

### Callout: what the consumer provides

Whether the block is announced. A caveat is prose and takes no role; a consequence the reader must
not miss takes `role="note"` with a label. Nothing here is a live region -
[65-components.md](65-components.md#toast) owns those.

## Key-value pair list

One record's fields, read down rather than compared across.
[70-data-display.md](70-data-display.md) owns the table, which exists so columns can be compared; an
instrument of record displays a single record's fields constantly and had nothing for it.

### KeyValue: anatomy

| part | token |
|---|---|
| layout | two columns: the key column at `max-content` capped at 24ch, then the value |
| the key | `label` (12px/500) in `--hw-text-muted` |
| the value | `body-sm` in `--hw-text` |
| a machine value - a hash, an id, a duration, a timestamp | `--hw-font-mono` with `tabular-nums`, per [70-data-display.md](70-data-display.md) |
| row rhythm | `--hw-space-12`, the same as the spec card in [75-spec-sheet.md](75-spec-sheet.md#spec-card) |
| column gap | `--hw-space-24` |
| below `--hw-bp-md` | the key goes above its value, which is the same collapse [66-forms.md](66-forms.md) makes |

The 24ch cap is what stops one long key pushing every value off the right of the block. Past the cap
the key wraps and its value stays on the first line's baseline.

### KeyValue: rules

- **A missing value is written, never blank.** `Not set` in `--hw-text-muted` where the field has no
  value, `Unknown` where the product does not know. A blank cell makes those two indistinguishable,
  and for an instrument of record they are different facts.
- **Values are left-aligned, not right-aligned.** This is a list, not a column of figures: nothing
  here is compared to the value below it. That is the one place this differs from
  [70-data-display.md](70-data-display.md)'s numeric rule, and the reason is that the rule there is
  about comparison down a column.
- **About twelve pairs is the ceiling.** Past that the reader is scanning rather than reading, and
  scanning is a table or a set of sections.
- **A value that is a state takes a badge, not a coloured word.**
  [65-components.md](65-components.md#badge) owns it.
- **No leader dots between key and value.** A leader is fixed geometry between two points and has to
  be re-authored at every width; [75-spec-sheet.md](75-spec-sheet.md#spec-card) already settles this
  for the specimen case.

### KeyValue: what the consumer provides

`<dl>` with `<dt>` and `<dd>`, so a screen reader announces the pairing. A two-column `<table>` for
this is a table with one row per field and no columns to compare.

## Inline destructive confirm

The question asked where the action was, instead of in a dialog.

Before this card, every delete in the system was a modal: `65-components.md#dialog` was the only
place a confirmation could live, and [80-anti-patterns.md](80-anti-patterns.md) cares about
destructive items without saying where the confirmation goes.

### When it applies, and when the dialog does instead

| | inline confirm | dialog |
|---|---|---|
| scope | one row, one item | many items, or the whole account |
| reversible | yes - a key that can be reissued, a row that can be restored | no |
| what the reader needs told | the object's name | the object's name **and the count of what else breaks** |

A dialog interrupts to ask for one decision that cannot be deferred. Revoking one key in a list of
forty is not that, and making it a modal trains the reader to dismiss modals.

### InlineConfirm: anatomy

The row's action area is replaced in place, and **the row keeps its height**, so the list does not
reflow under the reader's cursor - which is the same rule
[60-states.md](60-states.md#loading-holds-the-width) applies to a loading button.

| part | token |
|---|---|
| the question | `body-sm` in `--hw-text`, naming the object: `Revoke key ab3f?` |
| the destructive action | the `danger` button variant at `--hw-control-h-sm`, carrying the verb |
| the cancel | the `quiet` variant at `--hw-control-h-sm` |
| between them | `--hw-space-8` |

### InlineConfirm: rules

- **Focus moves to Cancel, never to the destructive button.** A confirmation whose safe answer is
  not the one under the reader's hands is a confirmation that will be passed by reflex. Escape also
  cancels.
- **The question names the object.** `Are you sure?` asks the reader to remember which row they
  clicked; `Revoke key ab3f?` does not.
- **The destructive button says the verb**, exactly as the dialog's does:
  `Revoke`, never `Yes` or `OK`.
- **No scrim.** It makes no claim on the rest of the screen - the same argument the menu-bar panel
  makes in [36-form-factors.md](36-form-factors.md).
- **One open at a time in a list**, and anything else the reader does in that list cancels it. Two
  open confirmations is two pending destructions with one Escape key between them.
- **It never auto-dismisses**, and it never times out into either answer.

**Keys:** Escape cancels. Tab moves between the two buttons, and the confirm is one tab stop group
inside the row. Full map in [72-keyboard.md](72-keyboard.md).

### InlineConfirm: what the consumer provides

Moving focus to Cancel on open and returning it to the trigger on cancel, and the live region that
announces the question - because a reader who activated the trigger by keyboard must be told the
question was asked.

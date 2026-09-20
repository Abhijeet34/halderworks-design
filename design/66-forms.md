# Forms

A form is where an instrument of record takes input, so it is the surface where a wrong value costs the most.
This file owns the controls and the furniture around them.
[67-validation.md](67-validation.md) owns when a value is judged and how the verdict is shown.

Three layers are not repeated here.
[60-states.md](60-states.md) owns the nine interaction states every control answers.
[45-density.md](45-density.md) owns what compact changes.
[36-form-factors.md](36-form-factors.md) owns what changes on touch and in a floating panel.

## What was wrong before this file

The component set contained one form control, `Input`.
A keyword sweep over the other files returned zero for `textarea`, `radio`, `slider`, `stepper`, `combobox`, `fieldset` and `helper`, and the twelve files containing `select` all use it as the English verb.
So every product built its own, which is the habit that produced 24 type sizes and 34 spacing values in quoth.

Two defects were found by specifying the family rather than one member of it, and both are corrected below.

**The control edge did not clear the bar it exists to clear.**
`--hw-border-strong` is the token [50-surface-texture.md](50-surface-texture.md) assigns to "a control outline that must be found without hovering: an input, a select, a secondary button".
WCAG 2.2 SC 1.4.11 holds that outline to 3:1, because it is the visual information that identifies the control.
Measured against the surfaces it is permitted to sit on, it ran **1.45:1 to 2.14:1 and never reached 3:1 in either theme**.
[15-color-combinations.md](15-color-combinations.md) already printed `1.64:1` for it, as evidence that it may not be used as an ink, and never checked it against the bar it actually had to meet.
It is now re-solved against the surface closest to it in lightness, exactly as the focus ring was after the 2.56:1 defect: `oklch(0.637 0.006 198)` in light and `oklch(0.516 0.0084 198)` in dark, worst case **3.01:1** in both themes.

**A field and a button in the same row were different heights.**
`--hw-control-h` is 32px and is defined as "button, select, input outer height".
The shipped `Input` anatomy was `7px 10px` of padding on 13px text at 1.5 line-height, which renders **35.5px**: 19.5 of line box, 14 of padding, 2 of border.
Measured in a browser, not derived: the field rendered 35.5px beside a 32px button.
The artifact's own two previews already disagreed about it, `States/preview.html` setting `height: var(--hw-control-h)` while `Input/preview.html` set the padding.

The rule that fixes it is worth more than the number.
**A single-line control's outer height is `--hw-control-h`, and its vertical padding is a consequence rather than a decision.**
Set the height, centre the line box, and pad horizontally only.
Then the field, the button, the select, the stepper and the segmented control are all 32px by construction, and compact moves all five together.
Re-measured after the change: input, select, button, stepper and segmented control all render exactly 32.0px.

`--hw-field-pad-y` now applies only to a control with no fixed height, which is the textarea.

## The box model every control shares

| property | value | why |
|---|---|---|
| outer height | `--hw-control-h` | one token, so a row of mixed controls shares a baseline |
| horizontal padding | `--hw-field-pad-x`, **12px** | was 10px, which is off the 4px grid and was the third such value in the system. 12px is `--hw-space-12` and reads better against the 6px radius |
| radius | `--hw-radius-md` | the role is "interactive control", per [30-space-radius-elevation.md](30-space-radius-elevation.md) |
| border | 1px `--hw-border-strong` | re-solved to 3:1, above |
| fill | `--hw-surface` | not `--hw-surface-sunken`; see the contradiction note below |
| text | `body-sm` 13px, or `--hw-font-mono` for machine output | a hash is read character by character |
| label gap | `--hw-space-4` above, `--hw-space-4` below to the helper | |
| field to field | `--hw-space-16` | |
| group to group | `--hw-space-24` | |

**A contradiction this file settles.**
[50-surface-texture.md](50-surface-texture.md) lists "an input at rest" as a *filled* surface on `--hw-surface-sunken`, while [65-components.md](65-components.md) says the input rests on `--hw-surface`.
The fill is `--hw-surface` and the sunken variant is reserved for read-only and disabled, because those two states need a fill that says "not for typing into" and nothing else in the field family may claim it.

## The controls

Anatomy, then what is specific to the control.
Every one of them answers all nine states in [60-states.md](60-states.md); only departures are noted.

### Text input

Already specified in [65-components.md](65-components.md); the box model above replaces its padding line.
A field holding machine output is `--hw-font-mono`.

### Textarea

The one control with no fixed height.
Minimum three lines: `calc(3 * 1.5 * var(--hw-text-body-sm) + 2 * var(--hw-field-pad-y) + 2px)`, which renders 74.5px.
Padding is `--hw-field-pad-y` `--hw-field-pad-x`.

- **`resize: vertical`, never `both` and never `none`.**
  Horizontal resize breaks the measure the column was laid out to; `none` takes away the only escape from a field that is too small for what the user must type.
- A textarea that needs a character count gets one, and [67-validation.md](67-validation.md) owns when it turns red.
- It never auto-grows past half the viewport height. Past that the content wants a page, not a field.

### Select, and native against custom

**Use the native `<select>` unless the options need more than a word each.**
The native control gets the platform's own keyboard handling, its type-ahead, its touch wheel and its scroll containment for free, and every custom listbox re-implements those four things imperfectly.

Anatomy: the shared box model, plus right padding of `calc(var(--hw-field-pad-x) * 2 + var(--hw-icon))` to clear a 16px chevron sitting at `--hw-field-pad-x` from the right edge.
The chevron is `--hw-text-secondary`, not full-strength text: it is an affordance, not content.

Go custom only when an option needs a secondary line, a status mark or a count.
A custom listbox is then a combobox without the text field, and it takes the popover rules below.

**Keys:** Space or Down Arrow opens, the arrows move, Enter commits, Escape closes. A native select gets all of this from the platform, which is the first argument for using one. Full map in [72-keyboard.md](72-keyboard.md).

### Combobox, with type-ahead

A text field plus a filtered list, for a set too long to scan.

- The popover is `--hw-surface-raised`, 1px `--hw-border`, `--hw-radius-lg`, `--hw-shadow-overlay`, at `--hw-z-dropdown`.
  It floats and can be dismissed, so it earns its shadow under [50-surface-texture.md](50-surface-texture.md).
- **The match is on a substring, not a prefix**, and the matched run is set at weight 600 inside the option.
  A prefix-only match hides `nightly-reload` from someone who typed `rel`, and they conclude the record is not there.
- One option is the **active descendant**, filled `--hw-surface-hover`; the **selected** option is filled `--hw-accent-quiet` with its text still `--hw-text`.
  They are different states and a combobox shows both at once, which is why they take different fills.
- Typing never commits. The active descendant moves with the arrow keys and Enter commits it.
- Zero matches is an empty state with the searched string in it, not a blank popover: `No pipeline matches "rel".`
- An option carries at most one secondary value, right-aligned, mono, tabular.

**Keys:** the largest contract in the map at 80 bindings. Down Arrow opens and moves, Alt+Down Arrow opens without moving, Enter commits, Escape closes then clears, printable characters filter. Focus stays in the field and `aria-activedescendant` carries the active option. Full map in [72-keyboard.md](72-keyboard.md).

### Checkbox and radio

Both are a **16px box**, which is `--hw-icon`, so a column of checkboxes, radios, switches and icons shares one optical box.
Checkbox takes `--hw-radius-sm`; radio takes `--hw-radius-full`, because the round shape is what distinguishes one-of-many from any-of-many.

| state | box | mark |
|---|---|---|
| unchecked | `--hw-surface` fill, 1px `--hw-border-strong` | none |
| checked | `--hw-ink` fill and border | `--hw-ink-text`: a 12px check, or a 6px dot for a radio |
| indeterminate | `--hw-ink` fill | a 12px `--hw-ink-text` dash, checkbox only |

`--hw-ink` on `--hw-surface` measures 17.88:1 light and 16.00:1 dark, far above the 3:1 an indicator needs.
The filled box is `--hw-ink` rather than the accent for the reason in [10-color.md](10-color.md): the accent has four jobs and "a control is on" is not one of them.

- **The label is part of the hit target**, and the whole row is clickable.
- A checkbox with a description puts it on its own line under the title in `label` at `--hw-text-secondary`, never inline after it.
- A radio group always has a selected member once the user has chosen; it has no empty state to return to. If "none" is a real answer, it is an option in the group with that word on it.
- **A radio group of two where the options are opposites is a checkbox or a switch**, not two radios.

**Keys:** Space toggles a checkbox. A radio **group** is one tab stop and the arrows move and select within it - not one stop per radio. Full map in [72-keyboard.md](72-keyboard.md).

### Switch

Track 28x16 with a 12px thumb and 12px of travel, all on the 4px grid, and the same 16px outer box as the checkbox so a settings column aligns.

| state | track | thumb |
|---|---|---|
| off | `--hw-surface-sunken`, 1px `--hw-border-strong` | `--hw-border-strong` |
| on | `--hw-ink` fill and border | `--hw-ink-text` |

**Switch or checkbox, which is the question this control always raises.**
A **switch** takes effect the moment it moves and needs no confirming action.
A **checkbox** states an intention that some later button commits.
So a settings pane that saves as you go takes switches, and the same pane with a `Save changes` button at the bottom takes checkboxes.
Mixing them in one form tells the user two different things about when their change lands.

A switch is never used to answer a question in a form that has an action row.

**Keys:** Enter or Space toggles. Full map in [72-keyboard.md](72-keyboard.md).

### Slider

A 4px rail (`--hw-space-4`) with a 16px thumb (`--hw-icon`), the thumb centred on the value.

- Rail `--hw-surface-sunken` with a 1px `--hw-border-strong` edge; the filled portion `--hw-ink`; the thumb `--hw-surface` with a 1px `--hw-ink` edge.
- **A slider always shows its value as text beside the label**, mono and tabular.
  A slider with no number is a control that cannot be read back, and in an instrument of record that is disqualifying.
- **A slider is for a value where the approximate position carries meaning** and the exact number does not have to be typed.
  Where the number matters, use a stepper or a field. Retention in days is a slider; a port number is not.
- The keyboard moves it by one step with the arrows and by ten with Page Up and Page Down.

**Keys:** Left and Down Arrow decrease, Right and Up Arrow increase, Page Up and Page Down take a larger step, Home and End go to the bounds. Full map in [72-keyboard.md](72-keyboard.md).

### Numeric stepper

The shared box model, with the value right-aligned in mono and tabular figures, and two `--hw-control-h`-wide buttons divided by a 1px `--hw-border-strong`.

- **The field stays typable.** A stepper whose field is read-only forces 40 clicks to reach 40.
- It is sized by its content, never stretched to the column width. A stepper stretched to 320px puts its buttons an inch from its number.
- Out-of-range input is an error under [67-validation.md](67-validation.md), not a silent clamp. Silently clamping 500 to 100 tells the user their value was accepted.

**Keys:** Up and Down Arrow by one step, Page Up and Page Down by a larger step, Home and End to the bounds. The two buttons are a pointer affordance, not the keyboard route. Full map in [72-keyboard.md](72-keyboard.md).

### Date and time

**The typed field is the control and the calendar is an aid.**
A picker that cannot be typed into costs a keyboard user four times the keystrokes.

- The field is mono, and the format is stated in the helper text rather than guessed: `2026-03-12`, `14:03`.
  [70-data-display.md](70-data-display.md) owns display formatting; this is input, and input takes ISO 8601 because it is unambiguous between countries, which `03/04` is not.
- The timezone is named beside the field, once per form.
- The calendar popover takes the same surface, border, radius and shadow as the combobox popover.
  Its day cells are 28px, tabular; the selected day is `--hw-ink` with `--hw-ink-text`; today carries a 1px `--hw-border-strong` inset ring; days outside the month are `--hw-text-disabled`.
- Today and selected are different marks, because on the day you are choosing today they would otherwise be one.

### File upload

A drop target plus the list of what was chosen.

- Target: 1px **dashed** `--hw-border-strong` on `--hw-surface-sunken`, `--hw-radius-lg`, minimum height `--hw-space-96`.
  Dashed is the one place a dashed border exists in this system, and it is carrying the meaning "not yet filled".
- On drag-over the border goes solid `--hw-accent` and the fill goes `--hw-accent-quiet`.
  This is the fourth job of the accent, a live state, and it is the only state the drop target has.
- **The target always contains a real button as well.** Drag and drop is not reachable by keyboard and is awkward on touch, so it is never the only route.
- The accepted types and the size ceiling are stated on the target before an upload is refused, not in the error afterwards.
- Each chosen file is a row with its name, its size right-aligned in mono and tabular units per [70-data-display.md](70-data-display.md), and a remove control.
  **A list with no remove control is a report, not a control**, and the user's only recovery is to reload the form.
- Upload progress is determinate or it is not shown. A determinate bar is the one thing in this system allowed to loop, per [40-motion.md](40-motion.md).

### Search

The shared box model with a 16px leading magnifier in `--hw-text-muted` and, once there is a value, a trailing clear control in `--hw-text-secondary`.
Both sit at `--hw-field-pad-x` from their edge, and the text padding clears them.

- **The clear control appears only when there is something to clear**, and it is a real button with an accessible name, not a decoration.
- Search filters on a debounce; it does not submit. Where it must submit, it has a button and Enter is not the only route.
- A search that filtered to nothing produces the "nothing found" empty state in [70-data-display.md](70-data-display.md), naming the string, never the "nothing yet" one.

### Segmented control

A `--hw-control-h` track on `--hw-surface-sunken` with a 1px `--hw-border`, 2px of inner padding, and segments at `calc(var(--hw-control-h) - 6px)`.

The selected segment is `--hw-surface` **with a 1px `--hw-border-strong` edge**, and the edge is not decoration.
`--hw-surface` against `--hw-surface-sunken` measures **1.129:1 in light and 1.115:1 in dark**, so the fill alone cannot identify which segment is selected against the 3:1 bar.
The border carries it at 3.01:1 or better.

- Two to four segments, all one or two words. Past four it is a select.
- The segments are views of one thing, like `Comfortable` and `Compact`. If they are actions, they are buttons.
- It is sized by its content.

**Keys:** one tab stop for the whole control, arrows move and select, which is the radio-group pattern. Full map in [72-keyboard.md](72-keyboard.md).

## The furniture, which is the half that was missing

### Label

`label` step, 12px weight 500, `--hw-text`, one line, sentence case, `--hw-space-4` above the field.

**A placeholder is never a label.**
It disappears the moment the user types, so the field loses its name exactly when the value needs checking, and it fails for every screen reader that does not announce it.

### Required and optional

**Mark the smaller set, and mark it with a word.**

A bare red asterisk is a colour and a glyph carrying meaning with no word beside it, which [15-color-combinations.md](15-color-combinations.md) already forbids for state.

- Where most fields are required, mark the optional ones: the word `Optional` in `label` at `--hw-text-secondary`, beside the label.
- Where most are optional, mark the required ones with the word `Required`, same treatment.
- Never both in one form.

### Helper text

`label` step at `--hw-text-secondary`, `--hw-space-4` below the field, one line.
It says the format, the constraint or the consequence: `Paste the full digest or its first seven characters.`

**The error replaces it; the two never stack.**
That rule is already in [60-states.md](60-states.md) and it is the one most often broken, because stacking is what a naive implementation does by default.

### Character count

Right-aligned on the same line as the helper text, `label` step, `--hw-text-secondary`, in the form `36/280`.

- Only where a limit is real and enforced. A count under a field with no limit is noise.
- It goes `--hw-danger` at the limit, and the field goes into error only when the user tries to submit, not while typing.

### Field group and legend

A `<fieldset>` with a real `<legend>` at `title-3`, optionally followed by one line of group helper text at `label` in `--hw-text-secondary`.

- **A radio group is always a fieldset**, because the legend is the question and the labels are only the answers. Without it a screen reader reads four unrelated options.
- The fieldset carries no border and no fill. It is a flat surface under [50-surface-texture.md](50-surface-texture.md); the grouping is done by the legend and the `--hw-space-24` below the group.
- Three to seven fields per group. Past that the group is two groups.

### Form layout, by breakpoint

Labels sit **above** their field, always.

Label-beside was measured against label-above and label-above wins on every count that matters here: it survives a 390px viewport without a second layout, it never truncates a long label, it keeps one left edge down the column as [80-anti-patterns.md](80-anti-patterns.md) requires, and it does not need a second column width to be agreed per screen.
Label-beside exists to save vertical space, and a form is not a surface this portfolio optimises for density.

| from | to | form column |
|---|---|---|
| 0 | `--hw-bp-md` | one column, full width inside `--hw-gutter-sm` |
| `--hw-bp-md` | `--hw-bp-lg` | one column, capped at `--hw-measure-ui` |
| `--hw-bp-lg` | up | one column at `--hw-measure-ui`; two only where fields are genuinely paired |

**A form does not use the twelve-column grid.**
A form is a reading column with controls in it, so it takes a measure, not a column count, and `--hw-measure-ui` at 56ch is that measure.
A form stretched to a 1200px container produces a 100-character label over a 1200px input, which is the same defect as a 95-character measure in [80-anti-patterns.md](80-anti-patterns.md).

Two fields share a row only when they are one value: a date and its time, a quantity and its unit, a first and a last name.
Never because two happened to fit.

### The action row

Separated from the last field by `--hw-space-16` and a 1px `--hw-border` rule.

- **The primary action is first and the row is left-aligned.**
  This differs from a dialog, where [65-components.md](65-components.md) puts the actions right-aligned with the primary last, and the difference is deliberate: a dialog's row is read at the end of a sentence the dialog just made, while a page form's row is read down the same left edge as every label above it.
- One primary action. A `Cancel` beside it is `secondary`; a destructive alternative is `danger`.
- The primary action is **not disabled while the form is incomplete**.
  Disabling it hides which field is wrong and gives the user nothing to press to find out.
  It stays enabled, and pressing it runs validation and moves focus to the first error, which is the whole subject of [67-validation.md](67-validation.md).
- On submit the label becomes the verb in progress and the width is held, per [60-states.md](60-states.md).

### Disabled against read-only, which are not the same control

This distinction already exists in [60-states.md](60-states.md) and forms are where confusing it costs the most.

| | fill | text | may be copied | in the tab order |
|---|---|---|---|---|
| **read-only** | `--hw-surface-sunken` | `--hw-text`, 13.98:1 light and 16.98:1 dark | yes | yes |
| **disabled** | `--hw-surface-sunken` | `--hw-text-disabled`, 3.00:1 light and 3.64:1 dark | no | see below |

A generated key, a run id or a hash the user is meant to hand to something else is **read-only**, never disabled.
Setting it disabled puts the one string the product exists to give away at 3:1 and blocks selecting it.

A control disabled for a reason says the reason beside it rather than in a tooltip, and where the reason is not obvious it takes `aria-disabled` with a real handler that explains, rather than `disabled`.

## What the consumer provides

The `id` and `for` that bind a label to its control, the `aria-describedby` that binds the helper and the error, `aria-invalid` on a field in error, `fieldset` and `legend` markup, the combobox ARIA pattern and its arrow-key handling, the debounce, the upload transport, and the submit handler.
This system provides the tokens, the geometry and the rules.

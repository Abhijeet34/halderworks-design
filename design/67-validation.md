# Validation

The moment a form tells a person they are wrong is the moment it is least trusted, so this is the part to get right.

[66-forms.md](66-forms.md) owns the controls.
[25-content.md](25-content.md) owns the words in the message.
This file owns when the judgement happens, where the verdict sits, how it is bound to the field for a screen reader, and what colour it is allowed to be.

## When validation fires

The timing rule is one sentence: **never judge a field the user has not finished, and never make them press submit to find out.**

| moment | what runs |
|---|---|
| while typing, field never yet valid | nothing |
| while typing, field **already in error** | re-validate on every keystroke, and clear the error the instant it passes |
| on blur | validate that field |
| on submit | validate every field, then move focus to the first that failed |
| after the server answers | show what the server rejected, on the field it belongs to |

The asymmetry in the second row is the whole of it.
Validating as someone types their fourth character tells them a 64-character hash is too short, which they know.
Not clearing the error until they blur leaves a red field around a value that is now correct, which is worse, because the product is now making a false statement about a value the user is looking at.

**Format is checked in the browser; truth is checked on the server.**
A hash can be checked for 64 hex characters locally.
Whether that artifact exists cannot be, so a field can pass every local rule and still be rejected, and the form must be built expecting that rather than treating a server rejection as an exception.

## Where the message sits

Directly under the field, `--hw-space-4` clear, at the `label` step, in `--hw-danger`.

- **It replaces the helper text.** Never stacked, and this is the rule most often broken.
- **The field's border becomes `--hw-danger`, and its fill does not change.**
  A red fill puts the user's own text on a ground no contrast pair in this system was solved for.
- The message names what failed and what to do, with the specific values, per [25-content.md](25-content.md): `Expected 64 hex characters. That value is 40.`
- One message per field. Two rules failing is one message naming the first the user should fix.

## The error colour, on every surface it can appear on

A form appears on the page, inside a card, inside a dialog, inside a read-only row and inside a floating panel, so the error ink has to clear AA on all of them and not only on the page ground.
Every pair below is measured, not asserted.

| `--hw-danger` on | light | dark |
|---|---:|---:|
| `--hw-ground` | 5.09 | 5.61 |
| `--hw-surface` | 5.42 | 5.22 |
| `--hw-surface-raised`, which is a dialog and a menu-bar panel | 5.42 | **4.80** |
| `--hw-surface-sunken`, which is a read-only or disabled field | **4.80** | 5.82 |
| `--hw-surface-hover` | 5.00 | 5.01 |
| `--hw-surface-active` | 4.80 | 4.80 |
| `--hw-danger-quiet`, which is the summary block | **4.61** | **4.59** |

Worst case **4.59:1** against a 4.5:1 bar, which holds with 0.09 to spare and no more.
The tightest three are bolded because they are the ones a new surface would break first: adding a surface between `--hw-surface-active` and `--hw-danger` re-opens every one of them, and [95-extending.md](95-extending.md) owns that check.

`--hw-success` and `--hw-warning` run within 0.01 of these figures on the same grounds, because all three semantics were solved to one target.

**The border in error is the same token at the same value**, and as a non-text boundary it needs 3:1 rather than 4.5:1, which every figure above clears twice over.

## Binding the error to the field

Colour and position are how a sighted user finds the error.
These attributes are how everyone else does, and they are the consumer's to provide.

- `aria-invalid="true"` on the control, removed when it passes.
- `aria-describedby` on the control pointing at the message element's `id`.
  The same attribute points at the helper text when there is no error, which is why the error **replaces** the helper rather than stacking: two ids in `describedby` read both, and the user hears the rule and the failure as one run-on sentence.
- The message element is `role="alert"` **only** when it appears after submit.
  On blur it is a plain element already referenced by `describedby`, because an alert interrupts whatever is being read, and being interrupted on every field you leave is worse than not being told.
- A field in error is never removed from the tab order and never disabled.

## The form-level error summary

When submit fails, a summary appears **above the form**, before the first field.

- `--hw-danger-quiet` fill, 1px `--hw-danger` border, `--hw-radius-md`.
- A title at `body-sm` weight 600 in `--hw-text`, which is 13.4:1 on that fill, naming the count: `Two fields need attention`.
- Under it, one link per failed field, in `--hw-danger` at 4.61:1 light and 4.59:1 dark, each carrying the field name and its message: `Artifact hash: expected 64 hex characters, that value is 40.`
- **Each entry is a real link to its field**, and following it moves focus into the control, not merely scrolls to it.
- Focus moves to the summary on failed submit, once. It does not move again while the user fixes fields.
- The summary disappears on the next successful submit and not before.

A summary is worth building at three failed fields; below that the per-field messages are enough and a summary repeating one message twice reads as an error about the error.

## Success and pending

**A field that passes says nothing.**
There is no green tick. <!-- covered-by: Success and pending states -->
Passing is the expected case and marking it spends the reader's attention on the outcome that needed none, and a column of green ticks beside every field makes the one red field harder to find rather than easier.

Success belongs at the **form** level, not the field level, and it is the toast in [65-components.md](65-components.md): past tense, matching the button.
`Save changes` produces `Changes saved`.

**Pending** is for a check that has to leave the machine, such as "is this hash known to the registry".

- The control keeps its rest border. Pending is not a state the border reports.
- The helper text is replaced by the check in progress, in `--hw-text-secondary`: `Checking the registry...`
- `aria-busy="true"` on the field, and the live region announces the **outcome**, never the start, per [60-states.md](60-states.md).
- A pending check never blocks typing in the field it is checking.
- If the check cannot complete, that is a pending failure and it says so: `Could not reach the registry. Save anyway, or retry.` It is never silently treated as a pass or as a failure.

`--hw-warning` is available for a field that is valid but worth a second look, such as a retention of 3650 days.
It takes the same geometry as an error and it never blocks submit.
A warning that blocks submit is an error that was too polite to say so.

## What the consumer provides

The rules themselves, the server round trip, `aria-invalid`, `aria-describedby`, the `role="alert"` timing, the focus moves on failed submit, and the live region.
This system provides the timing contract, the geometry, the certified colours and the words' shape.

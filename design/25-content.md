# Content

Words are design material.
A screen with perfect spacing and the label `Submit` on its primary button is an unfinished screen.

## Case

**Sentence case everywhere.**
Headings, buttons, labels, menu items, column heads, tabs, toasts, errors.

Measured across 1211 control labels on 44 sites: 60.9% sentence case, 21.4% all-lowercase, 11.0% title case, 2.8% upper case.
`text-transform` on those controls was `none` 1155 times against `uppercase` 50.

The two exceptions:

- **`micro` is uppercase**, and only for a column head or an eyebrow, which is a typographic style rather than a case choice. The underlying string is still sentence case.
- **Proper nouns keep their own case.** `Export to CSV`, `Sign in with GitHub`, `sha256`.

Title case is not used at all.
`Create New Run` reads as a brochure; `Create run` reads as a control.

## Naming

**Name things the way the person names them.**
A run, an artifact, a gate, a key, a record.
Not a job, a blob, a validator, a credential record, an entity.

One name per concept per product.
A thing called a run in the sidebar, an execution in the table head and a job in the error message is three things to a reader.

## Buttons and controls

**A control says what will happen. Its confirmation says it happened.**

| write | not |
|---|---|
| `Revoke key` | `Submit`, `Confirm`, `OK`, `Continue` |
| `Rotate key` and `Cancel` | `OK` and `Cancel` |
| `Save changes` | `Save` where it is not obvious what is saved |
| `Clear filters` | `Reset` |
| `Delete 3 runs` | `Delete selected` |

`OK` is the worst of these because it forces the reader back up to the title to learn what they are agreeing to.

A verb, and the object where the object is not obvious from context.
Never a sentence, never more than four words, never an ampersand.

## Errors

**An error says what went wrong and what to do.**
Three parts, in this order: what failed, why, and the next action, with the specifics.

```text
The signing key expired on 12 March. Generate a new one in Settings, Keys.
```

Not `An error occurred`, not `Invalid input`, not `Something went wrong`.

- **Name the value that was wrong** where the user supplied it.
  `Expected a sha256 hash, 64 hex characters. That value is 40.`
- **Never blame the user and never apologise.**
  No "Oops", no "Sorry", no "Please try again later" with no reason.
  The product is not sorry; it is telling you something.
- **A retryable error says so and offers the retry.** A permanent one does not offer a retry that will fail again.
- **An error toast never auto-dismisses.**
  The one person who needed to read it is the one who looked away.

## Empty states

One sentence of explanation, at a measure of about 40ch, and at most one action.
The three kinds are not interchangeable and [70-data-display.md](70-data-display.md) owns which is which.

`No runs yet. A run appears here when a pipeline starts.` is an empty state.
`No data` is a shrug.

## Numbers, units and dates in prose

The rules in [70-data-display.md](70-data-display.md) apply in a sentence as well as in a column.
Carry the unit and the precision: `04:12`, `$1.84`, `2.4 MiB`, `sha256:77c2d4e...`.

In running prose, numbers keep Public Sans' proportional figures, which are better inside a sentence.
`tabular-nums` is for columns and for numbers a reader will compare against the one above.

## Truncation

- **Truncate at the end for a name**, with the full value in `title`.
- **Truncate in the middle for a hash, an id or a path**, because the tail distinguishes.
- **Never truncate an error, a total, or a unit.**
- **Clipped text with no way to read it is a bug**, not a layout decision.
- A cell that can overflow truncates inside its own container, so the column width does not depend on the longest value that ever loaded.

## Tone

- **No exclamation marks.** Not one, anywhere.
- **No emoji.** It is on the anti-pattern list and it is not a close call.
- **No marketing verbs in product UI.** Nothing is seamless, effortless, powerful, or supercharged. [80-anti-patterns.md](80-anti-patterns.md) has the register.
- **Second person and the imperative for instructions.** "Generate a new key", not "A new key should be generated".
- **Present tense for behaviour.** "The gate refuses a change that cannot prove itself."
- **Spell out an acronym on first use per screen**, then use it freely.

## Microcopy that carries weight

| place | rule |
|---|---|
| placeholder | an example of the format, never a substitute for the label. `sha256:77c2d4e...` is a placeholder; `Artifact hash` is a label |
| hint | one line, under the field, replaced by the error rather than stacked with it |
| tooltip | for an icon-only control's name, or a truncated value in full. Never for a rule the user needs before acting |
| confirmation | past tense, matching the button that caused it. `Rotate key` produces `Key rotated` |
| destructive dialog | names what will be lost, with the number: `47 builds signed with this key will no longer verify` |
| badge | one word where one word will do. `Settled`, not `Successfully settled` |
| tab label | a noun, not a verb. `Evidence`, not `View evidence` |

Say the true thing in the fewest words the reader can act on.

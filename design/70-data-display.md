# Data display

These products exist to be trusted about a number, a state or a record.
This file is how a number reaches the screen.

[65-components.md](65-components.md) owns the anatomy of the DataTable, ListRow and EmptyState components.
This file owns what goes in them: alignment, formatting, the five states a data container has, and the charts.

## Table or list

| use a **table** when | use a **list row** when |
|---|---|
| the reader compares column to column | the reader scans for one subject |
| every row has the same fields | rows carry a title and a secondary line |
| a column can be sorted and that is useful | ordering is fixed or by recency |

If nobody compares column to column, a table is a list with rules drawn on it.

## Alignment

| column holds | alignment | why |
|---|---|---|
| a name, a description, a status word | left | the eye returns to one left edge |
| a number to be compared: count, duration, cost, size, percentage | **right** | digits line up by place value, so 1,204 and 998 are visibly different magnitudes |
| a date or timestamp | left | it is read as a token, not compared digit by digit |
| a hash, an id, a path | left, `--hw-font-mono` | read character by character |
| a single icon or a checkbox | centre in a fixed-width column | it has no text edge to align to |

**Every numeric column is right-aligned and carries `font-variant-numeric: tabular-nums`.**
In Public Sans a `1` is a third narrower than a `0`: at 100px, `1111111111` measures 407px and `0000000000` measures 606px, so a column without it visibly jitters row to row.

This is where the house rule deliberately departs from measured practice, and it is worth saying so.
Across 777 table cells sampled on 15 sites in the capture, **0 set `tabular-nums` and 3 were right-aligned**.
Those are documentation tables, which compare nothing.
A product whose tables carry compared numbers and copies documentation-table habits ships a jittering ledger.

Column heads are `micro` (11px, weight 600, 0.06em, uppercase) in `--hw-text-muted`, and a numeric column's head is right-aligned with its column.

## Numeric formatting

| kind | format | example |
|---|---|---|
| duration under an hour | `mm:ss`, mono, tabular | `04:12` |
| duration over an hour | `h:mm:ss` | `1:03:47` |
| duration under a second | milliseconds, integer | `412ms` |
| money | currency symbol, two decimals, always both | `$1.84`, `$12.00` |
| count | thousands separator above 9999 | `1,204` |
| percentage | one decimal below 10, none above | `4.2%`, `87%` |
| bytes | binary units, one decimal | `2.4 MiB` |
| hash or id | mono, truncate in the middle | `sha256:77c2d4e...9f01` |

Rules:

- **A unit is part of the value, not a column heading's job alone.**
  A column headed `DURATION` full of bare integers makes the reader carry the unit.
- **Precision is fixed per column.**
  `$1.8` beside `$12.00` is two formats in one column.
- **Zero is `0`, not a dash.**
  A dash means "no value"; `0` means "we measured, and it was none". They are different facts.
- **A truncated hash truncates in the middle**, because the tail is what distinguishes two hashes with the same prefix.

## Dates

- **Absolute where the exact moment matters**, which in these products is almost always: `12 Mar 2026, 14:03 UTC`.
- **Relative only within the last 24 hours, and only beside the absolute one**: `3 min ago`, with the timestamp in the title attribute.
- **Never "a few minutes ago" where a timestamp is known.**
  A record that will not say when is a record that cannot be checked.
- One timezone per screen, named on the screen.
- `1 Mar` not `01 Mar`, `14:03` not `2:03 PM`, and the month is a word because `03/04` is two different dates in two countries.

## The five states of a data container

A table, a list and a chart each have all five.
Shipping three of them is how a product gets a spinner that never resolves and a "No data" that means four different things.

| state | what it shows |
|---|---|
| **loading** | a skeleton in `--hw-surface-active` at the shape of the real rows, three to five of them, `aria-busy="true"`. Never a spinner, never a blank container |
| **loaded** | the rows |
| **empty: nothing yet** | what will appear here and what makes it appear, plus the action that creates the first one |
| **empty: nothing found** | what was searched, and `Clear filters` in the `quiet` variant |
| **error** | what failed, in one sentence, plus `Retry`. The error stays until it is acted on |

The two empty states are not interchangeable, and confusing them is the most common failure here: the user who filtered to zero results gets told how to create their first run, which they already have four of.
Only the consumer knows which applies, because only the consumer knows whether zero rows means new or filtered.

**A partial failure is not an error state.**
A table that loaded 400 of 500 rows shows the 400 with a banner above them naming what is missing, because hiding successful data behind a failure is a worse answer than an incomplete one.

## Charts

Six chart colours, `--hw-chart-1` to `--hw-chart-6`, held to the same 3:1 non-text bar as the focus ring because they are fills rather than text, on every surface a chart is drawn on.

| | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| on the light ground | 3.29 | 8.13 | 3.62 | 8.41 | 3.43 | 7.55 |
| on `--hw-surface-sunken`, the light theme's worst surface | 3.10 | 7.66 | 3.41 | 7.93 | 3.24 | 7.12 |
| on the dark ground | 8.54 | 13.62 | 7.84 | 13.37 | 8.18 | 14.14 |
| on `--hw-surface-raised`, the dark theme's worst surface | 7.31 | 11.65 | 6.71 | 11.44 | 7.00 | 12.10 |

Adjacent series alternate in lightness, by 0.20 in light and 0.15 in dark, so series two, four and six are the strong members in both themes.
Every chart colour sits at least 8.0 in oklab distance times 100 from `--hw-success`, `--hw-warning` and `--hw-danger`, the bar the accent was held to before [three painted bars](10-color.md#the-three-bars-the-accent-is-held-to) replaced it, and the closest chart pair sits 15.4 apart in light and 10.2 in dark.
Until 2026-09-21 series four, five and six sat 1.6, 2.5 and 3.7 from danger, warning and success in light, because the chart hues rotate with the accent while the semantics stay put; `tools/build.py` now refuses an accent hue that would put any series that close.

Rules:

- **Order is fixed.** `--hw-chart-1` is always the first series, so the same series is the same colour on every chart in the product.
- **Six is the ceiling.** A seventh series is an "Other" bucket, or the chart is the wrong chart.
- **Colour is never the only key.** A line carries a direct label at its end; a bar chart carries its axis. A legend a reader must look back and forth to is a chart that needed labels.
- **The axis and gridlines are `--hw-border`**, and no horizontal gridline is drawn where the bars already start from a baseline.
- **A single-series chart uses `--hw-accent`, not `--hw-chart-1`**, because one series is a state rather than a category.
- **Start a bar chart's value axis at zero.** A truncated axis makes a 3% difference look like a 300% one, which in an instrument of record is a false statement.
- **A sparkline carries no axis, no grid and no label**, only its line and its last value in mono beside it.
- Numbers on a chart follow the formatting table above, tabular figures included.

`--hw-success` and `--hw-danger` are for a delta against a baseline, not for series colour.
Green bars that mean "series one" and green bars that mean "passed" cannot coexist in one product.

## Bulk selection and select-all

A table that handles hundreds of rows is a table somebody will want to act on twenty of.
Before this entry, `bulk|select all|multi-select` returned **0** across the whole book while this
file required a table to handle hundreds of rows.

### Anatomy

| part | token |
|---|---|
| the selection column | a fixed `--hw-space-48` leading column, checkbox centred, which is what the alignment table above already says a lone checkbox takes |
| the head checkbox | the same control, in three states: none, some, all |
| a selected row | `--hw-accent-quiet` fill with its text in `--hw-text`, which is the selected-row pairing in [15-color-combinations.md](15-color-combinations.md) |
| the action bar | the toolbar's own content, replaced in place at `--hw-space-48` - never a second bar appearing, which would push every row down at the moment the reader is aiming at one |
| the count | `body-sm` in `--hw-text`, naming the unit: `3 runs selected` |

### Rules

- **The head checkbox selects what is loaded, not what exists.** With 400 rows loaded of 12,043, a
  head checkbox that means all 12,043 is a control whose effect the reader cannot see.
- **Selecting everything is a second, explicit affordance**, and it states the number. Once the page
  is selected, one line appears in the action bar: `All 400 on this page are selected.` with
  `Select all 12,043` beside it. The reader opts into the larger scope and is told its size.
- **The some state is `indeterminate`, not unchecked.** An unchecked head checkbox above three
  ticked rows is a control reporting a false state.
- **Selection survives a sort and does not survive a filter**, because sorting reorders the same set
  and filtering changes it. Where a product does carry selection across a filter, the count must say
  so: `3 selected, 2 not shown`. A hidden selection is how a bulk action reaches a row the reader
  never saw.
- **A destructive bulk action always takes the dialog**, never the inline confirm in
  [65-components.md](65-components.md#inline-destructive-confirm). Scope is the whole test there,
  and many rows is out of scope by construction. The dialog names the count.
- **The bulk actions are the row actions, and nothing else.** A capability that exists only in bulk
  is a capability nobody can try on one row first.
- **Clearing is always one action away**, named `Clear selection`, and Escape does it.

**Keys:** Space toggles the focused row. Shift with Up or Down Arrow extends the selection from the
anchor, which is the APG listbox binding; Shift with a click does the same by pointer. Full map in
[72-keyboard.md](72-keyboard.md).

### What the consumer provides

`aria-selected` on each selected row, the `indeterminate` property on the head checkbox - it is a
DOM property, not an attribute, and setting `checked` does not produce it - and the anchor row that
a range extends from.

## Density

A dense table takes `data-density="compact"`, which changes row height and vertical padding and nothing else.
[45-density.md](45-density.md) owns exactly what moves, and the fact that horizontal padding does not is what keeps a column in the same place across the toggle.

Show the number, its unit and its precision, and let the reader do the comparing.

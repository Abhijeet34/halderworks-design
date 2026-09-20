# Keyboard and input modality

This is the single page a reviewer checks a screen against.

Before it existed, [05-coverage.md](05-coverage.md) recorded "no keyboard map for the system as a
whole" as a gap in accessibility. It was not. It was a gap in **architecture**: this book had a
form-factor axis and no input axis, so a keyboard rule had nowhere to live except inside each
component card, which is exactly why there was no page to check against.

Counted before this file was written, over the whole book: `roving` and `tabindex` **0**,
`activedescendant` **0**, arrow keys **2**, `aria-disabled` **2** and both about a blocked submit
button. [90-evidence.md](90-evidence.md) carries the commands.

## Input modality is a peer of form factor, not a part of it

Apple's Human Interface Guidelines put `inputs` at the top level beside `components`, holding 13
modalities. Three of them apply to every product this system ships: **focus and selection,
keyboards, pointing devices.**

That is the split this book now makes:

| axis | owned by | what it decides |
|---|---|---|
| **form factor** - how much room there is | [36-form-factors.md](36-form-factors.md) | the shell, the container, what stacks and at which breakpoint |
| **input modality** - what is driving it | this file | the tab sequence, the key bindings, the hit target, whether hover exists at all |

**A touch laptop is a large viewport with a coarse pointer**, and a keyboard-only desktop user is a
fine-pointer form factor with no pointer in use. Reading those two off one axis is what produced a
book with a `--hw-control-h` rebind under `(pointer: coarse)` and no statement of what a keyboard
does anywhere.

The pointer half is short and already decided: `(pointer: coarse)` rebinds `--hw-control-h` to the
44px floor, hover does not exist, and every hover-reachable state is also focus-reachable.
[36-form-factors.md](36-form-factors.md) owns the geometry and [60-states.md](60-states.md) owns the
states. The rest of this file is the keyboard.

## The convention the whole map rests on

**Tab and Shift+Tab move between components. Everything else moves within one.**

That single convention, published by the ARIA Authoring Practices Guide, is what makes 381
scattered key bindings a system rather than a list, and it is the sentence this book did not have.

Two consequences a reader should take before reading any table below:

- **A composite widget is one tab stop, not one per item.** A tablist with six tabs, a listbox with
  four hundred rows and a toolbar with nine buttons each take exactly one stop in the page's tab
  sequence, and the arrows move inside.
- **Tab is how you leave.** Across the APG's 381 enumerated bindings Tab appears 15 times, because
  inside a composite it is an exit rather than a traversal.

### The two ways focus moves inside a composite

| technique | what carries focus | when this system uses it |
|---|---|---|
| **roving `tabindex`** | the DOM element itself; the active item is `tabindex="0"` and every sibling is `tabindex="-1"` | tabs, toolbar, navigation rail, segmented control, menu - anywhere the item is a real focusable element |
| **`aria-activedescendant`** | a reference on the container to the id of the active item; DOM focus never leaves the container | combobox and any listbox driven from a text input, where focus must stay in the field the user is typing in |

Pick one per widget and never both.
The combobox is the case that forces `aria-activedescendant`: the caret has to stay in the input, so
the active option cannot hold DOM focus. [66-forms.md](66-forms.md) describes the behaviour in prose
and this is the attribute that implements it.

### A disabled item inside a composite stays focusable

`disabled` removes an element from the tab sequence. `aria-disabled="true"` does not.

**Inside a composite widget, use `aria-disabled`.** A disabled menu item, listbox option or toolbar
button stays reachable by the arrow keys and announces its state.

The reason is the APG's and it is not obvious: skipping disabled elements saves a sighted keyboard
user key presses, but a screen-reader user is far less likely to ever discover a disabled element
they cannot reach. The saving is small and the loss is total.

**Outside a composite this reverses.** A disabled submit button is a single tab stop and uses the
real `disabled` attribute, which is what
[66-forms.md](66-forms.md#disabled-against-read-only-which-are-not-the-same-control) already
specifies. The two `aria-disabled` mentions this book had before this file were both that case; the
composite case had never been stated.

### Selection follows focus on tabs, and that is a decision

The APG marks arrow-key activation "Optionally" and Home/End "(Optional)", so a specification that
says nothing gets built two ways by two authors.

**This system's answer: automatic activation.** Moving to a tab with an arrow key selects it and
shows its panel.

It holds because tabs here switch between views of one subject ([65-components.md](65-components.md))
and switching is cheap and reversible. Where switching is expensive - a panel that fetches, a form
that would lose state - the tab set is the wrong component, not a case for manual activation.

## The map

Every component this system specifies, with the keys it owes.
Where a row is thinner than the APG pattern behind it, that is because this system's component is
narrower, and the pattern name is given so the full set can be read.

| component | APG pattern | focus technique | keys |
|---|---|---|---|
| **Button** | `button` | - | Enter, Space activate |
| **Link** | `link` | - | Enter activates. **Never Space**: Space scrolls, and a link that eats it breaks the page |
| **Tabs** | `tabs` (14 rows) | roving `tabindex` | Left/Right Arrow move and activate, Home/End to first and last, Tab into the panel |
| **Accordion, disclosure** | `accordion`, `disclosure` (4, 2) | - | Enter or Space toggles the header. Each header is its own tab stop; arrows are not used |
| **Menu, dropdown, context menu** | `menu-button`, `menubar` (5, 41) | roving `tabindex` | Enter/Space/Down Arrow open, Up/Down Arrow move, Escape closes and returns focus to the trigger, Home/End, a printable character jumps to the next item starting with it |
| **Select, native** | - | the browser's | whatever the platform does. This is why [66-forms.md](66-forms.md) prefers it |
| **Combobox with type-ahead** | `combobox` (80 rows, the largest) | `aria-activedescendant` | Down Arrow opens and moves, Up Arrow moves, Alt+Down Arrow opens without moving, Enter commits, Escape closes then clears, Home/End inside the field, printable characters filter |
| **Listbox, custom select** | `listbox` (32) | roving or `aria-activedescendant` | Up/Down Arrow, Home/End, Space selects, Shift+Arrow extends where multi-select is permitted |
| **Checkbox, radio** | `checkbox`, `radio` (15) | radio group is roving | Space toggles a checkbox. A radio **group** is one tab stop and the arrows move and select within it |
| **Switch** | `switch` (2) | - | Enter or Space toggles |
| **Slider** | `slider` (10) | - | Left/Down Arrow decrease, Right/Up Arrow increase, Page Up/Down by a larger step, Home/End to the bounds |
| **Numeric stepper** | `spinbutton` (13) | - | Up/Down Arrow by one step, Page Up/Down by a larger step, Home/End to the bounds |
| **Dialog** | `dialog-modal` (14, of which Escape is the only key) | focus trap | Escape closes. Tab cycles within the dialog and never leaves it. Focus enters on open and returns to the trigger on close |
| **Toast** | `alert` ("Not applicable") | - | no keys. A toast never takes focus, which is why an action inside one must also exist on the page |
| **Data table** | `grid` (20) where cells are interactive | roving `tabindex` | a static table is not a grid and takes no keys at all. Where cells are interactive: the four arrows, Home/End for the row, Control+Home/End for the table |
| **Toolbar** | `toolbar` (10) | roving `tabindex` | Left/Right Arrow move, Home/End to first and last, one tab stop for the whole toolbar |
| **Navigation rail** | - | roving `tabindex` | Up/Down Arrow move between items, Enter activates, and a group that expands uses `aria-expanded` with Right/Left Arrow to open and close |
| **In-page table of contents** | - | - | a list of links. Each is its own tab stop and Enter activates |
| **Tooltip** | `tooltip` (3 rows, none of them a key) | - | it appears on focus as well as hover and Escape dismisses it. A tooltip is never a tab stop |
| **Segmented control** | `radio` | roving `tabindex` | one tab stop, arrows move and select |

**Where this system has no answer**, said plainly rather than left blank: `treegrid` (43 rows),
`treeview` (40) and `menubar` as a persistent application menu bar (41) are the three largest
keyboard contracts in the APG and none of them is a component here.
[05-coverage.md](05-coverage.md) carries all three as `excluded` rows with their reasons.

## The cross-component key conventions

These apply anywhere their function applies, and the platform split is not cosmetic.

| function | Windows and Linux | macOS |
|---|---|---|
| open a context menu | Shift+F10 | - |
| copy | Control+C | Command+C |
| paste | Control+V | Command+V |
| cut | Control+X | Command+X |
| undo | Control+Z | Command+Z |
| redo | Control+Y | Command+Shift+Z |

**Shift+F10 is the one most often missed and the one this system most needs.**
[36-form-factors.md](36-form-factors.md) specifies a desktop application shell, and a desktop shell
with no context-menu key is a desktop shell a keyboard user cannot right-click in.

The Windows and Linux assignments work in a browser on macOS. Replacing them with the macOS
assignments when the browser is running on macOS makes the interface more discoverable there, and
avoids colliding with system shortcuts.

## The focus ring, which is not optional and is already solved

[60-states.md](60-states.md) owns the states and
[15-color-combinations.md](15-color-combinations.md) owns the certification.
Three facts belong here because they are keyboard facts:

- `--hw-accent-ring` at `--hw-focus-w` 2px on `--hw-focus-offset` 2px, solved to 3:1 against the
  surface **closest to it in lightness**, which is 3.05:1 at its worst in both themes. It was solved
  that way precisely so it can stay on. Never remove it.
- **`:focus-visible`, never `:focus`.** A mouse click on a button should not leave a ring behind it;
  a Tab onto the same button must.
- **The ring goes inside a scrolling container's row, not around it**, so the container does not clip
  it. [65-components.md](65-components.md)'s list row already says this.

## Two rules that decide whether any of the above is reachable

- **Every hover-reachable state is also focus-reachable.** A row action that appears on hover and
  has no keyboard path does not exist for a keyboard user.
  [65-components.md](65-components.md) states it per component; this is the general form.
- **A skip link is the first tab stop on any shell with a permanent rail.**
  [37-navigation.md](37-navigation.md) specifies it. Without one, a keyboard user tabs the whole
  rail before reaching the content, on every page, forever.

## What the consumer provides

This system provides the map. The product provides the implementation, and these five are the ones
that are got wrong:

1. The roving `tabindex` or `aria-activedescendant` wiring, whichever the table above names.
2. `aria-expanded` on anything that opens, and `aria-current` on the navigation item for the page
   you are on.
3. The focus trap and the return target for a dialog.
4. `aria-disabled` rather than `disabled` inside a composite.
5. The platform branch on the context-menu and clipboard keys.

Tab leaves. Everything else stays inside.

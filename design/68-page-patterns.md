# Page patterns

Two whole-page compositions that every product with a rail ships and that this book had no entry
for. Neither is a component: each is a layout, a set of existing components and the two or three
decisions that go wrong when nobody has written them down.

Before these entries, a sweep of the whole book returned **one** match for
`log in|login|sign in|sign up|authenticat`, a casing example in [25-content.md](25-content.md), and
**one** for a settings page - an aside in [45-density.md](45-density.md) that presumed a page this
book never specified. [90-evidence.md](90-evidence.md) carries the cross-check.

## The way in: sign in, sign up, reset password

Three screens, one shape. Every product with a rail has a way in, and it is the first screen a new
user ever sees of the system.

### Sign-in: anatomy

| part | token | derivation |
|---|---|---|
| shell | the site header from [37-navigation.md](37-navigation.md) **with the nav removed**, the mark only | there is nowhere to navigate to yet |
| column width | `--hw-panel-w`, 352px | the same derivation as the menu-bar panel: 40ch of `body-sm` plus `--hw-cell-pad-x` each side. Two fields read in a glance |
| vertical placement | the column centred horizontally, `--hw-space-96` from the header | |
| heading | `title-2` (21px/600), one line, `--hw-space-24` above the first field | |
| fields | [66-forms.md](66-forms.md) unchanged, label above, one column | |
| the action | `primary` at `--hw-control-h`, **full width of the column** | the same rule the menu-bar panel's footer action takes |
| the alternate route | one `body-sm` line below the action in `--hw-text-secondary`, its link in `--hw-accent` | a link is the first of the accent's four jobs |

**This is the second place in this system where centring is correct, and it is correct for the same
reason as the first.** [65-components.md](65-components.md) permits a centred empty state because
there is a single element and nothing to align it to. A sign-in page is that case at page scale:
the form is the whole screen. Everything inside the column is still left-aligned.

### Sign-in: rules

- **One route per screen.** Sign in and sign up are two pages with two addresses, never two tabs on
  one page. A reader who arrived to do one of them should not have to notice which half is
  selected, and an address that resolves to both cannot be linked to.
- **An authentication failure is a form-level error, not a field error.**
  [67-validation.md](67-validation.md) owns the form-level summary and this is the case for it.
  Telling the reader that the address is fine and the password is wrong tells anybody who asks which
  addresses have accounts. One message: the pair did not match.
- **The reset-request screen says the same thing whether or not the address exists.** "If that
  address has an account, a reset link is on its way." Same reason.
- **Requirements are stated before the field, not after the failure.** A password rule discovered by
  breaking it is a rule the product knew and withheld.
  [67-validation.md](67-validation.md#when-validation-fires) already fixes when validation fires.
- **No strength meter.** A meter that scores a password against a guess is a number the product
  invented, and [80-anti-patterns.md](80-anti-patterns.md) refuses invented metrics. State the
  requirement, check the requirement.
- **No provider buttons the product does not actually have**, and where it has them they are
  `secondary`, above the form with a `--hw-border` rule and `--hw-space-24` between, never below
  the primary action.
- **The reset flow is three screens** - request, sent, set new - and each is this same column. A
  flow that tries to be one screen with three states cannot be linked to from an email.

### Sign-in: what the consumer provides

`autocomplete` on every field (`username`, `current-password`, `new-password`), which is what makes
a password manager work and is the single most commonly missed attribute on this screen. Also the
`<form>` element itself, the submit handler, and the rate limiting.

## The settings page

### Where it lives

**A destination in the rail, never a dialog.** A dialog interrupts to ask for one decision that
cannot be deferred ([65-components.md](65-components.md)); settings are a page of decisions all of
which can be deferred, which is the definition of the thing that belongs on a page.

It uses the app shell from [35-layout.md](35-layout.md) whole. Nothing here changes it.

[45-density.md](45-density.md) notes in passing that a settings page does not offer the density
toggle, because density belongs to the surface it applies to and is set there.
**That aside presumed this page.** This is the page it presumed, and the note stands.

### Settings: anatomy

| part | token |
|---|---|
| content width | `--hw-measure-ui`, 56ch, left-aligned with the page margin - a form, not a page of columns |
| a section | `--hw-surface` on `1px solid var(--hw-border)`, `--hw-radius-lg`, `--hw-space-16` padding, which is the card from [65-components.md](65-components.md) unchanged |
| section heading | `title-3` (17px/600), with one line of `body-sm` in `--hw-text-secondary` under it where the section needs explaining |
| between sections | `--hw-space-24` |
| within a section | the field group and its layout from [66-forms.md](66-forms.md) |
| the action row | `--hw-surface-sunken` footer inside the section, which is the card's own footer rule |

### Settings: rules

- **Every section saves itself.** One `Save` at the foot of a page of twelve sections asks the
  reader to remember which of the twelve they touched, and reports one outcome for twelve
  independent things.
  A section's action row appears when that section is dirty and names what it saves: `Save
  notification settings`, not `Save`.
- **A toggle that takes effect immediately is a switch and says so; anything that needs saving is a
  field in a section with an action row.** Mixing the two on one page is what makes a settings page
  feel unreliable, because the reader cannot tell which of their changes are already live.
  [66-forms.md](66-forms.md#switch) owns which control a case takes.
- **The destructive section is last, and it is the only section with a `--hw-danger` border.**
  It is separated by `--hw-space-48` rather than `--hw-space-24`, so a misfired scroll does not land
  on it.
- **Reversible destruction takes the inline confirm; irreversible destruction takes the dialog.**
  Revoking a key that can be reissued is an inline confirm
  ([65-components.md](65-components.md#inline-destructive-confirm)). Deleting an account is a
  dialog that names what will be lost, with the number.
- **A setting the product cannot honour is not shown.** A disabled toggle with a tooltip explaining
  why the plan does not include it is an advertisement wearing a control's clothes.
- **No accent anywhere on this page unless a state is being reported.** A settings page is the
  surface most likely to acquire a blue Save button, and
  [15-color-combinations.md](15-color-combinations.md) gives the accent four jobs of which that is
  not one. The primary action is `--hw-ink`.

### Settings: what the consumer provides

Which settings are per-user and which are per-workspace, and the permission model that decides which
sections a given reader may see at all. The system cannot tell those apart and the answer changes
the page.

A page of settings is a page of forms, and every rule in [66-forms.md](66-forms.md) applies to all
of them.

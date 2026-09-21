# Page patterns

Five whole-page compositions this book had no entry for. The first three every product with a rail
ships; the last two every product with a public address ships. None is a component: each is a
layout, a set of existing components and the two or three decisions that go wrong when nobody has
written them down.

Before these entries, a sweep of the whole book returned **one** match for
`log in|login|sign in|sign up|authenticat`, a casing example in [25-content.md](25-content.md), and
**one** for a settings page - an aside in [45-density.md](45-density.md) that presumed a page this
book never specified. [90-evidence.md](90-evidence.md) carries the cross-check.

The 404 page and the pricing page are a different failure. Two sentences in this book claimed both
had entries from its first public commit, and a sweep for
`404|link.preview|open.graph|og:image|og:title|pricing|paywall` returned no entry and no inventory
row for either. `tools/check-coverage.py` now fails a claim of an entry that resolves to no row.

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

## First run and setup

The screen between the way in and the product's first real screen: the permissions, the folder or
model to choose, the one test that proves the product works on this machine. Every product that
needs something from the machine before it can do its job ships one.

**It is a page, never a modal wizard and never a tour.** A tour's coachmarks point at controls the
reader cannot use yet, and [05-coverage.md](05-coverage.md#ruled-out-with-the-reason) rules one out.

This entry came from a review rather than a sweep. On 2026-09-21 the system's owner reviewed a
product's first-run screen, a setup checklist: a disabled primary control, a large microphone orb,
was the biggest object on the screen, the checklist that was the only thing the reader could do sat
off-centre beside it, reward copy competed in a sidebar, and three different marks appeared on one
screen. Each of those is a rule below, and the three that hold on every screen are stated where
they belong: [one primary focus](35-layout.md#one-primary-focus-per-screen),
[a disabled control's weight](60-states.md#disabled-is-a-solved-colour-not-an-opacity) and
[one mark](00-brand-book.md#the-mark).

### First run: anatomy

| part | token | derivation |
|---|---|---|
| shell | the sign-in page's: the site header with the nav removed, the mark only, and no rail | until setup is done every destination a rail offers opens onto a nothing-yet empty state, so a rail here is a column of dead ends |
| column width | `--hw-measure-ui`, 56ch, centred horizontally | each task carries one sentence of explanation, which is running text in product UI, and [56ch is its measure](35-layout.md#measure). The sign-in column's 352px is sized for two fields, not for a sentence |
| vertical placement | `--hw-space-96` from the header | the sign-in column's placement |
| heading | `title-2` (21px/600), naming what is being set up in the product's words: `Set up papertrace` | [25-content.md](25-content.md#naming) names things the way the person does |
| progress | one `body-sm` line under the heading in `--hw-text-secondary`, `2 of 4 done`, `tabular-nums` | a count is exact and reads aloud as written; a bar or a ring over four tasks draws a precision it does not have |
| the tasks | one [list row](65-components.md#list-row) per task, in the order they must be done, all of them visible from the start | the reader sees the whole cost of setup before paying any of it |
| a task's state | a leading 16px Lucide mark in `currentColor` and a trailing word: `check` and `Done`, `circle` and `To do`, `Skipped` for a skipped optional task; a finished or waiting task's title in `--hw-text-secondary` | every state carries a word, and the words are neutral |
| the current task | its row expanded: one sentence of what the task does and why the product needs it, then its one action as `primary` at `--hw-control-h` | the screen's one primary action is always the current task's |

Centred for the sign-in page's reason: the column is the whole screen. Everything inside it is
left-aligned.

### First run: rules

- **The setup task is the only focus.** No sidebar, no feature preview, no tip and no view of the
  product waiting behind it. [One primary focus](35-layout.md#one-primary-focus-per-screen) is
  the general rule; here the setup list is the focus by construction, because it is the only thing
  the reader can do.
- **The product's main control does not appear until the step that uses it.** A record button, a
  microphone or a run control that cannot work yet is not drawn disabled at full size: it is
  absent, and it appears inside the task that tests it, at that task's action size, enabled. This
  is the screen where a disabled control is most likely to carry the most weight, because the main
  control is the product's signature and is the first thing drawn.
- **Progress is a count in a neutral colour.** A finished task is not a passed check, so it takes
  `--hw-text-secondary` and the word `Done`, never `--hw-success`, and a column of green ticks is
  the one [67-validation.md](67-validation.md#success-and-pending) already refuses on a form.
  `--hw-warning` appears only on a task blocked by a real problem, with its mark and a sentence
  naming the problem and the fix: `Microphone access is off. Turn it on in System Settings, Privacy
  and Security, Microphone.` A task not yet reached is not a problem, and a task that failed takes
  `--hw-danger` as [the state table](15-color-combinations.md#semantic-and-its-quiet-fill) assigns it.
- **No reward copy.** No points, streaks, levels, percentages, `You're almost there`, and no
  celebration when setup ends. An instrument reports that setup is done; it does not congratulate,
  and [25-content.md](25-content.md) refuses the exclamation mark such copy ends in.
- **One mark, the product's own**, in the header and nowhere else on the screen.

**The dead-end rules**, because a setup screen is the one place a reader can be stuck before the
product has done anything for them:

- **Every task says why it is needed** in its one sentence, before its action. A permission asked
  for with no reason is the one a reader refuses.
- **An optional task can be skipped** with a `quiet` `Skip for now`, it then reads `Skipped`, and
  the settings page reaches it again. A required task says that it is required and why, and has no
  skip.
- **A task blocked outside the product says where to fix it, and notices the fix**: it re-checks
  when the window regains focus, or offers `Check again`. It never asks the reader to restart the
  product.
- **A task that fails says what failed and offers the retry in place**, in the shape
  [25-content.md](25-content.md#errors) gives an error. The reader is never sent back to the first
  task.
- **Setup can always be left.** Quitting or signing out stays reachable, and a reader who comes
  back resumes at the first unfinished task with the finished ones still `Done`.
- **The last task lands on the product's first screen**, the nothing-yet
  [empty state](65-components.md#empty-state) of whatever setup made possible, never a completion
  page with a `Get started` button.

### First run: what the consumer provides

Which tasks exist, which are required and in what order, how each task's completion is detected - a
permission API, a file on disk, a test that passed - and the persistence that lets a reader resume
across launches.

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

## The 404 page

What a reader gets at an address that does not exist. It is the one page every public product ships
without deciding to, so it is usually the framework's default.

Measured on four sites on 2026-09-21, with the status read from
`performance.getEntriesByType('navigation')[0].responseStatus` in a real browser:

| site | status | what the page says | recovery |
|---|---:|---|---|
| `github.com` | 404 | "404", inside an illustration | one search field |
| `stripe.com` | 404 | `Page not found`, 38px/500 | six labelled destinations and a link home |
| `vercel.com` | **200** | `Log in to Vercel`; the address is replaced by `/login?next=...` | none |
| `linear.app` | **200** | `Loading...` for about six seconds, then a sign-in screen | none, 0 links |

### 404: anatomy

| part | token | derivation |
|---|---|---|
| shell | the site header and footer from [37-navigation.md](37-navigation.md), whole | both sites that got this right kept their full chrome, so the reader is still inside the site they meant to reach |
| content column | `--hw-measure-ui`, 56ch, left-aligned with the page margin | a statement and one recovery; nothing here is centred, because unlike the sign-in form it is not the whole screen |
| vertical placement | `--hw-space-96` from the header | the sign-in column's placement |
| heading | `title-1` (28px/600), `Page not found` | the screen's own name, one per screen |
| what happened | one `body` line in `--hw-text-secondary` that names the address asked for, in `--hw-font-mono` | [25-content.md](25-content.md#errors): an error names the value that was wrong |
| the recovery | [the search field](66-forms.md#search) where the product has search; otherwise at most six destinations as list rows | the two measured answers: GitHub's one field, Stripe's six destinations |

### 404: rules

- **The status code is part of the design, and it is 404.** 410 where the page was removed on
  purpose; never 200, and never a redirect to sign-in or to the home page. Two of the four sites
  measured answer 200 at an address that does not exist, so a crawler, a link checker and a
  monitoring probe all record that page as healthy. A 404 page that does not return 404 is not a
  404 page.
- **Behind sign-in, a signed-out request for any address that is not public answers the same way
  whether or not the address exists**: 404, with the sign-in form as the page body. The reset
  screen above says the same thing whether or not an account exists, for the same reason, and the
  status stays true for the probe. This is derived from those two rules, not measured: both sites
  that failed the first rule are the two whose missing address became a sign-in screen at 200.
- **The page says what happened before it says what to do.** GitHub and Stripe name it; Vercel and
  Linear never do. Linear's is the worse, because `Loading...` is a false statement about an
  address that will never load, and [60-states.md](60-states.md#loading-holds-the-width) already
  says what a spinner tells the reader: that the product does not know either.
- **The recovery is the content.** A lone `Go home` button assumes the reader wanted the home page.
- **One `h1`.** Stripe's 404 page declares 25 `h1` elements and no `h2`: the heading, each
  destination title and every navigation group. Here the heading is the only `h1` and each
  destination is a list item.
- **No illustration and no apology.** The one pictogram set in [55-iconography.md](55-iconography.md#illustration-one-pictogram-set-and-no-figurative-drawing)
  is for a nothing-yet empty state and a 404 is not one, and [25-content.md](25-content.md#errors)
  refuses "Oops".

### 404: what the consumer provides

**The status code, which the page cannot set for itself.** A client-routed application whose
server answers every unknown path with its index at 200 has failed the first rule before any of
this page renders, so the server's fallback for an unknown path must answer 404. Also the search,
where the product has one, and the list of destinations.

## The pricing page

The plans a product sells, side by side. A marketing page in the
[form factor](36-form-factors.md#3-the-marketing-or-documentation-page), carrying its own address
rather than being a section inside another page.

Measured on two pages on 2026-09-21 with `getComputedStyle`. They are close to identical everywhere
except one value:

| | `linear.app/pricing` | `vercel.com/pricing` |
|---|---|---|
| columns | 4 | 3 |
| plan name | 24px / 590 | - |
| **the price** | **17px / 510** | **56px / 450 / -0.060em** |
| recommended plan | not marked | an 11px / 500 capitalised word, `Popular`, with no fill, no radius and no padding |
| column separation | - | one `1px rgba(255,255,255,0.14)` rule, no radius, no shadow, the column fill 10/255 above the page |
| the top tier | `Custom`, with `Annual billing only` beside it | `Custom`, at the prices' 56px |

**The price's size is this page's one real decision**: Vercel's is 3.3 times Linear's, on two
products of comparable standing.

### Pricing: the decision

**The price is data, not display type.** `display-1` is one page-defining headline
([20-type.md](20-type.md#the-scale)), and a three-plan page would carry three. A price is a value
the reader compares across columns, which is what [70-data-display.md](70-data-display.md#numeric-formatting)
formats and what `tabular-nums` is for. It therefore sits one step below the plan name, which is
Linear's side of the two measurements: Linear gives the larger step to the plan name, Vercel to
the number.

The one case that reverses it: a page whose whole content is one price. That price is then the
page-defining headline and takes `display-1`.

### Pricing: anatomy

| part | token | derivation |
|---|---|---|
| shell | the site header and footer from [37-navigation.md](37-navigation.md) | a marketing page |
| page heading | `display-1`, the page's one headline | [20-type.md](20-type.md#the-scale) |
| plans | one column each on the twelve-column grid, **at most four**; below `--hw-bp-md` they stack in the same order | Linear four, Vercel three |
| column separation | the plans share one frame on `--hw-surface`, divided by a single `--hw-border` rule; no radius between columns, no shadow | Vercel's hairline and 10/255 fill, which is [separation by geometry](50-surface-texture.md#the-four-ways-a-surface-may-separate) |
| plan name | `title-2` (21px/600) | a section inside a screen |
| the price | `title-3` (17px/600), `tabular-nums`, in the money format of [70-data-display.md](70-data-display.md#numeric-formatting) with the same precision in every column | Linear's 17px |
| the billing period | `body-sm` in `--hw-text-secondary`, beside the price, never in a footnote | Linear prints `Billed yearly` inside each plan's column |
| the recommended plan | one `micro` word in `--hw-text-muted`, above the plan name, with no fill, no radius and no padding | Vercel's 11px `Popular`; `micro` is the house 11px |
| a plan with no number | the word, `Custom`, at the price's step, with its billing constraint beside it | both pages |

### Pricing: rules

- **The recommended plan is marked with a word, never a treatment.** No coloured pill, no taller
  column, no border glow, no shadow and no accent: neither page measured uses any of the four, and
  they are the first four a generated pricing page reaches for.
- **Every figure is real.** A crossed-out "was" price, a seat count or a "most teams choose" line
  is a claim, and [80-anti-patterns.md](80-anti-patterns.md) refuses invented metrics without
  exception.

### Pricing: what the consumer provides

The plans, the prices, the currency, and what each plan actually includes. The system cannot tell
whether a price is per seat or per workspace, and the answer changes the line beside every price.

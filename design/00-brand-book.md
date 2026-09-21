# Halderworks Instrument

The house design system for everything Halderworks ships: quoth, papertrace, pointback, treadling, foliot, gates and the tools around them.
One system, one set of tokens, two themes, two densities.
A product takes its identity from a brand seed of eleven bounded inputs, solved by the same build and certified by the same second instrument ([12-brand.md](12-brand.md)); nothing else is negotiable.

## The rule that matters most

Every value here is a measurement or a decision with a reason attached.
If you need a colour, a size or a duration that is not in this system, you are about to invent one, and inventing one is how a system dies.
Ask for the token instead.

A token with no rationale is the thing this replaces.

## What these products are, and why the system looks like this

Everything in this portfolio is an instrument of record.
quoth captures speech and writes it down. papertrace checks a manuscript's integrity on the author's own machine and reports the evidence rather than a verdict. pointback carries a reviewer's pointing back to an agent. treadling records what an agent was asked to do, did, and decided. foliot orchestrates that work. gates refuses a change that cannot prove itself.

The common job is not to be admired. It is to be trusted about a number, a state or a record.

So the system behaves like a calibrated instrument rather than like a brochure:

- **The house ground is neutral**, because a tinted ground biases every reading placed on it. A brand may warm or cool its own within the bound [12-brand.md](12-brand.md#neutral-hue-and-chroma) measures, and data still never sits on the tint.
- **Colour means something or it is not there.** The loudest control on a screen carries no hue at all.
- **Nothing is decorated to look important.** Weight, size and position carry hierarchy; shadow and colour do not.
- **The type is set to be read for a long time**, not to be photographed once.

Instruments earn trust by being boring in the same way every time.

## How to build with it

Read this file, then [README.md](../README.md), which says which file answers the task in front of you.
Load `tokens/tokens.json` for the values and `tokens/tokens.css` for the compiled custom properties.
Names are prefixed `hw-`, so a token reads `var(--hw-accent)` in any product without colliding with a framework's own variables.

Three rules cover most of what goes wrong:

1. **Never write a literal colour, size, radius, duration, breakpoint or z-index.** If a screen needs a value the system lacks, that is a gap to report, not a number to invent.
2. **Never re-derive a contrast ratio by eye.** Every text token here already clears WCAG AA 4.5:1 against every surface it is allowed to sit on. Put ink only on the grounds [15-color-combinations.md](15-color-combinations.md) permits.
3. **Start from the component card.** A button with the right colours and the wrong padding is still off-system.
4. **Run the checklist at the end of [80-anti-patterns.md](80-anti-patterns.md)** against the screen before you ship it.

## Foundations

| | |
|---|---|
| **Colour** | 33 tokens per theme. Ground and five surfaces, two borders, four text weights including a solved disabled, an ink triple for primary action, four accent tokens, three semantics with their fills, a six-step chart ramp and a scrim. 108 text pairs checked, 0 below AA; 90 non-text pairs at 3:1, 0 below it; 0 outside sRGB. Accent hue 198. |
| **Type** | Public Sans for interface and text, Newsreader for display, IBM Plex Mono for machine output, all self-hosted. A brand may name its own display and text face. Nine distinct sizes. Running text at 56ch in product, 68ch in long-form. |
| **Space** | Base unit 4px, ten steps, 2px for one case only. |
| **Radius** | Three sizes and a pill, each bound to a role, in one of three registers a brand may take. |
| **Elevation** | Border first. Two shadows exist, light-theme only inside a window, and kept in both themes for a panel floating over the user's desktop. |
| **Motion** | 150ms is the default. Four durations, three easings, and a reduced-motion rule that keeps feedback while removing movement. |
| **Layout** | Twelve columns above 1024px, six above 768px, four below. Five breakpoints, three container widths, two page shells. |
| **Density** | Comfortable and compact. One attribute, four tokens, and a written list of what does not change. |
| **Icons** | Lucide, ISC-licensed, 16px default, painted 1.5px stroke at every size, or a brand's 1.75px or 2px. |
| **Brand** | Eleven bounded inputs a product's brand seed may set, solved and certified like the house set. Three product brands, quoth, papertrace and pointback, and three reserved slots. |
| **States** | Nine states for every interactive element, as a matrix. |
| **Forms** | Fourteen controls, the furniture around them, and validation as its own layer. |
| **Form factors** | The app shell, the menu-bar panel, the marketing page and touch, plus what is out of scope and why. |

Each has its own section below this one.

## Writing

The words are part of the system.

- **Name things the way the person names them.** A run, an artifact, a gate, a key. Not a job, a blob, a validator, a credential record.
- **A control says what will happen, and the confirmation says it happened.** "Revoke key", then "Key revoked". Never "Submit" and never "Success!".
- **An error says what went wrong and what to do.** "The signing key expired on 12 March. Generate a new one in Settings, Keys." Not "An error occurred."
- **Numbers carry their unit and their precision.** `04:12`, `$1.84`, `sha256:77c2d4e…`. Never "a few minutes ago" where a timestamp is known.
- **No exclamation marks, and no apologies.** The product is not sorry; it is telling you something.

Say the true thing in the fewest words the reader can act on.

## Iconography

Icons are 16px on a 16px box at a painted 1.5px stroke, drawn on the same 4px grid as everything
else, and they always sit beside a label unless the control is in a toolbar where the label lives
in its tooltip.
Stroke colour is `currentColor` so an icon inherits whatever text token it sits in.
The set is **Lucide**, under the ISC licence; [55-iconography.md](55-iconography.md) says why, and
owns the grid, the stroke arithmetic and the alignment rule.

An icon that needs a legend is a label that should have been written.

## The mark

There is no logomark and no wordmark yet, and none has been drawn here, because a mark is a commission rather than something an agent invents. <!-- covered-by: Logomark and wordmark -->
Until one exists, the name is set plainly in the display face at `display-2` weight 500, as the cover shows; a product's name is set the same way in its brand's display face.

**One mark per screen, and it is the product's own.**
A mark answers whose screen this is, and a screen that answers twice makes the reader choose.
On a product's screen the mark is the product's name, set as above or at the header's `title-3` ([37-navigation.md](37-navigation.md#site-header)), once; the house name, another product's name and an app icon beside the name are not added as further marks.
Checked on the render: count the elements that set a product or house name as a mark or draw a logo, and the count is one.
`halderworks.com` is the registered umbrella domain, and it is a name here rather than a link: its mail resolves, and no web host answers the apex yet.
The visual identity that will sit on it is open work.

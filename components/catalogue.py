"""The component catalogue, the one source for every component sheet.

tools/components.py reads COMPONENTS and GROUPS from this file and writes both the rendered
catalogue pages (components/sheets/<group>.html) and the sheets in design/64-component-sheets.md,
so the words and the render cannot drift apart. A component's token list is not written here: it
is read from the rules in components.css that name the component's classes.

A demo is the live render on the sheet; markup is what a product copies, one (variant, snippet)
pair per variant, using only the classes components.css defines. {{icon:name}} becomes the Lucide
icon from components/icons/ (ISC, LICENSE there) in a demo, and in markup an empty svg naming that
file, so the snippet keeps the icon's box and says which file fills it.
Demo content is real product copy and fixture data, as the review that proposed this layer used.
"""

GROUPS = [
    ("type", "Type styles"),
    ("actions", "Actions"),
    ("inputs", "Inputs"),
    ("feedback", "Feedback and status"),
    ("overlays", "Overlays"),
    ("navigation", "Navigation"),
    ("data", "Data display"),
    ("marks", "Marks, the house signature"),
    ("stage", "Stage"),
]

COMPONENTS = []


def component(group, name, classes, used, purpose, notfor, anatomy, states, keyboard, do, dont,
              demo, markup):
    COMPONENTS.append(dict(group=group, name=name, classes=classes, used=used, purpose=purpose,
                           notfor=notfor, anatomy=anatomy, states=states, keyboard=keyboard, do=do,
                           dont=dont, demo=demo, markup=markup))


# --------------------------------------------------------------------------------------- type
component(
    "type", "Type styles", [".hw-headline", ".hw-title", ".hw-heading", ".hw-subheading", ".hw-lead",
                            ".hw-body", ".hw-small", ".hw-label", ".hw-num"],
    "all four",
    "Sets text on the house type ramp by its job, on any element.",
    "Choosing a heading level: the element says the level, the class says the size.",
    "Headline 3xl/700 in the display face, title 2xl/650, heading xl/650, subheading lg/600, lead lg "
    "in muted, body md, small sm in muted, label xs/550 in muted; lead and body stop at "
    "--hw-measure-prose. hw-num sets tabular figures on any of them. Each zeroes its margins.",
    "static; every size follows html[data-text-size]",
    "Not focusable; a heading class on a real h1 to h6 keeps the outline a screen reader walks.",
    "Put the class on the element whose level is right, and one headline per page.",
    "Use a heading class on a div to fake a heading. Set a size in px beside it.",
    """<p class="hw-headline">Words that land right the first time.</p><p class="hw-title">Settings</p><p class="hw-heading">Dictation</p><p class="hw-subheading">Microphone</p><p class="hw-lead">Dictation that stays on your Mac.</p><p class="hw-body">quoth types what you say into the app in front, and keeps nothing it cannot explain.</p><p class="hw-small">Kept on this Mac for 30 days.</p><p class="hw-label">Microphone</p><p class="hw-body">Cited <span class="hw-num">1,204</span> times, against <span class="hw-num">87</span>.</p>""",
    [("Display, title and headings", """<h1 class="hw-headline">Words that land right the first time.</h1>
<h1 class="hw-title">Settings</h1>
<h2 class="hw-heading">Dictation</h2>
<h3 class="hw-subheading">Microphone</h3>"""),
     ("Running text", """<p class="hw-lead">Dictation that stays on your Mac.</p>
<p class="hw-body">quoth types what you say into the app in front.</p>
<p class="hw-small">Kept on this Mac for 30 days.</p>
<p class="hw-label">Microphone</p>"""),
     ("Tabular figures", """<span class="hw-num">1,204</span>""")])

# ------------------------------------------------------------------------------------ actions
component(
    "actions", "Button", [".hw-btn"],
    "all four",
    "Starts an action whose verb is its label.",
    "Moving to another page (a link); choosing between options (segmented control).",
    "A box at least --hw-control-h tall in three sizes, 12px side padding at M, radius --hw-radius-md, "
    "a 13px label at weight 560, an optional icon at 1.15em with an 8px gap. Variants: secondary (the "
    "default), primary in ink, accent, quiet, danger outlined and danger solid, and icon-only.",
    "rest, hover (fill), active (1px press), focus-visible (2px ring at 2px offset), disabled (fill, "
    "disabled ink, no border), busy (a spinner before the label; still under reduced motion)",
    "A native button: Tab reaches it, Enter and Space press it. An icon-only button carries aria-label.",
    "One primary per view, in ink. Keep the accent variant for a stage or the one brand moment a "
    "product names.",
    "Two primaries side by side. Colour a button to make it louder. Disable a submit because a form "
    "is incomplete.",
    """<div class="row"><button class="hw-btn hw-btn--primary">Agree and finish</button><button class="hw-btn">{{icon:copy}}Copy</button><button class="hw-btn hw-btn--quiet">Cancel</button><button class="hw-btn hw-btn--accent">Download for Mac</button></div>
<div class="row"><button class="hw-btn hw-btn--danger">{{icon:trash-2}}Forget repository</button><button class="hw-btn hw-btn--danger-solid">Delete 412 dictations</button><button class="hw-btn" disabled>Export report</button><button class="hw-btn" aria-busy="true">Checking DOIs</button></div>
<div class="row"><button class="hw-btn hw-btn--sm">Show changes</button><button class="hw-btn">Insert again</button><button class="hw-btn hw-btn--lg hw-btn--primary">Dictate</button><button class="hw-btn hw-btn--icon" aria-label="More actions">{{icon:ellipsis}}</button></div>""",
    [("Secondary, the default", """<button type="button" class="hw-btn">Insert again</button>"""),
     ("With an icon before the label", """<button type="button" class="hw-btn">{{icon:copy}}Copy</button>"""),
     ("Primary, in ink, one per view", """<button type="button" class="hw-btn hw-btn--primary">Agree and finish</button>"""),
     ("Accent, for a stage or the brand moment", """<button type="button" class="hw-btn hw-btn--accent">Download for Mac</button>"""),
     ("Quiet", """<button type="button" class="hw-btn hw-btn--quiet">Cancel</button>"""),
     ("Danger, outlined", """<button type="button" class="hw-btn hw-btn--danger">{{icon:trash-2}}Forget repository</button>"""),
     ("Danger solid, the answer in a destructive dialog", """<button type="button" class="hw-btn hw-btn--danger-solid">Delete 412 dictations</button>"""),
     ("Small and large", """<button type="button" class="hw-btn hw-btn--sm">Show changes</button>
<button type="button" class="hw-btn hw-btn--lg hw-btn--primary">Dictate</button>"""),
     ("Icon only, named by aria-label", """<button type="button" class="hw-btn hw-btn--icon" aria-label="More actions">{{icon:ellipsis}}</button>"""),
     ("Disabled", """<button type="button" class="hw-btn" disabled>Export report</button>"""),
     ("Busy", """<button type="button" class="hw-btn" aria-busy="true">Checking DOIs</button>""")])

component(
    "actions", "Link", [".hw-link"], "the house",
    "Moves the reader somewhere else; underlined, so it never relies on colour.",
    "Starting an action in place (a button).",
    "Inline text in --hw-accent-text with a 1px underline at 0.18em offset, 2px under the pointer. "
    "In print an external link prints its address after it.",
    "rest, hover, focus-visible; visited is left unstyled because tools are revisited",
    "A native anchor: Tab reaches it, Enter follows it.",
    "Write the destination as the link text.",
    "Write 'click here'. Remove the underline in running text.",
    """<p class="hw-body">The report cites <a class="hw-link" href="https://doi.org/10.1038/s41586-019-1666-5">doi:10.1038/s41586-019-1666-5</a>, which resolves to a different title.</p>""",
    [("Inline", """<a class="hw-link" href="https://doi.org/10.1038/s41586-019-1666-5">doi:10.1038/s41586-019-1666-5</a>""")])

component(
    "actions", "Keycap", [".hw-kbd"], "quoth, pointback",
    "Names a key or a shortcut the person presses.",
    "Code (the code mark); a pressable control (a button).",
    "Mono at 0.8em and never under 11px, a 1px --hw-line-strong border with a 2px bottom edge, "
    "radius --hw-radius-sm, on --hw-surface.",
    "static",
    "Not focusable: it names a key, it is not one.",
    "Use the platform's symbols: ⌘ ⌥ ⇧ ⌃.",
    "Spell out 'Cmd'. Use it as a pressable control.",
    """<p class="hw-body">Hold <kbd class="hw-kbd">⌥ Space</kbd> in any app and speak. Let go to type it there. Open History with <kbd class="hw-kbd">⌘2</kbd>.</p>""",
    [("A shortcut", """Open History with <kbd class="hw-kbd">⌘2</kbd>."""),
     ("A chord, one keycap per key", """<kbd class="hw-kbd">⌥</kbd><kbd class="hw-kbd">Space</kbd>""")])

component(
    "actions", "Segmented control", [".hw-segmented"], "the house",
    "Chooses one of two to five mutually exclusive views or values in place.",
    "Moving between pages (tabs, rail); more than five options (select).",
    "A track on --hw-fill with a 2px inset; the selected segment sits on --hw-surface with a 1px "
    "--hw-line-strong edge. Segments wrap rather than overflow at large text sizes.",
    "rest, hover, selected, focus-visible, disabled",
    "A radio group: one Tab stop on the selected segment, arrow keys move the choice, Home and End "
    "jump to the ends, disabled segments are skipped. components/radiogroup.js is the whole script.",
    "Label every segment with a word.",
    "Use icons alone. Animate the selection sliding.",
    """<div class="hw-segmented" role="radiogroup" aria-label="Text size"><button type="button" role="radio" aria-checked="false">S</button><button type="button" role="radio" aria-checked="true">M</button><button type="button" role="radio" aria-checked="false">L</button><button type="button" role="radio" aria-checked="false">XL</button><button type="button" role="radio" aria-checked="false">XXL</button></div>""",
    [("Radio group; load components/radiogroup.js once for its arrow keys", """<div class="hw-segmented" role="radiogroup" aria-label="Text size">
  <button type="button" role="radio" aria-checked="false">S</button>
  <button type="button" role="radio" aria-checked="true">M</button>
  <button type="button" role="radio" aria-checked="false">L</button>
  <button type="button" role="radio" aria-checked="false" disabled>XL</button>
</div>""")])

# ------------------------------------------------------------------------------------- inputs
component(
    "inputs", "Text field", [".hw-field", ".hw-field-label", ".hw-field-hint", ".hw-field-error", ".hw-input"],
    "all four",
    "Takes a short typed value.",
    "Long text (textarea); picking from a known list (select).",
    "A 13px/560 label above at 4px; the box at least --hw-control-h with --hw-field-pad-y and "
    "--hw-field-pad-x inside, a 1px --hw-line-strong edge (3:1), radius --hw-radius-md; a hint or "
    "an error sentence below at 12px.",
    "rest, hover (edge to muted), focus-visible (edge and inset ring), invalid (danger edge plus an "
    "error sentence with an icon), disabled, read-only (dashed edge on --hw-bg-subtle)",
    "Native input; the label is a real label, and the error is tied with aria-describedby.",
    "Say what is wrong and what is expected in the error.",
    "Use the placeholder as the label. Turn the edge red without a sentence.",
    """<div class="grid2"><div class="hw-field"><label class="hw-field-label" for="tf-a">When I say</label><input id="tf-a" class="hw-input" value="priya anka" aria-describedby="tf-a-hint"><span id="tf-a-hint" class="hw-field-hint">Spoken form, lower case</span></div>
<div class="hw-field"><label class="hw-field-label" for="tf-b">Fingerprint</label><input id="tf-b" class="hw-input" aria-invalid="true" aria-describedby="tf-b-err" value="9f2c1a"><span id="tf-b-err" class="hw-field-error">{{icon:circle-alert}}Expected 64 hex characters. That value is 6.</span></div>
<div class="hw-field"><label class="hw-field-label" for="tf-c">Type</label><input id="tf-c" class="hw-input" placeholder="Priyanka"></div>
<div class="hw-field"><label class="hw-field-label" for="tf-d">Model</label><input id="tf-d" class="hw-input" disabled value="Base (English), 148 MB"></div></div>""",
    [("With a hint", """<div class="hw-field">
  <label class="hw-field-label" for="say">When I say</label>
  <input id="say" class="hw-input" aria-describedby="say-hint">
  <span id="say-hint" class="hw-field-hint">Spoken form, lower case</span>
</div>"""),
     ("Invalid, with its sentence", """<div class="hw-field">
  <label class="hw-field-label" for="fp">Fingerprint</label>
  <input id="fp" class="hw-input" aria-invalid="true" aria-describedby="fp-err" value="9f2c1a">
  <span id="fp-err" class="hw-field-error">{{icon:circle-alert}}Expected 64 hex characters. That value is 6.</span>
</div>"""),
     ("Disabled and read-only: the same field, with the attribute on the input", """<input id="model" class="hw-input" disabled value="Base (English), 148 MB">
<input id="path" class="hw-input" readonly value="~/Developer/atlas">""")])

component(
    "inputs", "Textarea", [".hw-textarea"], "pointback",
    "Takes several lines of text.", "One line (text field).",
    "As the text field, at least three lines tall, resizing vertically only.",
    "as the text field",
    "Native textarea; Tab leaves it, so it never traps focus.",
    "Show a count only when there is a limit.", "Grow without a maximum.",
    """<div class="hw-field"><label class="hw-field-label" for="ta-a">Note to the agent</label><textarea id="ta-a" class="hw-textarea">The primary button on checkout sits 4px lower than the secondary; align their baselines.</textarea></div>""",
    [("In a field", """<div class="hw-field">
  <label class="hw-field-label" for="note">Note to the agent</label>
  <textarea id="note" class="hw-textarea"></textarea>
</div>""")])

component(
    "inputs", "Select", [".hw-select"], "quoth",
    "Picks one value from a list the platform can show natively.",
    "Fewer than three options (segmented control).",
    "The text field box with a drawn chevron in --hw-text-muted; the list itself is the platform's.",
    "as the text field",
    "Native select: arrow keys change the value, and the platform's own list opens on Space.",
    "Keep it native: it is accessible for free.", "Rebuild the list in a script to restyle it.",
    """<div class="hw-field narrow"><label class="hw-field-label" for="se-a">Microphone</label><select id="se-a" class="hw-select"><option>MacBook Pro Microphone</option><option>AirPods Pro</option></select></div>""",
    [("In a field", """<div class="hw-field">
  <label class="hw-field-label" for="mic">Microphone</label>
  <select id="mic" class="hw-select">
    <option>MacBook Pro Microphone</option>
    <option>AirPods Pro</option>
  </select>
</div>""")])

component(
    "inputs", "Search field", [".hw-search"], "quoth, papertrace",
    "Filters what is on the screen as the person types.",
    "Submitting a query to a server page (a form).",
    "The text field with a leading magnifier at 1.15em; the label is visually hidden and says what "
    "is searched.",
    "as the text field",
    "Native input of type search; Escape clears it in every engine.",
    "Say what is searched: 'Search your words'.", "Write 'Search...'.",
    """<label class="hw-search narrow"><span class="hw-visually-hidden">Search your words</span>{{icon:search}}<input class="hw-input" type="search" placeholder="Search your words"></label>""",
    [("A visually hidden label, the icon, the input", """<label class="hw-search">
  <span class="hw-visually-hidden">Search your words</span>
  {{icon:search}}
  <input class="hw-input" type="search" placeholder="Search your words">
</label>""")])

component(
    "inputs", "Checkbox and radio", [".hw-check"], "the house",
    "Checkbox: an independent yes or no, or several of a set. Radio: one of a small set, all visible.",
    "A setting that applies at once (switch).",
    "A 1.15em box with a 1px --hw-line-strong edge; checked fills --hw-ink with an --hw-on-ink mark; "
    "the 13px label beside it, and the whole row is the target.",
    "unchecked, checked, indeterminate, focus-visible, disabled; under forced colours the checked box "
    "takes Highlight",
    "Native inputs: Space toggles a checkbox; radios in one name are one Tab stop with arrow keys.",
    "Write the label as the thing that becomes true.",
    "Use a checkbox for a setting that applies at once.",
    """<div class="row"><label class="hw-check"><input type="checkbox" checked>Include figures</label><label class="hw-check"><input type="checkbox">Include supplementary files</label><label class="hw-check"><input type="checkbox" disabled>Include raw data</label></div>
<div class="row" role="radiogroup" aria-label="Export as"><label class="hw-check"><input type="radio" name="cr-fmt" checked>Plain text</label><label class="hw-check"><input type="radio" name="cr-fmt">Markdown</label></div>""",
    [("Checkbox", """<label class="hw-check"><input type="checkbox" checked>Include figures</label>"""),
     ("Disabled", """<label class="hw-check"><input type="checkbox" disabled>Include raw data</label>"""),
     ("Radios, one name, one Tab stop", """<div role="radiogroup" aria-label="Export as">
  <label class="hw-check"><input type="radio" name="export-as" checked>Plain text</label>
  <label class="hw-check"><input type="radio" name="export-as">Markdown</label>
</div>""")])

component(
    "inputs", "Switch", [".hw-switch"], "quoth",
    "Turns a setting on or off, effective at once.", "A choice that waits for a Save (checkbox).",
    "A track 2.13em by 1.2em with the thumb inset; on is --hw-ink. The label sits before it in a "
    "settings row.",
    "off, on, focus-visible, disabled",
    "A native checkbox with role switch: Space toggles it.",
    "Name the setting, not the state.", "Write 'Enabled' as the label.",
    """<div class="stack"><label class="hw-switch">Learn words from the repository in front <input type="checkbox" role="switch" checked></label><label class="hw-switch">Keep recordings when typing fails <input type="checkbox" role="switch"></label></div>""",
    [("On", """<label class="hw-switch">Learn words from the repository in front <input type="checkbox" role="switch" checked></label>"""),
     ("Disabled", """<label class="hw-switch">Keep recordings when typing fails <input type="checkbox" role="switch" disabled></label>""")])

component(
    "inputs", "Slider", [".hw-slider"], "quoth",
    "Sets a value on a continuous range where the exact number matters less than the feel.",
    "A precise number (a text field).",
    "A track 0.27em tall with the ink fill reaching the thumb's centre (the page sets --_p to the "
    "value's fraction of the range), a 1.07em thumb with a 2px ink ring; the value printed beside it.",
    "rest, focus-visible, disabled",
    "Native range input: arrow keys step it, Home and End jump to the ends.",
    "Print the value with its unit.", "Hide the value.",
    """<div class="hw-field narrow"><label class="hw-field-label" for="sl-a">Keep history for <span class="hw-num muted">30 days</span></label><input id="sl-a" class="hw-slider" type="range" min="1" max="90" value="30" style="--_p:0.326"></div>""",
    [("The page sets the fill to (value - min) / (max - min) as the value moves", """<div class="hw-field">
  <label class="hw-field-label" for="keep">Keep history for <span class="hw-num">30 days</span></label>
  <input id="keep" class="hw-slider" type="range" min="1" max="90" value="30" style="--_p:0.326">
</div>""")])

component(
    "inputs", "Hotkey field", [".hw-hotkey"],
    "quoth",
    "Shows the shortcut that starts something, and records a new one when pressed.",
    "Typing text (a text field); naming a key in prose (a keycap).",
    "The text field box as a button, holding the current shortcut as keycaps. While recording it is "
    "pressed, with a focus-coloured inset edge and a muted prompt; a clash shows the field error "
    "below it.",
    "set, recording (aria-pressed), invalid (a clash, with a sentence), disabled",
    "A native button: Enter or Space starts recording, the next chord is taken, Escape cancels. "
    "Capturing the chord is the product's script; this layer draws the states.",
    "Show the shortcut in the platform's symbols, as the menu bar will.",
    "Accept a chord the system already owns without saying so.",
    """<div class="grid2"><div class="hw-field"><span class="hw-field-label" id="hk-a-l">Dictate</span><button type="button" class="hw-hotkey" aria-labelledby="hk-a-l hk-a" id="hk-a"><kbd class="hw-kbd">⌥</kbd><kbd class="hw-kbd">Space</kbd></button></div>
<div class="hw-field"><span class="hw-field-label" id="hk-b-l">Open History</span><button type="button" class="hw-hotkey" aria-pressed="true" aria-labelledby="hk-b-l hk-b" id="hk-b">Press the new shortcut</button></div>
<div class="hw-field"><span class="hw-field-label" id="hk-c-l">Paste last</span><button type="button" class="hw-hotkey" aria-invalid="true" aria-describedby="hk-c-err" aria-labelledby="hk-c-l hk-c" id="hk-c"><kbd class="hw-kbd">⌘</kbd><kbd class="hw-kbd">V</kbd></button><span id="hk-c-err" class="hw-field-error">{{icon:circle-alert}}macOS uses ⌘V for Paste. Choose another.</span></div></div>""",
    [("Set", """<div class="hw-field">
  <span class="hw-field-label" id="dictate-l">Dictate</span>
  <button type="button" class="hw-hotkey" id="dictate" aria-labelledby="dictate-l dictate"><kbd class="hw-kbd">⌥</kbd><kbd class="hw-kbd">Space</kbd></button>
</div>"""),
     ("Recording: the same button, pressed", """<button type="button" class="hw-hotkey" id="dictate" aria-pressed="true" aria-labelledby="dictate-l dictate">Press the new shortcut</button>"""),
     ("A clash: the same button, invalid, with its sentence", """<button type="button" class="hw-hotkey" id="dictate" aria-invalid="true" aria-describedby="dictate-err" aria-labelledby="dictate-l dictate"><kbd class="hw-kbd">⌘</kbd><kbd class="hw-kbd">V</kbd></button>
<span id="dictate-err" class="hw-field-error">{{icon:circle-alert}}macOS uses ⌘V for Paste. Choose another.</span>""")])

# ----------------------------------------------------------------------------------- feedback
component(
    "feedback", "Badge and status", [".hw-badge", ".hw-status"],
    "all four",
    "Badge: a short state word on a row. Status: a dot and a word for a live condition.",
    "Counts on navigation; a state without a word.",
    "Badge: 12px/600 on its state fill with a 0.45em dot, radius --hw-radius-sm; the plain variant "
    "drops the dot. Status: a 0.6em dot in the state's step-9 solid, muted when neutral, the word in "
    "text colour beside it.",
    "neutral, accent, success, warning, danger",
    "Not focusable; the word is the accessible text.",
    "Always a word beside the colour.", "Colour alone. A badge that says 'New'.",
    """<div class="row"><span class="hw-badge hw-badge--success">Verified</span><span class="hw-badge hw-badge--warning">Check</span><span class="hw-badge hw-badge--danger">Retracted</span><span class="hw-badge">Unresolved</span><span class="hw-badge hw-badge--accent">Sent</span><span class="hw-badge hw-badge--plain">Draft</span></div>
<div class="row"><span class="hw-status">Idle</span><span class="hw-status hw-status--ok">Ready</span><span class="hw-status hw-status--warn">Model downloading</span><span class="hw-status hw-status--bad">Microphone off</span></div>""",
    [("Badge, neutral", """<span class="hw-badge">Unresolved</span>"""),
     ("Badge, by state", """<span class="hw-badge hw-badge--success">Verified</span>
<span class="hw-badge hw-badge--warning">Check</span>
<span class="hw-badge hw-badge--danger">Retracted</span>
<span class="hw-badge hw-badge--accent">Sent</span>"""),
     ("Badge without its dot", """<span class="hw-badge hw-badge--plain">Draft</span>"""),
     ("Status, neutral and by state", """<span class="hw-status">Idle</span>
<span class="hw-status hw-status--ok">Ready</span>
<span class="hw-status hw-status--warn">Model downloading</span>
<span class="hw-status hw-status--bad">Microphone off</span>""")])

component(
    "feedback", "Callout", [".hw-callout", ".hw-callout-actions"], "quoth, papertrace",
    "Says one thing the reader must know before acting on this view.",
    "A transient confirmation (toast); an error on one field (field error).",
    "An icon, a bold first phrase, at most three lines, optional actions; the state fill with a 1px "
    "state line on all four sides.",
    "neutral, success, warning, danger",
    "Its actions are ordinary buttons in reading order after the text.",
    "Lead with what happened, then where the work is, then the one action.",
    "A coloured left stripe. More than one callout per view.",
    """<div class="hw-callout hw-callout--danger" role="alert">{{icon:mic-off}}<div><strong>quoth can't hear you.</strong> macOS has the microphone switched off for quoth. Switch it on in System Settings, then come back. Nothing you said was lost.</div><div class="hw-callout-actions"><button class="hw-btn hw-btn--sm hw-btn--primary">Open System Settings</button></div></div>
<div class="hw-callout hw-callout--warning">{{icon:triangle-alert}}<div><strong>3 citations unresolved.</strong> Crossref returned no record for these DOIs; they are listed under Findings with the query that was sent.</div></div>
<div class="hw-callout hw-callout--success">{{icon:check}}<div><strong>All 48 references resolved.</strong> Each DOI returned a record whose title matches the citation.</div></div>
<div class="hw-callout">{{icon:info}}<div><strong>Similarity was not compared.</strong> papertrace checks citations and grammar; it does not search for copied text.</div></div>""",
    [("Neutral", """<div class="hw-callout">
  {{icon:info}}
  <div><strong>Similarity was not compared.</strong> papertrace checks citations and grammar.</div>
</div>"""),
     ("Success, warning and danger: add the modifier and its icon", """<div class="hw-callout hw-callout--success">{{icon:check}}<div><strong>All 48 references resolved.</strong></div></div>
<div class="hw-callout hw-callout--warning">{{icon:triangle-alert}}<div><strong>3 citations unresolved.</strong></div></div>
<div class="hw-callout hw-callout--danger" role="alert">{{icon:mic-off}}<div><strong>quoth can't hear you.</strong></div></div>"""),
     ("With its actions", """<div class="hw-callout hw-callout--danger" role="alert">
  {{icon:mic-off}}
  <div><strong>quoth can't hear you.</strong> Switch the microphone on in System Settings, then come back.</div>
  <div class="hw-callout-actions"><button type="button" class="hw-btn hw-btn--sm hw-btn--primary">Open System Settings</button></div>
</div>""")])

component(
    "feedback", "Toast", [".hw-toast"],
    "quoth, pointback",
    "Confirms an action finished, with an Undo when the action can be undone.",
    "Errors that need action (callout); anything the person must read twice.",
    "An ink surface at radius --hw-radius-lg and at least --hw-row-h tall, 13px text, an optional "
    "outlined action; bottom centre, one at a time, 5 seconds, paused on hover and on focus.",
    "shown, dismissed; the layer draws no entrance or exit motion, and the product's script places, "
    "times and removes it",
    "role status, so it is announced without taking focus; its Undo is reachable by Tab.",
    "Name the result: 'Copied'. Offer Undo for a delete.",
    "Stack three. Put an error in a toast.",
    """<div class="row"><div class="hw-toast" role="status">{{icon:check}}Copied to the clipboard</div><div class="hw-toast" role="status">Repository forgotten <button class="hw-btn hw-btn--sm">Undo</button></div></div>""",
    [("With an icon", """<div class="hw-toast" role="status">{{icon:check}}Copied to the clipboard</div>"""),
     ("With Undo", """<div class="hw-toast" role="status">Repository forgotten <button type="button" class="hw-btn hw-btn--sm">Undo</button></div>""")])

component(
    "feedback", "Progress", [".hw-progress"],
    "quoth, papertrace",
    "Shows how far a known task has gone; indeterminate only when the total is unknown.",
    "A live level (level meter).",
    "A 0.27rem track on --hw-fill-active with an ink fill and full radius; a sentence with the numbers "
    "beside it.",
    "determinate, indeterminate (sweeps; under reduced motion a still full-width bar at 35% opacity)",
    "role progressbar with aria-valuenow, or no value when indeterminate; not focusable.",
    "Print what and how much: '86 of 148 MB'.", "A percentage with no unit of work.",
    """<div class="stack wide"><div class="spread"><span class="hw-small strong" id="pg-a">Downloading the speech model</span><span class="hw-small hw-num">86 of 148 MB</span></div><div class="hw-progress" role="progressbar" aria-labelledby="pg-a" aria-valuenow="58" aria-valuemin="0" aria-valuemax="100"><span style="--_v:58%"></span></div>
<span class="hw-small strong" id="pg-b">Asking Crossref about 3 DOIs</span><div class="hw-progress hw-progress--indeterminate" role="progressbar" aria-labelledby="pg-b"><span></span></div></div>""",
    [("Determinate: the inner span's style sets the filled width", """<span class="hw-small" id="model-dl">Downloading the speech model, 86 of 148 MB</span>
<div class="hw-progress" role="progressbar" aria-labelledby="model-dl" aria-valuenow="58" aria-valuemin="0" aria-valuemax="100"><span style="--_v:58%"></span></div>"""),
     ("Indeterminate", """<span class="hw-small" id="crossref">Asking Crossref about 3 DOIs</span>
<div class="hw-progress hw-progress--indeterminate" role="progressbar" aria-labelledby="crossref"><span></span></div>""")])

component(
    "feedback", "Skeleton", [".hw-skeleton"], "the house",
    "Holds the shape of content that takes more than 300ms to arrive.",
    "Content that loads at once; a spinner in a list.",
    "Bars on --hw-fill-active at text height and the expected width; no shimmer.",
    "static",
    "Hidden from assistive technology; the container says it is busy with aria-busy.",
    "Match the width of what will arrive.", "Shimmer.",
    """<div class="stack wide" aria-busy="true"><span class="hw-skeleton" style="width:70%"></span><span class="hw-skeleton" style="width:92%"></span><span class="hw-skeleton" style="width:40%"></span></div>""",
    [("Bars at the width of what will arrive", """<div aria-busy="true">
  <span class="hw-skeleton" style="width:70%"></span>
  <span class="hw-skeleton" style="width:40%"></span>
</div>""")])

component(
    "feedback", "Level meter", [".hw-meter"],
    "quoth",
    "Shows a live input level; one of the three things in the house that move on their own.",
    "Progress; decoration.",
    "Bars 0.2em wide and 0.13em apart on --hw-fill-active; lit bars take the product's live colour "
    "through --_live, set to its live hue's step 8, a mark at 3:1 (quoth: --_live: var(--hw-live-8)). "
    "Always beside a word.",
    "idle, live (bars follow the input; under reduced motion they still follow it and nothing else "
    "moves)",
    "aria-hidden: the word beside it carries the state.",
    "Pair it with 'Listening'.", "Animate it when no audio arrives.",
    """<div class="row"><span class="hw-meter" style="--_live:var(--hw-live-8)" aria-hidden="true"><i class="on" style="height:30%"></i><i class="on" style="height:55%"></i><i class="on" style="height:85%"></i><i class="on" style="height:60%"></i><i style="height:40%"></i><i style="height:25%"></i></span><span class="hw-small strong">Listening</span></div>""",
    [("Lit bars carry class on; the style names the product's live hue at step 8", """<span class="hw-meter" style="--_live:var(--hw-live-8)" aria-hidden="true"><i class="on" style="height:30%"></i><i class="on" style="height:85%"></i><i style="height:40%"></i></span>
<span class="hw-small">Listening</span>""")])

# ----------------------------------------------------------------------------------- overlays
component(
    "overlays", "Menu", [".hw-menu", ".hw-menu-item", ".hw-menu-key", ".hw-menu-sep", ".hw-menu-label"],
    "quoth, pointback",
    "Lists actions on a thing, opened from a button or a secondary click.",
    "Picking a value (select); navigation (rail).",
    "A raised surface with a 4px inset; items at control height minus 2px with a 1.15em icon and "
    "the shortcut right-aligned in muted; a 1px separator; the destructive item last, in danger.",
    "item rest, active (fill), checked (tick), disabled, destructive",
    "Opened as a popover from its button, so Escape and an outside click close it and focus returns. "
    "Items are buttons in a column: Tab moves through them. Arrow-key roving is the product's.",
    "Put the destructive item last, after a separator.", "Nest more than one level.",
    """<div class="hw-menu" role="menu" aria-label="Dictation"><p class="hw-menu-label hw-label">Microphone</p><button class="hw-menu-item" role="menuitemradio" aria-checked="true">MacBook Pro Microphone</button><button class="hw-menu-item" role="menuitemradio" aria-checked="false">AirPods Pro</button><hr class="hw-menu-sep"><button class="hw-menu-item" role="menuitem" data-active>{{icon:mic-off}}Mute<span class="hw-menu-key">⌥⌘M</span></button><button class="hw-menu-item" role="menuitem">{{icon:history}}Open History<span class="hw-menu-key">⌘2</span></button><button class="hw-menu-item" role="menuitem" disabled>{{icon:copy}}Copy last</button><hr class="hw-menu-sep"><button class="hw-menu-item hw-menu-item--danger" role="menuitem">{{icon:trash-2}}Delete this dictation</button></div>""",
    [("Opened as a popover from its button", """<button type="button" class="hw-btn" popovertarget="dictation-menu">Dictation</button>
<div class="hw-menu" id="dictation-menu" popover role="menu" aria-label="Dictation">
  <p class="hw-menu-label hw-label">Microphone</p>
  <button class="hw-menu-item" role="menuitemradio" aria-checked="true">MacBook Pro Microphone</button>
  <button class="hw-menu-item" role="menuitemradio" aria-checked="false">AirPods Pro</button>
  <hr class="hw-menu-sep">
  <button class="hw-menu-item" role="menuitem">{{icon:history}}Open History<span class="hw-menu-key">⌘2</span></button>
  <button class="hw-menu-item" role="menuitem" disabled>{{icon:copy}}Copy last</button>
  <hr class="hw-menu-sep">
  <button class="hw-menu-item hw-menu-item--danger" role="menuitem">{{icon:trash-2}}Delete this dictation</button>
</div>""")])

component(
    "overlays", "Tooltip", [".hw-tip", ".hw-tooltip"],
    "all four",
    "Names an icon-only control and its shortcut.",
    "Anything the person needs in order to act: it is unreachable on touch.",
    "An ink box, 12px/500, at most 18rem wide, radius --hw-radius-sm, 8px from its control. Wrap the "
    "control in .hw-tip; it shows above, or below with .hw-tip--below.",
    "hidden; shown 500ms after hover or keyboard focus of the control, hidden at once",
    "Shown on focus as well as hover, from CSS alone. The control keeps its own aria-label; the tip "
    "repeats it for sighted readers.",
    "Show it on focus as well as hover.", "Put a sentence of help in it.",
    """<div class="row tall"><span class="hw-tip"><button class="hw-btn hw-btn--icon" aria-label="Copy">{{icon:copy}}</button><span class="hw-tooltip" aria-hidden="true">Copy <kbd class="hw-kbd">⌘C</kbd></span></span><span class="hw-tooltip">Copy <kbd class="hw-kbd">⌘C</kbd></span><span class="hw-small">The second is drawn open, as it shows after the delay.</span></div>""",
    [("Above its control", """<span class="hw-tip">
  <button type="button" class="hw-btn hw-btn--icon" aria-label="Copy">{{icon:copy}}</button>
  <span class="hw-tooltip" aria-hidden="true">Copy <kbd class="hw-kbd">⌘C</kbd></span>
</span>"""),
     ("Below its control", """<span class="hw-tip hw-tip--below">...</span>""")])

component(
    "overlays", "Popover", [".hw-popover"],
    "quoth, pointback",
    "Shows a small panel of detail or controls tied to one thing on screen.",
    "A task with its own flow (dialog).",
    "A raised surface, 16px padding, 20rem wide, --hw-shadow-overlay; opens below its anchor and flips "
    "above or across at the edge, where the engine supports anchor positioning.",
    "closed, open",
    "The popover attribute and popovertarget: no script, Escape and an outside click close it, and "
    "focus returns to the button.",
    "Use the popover attribute so it escapes overflow.",
    "Position it absolutely inside a scrolling list.",
    """<div class="row"><button class="hw-btn" popovertarget="po-live" style="anchor-name:--po-live">Postgres</button></div>
<div class="hw-popover" id="po-live" popover style="position-anchor:--po-live"><p class="hw-subheading">Postgres</p><dl class="hw-kv"><dt>You say</dt><dd>postgres, post gress</dd><dt>quoth types</dt><dd>Postgres</dd><dt>Learned from</dt><dd>~/Developer/atlas</dd></dl><div class="row"><button class="hw-btn hw-btn--sm">Edit</button><button class="hw-btn hw-btn--sm hw-btn--danger">Forget</button></div></div>
<div class="hw-popover"><p class="hw-subheading">Postgres</p><dl class="hw-kv"><dt>You say</dt><dd>postgres, post gress</dd><dt>quoth types</dt><dd>Postgres</dd><dt>Learned from</dt><dd>~/Developer/atlas</dd></dl><div class="row"><button class="hw-btn hw-btn--sm">Edit</button><button class="hw-btn hw-btn--sm hw-btn--danger">Forget</button></div></div>""",
    [("The popover attribute, anchored to its button", """<button type="button" class="hw-btn" popovertarget="term" style="anchor-name:--term">Postgres</button>
<div class="hw-popover" id="term" popover style="position-anchor:--term">
  <p class="hw-subheading">Postgres</p>
  <dl class="hw-kv"><dt>You say</dt><dd>postgres, post gress</dd><dt>quoth types</dt><dd>Postgres</dd></dl>
</div>""")])

component(
    "overlays", "Dialog", [".hw-dialog", ".hw-dialog-actions", ".hw-scrim"], "quoth",
    "Asks for a decision that blocks the task until it is answered.",
    "Information (callout); a confirmation that fits its row (inline confirm).",
    "A raised surface at radius --hw-radius-lg, 24px padding, a 21px title, the body, actions right "
    "with the primary last; the scrim behind.",
    "open (320ms rise, none under reduced motion), closing",
    "A native dialog opened with showModal or a command button: focus moves in, is held there, and "
    "returns on close; Escape closes it.",
    "Write the title as the question and the button as the answer.",
    "'Are you sure?' with OK and Cancel.",
    """<div class="row"><button class="hw-btn hw-btn--danger" commandfor="dl-live" command="show-modal">Delete all dictations</button></div>
<dialog class="hw-dialog" id="dl-live" aria-labelledby="dl-live-t"><h3 id="dl-live-t" class="hw-heading">Delete 412 dictations?</h3><p class="hw-small strong">They are removed from this Mac and cannot be recovered. Vocabulary and settings are kept.</p><div class="hw-dialog-actions"><button class="hw-btn hw-btn--quiet" commandfor="dl-live" command="close" autofocus>Keep them</button><button class="hw-btn hw-btn--danger-solid" commandfor="dl-live" command="close">Delete 412 dictations</button></div></dialog>
<div class="hw-scrim backdrop"><div class="hw-dialog" role="dialog" aria-labelledby="dl-t"><h3 id="dl-t" class="hw-heading">Delete 412 dictations?</h3><p class="hw-small strong">They are removed from this Mac and cannot be recovered. Vocabulary and settings are kept.</p><div class="hw-dialog-actions"><button class="hw-btn hw-btn--quiet">Keep them</button><button class="hw-btn hw-btn--danger-solid">Delete 412 dictations</button></div></div></div>""",
    [("A native dialog, opened by a command button", """<button type="button" class="hw-btn hw-btn--danger" commandfor="delete-all" command="show-modal">Delete all dictations</button>
<dialog class="hw-dialog" id="delete-all" aria-labelledby="delete-all-t">
  <h2 id="delete-all-t" class="hw-heading">Delete 412 dictations?</h2>
  <p class="hw-small">They are removed from this Mac and cannot be recovered.</p>
  <div class="hw-dialog-actions">
    <button type="button" class="hw-btn hw-btn--quiet" commandfor="delete-all" command="close" autofocus>Keep them</button>
    <button type="button" class="hw-btn hw-btn--danger-solid" commandfor="delete-all" command="close">Delete 412 dictations</button>
  </div>
</dialog>"""),
     ("Drawn in the page rather than the top layer, the scrim behind it", """<div class="hw-scrim">
  <div class="hw-dialog" role="dialog" aria-labelledby="delete-t">...</div>
</div>""")])

component(
    "overlays", "Sheet", [".hw-sheet", ".hw-sheet-head"],
    "quoth",
    "Holds a secondary task beside the page it belongs to, such as a setting's detail or a record's "
    "history, without leaving the page.",
    "A decision that blocks (dialog); the app's own navigation (rail).",
    "A dialog anchored to the inline end, full height, 26rem wide at most and the full width below "
    "that, radius --hw-radius-lg on its open edge; a head with the title and a close button, a body "
    "that scrolls, and actions at the foot.",
    "open (slides in over 320ms; appears in place under reduced motion), closing",
    "A native dialog opened modally: focus moves to its first control, is held, and returns on "
    "close; Escape closes it.",
    "Keep the page it belongs to visible behind the scrim.",
    "Open a sheet from a sheet.",
    """<div class="row"><button class="hw-btn" commandfor="sh-live" command="show-modal">Show the vocabulary sheet</button></div>
<dialog class="hw-sheet" id="sh-live" aria-labelledby="sh-live-t"><div class="hw-sheet-head"><h3 id="sh-live-t" class="hw-heading">Postgres</h3><button class="hw-btn hw-btn--quiet hw-btn--icon" commandfor="sh-live" command="close" aria-label="Close">{{icon:x}}</button></div><dl class="hw-kv"><dt>You say</dt><dd>postgres, post gress</dd><dt>quoth types</dt><dd>Postgres</dd><dt>Learned from</dt><dd>~/Developer/atlas</dd><dt>Typed</dt><dd>38 times since 4 September</dd></dl><div class="hw-dialog-actions"><button class="hw-btn hw-btn--danger" commandfor="sh-live" command="close">Forget</button></div></dialog>
<div class="hw-scrim backdrop sheetframe"><div class="hw-sheet" role="dialog" aria-labelledby="sh-t"><div class="hw-sheet-head"><h3 id="sh-t" class="hw-heading">Postgres</h3><button class="hw-btn hw-btn--quiet hw-btn--icon" aria-label="Close">{{icon:x}}</button></div><dl class="hw-kv"><dt>You say</dt><dd>postgres, post gress</dd><dt>quoth types</dt><dd>Postgres</dd><dt>Learned from</dt><dd>~/Developer/atlas</dd><dt>Typed</dt><dd>38 times since 4 September</dd></dl><div class="hw-dialog-actions"><button class="hw-btn hw-btn--danger">Forget</button></div></div></div>""",
    [("A native dialog at the inline end", """<dialog class="hw-sheet" id="term-sheet" aria-labelledby="term-sheet-t">
  <div class="hw-sheet-head">
    <h2 id="term-sheet-t" class="hw-heading">Postgres</h2>
    <button type="button" class="hw-btn hw-btn--quiet hw-btn--icon" commandfor="term-sheet" command="close" aria-label="Close">{{icon:x}}</button>
  </div>
  <dl class="hw-kv"><dt>You say</dt><dd>postgres, post gress</dd></dl>
  <div class="hw-dialog-actions"><button type="button" class="hw-btn hw-btn--danger" commandfor="term-sheet" command="close">Forget</button></div>
</dialog>""")])

component(
    "overlays", "Inline confirm", [".hw-confirm", ".hw-confirm-actions"], "quoth",
    "Confirms a destructive action on one row without leaving it.",
    "Bulk or irreversible deletes of many things (dialog).",
    "Replaces the row's actions at the row's height: a sentence, the danger button, Cancel. It wraps "
    "rather than overflows at large text sizes.",
    "open; it never times out",
    "Focus moves to Cancel when it opens and returns to the row's action when it closes.",
    "Repeat the verb on the button.", "Time it out.",
    """<div class="hw-confirm"><span>Forget the 400 words learned from <b>quoth</b>?</span><div class="hw-confirm-actions"><button class="hw-btn hw-btn--sm hw-btn--danger">Forget</button><button class="hw-btn hw-btn--sm hw-btn--quiet">Cancel</button></div></div>""",
    [("In place of the row's actions", """<div class="hw-confirm">
  <span>Forget the 400 words learned from <b>quoth</b>?</span>
  <div class="hw-confirm-actions">
    <button type="button" class="hw-btn hw-btn--sm hw-btn--danger">Forget</button>
    <button type="button" class="hw-btn hw-btn--sm hw-btn--quiet">Cancel</button>
  </div>
</div>""")])

# --------------------------------------------------------------------------------- navigation
component(
    "navigation", "Rail and navigation item", [".hw-rail", ".hw-nav-item", ".hw-nav-key"],
    "quoth",
    "Moves between the four to six places of an app.",
    "Actions (buttons); sections within a page (tabs).",
    "The rail on --hw-bg-subtle; items at control height with a 1.15em icon, a 13px label and the "
    "shortcut right; the current item sits on --hw-surface with a 1px --hw-line-strong edge.",
    "rest, hover, current (aria-current page), focus-visible",
    "Links in a nav landmark, in order; the shortcut is the product's.",
    "Show the shortcut beside each item.", "Badges or counts on the rail.",
    """<nav class="hw-rail framed" aria-label="quoth"><a class="hw-nav-item" href="#today">{{icon:sun}}Today<span class="hw-nav-key">⌘1</span></a><a class="hw-nav-item" aria-current="page" href="#history">{{icon:history}}History<span class="hw-nav-key">⌘2</span></a><a class="hw-nav-item" href="#vocabulary">{{icon:book-open}}Vocabulary<span class="hw-nav-key">⌘3</span></a><a class="hw-nav-item" href="#insights">{{icon:chart-no-axes-column}}Insights<span class="hw-nav-key">⌘4</span></a></nav>""",
    [("The current item carries aria-current", """<nav class="hw-rail" aria-label="quoth">
  <a class="hw-nav-item" href="/today">{{icon:sun}}Today<span class="hw-nav-key">⌘1</span></a>
  <a class="hw-nav-item" href="/history" aria-current="page">{{icon:history}}History<span class="hw-nav-key">⌘2</span></a>
</nav>""")])

component(
    "navigation", "Tabs", [".hw-tabs", ".hw-tab", ".hw-tab-count"],
    "papertrace, pointback",
    "Switches between views of the same thing.",
    "Moving between places (rail); filtering (segmented control).",
    "13px labels 16px apart on a 1px line, each at control height; the active tab has a 2px rule in "
    "--hw-text and weight 620; a count may follow in muted. Tabs wrap at large text sizes.",
    "rest, hover, selected, focus-visible",
    "The layer styles role tab; the product owns the panels and the arrow-key roving between tabs, "
    "since the panels are its own.",
    "Keep to three to six.", "Colour the active tab.",
    """<div class="hw-tabs" role="tablist" aria-label="Report"><button class="hw-tab" role="tab" aria-selected="true">Findings<span class="hw-tab-count">7</span></button><button class="hw-tab" role="tab" aria-selected="false" tabindex="-1">References<span class="hw-tab-count">48</span></button><button class="hw-tab" role="tab" aria-selected="false" tabindex="-1">Figures<span class="hw-tab-count">12</span></button><button class="hw-tab" role="tab" aria-selected="false" tabindex="-1">Run log</button></div>""",
    [("The selected tab, a count, the rest out of the Tab order", """<div class="hw-tabs" role="tablist" aria-label="Report">
  <button class="hw-tab" role="tab" aria-selected="true">Findings<span class="hw-tab-count">7</span></button>
  <button class="hw-tab" role="tab" aria-selected="false" tabindex="-1">References<span class="hw-tab-count">48</span></button>
  <button class="hw-tab" role="tab" aria-selected="false" tabindex="-1">Run log</button>
</div>""")])

component(
    "navigation", "Toolbar", [".hw-toolbar", ".hw-toolbar-sep"], "the house",
    "Groups the actions for the current view.", "Navigation.",
    "A row of controls 8px apart within a group, a further 8px spacer between groups; it wraps "
    "rather than clips, and its overflow goes into a menu.",
    "as its buttons",
    "role toolbar with an aria-label; its buttons are Tab stops in order.",
    "Order by frequency.", "Icon-only buttons without tooltips.",
    """<div class="hw-toolbar" role="toolbar" aria-label="Dictation"><button class="hw-btn hw-btn--sm">{{icon:copy}}Copy</button><button class="hw-btn hw-btn--sm">Insert again</button><span class="hw-toolbar-sep"></span><button class="hw-btn hw-btn--sm hw-btn--quiet">{{icon:pencil}}Edit</button><span class="hw-tip"><button class="hw-btn hw-btn--sm hw-btn--icon" aria-label="More actions">{{icon:ellipsis}}</button><span class="hw-tooltip" aria-hidden="true">More actions</span></span></div>""",
    [("Two groups, the spacer between them", """<div class="hw-toolbar" role="toolbar" aria-label="Dictation">
  <button type="button" class="hw-btn hw-btn--sm">{{icon:copy}}Copy</button>
  <button type="button" class="hw-btn hw-btn--sm">Insert again</button>
  <span class="hw-toolbar-sep"></span>
  <button type="button" class="hw-btn hw-btn--sm hw-btn--quiet">{{icon:pencil}}Edit</button>
</div>""")])

# ------------------------------------------------------------------------------- data display
component(
    "data", "List row", [".hw-list", ".hw-row", ".hw-row-meta", ".hw-row-actions"],
    "quoth, pointback",
    "One record in a list scanned for a single subject.",
    "Comparing values across records (table).",
    "A grid of time, content and source; --hw-cell-pad-y and 12px padding; a 1px --hw-line between "
    "rows; at least --hw-row-h tall; a selected row becomes a bordered surface holding its actions.",
    "rest, hover, selected (expanded), focus-visible",
    "The row's own control, usually its content as a button, is the Tab stop; its actions follow it "
    "only when it is selected.",
    "Show actions on the selected row only.", "A card per row; four icon buttons on every row.",
    """<ul class="hw-list"><li class="hw-row"><span class="hw-row-meta">12:30 pm</span><p>Call <code class="hw-code">getUserName</code></p><span class="hw-row-meta">VS Code</span></li><li class="hw-row" aria-selected="true"><span class="hw-row-meta">10:41 am</span><p>Deploy to <span class="hw-mark">K8s</span> cluster</p><span class="hw-row-meta">Linear</span><div class="hw-row-actions"><button class="hw-btn hw-btn--sm">{{icon:copy}}Copy</button><button class="hw-btn hw-btn--sm">Insert again</button><button class="hw-btn hw-btn--sm hw-btn--quiet hw-btn--danger">Delete</button></div></li><li class="hw-row"><span class="hw-row-meta">9:02 am</span><p>Ship it.</p><span class="hw-row-meta">Slack</span></li></ul>""",
    [("A row, and a selected row holding its actions", """<ul class="hw-list">
  <li class="hw-row"><span class="hw-row-meta">12:30 pm</span><p>Call getUserName</p><span class="hw-row-meta">VS Code</span></li>
  <li class="hw-row" aria-selected="true">
    <span class="hw-row-meta">10:41 am</span><p>Deploy to K8s cluster</p><span class="hw-row-meta">Linear</span>
    <div class="hw-row-actions"><button type="button" class="hw-btn hw-btn--sm">{{icon:copy}}Copy</button></div>
  </li>
</ul>""")])

component(
    "data", "Table", [".hw-table"], "papertrace",
    "Compares values across records.", "Scanning for one subject (list row).",
    "A 12px/560 muted head over a 1px --hw-line-strong rule; 13px cells with 12px side padding; "
    "numbers right-aligned and tabular; no zebra, no vertical rules.",
    "rest, hover, sorted (head in text colour, aria-sort), selected (accent fill)",
    "A native table; a sortable head is a button inside the th.",
    "Right-align numbers with tabular figures.", "Centre text columns.",
    """<div class="scroll"><table class="hw-table"><thead><tr><th scope="col">Reference</th><th scope="col">Status</th><th scope="col" class="num" aria-sort="descending">Year</th><th scope="col" class="num">Citations</th></tr></thead><tbody><tr><td>Hwang, Nature 579</td><td><span class="hw-badge hw-badge--danger">Retracted</span></td><td class="num">2020</td><td class="num">1,204</td></tr><tr aria-selected="true"><td>doi:10.1101/2020.03.12</td><td><span class="hw-badge hw-badge--warning">Preprint</span></td><td class="num">2020</td><td class="num">12</td></tr><tr><td>Smith, Cell Rep 31</td><td><span class="hw-badge hw-badge--success">Verified</span></td><td class="num">2019</td><td class="num">87</td></tr></tbody></table></div>""",
    [("Numbers in class num; the sorted head carries aria-sort", """<table class="hw-table">
  <thead><tr><th scope="col">Reference</th><th scope="col" class="num" aria-sort="descending">Year</th></tr></thead>
  <tbody>
    <tr><td>Hwang, Nature 579</td><td class="num">2020</td></tr>
    <tr aria-selected="true"><td>Smith, Cell Rep 31</td><td class="num">2019</td></tr>
  </tbody>
</table>""")])

component(
    "data", "Key-value list", [".hw-kv"], "all four",
    "Shows the properties of one thing.", "Many things (table).",
    "Two columns, keys muted at 13px and values in text; an 8px row gap and a 24px column gap; it "
    "stacks in a container narrower than 30rem.",
    "set, missing (the value reads 'Not set')",
    "A native description list; not focusable.",
    "Write units into the value.", "An empty dash for a missing value.",
    """<dl class="hw-kv"><dt>Model</dt><dd>Base (English), 148 MB</dd><dt>Runs on</dt><dd>This Mac, no network</dd><dt>History kept</dt><dd>30 days</dd><dt>Licence</dt><dd>Not set</dd></dl>""",
    [("A description list", """<dl class="hw-kv">
  <dt>Model</dt><dd>Base (English), 148 MB</dd>
  <dt>Licence</dt><dd>Not set</dd>
</dl>""")])

component(
    "data", "Empty state", [".hw-empty"], "quoth, pointback",
    "Says what will appear here and how to make it appear.", "An error (callout).",
    "A 2.67rem glyph in muted, a 17px sentence, a 13px line with the key or the action; aligned with "
    "the content column.",
    "nothing yet, nothing found, nothing permitted",
    "Its one action, when it has one, is the first Tab stop in the container.",
    "Teach the one action.", "A mascot. 'No data'.",
    """<div class="hw-empty">{{icon:quote}}<p class="hw-subheading">Nothing said yet.</p><p class="hw-small">Hold <kbd class="hw-kbd">⌥ Space</kbd> in any app and speak. What you say is kept here, on this Mac, for 30 days.</p></div>""",
    [("Glyph, sentence, the one action", """<div class="hw-empty">
  {{icon:quote}}
  <p class="hw-subheading">Nothing said yet.</p>
  <p class="hw-small">Hold <kbd class="hw-kbd">⌥ Space</kbd> in any app and speak.</p>
</div>""")])

component(
    "data", "Stat", [".hw-stat", ".hw-stat-value"], "quoth, papertrace",
    "A number the person comes back to check.", "Decoration on a dashboard.",
    "The value at 21px/650 in tabular figures, the label at 12px muted under it, the unit in the value.",
    "static",
    "Not focusable; the label follows the value in reading order.",
    "Say over what period or of what.", "The hero-metric template with a gradient.",
    """<div class="row gap-lg"><div class="hw-stat"><span class="hw-stat-value">162</span><span class="hw-label">words, planted-errors.txt</span></div><div class="hw-stat"><span class="hw-stat-value">21</span><span class="hw-label">grammar findings</span></div><div class="hw-stat"><span class="hw-stat-value">8.32</span><span class="hw-label">Flesch-Kincaid grade</span></div></div>""",
    [("Value, then label", """<div class="hw-stat"><span class="hw-stat-value">162</span><span class="hw-label">words, planted-errors.txt</span></div>""")])

component(
    "data", "Tag", [".hw-tag"], "quoth",
    "A word or short value from a set, often the product's own vocabulary.", "A state (badge).",
    "An inline box at least 1.6rem tall, 13px/500, on --hw-mark-quiet, radius --hw-radius-sm; a "
    "removable tag ends in a small button.",
    "rest, removable",
    "Only the remove button is a Tab stop, named 'Remove' and the word.",
    "Show the real word as the product will type it.", "Colour-code tags by category.",
    """<div class="row"><span class="hw-tag">parseHeader</span><span class="hw-tag">whisper.cpp</span><span class="hw-tag">Tauri</span><span class="hw-tag">TranscriptStore<button aria-label="Remove TranscriptStore">{{icon:x}}</button></span><span class="hw-tag">SQLCipher</span><span class="hw-small">and 394 more</span></div>""",
    [("Plain", """<span class="hw-tag">whisper.cpp</span>"""),
     ("Removable", """<span class="hw-tag">TranscriptStore<button type="button" aria-label="Remove TranscriptStore">{{icon:x}}</button></span>""")])

component(
    "data", "Disclosure", [".hw-disclosure"], "papertrace",
    "Hides detail most readers do not need.", "Primary content.",
    "A summary row at --hw-row-h with a chevron that turns in 120ms; the content below.",
    "closed, open, focus-visible",
    "A native details element: Enter or Space on the summary opens it.",
    "Write the summary as what is inside.", "Nest them.",
    """<details class="hw-disclosure" open><summary>Why this reference was flagged</summary><p class="hw-small strong">Retraction Watch lists DOI 10.1038/s41586-020-2012-7 as retracted on 2020-11-06. The manuscript cites it in section 2.1 without noting the retraction.</p></details>""",
    [("A details element", """<details class="hw-disclosure">
  <summary>Why this reference was flagged</summary>
  <p class="hw-small">Retraction Watch lists it as retracted on 2020-11-06.</p>
</details>""")])

component(
    "data", "Avatar", [".hw-avatar", ".hw-avatar-group"],
    "pointback",
    "Stands for a person beside what they did: who left a note, who sent a review.",
    "A product mark; decoration.",
    "A circle at --hw-radius-full in three sizes (1.6, 1.87 and 2.67rem), initials at 40% of its "
    "size on --hw-fill-active, never under 11px; an image covers the initials once it loads; a group "
    "overlaps by 0.4rem with a 2px ring in --hw-surface.",
    "initials, image, group",
    "Not focusable; the image's alt or an aria-label carries the name, and a group's count is text.",
    "Keep the initials under the image, so a failed load still names the person.",
    "Stack more than four; say '+3' as text after them.",
    """<div class="row"><span class="hw-avatar hw-avatar--sm" role="img" aria-label="Mira Shah">MS</span><span class="hw-avatar" role="img" aria-label="Priyanka Rao">PR</span><span class="hw-avatar hw-avatar--lg" role="img" aria-label="Reviewer">{{icon:user}}</span><span class="hw-avatar-group"><span class="hw-avatar" role="img" aria-label="Mira Shah">MS</span><span class="hw-avatar" role="img" aria-label="Priyanka Rao">PR</span><span class="hw-avatar" role="img" aria-label="Sam Lee">SL</span></span><span class="hw-small">and 3 more</span></div>""",
    [("Initials, in three sizes", """<span class="hw-avatar hw-avatar--sm" role="img" aria-label="Mira Shah">MS</span>
<span class="hw-avatar" role="img" aria-label="Priyanka Rao">PR</span>
<span class="hw-avatar hw-avatar--lg" role="img" aria-label="Sam Lee">SL</span>"""),
     ("An image over the initials", """<span class="hw-avatar" role="img" aria-label="Mira Shah">MS<img src="mira.jpg" alt=""></span>"""),
     ("A group, the count as text after it", """<span class="hw-avatar-group">
  <span class="hw-avatar" role="img" aria-label="Mira Shah">MS</span>
  <span class="hw-avatar" role="img" aria-label="Priyanka Rao">PR</span>
</span>
<span class="hw-small">and 3 more</span>""")])

# ------------------------------------------------------------------------------------- marks
component(
    "marks", "Highlight", [".hw-mark"],
    "all three apps",
    "Marks the words a product knows, matched or pointed at.",
    "Emphasis in prose (use weight); a state.",
    "Light: a highlighter swipe from 44% to 90% of the line box in --hw-mark, the text left in ink. "
    "Dark: a block in mark step 7 with the text in --hw-text, since a swipe under light text measured "
    "1.15:1; the bright solid (.hw-mark--solid) is kept for the one selected word.",
    "rest, solid (the selected word), quiet (--hw-mark-quiet, for dense lists)",
    "Not focusable unless the product makes the word a button that explains the mark.",
    "Mark only what the product can explain on click.",
    "Highlight a whole paragraph. Use it as the selection colour.",
    """<p class="hw-body large">We deploy with <span class="hw-mark">Kubernetes</span> and <span class="hw-mark">Postgres</span>, and <span class="hw-mark hw-mark--solid">pgvector</span> is the word selected.</p><p class="hw-small">quoth: the words its dictionary knows. papertrace: the passage matched elsewhere. pointback: the text the reviewer selected. Quiet: <span class="hw-mark hw-mark--quiet">TranscriptStore</span>.</p>""",
    [("A known word", """<span class="hw-mark">Kubernetes</span>"""),
     ("The selected word", """<span class="hw-mark hw-mark--solid">pgvector</span>"""),
     ("Quiet, for dense lists", """<span class="hw-mark hw-mark--quiet">TranscriptStore</span>""")])

component(
    "marks", "Proof marks", [".hw-proof", ".hw-ins", ".hw-del", ".hw-caret"],
    "quoth",
    "Shows what a product changed in someone's words, the way an editor marks a page.",
    "Code changes (diff).",
    "The original words in muted; removed words struck through in --hw-delete; inserted text in "
    "--hw-insert, bold, on its fill, with a caret under the line at the point of insertion.",
    "static",
    "Use ins and del elements, so the change is announced as well as drawn.",
    "Show the person's own words, then the result.",
    "Rely on colour alone: the strike and the caret carry it.",
    """<p class="hw-proof"><del class="hw-del">fix the bug</del> <del class="hw-del">scratch that</del> refactor the parser<span class="hw-caret"></span><ins class="hw-ins">.</ins> <del class="hw-del">period new line</del> ship it<span class="hw-caret"></span><ins class="hw-ins">.</ins></p><p class="hw-body">Refactor the parser.<br>Ship it.</p>""",
    [("Struck words, then the caret and the insertion", """<p class="hw-proof"><del class="hw-del">scratch that</del> refactor the parser<span class="hw-caret"></span><ins class="hw-ins">.</ins></p>""")])

component(
    "marks", "Diff", [".hw-diff"], "pointback, papertrace",
    "Shows changed lines of code or text with their context.",
    "Changes inside prose (proof marks).",
    "Mono 13px, a line per row; added rows on --hw-insert-fill with a + in --hw-insert, removed rows "
    "on --hw-delete-fill with a minus in --hw-delete; the text stays ink. It scrolls sideways rather "
    "than overflow its box.",
    "static",
    "Not focusable unless it scrolls; the signs are text, so a screen reader reads them.",
    "Keep the text in ink; the fill and the sign carry the change.",
    "Colour the text green and red.",
    """<div class="hw-diff"><div class="ctx">.checkout-actions {</div><div class="rem">  align-items: center;</div><div class="add">  align-items: baseline;</div><div class="ctx">  gap: 12px;</div><div class="ctx">}</div></div>""",
    [("One div per line: ctx, rem or add", """<div class="hw-diff">
  <div class="ctx">.checkout-actions {</div>
  <div class="rem">  align-items: center;</div>
  <div class="add">  align-items: baseline;</div>
  <div class="ctx">}</div>
</div>""")])

component(
    "marks", "Pin and margin note", [".hw-pin", ".hw-note", ".hw-note-locator"],
    "pointback",
    "Points at a place on a page and carries a note back.", "Decoration.",
    "A 1.6rem teardrop in the product's solid with its number; the note is a card beside it with the "
    "selector in mono, truncated to one line.",
    "placed, sent, resolved",
    "The note is the Tab stop; the pin is its label, read with it.",
    "Number pins in the order they were made.", "Hide the number.",
    """<div class="row top"><span class="hw-pin" aria-hidden="true">3</span><div class="hw-note"><p class="hw-small strong">The primary button sits 4px lower than Cancel.</p><code class="hw-code hw-note-locator">main &gt; .checkout-actions &gt; button.primary</code></div></div>""",
    [("The pin beside its note", """<span class="hw-pin" aria-hidden="true">3</span>
<div class="hw-note">
  <p class="hw-small">The primary button sits 4px lower than Cancel.</p>
  <code class="hw-code hw-note-locator">main &gt; .checkout-actions &gt; button.primary</code>
</div>""")])

component(
    "marks", "Code", [".hw-code"], "all four",
    "Inline code, identifiers and commands as typed.", "Keys (keycap).",
    "Mono at 0.92em on --hw-fill, radius --hw-radius-sm; a block is 13px with 8px and 12px padding "
    "and scrolls sideways.",
    "static",
    "A code element; a block that scrolls is focusable so the keyboard can scroll it.",
    "Show the identifier exactly as it is written.", "Syntax-colour a one-line command.",
    """<p class="hw-body">Call <code class="hw-code">getUserName</code>, then run <code class="hw-code">cargo build --release</code>.</p><pre class="hw-code" tabindex="0">python3 tools/components.py --check</pre>""",
    [("Inline", """<code class="hw-code">getUserName</code>"""),
     ("A block, focusable so it scrolls by keyboard", """<pre class="hw-code" tabindex="0">python3 tools/components.py --check</pre>""")])

# ------------------------------------------------------------------------------------- stage
component(
    "stage", "Stage", [".hw-stage"],
    "site, store frames",
    "The one loud surface a product may have: a welcome, a site section, a store frame, an empty "
    "state at most once.",
    "Any working view: lists, settings, reports. quoth's welcome, which stays on paper.",
    "A full field in the highlighter solid, the product's accent or ink, radius --hw-radius-lg or "
    "full bleed, display type at the stage sizes, at most one action and one drawing.",
    "static; one entry moment, none under reduced motion",
    "Its one action is an ordinary button or link; the focus ring takes the stage's own text colour.",
    "Put the person's real words or the product's real output on it.",
    "Gradients, glow, sparkles, a stock illustration.",
    """<div class="hw-stage"><p class="hw-label">quoth</p><p class="hw-headline">Words that land right the first time.</p><p class="hw-lead">Dictation that stays on your Mac.</p></div>
<div class="hw-stage hw-stage--ink"><p class="hw-label">quoth</p><p class="hw-headline">Dictation that stays on your Mac.</p><a class="hw-link" href="#stage">Download for Mac</a></div>
<div class="hw-stage hw-stage--accent"><p class="hw-label">quoth</p><p class="hw-headline">Words that land right the first time.</p></div>""",
    [("On the highlighter solid, the default", """<section class="hw-stage">
  <p class="hw-label">quoth</p>
  <h2 class="hw-headline">Words that land right the first time.</h2>
  <p class="hw-lead">Dictation that stays on your Mac.</p>
</section>"""),
     ("On ink, or on the product's accent", """<section class="hw-stage hw-stage--ink">...</section>
<section class="hw-stage hw-stage--accent">...</section>""")])

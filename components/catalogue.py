"""The component catalogue, the one source for every component sheet.

tools/components.py reads COMPONENTS and GROUPS from this file and writes both the rendered
catalogue pages (components/sheets/<group>.html) and the sheets in design/64-component-sheets.md,
so the words and the render cannot drift apart. A component's token list is not written here: it
is read from the rules in components.css that name the component's classes.

{{icon:name}} in a demo is replaced by the Lucide icon in components/icons/ (ISC, LICENSE there).
Demo content is real product copy and fixture data, as the review that proposed this layer used.
"""

GROUPS = [
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


def component(group, name, classes, verdict, used, purpose, notfor, anatomy, states, keyboard, do,
              dont, demo):
    COMPONENTS.append(dict(group=group, name=name, classes=classes, verdict=verdict, used=used,
                           purpose=purpose, notfor=notfor, anatomy=anatomy, states=states,
                           keyboard=keyboard, do=do, dont=dont, demo=demo))


# ------------------------------------------------------------------------------------ actions
component(
    "actions", "Button", [".hw-btn"],
    "rework: rem sizing, accent variant added, padding derived from height", "all four",
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
<div class="row"><button class="hw-btn hw-btn--sm">Show changes</button><button class="hw-btn">Insert again</button><button class="hw-btn hw-btn--lg hw-btn--primary">Dictate</button><button class="hw-btn hw-btn--icon" aria-label="More actions">{{icon:ellipsis}}</button></div>""")

component(
    "actions", "Link", [".hw-link"], "keep", "the house",
    "Moves the reader somewhere else; underlined, so it never relies on colour.",
    "Starting an action in place (a button).",
    "Inline text in --hw-accent-text with a 1px underline at 0.18em offset, 2px under the pointer. "
    "In print an external link prints its address after it.",
    "rest, hover, focus-visible; visited is left unstyled because tools are revisited",
    "A native anchor: Tab reaches it, Enter follows it.",
    "Write the destination as the link text.",
    "Write 'click here'. Remove the underline in running text.",
    """<p class="hw-body">The report cites <a class="hw-link" href="https://doi.org/10.1038/s41586-019-1666-5">doi:10.1038/s41586-019-1666-5</a>, which resolves to a different title.</p>""")

component(
    "actions", "Keycap", [".hw-kbd"], "new: quoth hand-rolls it; the house had no entry",
    "quoth, pointback",
    "Names a key or a shortcut the person presses.",
    "Code (the code mark); a pressable control (a button).",
    "Mono at 0.8em and never under 11px, a 1px --hw-line-strong border with a 2px bottom edge, "
    "radius --hw-radius-sm, on --hw-surface.",
    "static",
    "Not focusable: it names a key, it is not one.",
    "Use the platform's symbols: ⌘ ⌥ ⇧ ⌃.",
    "Spell out 'Cmd'. Use it as a pressable control.",
    """<p class="hw-body">Hold <kbd class="hw-kbd">⌥ Space</kbd> in any app and speak. Let go to type it there. Open History with <kbd class="hw-kbd">⌘2</kbd>.</p>""")

component(
    "actions", "Segmented control", [".hw-segmented"], "keep anatomy, rem sizing", "the house",
    "Chooses one of two to five mutually exclusive views or values in place.",
    "Moving between pages (tabs, rail); more than five options (select).",
    "A track on --hw-fill with a 2px inset; the selected segment sits on --hw-surface with a 1px "
    "--hw-line-strong edge. Segments wrap rather than overflow at large text sizes.",
    "rest, hover, selected, focus-visible, disabled",
    "A radio group: one Tab stop on the selected segment, arrow keys move the choice, Home and End "
    "jump to the ends, disabled segments are skipped. components/radiogroup.js is the whole script.",
    "Label every segment with a word.",
    "Use icons alone. Animate the selection sliding.",
    """<div class="hw-segmented" role="radiogroup" aria-label="Text size"><button type="button" role="radio" aria-checked="false">S</button><button type="button" role="radio" aria-checked="true">M</button><button type="button" role="radio" aria-checked="false">L</button><button type="button" role="radio" aria-checked="false">XL</button><button type="button" role="radio" aria-checked="false">XXL</button></div>""")

# ------------------------------------------------------------------------------------- inputs
component(
    "inputs", "Text field", [".hw-field", ".hw-field-label", ".hw-field-hint", ".hw-field-error", ".hw-input"],
    "rework: hint and error under the field, rem height", "all four",
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
<div class="hw-field"><label class="hw-field-label" for="tf-d">Model</label><input id="tf-d" class="hw-input" disabled value="Base (English), 148 MB"></div></div>""")

component(
    "inputs", "Textarea", [".hw-textarea"], "keep", "pointback",
    "Takes several lines of text.", "One line (text field).",
    "As the text field, at least three lines tall, resizing vertically only.",
    "as the text field",
    "Native textarea; Tab leaves it, so it never traps focus.",
    "Show a count only when there is a limit.", "Grow without a maximum.",
    """<div class="hw-field"><label class="hw-field-label" for="ta-a">Note to the agent</label><textarea id="ta-a" class="hw-textarea">The primary button on checkout sits 4px lower than the secondary; align their baselines.</textarea></div>""")

component(
    "inputs", "Select", [".hw-select"], "keep: native by default", "quoth",
    "Picks one value from a list the platform can show natively.",
    "Fewer than three options (segmented control).",
    "The text field box with a drawn chevron in --hw-text-muted; the list itself is the platform's.",
    "as the text field",
    "Native select: arrow keys change the value, and the platform's own list opens on Space.",
    "Keep it native: it is accessible for free.", "Rebuild the list in a script to restyle it.",
    """<div class="hw-field narrow"><label class="hw-field-label" for="se-a">Microphone</label><select id="se-a" class="hw-select"><option>MacBook Pro Microphone</option><option>AirPods Pro</option></select></div>""")

component(
    "inputs", "Search field", [".hw-search"], "keep", "quoth, papertrace",
    "Filters what is on the screen as the person types.",
    "Submitting a query to a server page (a form).",
    "The text field with a leading magnifier at 1.15em; the label is visually hidden and says what "
    "is searched.",
    "as the text field",
    "Native input of type search; Escape clears it in every engine.",
    "Say what is searched: 'Search your words'.", "Write 'Search...'.",
    """<label class="hw-search narrow"><span class="hw-visually-hidden">Search your words</span>{{icon:search}}<input class="hw-input" type="search" placeholder="Search your words"></label>""")

component(
    "inputs", "Checkbox and radio", [".hw-check"], "keep: ink when checked", "the house",
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
<div class="row" role="radiogroup" aria-label="Export as"><label class="hw-check"><input type="radio" name="cr-fmt" checked>Plain text</label><label class="hw-check"><input type="radio" name="cr-fmt">Markdown</label></div>""")

component(
    "inputs", "Switch", [".hw-switch"], "keep", "quoth",
    "Turns a setting on or off, effective at once.", "A choice that waits for a Save (checkbox).",
    "A track 2.13em by 1.2em with the thumb inset; on is --hw-ink. The label sits before it in a "
    "settings row.",
    "off, on, focus-visible, disabled",
    "A native checkbox with role switch: Space toggles it.",
    "Name the setting, not the state.", "Write 'Enabled' as the label.",
    """<div class="stack"><label class="hw-switch">Learn words from the repository in front <input type="checkbox" role="switch" checked></label><label class="hw-switch">Keep recordings when typing fails <input type="checkbox" role="switch"></label></div>""")

component(
    "inputs", "Slider", [".hw-slider"], "keep", "quoth",
    "Sets a value on a continuous range where the exact number matters less than the feel.",
    "A precise number (a text field).",
    "A track 0.27em tall with the ink fill reaching the thumb's centre (the page sets --_p to the "
    "value's fraction of the range), a 1.07em thumb with a 2px ink ring; the value printed beside it.",
    "rest, focus-visible, disabled",
    "Native range input: arrow keys step it, Home and End jump to the ends.",
    "Print the value with its unit.", "Hide the value.",
    """<div class="hw-field narrow"><label class="hw-field-label" for="sl-a">Keep history for <span class="hw-num muted">30 days</span></label><input id="sl-a" class="hw-slider" type="range" min="1" max="90" value="30" style="--_p:0.326"></div>""")

component(
    "inputs", "Hotkey field", [".hw-hotkey"],
    "new: quoth records a shortcut and the house had no anatomy for one", "quoth",
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
<div class="hw-field"><span class="hw-field-label" id="hk-c-l">Paste last</span><button type="button" class="hw-hotkey" aria-invalid="true" aria-describedby="hk-c-err" aria-labelledby="hk-c-l hk-c" id="hk-c"><kbd class="hw-kbd">⌘</kbd><kbd class="hw-kbd">V</kbd></button><span id="hk-c-err" class="hw-field-error">{{icon:circle-alert}}macOS uses ⌘V for Paste. Choose another.</span></div></div>""")

# ----------------------------------------------------------------------------------- feedback
component(
    "feedback", "Badge and status", [".hw-badge", ".hw-status"],
    "rework: status dot added for live states", "all four",
    "Badge: a short state word on a row. Status: a dot and a word for a live condition.",
    "Counts on navigation; a state without a word.",
    "Badge: 12px/600 on its state fill with a 0.45em dot, radius --hw-radius-sm. Status: a 0.6em dot "
    "in the state's step-9 solid, the word in text colour beside it.",
    "neutral, accent, success, warning, danger",
    "Not focusable; the word is the accessible text.",
    "Always a word beside the colour.", "Colour alone. A badge that says 'New'.",
    """<div class="row"><span class="hw-badge hw-badge--success">Verified</span><span class="hw-badge hw-badge--warning">Check</span><span class="hw-badge hw-badge--danger">Retracted</span><span class="hw-badge">Unresolved</span><span class="hw-badge hw-badge--accent">Sent</span></div>
<div class="row"><span class="hw-status hw-status--ok">Ready</span><span class="hw-status hw-status--warn">Model downloading</span><span class="hw-status hw-status--bad">Microphone off</span></div>""")

component(
    "feedback", "Callout", [".hw-callout"], "rework: neutral kind added, no left stripe",
    "quoth, papertrace",
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
<div class="hw-callout">{{icon:info}}<div><strong>Similarity was not compared.</strong> papertrace checks citations and grammar; it does not search for copied text.</div></div>""")

component(
    "feedback", "Toast", [".hw-toast"],
    "rework: ink surface, so it reads as transient in both themes", "quoth, pointback",
    "Confirms an action finished, with an Undo when the action can be undone.",
    "Errors that need action (callout); anything the person must read twice.",
    "An ink surface at radius --hw-radius-lg and at least --hw-row-h tall, 13px text, an optional "
    "outlined action; bottom centre, one at a time, 5 seconds, paused on hover and on focus.",
    "enter (200ms rise, a fade only under reduced motion), exit",
    "role status, so it is announced without taking focus; its Undo is reachable by Tab.",
    "Name the result: 'Copied'. Offer Undo for a delete.",
    "Stack three. Put an error in a toast.",
    """<div class="row"><div class="hw-toast" role="status">{{icon:check}}Copied to the clipboard</div><div class="hw-toast" role="status">Repository forgotten <button class="hw-btn hw-btn--sm">Undo</button></div></div>""")

component(
    "feedback", "Progress", [".hw-progress"],
    "new: absorbs the partial row; the house had a permission and no anatomy", "quoth, papertrace",
    "Shows how far a known task has gone; indeterminate only when the total is unknown.",
    "A live level (level meter).",
    "A 0.27rem track on --hw-fill-active with an ink fill and full radius; a sentence with the numbers "
    "beside it.",
    "determinate, indeterminate (sweeps; under reduced motion a still full-width bar at 35% opacity)",
    "role progressbar with aria-valuenow, or no value when indeterminate; not focusable.",
    "Print what and how much: '86 of 148 MB'.", "A percentage with no unit of work.",
    """<div class="stack wide"><div class="spread"><span class="hw-small strong" id="pg-a">Downloading the speech model</span><span class="hw-small hw-num">86 of 148 MB</span></div><div class="hw-progress" role="progressbar" aria-labelledby="pg-a" aria-valuenow="58" aria-valuemin="0" aria-valuemax="100"><span style="--_v:58%"></span></div>
<span class="hw-small strong" id="pg-b">Asking Crossref about 3 DOIs</span><div class="hw-progress hw-progress--indeterminate" role="progressbar" aria-labelledby="pg-b"><span></span></div></div>""")

component(
    "feedback", "Skeleton", [".hw-skeleton"], "keep", "the house",
    "Holds the shape of content that takes more than 300ms to arrive.",
    "Content that loads at once; a spinner in a list.",
    "Bars on --hw-fill-active at text height and the expected width; no shimmer.",
    "static",
    "Hidden from assistive technology; the container says it is busy with aria-busy.",
    "Match the width of what will arrive.", "Shimmer.",
    """<div class="stack wide" aria-busy="true"><span class="hw-skeleton" style="width:70%"></span><span class="hw-skeleton" style="width:92%"></span><span class="hw-skeleton" style="width:40%"></span></div>""")

component(
    "feedback", "Level meter", [".hw-meter"],
    "new: the house excluded a meter while quoth ships one", "quoth",
    "Shows a live input level; the only thing in the house that moves on its own.",
    "Progress; decoration.",
    "Bars 0.2em wide and 0.13em apart on --hw-fill-active; lit bars take the product's live colour "
    "through --_live (quoth sets --hw-live-9). Always beside a word.",
    "idle, live (bars follow the input; under reduced motion they still follow it and nothing else "
    "moves)",
    "aria-hidden: the word beside it carries the state.",
    "Pair it with 'Listening'.", "Animate it when no audio arrives.",
    """<div class="row"><span class="hw-meter" style="--_live:var(--hw-live-9)" aria-hidden="true"><i class="on" style="height:30%"></i><i class="on" style="height:55%"></i><i class="on" style="height:85%"></i><i class="on" style="height:60%"></i><i style="height:40%"></i><i style="height:25%"></i></span><span class="hw-small strong">Listening</span></div>""")

# ----------------------------------------------------------------------------------- overlays
component(
    "overlays", "Menu", [".hw-menu", ".hw-menu-item", ".hw-menu-key", ".hw-menu-sep", ".hw-menu-label"],
    "new: absorbs the partial row (item height, separator and destructive rule)", "quoth, pointback",
    "Lists actions on a thing, opened from a button or a secondary click.",
    "Picking a value (select); navigation (rail).",
    "A raised surface with a 4px inset; items at control height minus 2px with a 1.15em icon and "
    "the shortcut right-aligned in muted; a 1px separator; the destructive item last, in danger.",
    "item rest, active (fill), checked (tick), disabled, destructive",
    "Opened as a popover from its button, so Escape and an outside click close it and focus returns. "
    "Items are buttons in a column: Tab moves through them. Arrow-key roving is the product's.",
    "Put the destructive item last, after a separator.", "Nest more than one level.",
    """<div class="hw-menu" role="menu" aria-label="Dictation"><p class="hw-menu-label hw-label">Microphone</p><button class="hw-menu-item" role="menuitemradio" aria-checked="true">MacBook Pro Microphone</button><button class="hw-menu-item" role="menuitemradio" aria-checked="false">AirPods Pro</button><hr class="hw-menu-sep"><button class="hw-menu-item" role="menuitem" data-active>{{icon:mic-off}}Mute<span class="hw-menu-key">⌥⌘M</span></button><button class="hw-menu-item" role="menuitem">{{icon:history}}Open History<span class="hw-menu-key">⌘2</span></button><button class="hw-menu-item" role="menuitem" disabled>{{icon:copy}}Copy last</button><hr class="hw-menu-sep"><button class="hw-menu-item hw-menu-item--danger" role="menuitem">{{icon:trash-2}}Delete this dictation</button></div>""")

component(
    "overlays", "Tooltip", [".hw-tip", ".hw-tooltip"],
    "new: absorbs the partial row (delay, placement and width)", "all four",
    "Names an icon-only control and its shortcut.",
    "Anything the person needs in order to act: it is unreachable on touch.",
    "An ink box, 12px/500, at most 18rem wide, radius --hw-radius-sm, 8px from its control. Wrap the "
    "control in .hw-tip; it shows above, or below with .hw-tip--below.",
    "hidden; shown 500ms after hover or keyboard focus of the control, hidden at once",
    "Shown on focus as well as hover, from CSS alone. The control keeps its own aria-label; the tip "
    "repeats it for sighted readers.",
    "Show it on focus as well as hover.", "Put a sentence of help in it.",
    """<div class="row tall"><span class="hw-tip"><button class="hw-btn hw-btn--icon" aria-label="Copy">{{icon:copy}}</button><span class="hw-tooltip" aria-hidden="true">Copy <kbd class="hw-kbd">⌘C</kbd></span></span><span class="hw-tooltip">Copy <kbd class="hw-kbd">⌘C</kbd></span><span class="hw-small">The second is drawn open, as it shows after the delay.</span></div>""")

component(
    "overlays", "Popover", [".hw-popover"],
    "new: absorbs the partial row, generalised from the combobox popover", "quoth, pointback",
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
<div class="hw-popover"><p class="hw-subheading">Postgres</p><dl class="hw-kv"><dt>You say</dt><dd>postgres, post gress</dd><dt>quoth types</dt><dd>Postgres</dd><dt>Learned from</dt><dd>~/Developer/atlas</dd></dl><div class="row"><button class="hw-btn hw-btn--sm">Edit</button><button class="hw-btn hw-btn--sm hw-btn--danger">Forget</button></div></div>""")

component(
    "overlays", "Dialog", [".hw-dialog", ".hw-scrim"], "keep: actions right-aligned, primary last",
    "quoth",
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
<div class="hw-scrim backdrop"><div class="hw-dialog" role="dialog" aria-labelledby="dl-t"><h3 id="dl-t" class="hw-heading">Delete 412 dictations?</h3><p class="hw-small strong">They are removed from this Mac and cannot be recovered. Vocabulary and settings are kept.</p><div class="hw-dialog-actions"><button class="hw-btn hw-btn--quiet">Keep them</button><button class="hw-btn hw-btn--danger-solid">Delete 412 dictations</button></div></div></div>""")

component(
    "overlays", "Sheet", [".hw-sheet", ".hw-sheet-head"],
    "new: a general sheet was ruled out while quoth ships one", "quoth",
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
<div class="hw-scrim backdrop sheetframe"><div class="hw-sheet" role="dialog" aria-labelledby="sh-t"><div class="hw-sheet-head"><h3 id="sh-t" class="hw-heading">Postgres</h3><button class="hw-btn hw-btn--quiet hw-btn--icon" aria-label="Close">{{icon:x}}</button></div><dl class="hw-kv"><dt>You say</dt><dd>postgres, post gress</dd><dt>quoth types</dt><dd>Postgres</dd><dt>Learned from</dt><dd>~/Developer/atlas</dd><dt>Typed</dt><dd>38 times since 4 September</dd></dl><div class="hw-dialog-actions"><button class="hw-btn hw-btn--danger">Forget</button></div></div></div>""")

component(
    "overlays", "Inline confirm", [".hw-confirm"], "keep", "quoth",
    "Confirms a destructive action on one row without leaving it.",
    "Bulk or irreversible deletes of many things (dialog).",
    "Replaces the row's actions at the row's height: a sentence, the danger button, Cancel. It wraps "
    "rather than overflows at large text sizes.",
    "open; it never times out",
    "Focus moves to Cancel when it opens and returns to the row's action when it closes.",
    "Repeat the verb on the button.", "Time it out.",
    """<div class="hw-confirm"><span>Forget the 400 words learned from <b>quoth</b>?</span><div class="hw-confirm-actions"><button class="hw-btn hw-btn--sm hw-btn--danger">Forget</button><button class="hw-btn hw-btn--sm hw-btn--quiet">Cancel</button></div></div>""")

# --------------------------------------------------------------------------------- navigation
component(
    "navigation", "Rail and navigation item", [".hw-rail", ".hw-nav-item", ".hw-nav-key"],
    "rework: the current item is a surface, not an accent fill", "quoth",
    "Moves between the four to six places of an app.",
    "Actions (buttons); sections within a page (tabs).",
    "The rail on --hw-bg-subtle; items at control height with a 1.15em icon, a 13px label and the "
    "shortcut right; the current item sits on --hw-surface with a 1px --hw-line-strong edge.",
    "rest, hover, current (aria-current page), focus-visible",
    "Links in a nav landmark, in order; the shortcut is the product's.",
    "Show the shortcut beside each item.", "Badges or counts on the rail.",
    """<nav class="hw-rail framed" aria-label="quoth"><a class="hw-nav-item" href="#today">{{icon:sun}}Today<span class="hw-nav-key">⌘1</span></a><a class="hw-nav-item" aria-current="page" href="#history">{{icon:history}}History<span class="hw-nav-key">⌘2</span></a><a class="hw-nav-item" href="#vocabulary">{{icon:book-open}}Vocabulary<span class="hw-nav-key">⌘3</span></a><a class="hw-nav-item" href="#insights">{{icon:chart-no-axes-column}}Insights<span class="hw-nav-key">⌘4</span></a></nav>""")

component(
    "navigation", "Tabs", [".hw-tabs", ".hw-tab", ".hw-tab-count"],
    "rework: active rule in text colour, not accent", "papertrace, pointback",
    "Switches between views of the same thing.",
    "Moving between places (rail); filtering (segmented control).",
    "13px labels 16px apart on a 1px line, each at control height; the active tab has a 2px rule in "
    "--hw-text and weight 620; a count may follow in muted. Tabs wrap at large text sizes.",
    "rest, hover, selected, focus-visible",
    "The layer styles role tab; the product owns the panels and the arrow-key roving between tabs, "
    "since the panels are its own.",
    "Keep to three to six.", "Colour the active tab.",
    """<div class="hw-tabs" role="tablist" aria-label="Report"><button class="hw-tab" role="tab" aria-selected="true">Findings<span class="hw-tab-count">7</span></button><button class="hw-tab" role="tab" aria-selected="false" tabindex="-1">References<span class="hw-tab-count">48</span></button><button class="hw-tab" role="tab" aria-selected="false" tabindex="-1">Figures<span class="hw-tab-count">12</span></button><button class="hw-tab" role="tab" aria-selected="false" tabindex="-1">Run log</button></div>""")

component(
    "navigation", "Toolbar", [".hw-toolbar", ".hw-toolbar-sep"], "keep", "the house",
    "Groups the actions for the current view.", "Navigation.",
    "A row of controls 8px apart within a group, a further 8px spacer between groups; it wraps "
    "rather than clips, and its overflow goes into a menu.",
    "as its buttons",
    "role toolbar with an aria-label; its buttons are Tab stops in order.",
    "Order by frequency.", "Icon-only buttons without tooltips.",
    """<div class="hw-toolbar" role="toolbar" aria-label="Dictation"><button class="hw-btn hw-btn--sm">{{icon:copy}}Copy</button><button class="hw-btn hw-btn--sm">Insert again</button><span class="hw-toolbar-sep"></span><button class="hw-btn hw-btn--sm hw-btn--quiet">{{icon:pencil}}Edit</button><span class="hw-tip"><button class="hw-btn hw-btn--sm hw-btn--icon" aria-label="More actions">{{icon:ellipsis}}</button><span class="hw-tooltip" aria-hidden="true">More actions</span></span></div>""")

# ------------------------------------------------------------------------------- data display
component(
    "data", "List row", [".hw-list", ".hw-row", ".hw-row-meta", ".hw-row-actions"],
    "rework: hover tint, the selected row opens in place", "quoth, pointback",
    "One record in a list scanned for a single subject.",
    "Comparing values across records (table).",
    "A grid of time, content and source; --hw-cell-pad-y and 12px padding; a 1px --hw-line between "
    "rows; at least --hw-row-h tall; a selected row becomes a bordered surface holding its actions.",
    "rest, hover, selected (expanded), focus-visible",
    "The row's own control, usually its content as a button, is the Tab stop; its actions follow it "
    "only when it is selected.",
    "Show actions on the selected row only.", "A card per row; four icon buttons on every row.",
    """<ul class="hw-list"><li class="hw-row"><span class="hw-row-meta">12:30 pm</span><p>Call <code class="hw-code">getUserName</code></p><span class="hw-row-meta">VS Code</span></li><li class="hw-row" aria-selected="true"><span class="hw-row-meta">10:41 am</span><p>Deploy to <span class="hw-mark">K8s</span> cluster</p><span class="hw-row-meta">Linear</span><div class="hw-row-actions"><button class="hw-btn hw-btn--sm">{{icon:copy}}Copy</button><button class="hw-btn hw-btn--sm">Insert again</button><button class="hw-btn hw-btn--sm hw-btn--quiet hw-btn--danger">Delete</button></div></li><li class="hw-row"><span class="hw-row-meta">9:02 am</span><p>Ship it.</p><span class="hw-row-meta">Slack</span></li></ul>""")

component(
    "data", "Table", [".hw-table"], "rework: 12px cells, against the 9px the house once wrote",
    "papertrace",
    "Compares values across records.", "Scanning for one subject (list row).",
    "A 12px/560 muted head over a 1px --hw-line-strong rule; 13px cells with 12px side padding; "
    "numbers right-aligned and tabular; no zebra, no vertical rules.",
    "rest, hover, sorted (head in text colour, aria-sort), selected (accent fill)",
    "A native table; a sortable head is a button inside the th.",
    "Right-align numbers with tabular figures.", "Centre text columns.",
    """<div class="scroll"><table class="hw-table"><thead><tr><th scope="col">Reference</th><th scope="col">Status</th><th scope="col" class="num" aria-sort="descending">Year</th><th scope="col" class="num">Citations</th></tr></thead><tbody><tr><td>Hwang, Nature 579</td><td><span class="hw-badge hw-badge--danger">Retracted</span></td><td class="num">2020</td><td class="num">1,204</td></tr><tr aria-selected="true"><td>doi:10.1101/2020.03.12</td><td><span class="hw-badge hw-badge--warning">Preprint</span></td><td class="num">2020</td><td class="num">12</td></tr><tr><td>Smith, Cell Rep 31</td><td><span class="hw-badge hw-badge--success">Verified</span></td><td class="num">2019</td><td class="num">87</td></tr></tbody></table></div>""")

component(
    "data", "Key-value list", [".hw-kv"], "keep", "all four",
    "Shows the properties of one thing.", "Many things (table).",
    "Two columns, keys muted at 13px and values in text; an 8px row gap and a 24px column gap; it "
    "stacks in a container narrower than 30rem.",
    "set, missing (the value reads 'Not set')",
    "A native description list; not focusable.",
    "Write units into the value.", "An empty dash for a missing value.",
    """<dl class="hw-kv"><dt>Model</dt><dd>Base (English), 148 MB</dd><dt>Runs on</dt><dd>This Mac, no network</dd><dt>History kept</dt><dd>30 days</dd><dt>Licence</dt><dd>Not set</dd></dl>""")

component(
    "data", "Empty state", [".hw-empty"], "rework: left-aligned with the column, one glyph at most",
    "quoth, pointback",
    "Says what will appear here and how to make it appear.", "An error (callout).",
    "A 2.67rem glyph in muted, a 17px sentence, a 13px line with the key or the action; aligned with "
    "the content column.",
    "nothing yet, nothing found, nothing permitted",
    "Its one action, when it has one, is the first Tab stop in the container.",
    "Teach the one action.", "A mascot. 'No data'.",
    """<div class="hw-empty">{{icon:quote}}<p class="hw-subheading">Nothing said yet.</p><p class="hw-small">Hold <kbd class="hw-kbd">⌥ Space</kbd> in any app and speak. What you say is kept here, on this Mac, for 30 days.</p></div>""")

component(
    "data", "Stat", [".hw-stat", ".hw-stat-value"], "new", "quoth, papertrace",
    "A number the person comes back to check.", "Decoration on a dashboard.",
    "The value at 21px/650 in tabular figures, the label at 12px muted under it, the unit in the value.",
    "static",
    "Not focusable; the label follows the value in reading order.",
    "Say over what period or of what.", "The hero-metric template with a gradient.",
    """<div class="row gap-lg"><div class="hw-stat"><span class="hw-stat-value">162</span><span class="hw-label">words, planted-errors.txt</span></div><div class="hw-stat"><span class="hw-stat-value">21</span><span class="hw-label">grammar findings</span></div><div class="hw-stat"><span class="hw-stat-value">8.32</span><span class="hw-label">Flesch-Kincaid grade</span></div></div>""")

component(
    "data", "Tag", [".hw-tag"], "new: quoth's vocabulary chips are hand-rolled", "quoth",
    "A word or short value from a set, often the product's own vocabulary.", "A state (badge).",
    "An inline box at least 1.6rem tall, 13px/500, on --hw-mark-quiet, radius --hw-radius-sm; a "
    "removable tag ends in a small button.",
    "rest, removable",
    "Only the remove button is a Tab stop, named 'Remove' and the word.",
    "Show the real word as the product will type it.", "Colour-code tags by category.",
    """<div class="row"><span class="hw-tag">parseHeader</span><span class="hw-tag">whisper.cpp</span><span class="hw-tag">Tauri</span><span class="hw-tag">TranscriptStore<button aria-label="Remove TranscriptStore">{{icon:x}}</button></span><span class="hw-tag">SQLCipher</span><span class="hw-small">and 394 more</span></div>""")

component(
    "data", "Disclosure", [".hw-disclosure"], "keep", "papertrace",
    "Hides detail most readers do not need.", "Primary content.",
    "A summary row at --hw-row-h with a chevron that turns in 120ms; the content below.",
    "closed, open, focus-visible",
    "A native details element: Enter or Space on the summary opens it.",
    "Write the summary as what is inside.", "Nest them.",
    """<details class="hw-disclosure" open><summary>Why this reference was flagged</summary><p class="hw-small strong">Retraction Watch lists DOI 10.1038/s41586-020-2012-7 as retracted on 2020-11-06. The manuscript cites it in section 2.1 without noting the retraction.</p></details>""")

component(
    "data", "Avatar", [".hw-avatar", ".hw-avatar-group"],
    "new: absorbs the partial row (sizes, fallback initials and the group)", "pointback",
    "Stands for a person beside what they did: who left a note, who sent a review.",
    "A product mark; decoration.",
    "A circle at --hw-radius-full in three sizes (1.6, 1.87 and 2.67rem), initials at 40% of its "
    "size on --hw-fill-active, never under 11px; an image covers the initials once it loads; a group "
    "overlaps by 0.4rem with a 2px ring in --hw-surface.",
    "initials, image, group",
    "Not focusable; the image's alt or an aria-label carries the name, and a group's count is text.",
    "Keep the initials under the image, so a failed load still names the person.",
    "Stack more than four; say '+3' as text after them.",
    """<div class="row"><span class="hw-avatar hw-avatar--sm" role="img" aria-label="Mira Shah">MS</span><span class="hw-avatar" role="img" aria-label="Priyanka Rao">PR</span><span class="hw-avatar hw-avatar--lg" role="img" aria-label="Reviewer">{{icon:user}}</span><span class="hw-avatar-group"><span class="hw-avatar" role="img" aria-label="Mira Shah">MS</span><span class="hw-avatar" role="img" aria-label="Priyanka Rao">PR</span><span class="hw-avatar" role="img" aria-label="Sam Lee">SL</span></span><span class="hw-small">and 3 more</span></div>""")

# ------------------------------------------------------------------------------------- marks
component(
    "marks", "Highlight", [".hw-mark"],
    "new: the house signature; quoth's report asked for the ink-on-highlight pair", "all three apps",
    "Marks the words a product knows, matched or pointed at.",
    "Emphasis in prose (use weight); a state.",
    "Light: a highlighter swipe from 44% to 90% of the line box in --hw-mark, the text left in ink. "
    "Dark: a block in mark step 7 with the text in --hw-text, since a swipe under light text measured "
    "1.15:1; the bright solid (.hw-mark--solid) is kept for the one selected word.",
    "rest, solid (the selected word), quiet (--hw-mark-quiet, for dense lists)",
    "Not focusable unless the product makes the word a button that explains the mark.",
    "Mark only what the product can explain on click.",
    "Highlight a whole paragraph. Use it as the selection colour.",
    """<p class="hw-body large">We deploy with <span class="hw-mark">Kubernetes</span> and <span class="hw-mark">Postgres</span>, and <span class="hw-mark hw-mark--solid">pgvector</span> is the word selected.</p><p class="hw-small">quoth: the words its dictionary knows. papertrace: the passage matched elsewhere. pointback: the text the reviewer selected. Quiet: <span class="hw-mark hw-mark--quiet">TranscriptStore</span>.</p>""")

component(
    "marks", "Proof marks", [".hw-proof", ".hw-ins", ".hw-del", ".hw-caret"],
    "new: quoth's Show changes needs it; papertrace and pointback show diffs", "quoth",
    "Shows what a product changed in someone's words, the way an editor marks a page.",
    "Code changes (diff).",
    "The original words in muted; removed words struck through in --hw-delete; inserted text in "
    "--hw-insert, bold, on its fill, with a caret under the line at the point of insertion.",
    "static",
    "Use ins and del elements, so the change is announced as well as drawn.",
    "Show the person's own words, then the result.",
    "Rely on colour alone: the strike and the caret carry it.",
    """<p class="hw-proof"><del class="hw-del">fix the bug</del> <del class="hw-del">scratch that</del> refactor the parser<span class="hw-caret"></span><ins class="hw-ins">.</ins> <del class="hw-del">period new line</del> ship it<span class="hw-caret"></span><ins class="hw-ins">.</ins></p><p class="hw-body">Refactor the parser.<br>Ship it.</p>""")

component(
    "marks", "Diff", [".hw-diff"], "new", "pointback, papertrace",
    "Shows changed lines of code or text with their context.",
    "Changes inside prose (proof marks).",
    "Mono 13px, a line per row; added rows on --hw-insert-fill with a + in --hw-insert, removed rows "
    "on --hw-delete-fill with a minus in --hw-delete; the text stays ink. It scrolls sideways rather "
    "than overflow its box.",
    "static",
    "Not focusable unless it scrolls; the signs are text, so a screen reader reads them.",
    "Keep the text in ink; the fill and the sign carry the change.",
    "Colour the text green and red.",
    """<div class="hw-diff"><div class="ctx">.checkout-actions {</div><div class="rem">  align-items: center;</div><div class="add">  align-items: baseline;</div><div class="ctx">  gap: 12px;</div><div class="ctx">}</div></div>""")

component(
    "marks", "Pin and margin note", [".hw-pin", ".hw-note", ".hw-note-locator"],
    "new: pointback's mark, generalised", "pointback",
    "Points at a place on a page and carries a note back.", "Decoration.",
    "A 1.6rem teardrop in the product's solid with its number; the note is a card beside it with the "
    "selector in mono, truncated to one line.",
    "placed, sent, resolved",
    "The note is the Tab stop; the pin is its label, read with it.",
    "Number pins in the order they were made.", "Hide the number.",
    """<div class="row top"><span class="hw-pin" aria-hidden="true">3</span><div class="hw-note"><p class="hw-small strong">The primary button sits 4px lower than Cancel.</p><code class="hw-code hw-note-locator">main &gt; .checkout-actions &gt; button.primary</code></div></div>""")

component(
    "marks", "Code", [".hw-code"], "keep", "all four",
    "Inline code, identifiers and commands as typed.", "Keys (keycap).",
    "Mono at 0.92em on --hw-fill, radius --hw-radius-sm; a block is 13px with 8px and 12px padding "
    "and scrolls sideways.",
    "static",
    "A code element; a block that scrolls is focusable so the keyboard can scroll it.",
    "Show the identifier exactly as it is written.", "Syntax-colour a one-line command.",
    """<p class="hw-body">Call <code class="hw-code">getUserName</code>, then run <code class="hw-code">cargo build --release</code>.</p><pre class="hw-code" tabindex="0">python3 tools/components.py --check</pre>""")

# ------------------------------------------------------------------------------------- stage
component(
    "stage", "Stage", [".hw-stage"],
    "new: replaces the 'vivid field' rule with a component and a place", "site, store frames",
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
<div class="hw-stage hw-stage--ink"><p class="hw-label">quoth</p><p class="hw-headline">Dictation that stays on your Mac.</p><a class="hw-link" href="#stage">Download for Mac</a></div>""")

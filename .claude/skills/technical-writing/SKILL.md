---
name: technical-writing
description: >-
  Use when writing or revising any prose a person will read — chat replies to the
  user, docs, READMEs, wiki pages, CLI --help text, error and log messages,
  commit bodies, PR descriptions, release notes, code comments. Also use when
  text reads as stiff, hedged, padded, corporate, or breezy, or when an error
  message leaves the reader with nothing to do. Portable voice-and-tone rules
  adapted from the Microsoft Writing Style Guide; carries no Microsoft-specific
  terminology or UI conventions.
---

# Writing in Plain Voice

Adapted from the voice-and-tone half of the Microsoft Writing Style Guide — the
portable half. The terminology list, UI-element rules, and product conventions
are deliberately left out.

Target voice: **warm, crisp, useful.** Warm is plain and direct, not chatty.
Crisp is one idea per sentence. Useful means the reader can act on it.

## The recipe

Every sentence: **an actor, doing something, in the first clause.** The point
leads; the qualification follows.

1. **Second person, active voice.** "Set the token in your config" — not "The
   token should be set."
2. **First clause carries the point.** Reason, condition, and caveat go after.
   "Scope the tag — the runner pool is shared across regions."
3. **One idea per sentence.** Split compounds. If a sentence needs a second
   comma to survive, it's two sentences.
4. **Contractions are fine.** *don't*, *you're*, *it's*.
5. **Verbs, not nominalizations.** "when you configure" over "during
   configuration."
6. **Define a term the first time it appears.** Undefined jargon or an unexpanded
   acronym is a defect, not a style preference.
7. **Open on the substance.** The first sentence is the answer, the instruction,
   or the finding.
8. **Say what it does, not what it is.** Lead with the reader's action or
   outcome, not the taxonomy.

## Error, warning, and failure text

Three parts, in this order, in plain language:

**what happened → why → what to do next**

The reader is never the defect. State the condition, not their fault. Skip
codes and internals unless the reader can act on them; if a code must appear,
it goes last.

- ✅ `That date is in the past. Pick a future date.`
- ❌ `Invalid value entered (ERR_DATE_1042).`

## Quick reference

| Instead of | Write |
|---|---|
| In order to configure… | To configure… |
| It is important to note that the pool is shared | The pool is shared |
| Please be aware that this may fail | This fails when the token is expired |
| The file should be deleted by the user | Delete the file |
| Utilize / leverage | Use |
| Prior to / subsequent to | Before / after |
| An error occurred | Couldn't reach the API — check your token |
| We apologize for any inconvenience | *(cut)* |

## Common mistakes

- **Hedging as politeness.** "You may want to consider possibly…" — say it or
  don't. Uncertainty gets stated once, plainly: "I'm not sure this holds when…"
- **Padding the front.** "Great question! So, essentially, what's happening
  here is…" The answer starts at word one.
- **Warm read as breezy.** No jokes, no exclamation marks, no hype. Warmth comes
  from being direct and unpatronizing, not from enthusiasm.
- **Crisp read as clipped.** Short sentences, complete thoughts. Don't drop the
  reasoning — put it in the second clause.
- **Passive voice hiding the actor.** "The config is read at startup" — by what?
  Name it.
- **Long-sentence relapse in explanation.** Explaining something complex is
  exactly when clause-stacking creeps back in. Watch it there hardest.

## Scope note

This governs *voice*, not structure or content. Depth, length, and what to
include are set by the task and by other rules. Plain voice does not mean short
answers — it means every sentence in a long answer earns its place.
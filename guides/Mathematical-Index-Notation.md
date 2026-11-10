# Mathematical Wiki notation — adopted 10 November 2026

This is Julio's editorial rule for new or intentionally revised mathematical content across his scientific GitHub Wikis. It is not a request to rewrite already published pages or to alter quoted source material.

## Three typographic roles

__Input and index domain variables__ use Mathematical Monospace Unicode: `𝚒`, `𝚓`, `𝚝`, `𝚗`, `𝚡`, `𝚢`, `𝚣`.

__Functions and systems__ use Mathematical Italic Unicode: `𝑓`, `𝑔`, `𝑠`, `𝑇`.

__Named sets, domains and codomains/ranges__ use Mathematical Double-Struck Unicode (blackboard bold): `ℝ` for the real numbers, `ℕ` for natural numbers, `ℤ` for integers, `ℂ` for complex numbers, `𝔹` for binary values, and `𝕌` for a stated universal set. We may use other double-struck letters for explicitly defined set-valued objects where their role is unambiguous.

This convention identifies a **set**, not a variable constrained to that set. A function input such as `𝚡` remains mathematical monospace even when `𝚡 ∈ ℝ`. A function such as `𝑓` remains mathematical italic even when its codomain is `𝔹`. In set-theoretic examples, `𝔹 = {0,1}` is a convenient binary domain; define `ℕ` as starting at 0 or 1 when material, and state which universe `𝕌` denotes.

For example:

```math
𝑓: ℝ \rightarrow 𝔹, \qquad 𝚡 \in ℝ, \qquad 𝑓_{(𝚡)} \in 𝔹.
```

Distinguish the **codomain** of a function from its actual **image/range** if they differ. Double-struck lettering marks a set's role; it does not assert that its members fill the whole codomain. This rule must not automatically replace standard `Ω`, `A` or `B` notation already defined for sample spaces or events in an existing source or Wiki.

The style expresses *roles*, not the statement that every function's domain is time.

## Two kinds of subscripts

**Function evaluation / inputs:**

```math
𝑓_{(𝚡,𝚢,𝚣)}
```

The subscripted parenthesized tuple denotes the evaluation of the function with those inputs in our Wiki convention, even though some established literature uses parenthesized subscripts for indexing a family of functions. Explain this explicitly at first use.

**Indexed samples / components:**

```math
𝑠_{[𝚗]}
```

Square brackets mark the discrete index or component position. This continues the adopted `_{[i]}` style, now with Mathematical Monospace index glyphs.

A useful contrast is `$𝑇_{(𝚝)}$` (temperature model evaluated at time `𝚝`) versus `$𝑦_{[𝚗]}$` (the `𝚗`-th measured sample).

## Authoring conventions and safeguards

Use `$...$` for inline GitHub math and fenced `math` blocks for display equations. Use `_text_`, `__text__`, and `___text___` for prose emphasis. Ordinary mathematical grouping parentheses, source-defined array subscripts, derivatives, units and operators retain their own semantics.

Do not mechanically replace historical formulas, code identifiers, citations or symbols in an existing theorem. Preserve the quantity's domain/codomain, mathematical type, ordering and units. If an expression becomes ambiguous, provide a local notation key instead of silently changing its meaning.

Check the actual target Wiki for font/MathJax rendering of the chosen Unicode glyphs; an ordinary Markdown preview or a source-only check is not the same as successful GitHub rendering. If a renderer cannot display a glyph, report the limitation and suggest an explicit fallback for review.

Only Julio edits and publishes the canonical project Wikis. Drafts, proposals, agent updates and code-repository pull requests are not publication.

## Handoff for specialist agents

When a specialist writes, reviews or illustrates a mathematical Wiki page, the coordinator should include this notation rule in its task brief. The subject specialist retains the mathematical semantics; Wiky ensures written conventions; Euly checks formula meaning; Mermy/Plotographer check the symbols in diagrams and plots. This is an editorial preference, not a license to modify theorem statements or code.

## Sources

- User-adopted notation choice, 10 November 2026.
- [GitHub: Writing mathematical expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions).

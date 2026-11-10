# Mathematical Wiki notation — adopted 10 November 2026

This is an editorial rule for new or intentionally revised mathematical content across his scientific GitHub Wikis. It is not a request to rewrite already published pages or to alter quoted source material.

## Three typographic roles

__Input and index domain variables__ use Mathematical Monospace Unicode: `𝚒`, `𝚓`, `𝚝`, `𝚗`, `𝚡`, `𝚢`, `𝚣`.

__Functions and systems__ use Mathematical Italic Unicode: `𝑓`, `𝑔`, `𝑠`, `𝑇`.

__Named sets, domains and codomains/ranges__ use Mathematical Double-Struck Unicode (blackboard bold): `ℝ` for the real numbers, `ℕ` for natural numbers, `ℤ` for integers, `ℂ` for complex numbers, `𝔹` for binary values, and `𝕌` for a stated universal set. We may use other double-struck letters for explicitly defined set-valued objects where their role is unambiguous.

This convention identifies a **set**, not a variable constrained to that set. A function input such as `𝚡` remains mathematical monospace even when `𝚡 ∈ ℝ`. A function such as `𝑓` remains mathematical italic even when its codomain is `𝔹`. In set-theoretic examples, `𝔹 = {0,1}` is a convenient binary domain; **`ℕ` includes zero by default**, `ℕ⁰` explicitly denotes this same zero-inclusive set, and `ℕ⁺` denotes positive naturals. State which universe `𝕌` denotes.

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

## Natural numbers and set-theoretic starting point

- __Default__: `ℕ = ℕ⁰ = {0, 1, 2, 3, …}`; `ℕ⁺ = {1, 2, 3, …}`. Thus zero belongs to `ℕ`, and `ℕ⁺` excludes zero.
- The von Neumann construction takes `0 = ∅`, which is consistent with this adopted zero-inclusive convention. This is our modelling and editorial standard; it does not imply that every mathematical tradition must define `ℕ` the same way.
- Explicitly declare `ℕ⁰` as a zero-inclusive alias when used: in other contexts, the exponent in `ℕ⁰` is read as the zeroth Cartesian power. Avoid silently changing its meaning inside a source quotation or a theorem about powers of sets.
- A *variable* ranging over `ℕ` remains styled according to its role, e.g. `𝚗 ∈ ℕ`; the double-struck glyph belongs to the *set*.

## Unary marks and vector marks

__Earlier established notation__:

- The combining overline is an __additive opposite__: `2̅ = −2`; more generally `𝑎̅ = −𝑎` in an additive domain. It is not automatically a statistical mean or a complex conjugate in our personal notation. Retain those meanings when explicitly source-defined.
- The combining diaeresis is a __multiplicative reciprocal__: `2̈ = 1/2`; more generally `𝑎̈ = 1/𝑎` when `𝑎 ≠ 0`. It is not a time derivative. An inverse function `𝑓⁻¹` and a reciprocal value `1/𝑓_{(𝚡)}` remain distinct.

__Variants introduced or reconfirmed on 10 November 2026__:

- `2̎` (COMBINING DOUBLE VERTICAL LINE ABOVE, U+030E) is an additional proposed rendering of `1/2`, alongside `2̈` (COMBINING DIAERESIS, U+0308). The mathematics is the same, but the glyphs are not Unicode equivalents. Test readability in GitHub before promoting one as a replacement default.
- `u⃗` (COMBINING RIGHT ARROW ABOVE, U+20D7) and `u̱` (COMBINING MACRON BELOW, U+0331) are vector marks offered by the author. Either may be used in a **locally defined notation key**; do not automatically equate the underbar with the previously discussed *time/direct-representation underlay* (`u̲`, U+0332, a distinct low-line character). Preserve the previously adopted hat-only designation for unit direction (`û`) when the vector is nonzero.
- These vector alternatives are recorded as design choices under discussion, not an instruction to globally convert every vector symbol or to treat all marked quantities as vectors. Avoid ambiguity with conventional vector-arrow notation, overbars, and source-defined marks.

## Authoring conventions and safeguards

Use `$...$` for inline GitHub math and fenced `math` blocks for display equations. Use `_text_`, `__text__`, and `___text___` for prose emphasis. Ordinary mathematical grouping parentheses, source-defined array subscripts, derivatives, units and operators retain their own semantics.

Do not mechanically replace historical formulas, code identifiers, citations or symbols in an existing theorem. Preserve the quantity's domain/codomain, mathematical type, ordering and units. If an expression becomes ambiguous, provide a local notation key instead of silently changing its meaning.

Check the actual target Wiki for font/MathJax rendering of the chosen Unicode glyphs; an ordinary Markdown preview or a source-only check is not the same as successful GitHub rendering. If a renderer cannot display a glyph, report the limitation and suggest an explicit fallback for review.

## Handoff for specialist agents

When a specialist writes, reviews or illustrates a mathematical Wiki page, the coordinator should include this notation rule in its task brief. The subject specialist retains the mathematical semantics; Wiky ensures written conventions; Euly checks formula meaning; Mermy/Plotographer check the symbols in diagrams and plots. This is an editorial preference, not a license to modify theorem statements or code.

## Sources

- User-adopted notation choice, 10 November 2026.
- [GitHub: Writing mathematical expressions](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions).

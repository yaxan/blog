# AGENTS.md

Personal blog: ML/AI lessons written so anyone can follow along, 3b1b-inspired
— prose + build-time math + committed Manim animations. Hugo static site,
hand-written templates, no theme, no framework.

## Hard constraints

- **No JS frameworks, bundlers, or dependencies — and almost no JS at
  all.** Everything interactive is CSS/HTML (`<details>`, counters,
  media queries). The one sanctioned exception is the small inline
  vanilla script in `layouts/_partials/anim-controls.html` (the
  beat-stepper for Manim videos), loaded only on pages that set the
  `hasAnim` page-store flag. Do not add further scripts; find a
  build-time or CSS solution instead.
- **The dark background is `#14161a` and must not drift.** It matches the
  Manim render background exactly so animations sit borderless on the page in
  dark mode. If you change one, change both (`assets/css/main.css` `--board`
  and dark `--bg`; `BG` in `animations/*.py`).
- **CI never runs Python or LaTeX.** Rendered MP4s in `static/anim/` are
  committed; the GitHub Pages workflow only runs Hugo.
- Math renders at build time: goldmark passthrough + a render hook calling
  Hugo's embedded KaTeX (`layouts/_markup/render-passthrough.html`). KaTeX
  CSS/fonts are vendored in `static/katex/` and load only on pages where the
  hook set the `hasMath` page-store flag. Don't link KaTeX unconditionally.

## Commands

```sh
make serve    # dev server with drafts at http://localhost:1313
make build    # production build into public/
make anims    # render animations/*.py -> static/anim/<SceneName>.mp4 (needs .venv)
hugo new posts/<slug>.md   # new draft from archetype
```

## Design identity ("Chalk & Paper")

Light mode is a printed lecture handout; dark mode is the chalkboard the
animations are drawn on. Concretely:

- Body text: Charter (system font, zero bytes). Headings: KaTeX_Main via
  `@font-face` against the vendored KaTeX woff2s — titles and equations share
  a voice. Both preloaded in `layouts/_partials/head.html`.
- Links: `#1c6e9e` light / Manim blue `#58c4dd` dark. Selection in dark mode
  is chalk yellow. Accent palette = Manim's: blue `#58c4dd`, yellow
  `#f5e13d`, green `#83c167`, red `#fc6255`.
- Display equations are numbered with a CSS counter — except inside
  tangents, deliberately, so skipping a tangent leaves no numbering gap.
  Don't "fix" that.
- Every post can carry a **glyph**: a tiny SVG drawing of its core idea on a
  dark chip, shown on the home page. Front matter `glyph: <name>` + a case in
  `layouts/_partials/glyph.html` (56×34 viewBox, Manim palette, a few shapes
  max). Posts without one fall back to the tangent-line glyph.

## Writing flow

1. `hugo new posts/<slug>.md`, fill `description` (shows on the home page).
2. Write markdown with the live preview open (`make serve`; drafts visible).
3. Publish: set `draft: false`, commit (including any new MP4s), push to
   `main` — GitHub Actions deploys to Pages.

In-post vocabulary:

- Inline math `$...$`, display math `$$...$$` (auto-numbered).
- `{{</* tangent "Question it answers?" */>}}...{{</* /tangent */>}}` —
  collapsible primer for a prerequisite some readers already know (what's an
  RNN, what's a gradient). Full markdown + math inside; zero JS.
- `{{</* sidenote */>}}...{{</* /sidenote */>}}` — short numbered aside,
  written inline immediately after the text it annotates; floats into the
  margin on wide screens.
- `{{</* manim "SceneName" */>}}Caption.{{</* /manim */>}}` — embeds
  `static/anim/SceneName.mp4` as a looping muted video.

## Writing style

Explain like 3b1b: build intuition first, formalism second. Reach for a
tangent when a prerequisite might be missing, a sidenote for a one-breath
aside that would otherwise be parentheses. Prose first; structure on a
second pass.

### From messy draft to finished post

The author writes drafts as messy blobs — unstructured, out of order,
half-formed asides inline. Turning a blob into a well-structured post is
the agent's job, and structural work is encouraged: add section headings,
reorder so ideas build, split walls of text, pull prerequisite
explanations into tangents, turn parenthetical asides into sidenotes,
suggest where an animation or equation belongs.

The prose is a different matter. The author's sentences are the raw
material: carry them through the restructure, fix what's broken, and only
write new connective prose where the structure demands it (a bridge
sentence, a heading, a tangent body the draft only gestured at). New prose
must pass for the author's — same register, and everything in the tells
list below applies to it doubly.

Voice calibration: `content/posts/seq2seq.md` is the author's real
drafting voice — that's the reference. **`gradient-descent.md` was
AI-written** (as scaffolding for the theme) and is a reference for
formatting and component usage only, not for voice. The voice to preserve:
direct address ("you", "we"), rhetorical pivots mid-argument ("But wait —
why are we even encoding things into vectors?"), concrete examples doing
the explaining ("I am hungry" → "Я голоден"), contractions, em dashes
marking a spoken beat, the occasional fragment.

Ground rules:

- Structure freely; rewrite reluctantly. Within a sentence, make the
  smallest edit that fixes the problem — grammar, agreement, a genuinely
  clunky phrase, a sentence that reads better split. A polished paragraph
  should still be traceable, sentence by sentence, to the author's draft.
- Keep what makes it human: rhetorical questions, opinions, mild
  informality ("spit out a translation"). Don't formalize them away.
  Educated but not stiff is the register.
- Never pad. Headings and bridge sentences that the structure needs are
  fine; intros that preview, transitions that recap, and a closing
  paragraph that restates the post are not. If the edit removes words,
  good.
- Repeating a technical term is correct. Say "hidden state" five times if
  the paragraph is about hidden states. Synonym-rotating to avoid
  repetition ("the memory vector", "this internal representation") is an
  AI tell and makes technical prose worse.
- Plain copulas are fine. "The context is a vector" — never "serves as",
  "functions as", "stands as", or "represents" when "is" is meant.
- Don't even out sentence rhythm. A three-word sentence after a long one
  is doing its job. Leave it.

### AI tells — never introduce, remove on sight

Sourced from Wikipedia's "Signs of AI writing" catalog, filtered for this
blog:

- Vocabulary: delve, crucial, pivotal, testament, tapestry, landscape,
  underscore, highlight (as a verb of importance), showcase, foster,
  intricate, vibrant, boast, leverage, seamless, journey, realm, robust
  (as praise — "robustness" as the ML term of art is fine).
- Constructions: "not just X, but Y"; "It's not about X — it's about Y";
  tripled anything ("fast, simple, and powerful"); "from X to Y"
  comprehensiveness sweeps; trailing "-ing" analysis clauses ("…,
  highlighting the importance of attention"); "In conclusion" / "Overall";
  "Let's dive in".
- Filler and hedge: "It's worth noting that", "Importantly,",
  "Interestingly,", "arguably". If it's worth noting, note it.
- Structure: don't convert prose into bullet lists or bold-term-colon
  lists; don't add headings to short sections; no emoji.
- Em dashes are part of this voice, but match the draft's existing
  density — don't add more than the paragraph already had.

Litmus test: read the edited paragraph aloud. If it could open any ML blog
post on the internet, it lost the voice — put the author's phrasing back.

Overcorrection is its own tell. Mechanically inverting the list above —
stripping every dash, chopping every sentence, forcing casualness —
produces a voice as recognizable as the one it replaces. Fix each
sentence for its own reasons; the litmus test stays the same.

### Companion notebooks

Notebooks (`notebooks/*.ipynb`) are instructional, so their *structure*
follows developer-doc conventions (Google style, Simplified Technical
English) even where posts wouldn't: second person, active voice, present
tense, one instruction per sentence, condition before instruction
("Training takes minutes on a GPU, so pick Runtime → … first"), bullets
for how-to steps. The *sentences* still follow §Writing style and the
tells list, and this covers code comments, docstrings, and print strings,
not just markdown cells. Specifics:

- When the article already has the sentence, reuse it with its original
  punctuation — don't swap the author's colons for dashes.
- Bold marks a first-mention term or a UI path, never emphasis. Terms the
  article already bolded stay plain on re-mention.
- No inverted syntax ("Under each exercise sits…"), no caps-for-emphasis
  ("ONLY"), no passive where the actor is the reader or the code.
- Emoji only as cell-type signage (the ✋ solution marker), never in prose.
- The notebook itself is agent-written and is never a voice reference.
  Calibrate only against the author's article prose; when it matters
  whether a given line is the author's, check git history, since some
  article captions have passed through agent hands too.

Scenes live in `animations/*.py`, rendered by Manim CE from `.venv`
(`python3 -m venv .venv && .venv/bin/pip install manim` to recreate). Every
scene must subclass `BeatScene` (from `animations/beats.py`), not `Scene`:
it records the [start, end] of every `play()` call into
`data/anim/<SceneName>.json` at render time, which the manim shortcode
turns into the on-page beat-stepper (readers step through the animation
one `play()` at a time; waits are skipped). Every scene must set
`self.camera.background_color = "#14161a"`. Use `Text()` (Pango) rather
than `Tex()`/`MathTex` — no LaTeX distribution is installed. `make anims`
renders every scene and copies MP4s into `static/anim/`; commit the MP4s
and the `data/anim/` JSONs together.

## Layout map

```
hugo.toml                        site config; passthrough math delimiters
layouts/baseof.html              page shell (header/footer)
layouts/home.html, section.html  post list via _partials/post-list.html
layouts/single.html              article page
layouts/_partials/head.html      inlined CSS bundle, font preloads, conditional KaTeX CSS
layouts/_partials/glyph.html     per-post SVG glyphs (add new posts' glyphs here)
layouts/_shortcodes/             tangent, sidenote, manim
layouts/_markup/render-passthrough.html   build-time KaTeX render hook
assets/css/main.css              all site styling (Chalk & Paper tokens at top)
assets/css/syntax.css            chroma highlight palettes (generated)
content/posts/*.md               the posts
animations/*.py                  Manim scenes -> make anims
animations/beats.py              BeatScene base: records per-play() beat times
data/anim/*.json                 committed beat timestamps (one per scene)
static/anim/*.mp4                committed renders
layouts/_partials/anim-controls.html  the beat-stepper script (the site's only JS)
static/katex/                    vendored KaTeX CSS + fonts
```

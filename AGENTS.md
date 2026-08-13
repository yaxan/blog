# AGENTS.md

Personal blog: ML/AI lessons written so anyone can follow along, 3b1b-inspired
— prose + build-time math + committed Manim animations. Hugo static site,
hand-written templates, no theme, no framework.

## Hard constraints

- **Zero client-side JavaScript.** Everything interactive is CSS/HTML
  (`<details>`, counters, media queries). Do not add JS, bundlers, or
  frameworks; find a build-time or CSS solution instead.
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

Voice: explain like 3b1b — build intuition first, formalism second. Use a
tangent (not a paragraph of hedging) when a prerequisite might be missing;
use a sidenote for one-breath asides that would otherwise be parentheses.
Prose first, structure on a second pass.

## Animations

Scenes live in `animations/*.py`, rendered by Manim CE from `.venv`
(`python3 -m venv .venv && .venv/bin/pip install manim` to recreate). Every
scene must set `self.camera.background_color = "#14161a"`. Use `Text()`
(Pango) rather than `Tex()`/`MathTex` — no LaTeX distribution is installed.
`make anims` renders every scene and copies MP4s into `static/anim/`;
commit them.

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
static/anim/*.mp4                committed renders
static/katex/                    vendored KaTeX CSS + fonts
```

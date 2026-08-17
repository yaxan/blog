# blog

Minimal personal blog for ML/AI lessons. Hugo static site, no JS frameworks
or dependencies: math is rendered to HTML at build time (Hugo's embedded
KaTeX), and animations are Manim-rendered MP4s embedded as looping videos.
The only client-side script is a small inline one that turns those videos
into steppable slideshows: they autoplay by default, and an `auto` toggle
plus ◀ ▶ arrows let the reader play one animation beat at a time (beat
timestamps are recorded at render time into `data/anim/`).

## Everyday use

```sh
make serve             # live-reload dev server at http://localhost:1313
hugo new posts/my-post.md   # start a new post (drafts hidden in prod builds)
make build             # production build into public/
```

## Writing

- Inline math: `$e^{i\pi} = -1$` or `\( ... \)`; display math: `$$ ... $$` or `\[ ... \]`.
  KaTeX CSS is only loaded on pages that contain math.
- Code blocks get build-time syntax highlighting (light/dark automatic).
- Animations: add a scene class to a file in `animations/`, run `make anims`
  (renders every scene to `static/anim/<SceneName>.mp4`), then embed it:

  ```
  {{</* manim "SceneName" */>}}Optional caption.{{</* /manim */>}}
  ```

  Manim lives in `.venv/` (`python3 -m venv .venv && .venv/bin/pip install manim`
  to recreate). Rendered MP4s are committed, so CI never needs Python.
  Scenes use `Text()` (Pango) rather than `Tex()`, so no LaTeX install is
  needed; install a TeX distribution (e.g. `brew install --cask basictex`)
  if you want `MathTex` in animations. Render scenes on the site's dark
  background (`self.camera.background_color = "#14161a"`) — in dark mode the
  page background matches it exactly, so videos appear borderless.

- Tangents: collapsible primers for sub-concepts some readers already know
  (what's an RNN, what's a gradient). Zero JS — a styled `<details>`. The
  body is full markdown and may contain math; its display equations are
  deliberately unnumbered so skipping a tangent leaves no gaps.

  ```
  {{</* tangent "What's an RNN, and why use one here?" */>}}
  ...markdown with $math$...
  {{</* /tangent */>}}
  ```

- Sidenotes: short numbered asides, written inline right after the text they
  annotate. They float into the margin on wide screens and render as small
  inset blocks on narrow ones.

  ```
  ...the learning rate{{</* sidenote */>}}Too large and you overshoot.{{</* /sidenote */>}} controls...
  ```

- Glyphs: each post can carry a tiny chalkboard drawing of its core idea,
  shown on the home page (and usable as a tangent icon via `glyph="name"`).
  Set `glyph: my-post` in front matter and add a matching `if` case with a
  small SVG (Manim palette: blue `#58c4dd`, yellow `#f5e13d`, green
  `#83c167`, red `#fc6255`) in `layouts/_partials/glyph.html`. Posts without
  one fall back to the default tangent-line glyph.

## Deploying

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every
push to `main`. One-time setup: in the GitHub repo, Settings → Pages → set
Source to "GitHub Actions". Set `baseURL` in `hugo.toml` when you have a
custom domain.

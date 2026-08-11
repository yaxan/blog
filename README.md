# blog

Minimal personal blog for ML/AI lessons. Hugo static site, zero client-side
JavaScript: math is rendered to HTML at build time (Hugo's embedded KaTeX),
and animations are Manim-rendered MP4s embedded as looping videos.

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
  if you want `MathTex` in animations.

## Deploying

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every
push to `main`. One-time setup: in the GitHub repo, Settings → Pages → set
Source to "GitHub Actions". Set `baseURL` in `hugo.toml` when you have a
custom domain.

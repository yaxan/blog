MANIM := ./.venv/bin/manim

.PHONY: serve build anims clean

## serve: local dev server with live reload (http://localhost:1313)
serve:
	hugo server --buildDrafts

## build: production build into public/
build:
	hugo --minify --gc

## anims: render every scene in animations/*.py to static/anim/<SceneName>.mp4
anims:
	@for f in animations/*.py; do \
		$(MANIM) render -qh -a --media_dir .manim "$$f" || exit 1; \
	done
	@mkdir -p static/anim
	@find .manim/videos -name '*.mp4' -not -path '*partial_movie_files*' -exec cp {} static/anim/ \;
	@echo "Rendered animations:" && ls static/anim/

clean:
	rm -rf public .manim

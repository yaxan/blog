MANIM := ./.venv/bin/manim

.PHONY: serve build anims clean

## serve: local dev server with live reload (http://localhost:1313)
serve:
	hugo server --buildDrafts

## build: production build into public/
build:
	hugo --minify --gc

## anims: render every scene in animations/*.py to static/anim/<SceneName>.mp4
## (re-encoded for the web: 30fps, crf 28, moov atom up front so playback
## can start before the file finishes downloading)
anims:
	@for f in animations/*.py; do \
		$(MANIM) render -qh -a --media_dir .manim "$$f" || exit 1; \
	done
	@mkdir -p static/anim
	@find .manim/videos -name '*.mp4' -not -path '*partial_movie_files*' | while read f; do \
		ffmpeg -nostdin -y -loglevel error -i "$$f" -c:v libx264 -crf 28 -preset slow \
			-r 30 -pix_fmt yuv420p -movflags +faststart -an \
			"static/anim/$$(basename $$f)" || exit 1; \
	done
	@echo "Rendered animations:" && ls -lh static/anim/

clean:
	rm -rf public .manim

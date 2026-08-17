"""BeatScene: a Scene that records when each play() starts and ends.

The blog's player steps through animations beat by beat (one beat per
play() call, waits excluded), like a slideshow whose transitions are the
animations themselves. Every scene writes data/anim/<SceneName>.json on
render; the manim shortcode reads it into a data-beats attribute.
"""

import json
from pathlib import Path

from manim import Scene, Wait


class BeatScene(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._beats = []

    def play(self, *args, **kwargs):
        is_wait = bool(args) and all(isinstance(a, Wait) for a in args)
        t0 = self.renderer.time
        super().play(*args, **kwargs)
        if not is_wait:
            self._beats.append([round(t0, 3), round(self.renderer.time, 3)])

    def tear_down(self):
        super().tear_down()
        out = Path("data/anim")
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{type(self).__name__}.json"
        path.write_text(json.dumps(self._beats))

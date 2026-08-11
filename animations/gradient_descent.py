"""Manim scenes for the gradient-descent post.

Render with: make anims
Text() uses Pango, so no LaTeX installation is required.
"""

from manim import *

BG = "#14161a"  # matches the blog's dark background


class GradientDescent(Scene):
    def construct(self):
        self.camera.background_color = BG

        ax = Axes(
            x_range=[-3.4, 3.4, 1],
            y_range=[0, 5.2, 1],
            x_length=11,
            y_length=5.6,
            axis_config={"include_ticks": False, "color": GREY_C},
            tips=False,
        )

        def f(x):
            return 0.55 * x**2 + 0.5

        def df(x):
            return 1.1 * x

        curve = ax.plot(f, x_range=[-2.9, 2.9], color=BLUE, stroke_width=5)
        label = Text("L(w)", font_size=30, color=GREY_A, font="Helvetica")
        label.next_to(ax.c2p(-2.7, f(-2.7)), UR, buff=0.25)

        self.play(Create(ax, run_time=1), Create(curve, run_time=1.2), FadeIn(label))

        x, lr = 2.7, 0.35
        dot = Dot(ax.c2p(x, f(x)), color=YELLOW, radius=0.1)
        self.play(FadeIn(dot, scale=0.4))
        self.wait(0.3)

        for _ in range(10):
            new_x = x - lr * df(x)
            step = Arrow(
                ax.c2p(x, f(x)),
                ax.c2p(new_x, f(new_x)),
                buff=0,
                color=YELLOW,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.18,
            )
            self.play(GrowArrow(step), run_time=0.35)
            self.play(
                dot.animate.move_to(ax.c2p(new_x, f(new_x))),
                step.animate.set_opacity(0.3),
                run_time=0.35,
            )
            x = new_x

        self.wait(2)

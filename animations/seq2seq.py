"""Manim scenes for the seq2seq post.

Render with: make anims
Text() uses Pango, so no LaTeX installation is required (and Cyrillic
just works).

One numeric story runs through every scene: the words of "I love you"
become the same little vectors everywhere, and the memory follows the
same trajectory h0 -> h1 -> h2 -> h3, so the reader can track actual
numbers from diagram to diagram.
"""

from manim import *

from beats import BeatScene

BG = "#14161a"  # matches the blog's dark background

X_VALS = {
    "I": [0.9, 0.1, 0.4],
    "love": [0.2, 0.8, 0.6],
    "you": [0.4, 0.5, 0.1],
}
# Chosen so the attention dot products come out whole:
# D_VALS[2]·h = 0, 0, 2 and D_VALS[1]·h = 2, 0, 0 (exactly).
H_VALS = [
    [0.0, 0.0, 0.0, 0.0],
    [0.7, -0.6, 0.6, -0.6],
    [0.5, 0.0, -0.5, 0.0],
    [0.9, 0.8, 0.7, 0.8],
]
OUT_VALS = [0.7, 0.3]


def fmt(v):
    if v == 0:
        return "0"
    sign = "-" if v < 0 else ""
    return f"{sign}.{int(round(abs(v) * 10))}"


def value_texts(col, vals, font_size=15, color=WHITE):
    """Numbers living inside a column of unit-circles (or squares)."""
    texts = VGroup()
    for c, v in zip(col, vals):
        t = Text(fmt(v), font_size=font_size, color=color, font="Helvetica")
        if v < 0:  # "-.6" is a character wider than ".6"
            t.scale(0.85)
        t.move_to(c.get_center())
        texts.add(t)
    return texts


def val_column(vals, side=0.3, font_size=13, stroke=BLUE, fill=0.18,
               fill_color=None):
    """A vector drawn honestly: squares with the actual numbers inside."""
    squares = VGroup(
        *[
            Square(side, stroke_color=stroke, stroke_width=2.5,
                   fill_color=fill_color or BLUE, fill_opacity=fill)
            for _ in vals
        ]
    ).arrange(DOWN, buff=0.06)
    nums = value_texts(squares, vals, font_size=font_size)
    return VGroup(squares, nums)


def word_row(words, y, font_size=40, xs=None, center_x=0):
    """Lay a sentence out as one Text (so baselines line up), then split
    it into per-word groups. If xs is given, each word is shifted
    horizontally to that x; vertical positions are never touched."""
    sentence = Text(" ".join(words), font_size=font_size, font="Helvetica")
    sentence.move_to([center_x, y, 0])
    parts, i = [], 0
    for w in words:
        parts.append(sentence[i : i + len(w)])  # spaces produce no glyphs
        i += len(w)
    if xs is not None:
        for part, x in zip(parts, xs):
            part.shift(RIGHT * (x - part.get_center()[0]))
    return VGroup(*parts)


class WordByWord(BeatScene):
    """Why word-for-word translation fails: crossed alignments, then a
    word with no partner at all."""

    def construct(self):
        self.camera.background_color = BG

        def link(row_a, a, row_b, b, color):
            return Line(
                [a.get_center()[0], row_a.get_bottom()[1] - 0.2, 0],
                [b.get_center()[0], row_b.get_top()[1] + 0.2, 0],
                color=color,
                stroke_width=3.5,
            )

        # Phase 1: "I read Ivan's book" -> Russian forces "книгу Ивана"
        # (owner after the thing owned), so the alignment lines cross.
        en = word_row(["I", "read", "Ivan's", "book"], 1.6, xs=[-4, -1.5, 1.5, 4])
        ru = word_row(["Я", "читал", "книгу", "Ивана"], -1.6, xs=[-4, -1.5, 1.5, 4])

        self.play(FadeIn(en, lag_ratio=0.2, run_time=1))
        self.play(FadeIn(ru, lag_ratio=0.2, run_time=1))
        self.wait(0.3)

        lines = VGroup(
            link(en, en[0], ru, ru[0], GREY_B),
            link(en, en[1], ru, ru[1], GREY_B),
            link(en, en[2], ru, ru[3], BLUE),
            link(en, en[3], ru, ru[2], BLUE),
        )
        for ln in lines:
            self.play(Create(ln), run_time=0.55)
        self.wait(1.4)

        # Phase 2: "I am hungry" -> "am" has nowhere to go.
        self.play(FadeOut(lines), FadeOut(en), FadeOut(ru))

        en2 = word_row(["I", "am", "hungry"], 1.6, xs=[-3, 0, 3])
        ru2 = word_row(["Я", "голоден"], -1.6, xs=[-1.5, 1.5])
        self.play(FadeIn(en2, lag_ratio=0.2), FadeIn(ru2, lag_ratio=0.2))

        self.play(Create(link(en2, en2[0], ru2, ru2[0], GREY_B)), run_time=0.55)
        self.play(Create(link(en2, en2[2], ru2, ru2[1], GREY_B)), run_time=0.55)

        dangling = DashedLine(
            [0, en2.get_bottom()[1] - 0.2, 0],
            [0, -0.9, 0],
            color=RED,
            stroke_width=3.5,
        )
        question = Text("?", font_size=36, color=RED, font="Helvetica")
        question.next_to(dangling, DOWN, buff=0.15)
        self.play(en2[1].animate.set_color(RED), Create(dangling), run_time=0.7)
        self.play(FadeIn(question, scale=0.5))
        self.wait(2)


class Seq2SeqPipeline(BeatScene):
    """Encoder reads word by word, hands one context vector to the
    decoder, decoder emits the output word by word."""

    def construct(self):
        self.camera.background_color = BG

        def box(label, color, x):
            rect = RoundedRectangle(
                corner_radius=0.15,
                width=3.0,
                height=1.7,
                stroke_color=color,
                stroke_width=4,
                fill_color=color,
                fill_opacity=0.08,
            ).move_to([x, 0, 0])
            text = Text(label, font_size=32, color=color, font="Helvetica")
            text.move_to(rect)
            return VGroup(rect, text)

        encoder = box("Encoder", BLUE, -4)
        decoder = box("Decoder", GREEN, 4)
        self.play(FadeIn(encoder), FadeIn(decoder))

        # Input words queue above the encoder and get read one at a time.
        en_words = word_row(["I", "love", "you"], 2.4, font_size=34, center_x=-4)
        self.play(FadeIn(en_words, lag_ratio=0.2))
        self.wait(0.3)

        for word in en_words:
            self.play(
                word.animate.move_to(encoder[0].get_center()).set_opacity(0),
                Indicate(encoder[0], color=BLUE, scale_factor=1.03),
                run_time=0.8,
            )

        # The context: one small vector — the encoder's final memory,
        # actual numbers included.
        context = val_column(H_VALS[3], side=0.4, font_size=17, fill=0.3)
        context.next_to(encoder, RIGHT, buff=0.35)
        label = Text("context", font_size=26, color=BLUE, font="Helvetica")
        label.next_to(context, DOWN, buff=0.25)

        self.play(FadeIn(context, scale=0.6), FadeIn(label))
        self.wait(0.4)

        # Slide straight across: a pure horizontal shift, so the squares
        # stay level while the label rides along underneath.
        target_x = decoder[0].get_left()[0] - 0.35 - context.width / 2
        self.play(
            VGroup(context, label).animate.shift(
                RIGHT * (target_x - context.get_center()[0])
            ),
            run_time=1.2,
        )
        self.play(
            context.animate.move_to(decoder[0].get_center()).set_opacity(0),
            FadeOut(label),
            Indicate(decoder[0], color=GREEN, scale_factor=1.03),
            run_time=0.8,
        )

        # The decoder emits the output one word at a time.
        ru_words = word_row(["Я", "тебя", "люблю"], 2.4, font_size=34, center_x=4)

        for word in ru_words:
            start = word.copy().move_to(decoder[0].get_center()).set_opacity(0)
            self.add(start)
            self.play(
                start.animate.move_to(word.get_center()).set_opacity(1),
                Indicate(decoder[0], color=GREEN, scale_factor=1.03),
                run_time=0.8,
            )
        self.wait(2)


BOX_XS = [-3.5, 0.0, 3.5]
H_XS = [-5.4, -1.75, 1.75, 5.4]  # where h0..h3 sit between/beside the cells


def rnn_cell(x, color=BLUE, width=1.6, height=1.2, font_size=24):
    rect = RoundedRectangle(
        corner_radius=0.12,
        width=width,
        height=height,
        stroke_color=color,
        stroke_width=3.5,
        fill_color=color,
        fill_opacity=0.08,
    ).move_to([x, 0, 0])
    label = Text("RNN", font_size=font_size, color=color, font="Helvetica")
    label.move_to(rect)
    return VGroup(rect, label)


def h_label(t, color=GREY_A):
    return Text(f"h{'₀₁₂₃'[t]}", font_size=24, color=color, font="Helvetica")


def step_counter(t, color=GREY_A):
    return Text(f"t = {t}", font_size=28, color=color,
                font="Helvetica").move_to([-6, 3.15, 0])


def rnn_skeleton():
    cells = VGroup(*[rnn_cell(x) for x in BOX_XS])
    words = VGroup(
        *[
            Text(w, font_size=30, font="Helvetica").move_to([x, -2.1, 0])
            for w, x in zip(["I", "love", "you"], BOX_XS)
        ]
    )
    arrows = VGroup(
        *[
            Arrow(
                words[i].get_top(),
                cells[i][0].get_bottom(),
                buff=0.15,
                color=GREY_B,
                stroke_width=3,
                max_tip_length_to_length_ratio=0.25,
            )
            for i in range(3)
        ]
    )
    return cells, words, arrows


class RNNReads(BeatScene):
    """The unrolled walkthrough at the box level: one word per numbered
    time step, the memory's numbers changing, the final memory = context."""

    def construct(self):
        self.camera.background_color = BG

        cells, words, arrows = rnn_skeleton()
        self.play(FadeIn(cells, lag_ratio=0.15), FadeIn(words, lag_ratio=0.15),
                  FadeIn(arrows, lag_ratio=0.15))

        counter = step_counter(0)
        h = val_column(H_VALS[0], side=0.32, font_size=14,
                       stroke=GREY_B).move_to([H_XS[0], 0, 0])
        lab = h_label(0, color=GREY_B).next_to(h, UP, buff=0.2)
        self.play(FadeIn(h), FadeIn(lab), FadeIn(counter))
        self.wait(0.4)

        for t in range(1, 4):
            cell = cells[t - 1]
            self.play(
                h.animate.move_to(cell[0].get_center()).set_opacity(0),
                FadeOut(lab),
                Transform(counter, step_counter(t)),
                Indicate(cell[0], color=BLUE, scale_factor=1.04),
                Indicate(words[t - 1], color=BLUE, scale_factor=1.1),
                run_time=0.8,
            )
            h = val_column(H_VALS[t], side=0.32, font_size=14)
            h.move_to(cell[0].get_center()).set_opacity(0)
            self.add(h)
            lab = h_label(t).next_to([H_XS[t], 0.75, 0], UP, buff=0.1)
            self.play(
                h.animate.move_to([H_XS[t], 0, 0]).set_opacity(1),
                FadeIn(lab),
                run_time=0.7,
            )
        ctx = Text("context", font_size=24, color=BLUE, font="Helvetica")
        ctx.next_to(h, DOWN, buff=0.25)
        self.play(FadeIn(ctx), Indicate(h, color=BLUE, scale_factor=1.15))
        self.wait(2)


class RNNTrail(BeatScene):
    """What every step leaves behind: an output on top, a hidden-state
    snapshot along the bottom; seq2seq keeps only the last snapshot."""

    def construct(self):
        self.camera.background_color = BG

        cells, words, arrows = rnn_skeleton()
        trail = VGroup()
        trail_labs = VGroup()
        for t in range(1, 4):
            col = val_column(H_VALS[t], side=0.28,
                             font_size=12).move_to([H_XS[t], 0, 0])
            lab = h_label(t).next_to(col, UP, buff=0.2)
            trail.add(col)
            trail_labs.add(lab)
        self.add(cells, words, arrows, trail, trail_labs)
        self.wait(0.5)

        outs = VGroup()
        out_arrows = VGroup()
        for cell in cells:
            col = VGroup(
                *[
                    Square(0.16, stroke_color=GREEN, stroke_width=2.5,
                           fill_color=GREEN, fill_opacity=0.3)
                    for _ in range(3)
                ]
            ).arrange(DOWN, buff=0.05)
            col.move_to([cell[0].get_center()[0], 1.9, 0])
            arr = Arrow(
                cell[0].get_top(),
                col.get_bottom(),
                buff=0.12,
                color=GREY_B,
                stroke_width=3,
                max_tip_length_to_length_ratio=0.3,
            )
            outs.add(col)
            out_arrows.add(arr)
        outs_lab = Text("outputs", font_size=24, color=GREEN, font="Helvetica")
        outs_lab.move_to([-5.4, 1.9, 0])
        for arr, col in zip(out_arrows, outs):
            self.play(GrowArrow(arr), FadeIn(col, shift=UP * 0.2), run_time=0.5)
        self.play(FadeIn(outs_lab))
        self.wait(0.8)

        # The encoder ignores its outputs; what survives is the last snapshot.
        self.play(
            outs.animate.set_opacity(0.2),
            out_arrows.animate.set_opacity(0.2),
            outs_lab.animate.set_opacity(0.3),
        )
        self.play(Indicate(trail[0], color=BLUE), run_time=0.5)
        self.play(Indicate(trail[1], color=BLUE), run_time=0.5)
        ctx = Text("context", font_size=24, color=BLUE, font="Helvetica")
        ctx.next_to(trail[2], DOWN, buff=0.25)
        self.play(
            trail[0].animate.set_opacity(0.3),
            trail[1].animate.set_opacity(0.3),
            trail_labs[0].animate.set_opacity(0.4),
            trail_labs[1].animate.set_opacity(0.4),
            Indicate(trail[2], color=BLUE, scale_factor=1.15),
            FadeIn(ctx),
        )
        self.wait(2)


def unit_column(n, x, color, gap=0.85):
    """A layer: n unit-circles stacked at x, opaque so edges tuck behind."""
    return VGroup(
        *[
            Circle(radius=0.27, stroke_color=color, stroke_width=3,
                   fill_color=BG, fill_opacity=1)
            for _ in range(n)
        ]
    ).arrange(DOWN, buff=gap - 0.54).move_to([x, 0, 0])


def net_edges(col_a, col_b):
    return VGroup(
        *[
            Line(a.get_center(), b.get_center(), stroke_width=1.8,
                 color=GREY_C).set_opacity(0.55)
            for a in col_a
            for b in col_b
        ]
    )


def edge_flash(edges):
    return [
        ShowPassingFlash(
            e.copy().set_color(WHITE).set_opacity(1).set_stroke(width=3),
            time_width=0.5,
        )
        for e in edges
    ]


def layer_label(text, x, color=GREY_B):
    return Text(text, font_size=22, color=color, font="Helvetica").move_to(
        [x, -2.4, 0]
    )


def build_net():
    in_col = unit_column(3, -3, GREY_A)
    hid_col = unit_column(4, 0, BLUE)
    out_col = unit_column(2, 3, GREEN)
    e1 = net_edges(in_col, hid_col)
    e2 = net_edges(hid_col, out_col)
    labels = VGroup(
        layer_label("input", -3),
        layer_label("hidden layer", 0),
        layer_label("output", 3),
    )
    return in_col, hid_col, out_col, e1, e2, labels


class OrdinaryNet(BeatScene):
    """Anatomy of a plain feedforward network: units, layers, the hidden
    layer — then actual numbers flowing left to right."""

    def construct(self):
        self.camera.background_color = BG
        in_col, hid_col, out_col, e1, e2, labels = build_net()

        self.play(FadeIn(in_col, lag_ratio=0.1), FadeIn(labels[0]))
        self.play(Create(e1, lag_ratio=0.05, run_time=0.9),
                  FadeIn(hid_col, lag_ratio=0.1), FadeIn(labels[1]))
        self.play(Create(e2, lag_ratio=0.05, run_time=0.7),
                  FadeIn(out_col, lag_ratio=0.1), FadeIn(labels[2]))
        self.wait(0.4)

        ptr_text = Text("one unit", font_size=22, color=GREY_A,
                        font="Helvetica").move_to([2.1, 2.2, 0])
        ptr = Arrow(ptr_text.get_left(), hid_col[0].get_center() + UR * 0.15,
                    buff=0.12, color=GREY_A, stroke_width=2.5,
                    max_tip_length_to_length_ratio=0.15)
        self.play(FadeIn(ptr_text), GrowArrow(ptr))
        self.wait(0.8)

        # Real numbers flow through: in the inputs, transformed in the
        # hidden layer, out the other side.
        in_v = value_texts(in_col, X_VALS["I"])
        hid_v = value_texts(hid_col, H_VALS[1])
        out_v = value_texts(out_col, OUT_VALS)
        self.play(FadeIn(in_v, lag_ratio=0.2))
        self.play(*edge_flash(e1), run_time=0.9)
        self.play(FadeIn(hid_v, lag_ratio=0.15), run_time=0.5)
        self.play(*edge_flash(e2), run_time=0.7)
        self.play(FadeIn(out_v, lag_ratio=0.2), run_time=0.5)
        self.wait(2)


class RNNLoop(BeatScene):
    """The recurrence, run for real: numbered time steps, words becoming
    numbers, the memory's numbers riding the loop back in, and a photo
    of the network per step — unrolling is just the photos side by side."""

    def construct(self):
        self.camera.background_color = BG

        in_col = unit_column(3, -2.2, GREY_A).shift(UP * 0.9)
        hid_col = unit_column(4, 1.2, BLUE).shift(UP * 0.9)
        e1 = net_edges(in_col, hid_col)
        in_lab = Text("input", font_size=22, color=GREY_B,
                      font="Helvetica").move_to([-2.2, 2.45, 0])
        hid_lab = Text("hidden layer", font_size=22, color=GREY_B,
                       font="Helvetica").move_to([3.55, 0.9, 0])

        counter = step_counter(0)
        h_vals = value_texts(hid_col, H_VALS[0])

        self.play(FadeIn(in_col, lag_ratio=0.1), FadeIn(in_lab),
                  Create(e1, lag_ratio=0.03, run_time=0.8),
                  FadeIn(hid_col, lag_ratio=0.1), FadeIn(hid_lab))
        self.play(FadeIn(h_vals, lag_ratio=0.1), FadeIn(counter))

        loop = Arc(radius=0.55, start_angle=-0.2 * PI, angle=1.4 * PI,
                   arc_center=[1.2, 3.05, 0], color=BLUE, stroke_width=3.5)
        loop.add_tip(tip_length=0.16, tip_width=0.16)
        self.play(Create(loop), run_time=1)
        self.wait(0.5)

        photos = []
        slot_xs = [-4, 0, 4]
        for t, w in enumerate(["I", "love", "you"], start=1):
            word = Text(w, font_size=30, font="Helvetica")
            word.move_to([-2.2, -1.35, 0])
            in_v = value_texts(in_col, X_VALS[w])
            self.play(Transform(counter, step_counter(t)),
                      FadeIn(word, shift=UP * 0.2), run_time=0.6)
            self.play(FadeIn(in_v, lag_ratio=0.2), run_time=0.5)

            # The memory's current numbers ride the loop back in while
            # the new word's numbers flow across the edges.
            packet = val_column(H_VALS[t - 1], side=0.26, font_size=11,
                                fill=0.35)
            packet.move_to(loop.point_from_proportion(0))
            self.add(packet)
            self.play(MoveAlongPath(packet, loop), *edge_flash(e1),
                      run_time=1.1)
            new_vals = value_texts(hid_col, H_VALS[t])
            self.play(FadeOut(packet, shift=DOWN * 0.3),
                      Transform(h_vals, new_vals), run_time=0.6)
            self.wait(0.3)

            # Photograph the whole network at this moment.
            snap_src = VGroup(e1, in_col, hid_col, in_v, h_vals, word)
            photo = snap_src.copy()
            photo.generate_target()
            photo.target.scale(0.4).move_to([slot_xs[t - 1], -2.55, 0])
            chip = Text(f"t = {t}", font_size=20, color=GREY_A,
                        font="Helvetica")
            chip.next_to(photo.target, UP, buff=0.12)
            self.play(MoveToTarget(photo), FadeIn(chip), run_time=0.9)
            photos.append(VGroup(photo, chip))

            self.play(FadeOut(word), FadeOut(in_v), run_time=0.4)

        # Unroll: the photos ARE the unrolled diagram.
        self.play(
            FadeOut(VGroup(in_col, hid_col, e1, h_vals, in_lab, hid_lab,
                           loop, counter))
        )
        self.play(
            *[
                p.animate.scale(1.85).move_to([x, 0.4, 0])
                for p, x in zip(photos, [-4.3, 0, 4.3])
            ],
            run_time=1.2,
        )
        rects = VGroup(
            *[
                RoundedRectangle(
                    corner_radius=0.15,
                    width=p.width + 0.35,
                    height=p.height + 0.35,
                    stroke_color=BLUE,
                    stroke_width=3,
                ).move_to(p.get_center())
                for p in photos
            ]
        )
        self.play(FadeIn(rects))
        link_arrows = VGroup(
            *[
                Arrow(rects[i].get_right(), rects[i + 1].get_left(), buff=0.1,
                      color=BLUE, stroke_width=3.5,
                      max_tip_length_to_length_ratio=0.35)
                for i in range(2)
            ]
        )
        self.play(GrowArrow(link_arrows[0]), GrowArrow(link_arrows[1]))
        self.wait(2.5)


class KingQueen(BeatScene):
    """Embeddings as coordinates: words are points, and also arrows from
    the origin. king - man + woman is walked tip to tail, one equation
    term per move, and the walk lands on queen."""

    def construct(self):
        self.camera.background_color = BG

        ax = Axes(
            x_range=[0, 7, 1],
            y_range=[0, 5, 1],
            x_length=8.5,
            y_length=5.2,
            axis_config={"include_ticks": True, "color": GREY_C},
            tips=False,
        ).move_to([0, -0.7, 0])
        self.play(Create(ax, run_time=1))

        # word: (x, y, dot color, label direction)
        data = {
            "man": (2, 1, GREY_A, DOWN),
            "woman": (5, 1, GREY_A, DOWN),
            "king": (2, 4, BLUE, UP),
            "queen": (5, 4, GREEN, UP),
        }
        dots, labels, chips = {}, {}, {}
        for w, (x, y, color, direction) in data.items():
            p = ax.c2p(x, y)
            dots[w] = Dot(p, radius=0.09, color=color)
            labels[w] = Text(w, font_size=26, color=color, font="Helvetica")
            labels[w].next_to(dots[w], direction, buff=0.18)
            chips[w] = Text(f"({x}, {y})", font_size=20, color=GREY_B,
                            font="Helvetica")
            chips[w].next_to(labels[w], direction, buff=0.12)

        # "man" first, with helper lines tying its numbers to the axes.
        helpers = VGroup(
            DashedLine(dots["man"].get_center(), ax.c2p(2, 0), color=GREY_C,
                       stroke_width=2),
            DashedLine(dots["man"].get_center(), ax.c2p(0, 1), color=GREY_C,
                       stroke_width=2),
        )
        self.play(FadeIn(dots["man"], scale=0.5), FadeIn(labels["man"]),
                  FadeIn(chips["man"]))
        self.play(Create(helpers), run_time=0.7)
        self.wait(0.6)
        self.play(FadeOut(helpers))
        for w in ["woman", "king", "queen"]:
            self.play(FadeIn(dots[w], scale=0.5), FadeIn(labels[w]),
                      FadeIn(chips[w]), run_time=0.5)
        self.wait(0.5)

        # The equation builds at the top, one term per move below.
        eq_words = VGroup(
            Text("king", font_size=30, color=BLUE, font="Helvetica"),
            Text("− man", font_size=30, font="Helvetica"),
            Text("+ woman", font_size=30, font="Helvetica"),
            Text("≈ queen", font_size=30, color=GREEN, font="Helvetica"),
        ).arrange(RIGHT, buff=0.3).move_to([0, 3.45, 0])
        eq_nums = VGroup(
            Text("(2, 4)", font_size=22, color=GREY_B, font="Helvetica"),
            Text("− (2, 1)", font_size=22, color=GREY_B, font="Helvetica"),
            Text("+ (5, 1)", font_size=22, color=GREY_B, font="Helvetica"),
            Text("≈ (5, 4)", font_size=22, color=GREY_B, font="Helvetica"),
        ).arrange(RIGHT, buff=0.3).move_to([0, 2.9, 0])

        org = ax.c2p(0, 0)

        def vec(word):
            return Arrow(org, dots[word].get_center(), buff=0, color=BLUE,
                         stroke_width=4, max_tip_length_to_length_ratio=0.08)

        # king: a point, but also an arrow from the origin. The walker
        # starts on its tip.
        v_king = vec("king")
        walker = Dot(dots["king"].get_center(), radius=0.11, color=WHITE)
        self.play(FadeIn(eq_words[0]), FadeIn(eq_nums[0]),
                  GrowArrow(v_king), FadeIn(walker, scale=0.5), run_time=0.9)
        self.wait(0.4)

        # - man: a copy of man's arrow flips (the original stays put,
        # dimmed), hangs off king tip to tail, and the walker rides it
        # down to king - man = (0, 3).
        v_man = vec("man")
        self.play(FadeIn(eq_words[1]), FadeIn(eq_nums[1]), GrowArrow(v_man),
                  run_time=0.9)
        hop1 = v_man.copy()
        self.play(Rotate(hop1, PI, about_point=hop1.get_center()),
                  v_man.animate.set_opacity(0.35), run_time=0.5)
        self.play(hop1.animate.shift(dots["king"].get_center()
                                     - dots["man"].get_center()),
                  v_king.animate.set_opacity(0.35), run_time=0.9)
        mid = ax.c2p(0, 3)
        self.play(walker.animate.move_to(mid), run_time=0.9)
        im_dot = Dot(mid, radius=0.07, color=GREY_A)
        im_chip = Text("(0, 3)", font_size=20, color=GREY_B,
                       font="Helvetica").next_to(im_dot, UL, buff=0.15)
        self.play(FadeIn(im_dot), FadeIn(im_chip), run_time=0.4)
        self.wait(0.3)

        # + woman: a copy of woman's arrow chains on as is, and the
        # walker rides it up to (5, 4). Only now does the landing spot
        # get named.
        v_woman = vec("woman")
        self.play(FadeIn(eq_words[2]), FadeIn(eq_nums[2]),
                  GrowArrow(v_woman), run_time=0.9)
        hop2 = v_woman.copy()
        self.play(hop2.animate.shift(mid - org),
                  v_woman.animate.set_opacity(0.35), run_time=0.9)
        end = dots["queen"].get_center()
        self.play(walker.animate.move_to(end), run_time=0.9)
        ring = Circle(radius=0.28, color=GREEN, stroke_width=4)
        ring.move_to(end)
        self.play(FadeIn(eq_words[3]), FadeIn(eq_nums[3]), Create(ring),
                  Indicate(labels["queen"], color=GREEN))
        self.wait(1.0)

        # The two hops net out to one step, and it's the same step that
        # takes man to woman: the famous direction.
        net = Arrow(dots["king"].get_center(), end, buff=0.3, color=WHITE,
                    stroke_width=4, max_tip_length_to_length_ratio=0.08)
        twin = Arrow(dots["man"].get_center(), dots["woman"].get_center(),
                     buff=0.12, color=WHITE, stroke_width=4,
                     max_tip_length_to_length_ratio=0.08)
        self.play(VGroup(hop1, hop2).animate.set_opacity(0.3),
                  GrowArrow(net), run_time=0.9)
        self.play(GrowArrow(twin), run_time=0.7)
        self.wait(2.5)


D_VALS = [
    [0.9, 0.8, 0.7, 0.8],    # the decoder starts from the context itself
    [0.8, -0.7, 0.8, -0.9],  # h4: dot products with h1, h2, h3 = 2, 0, 0
    [0.6, 0.7, 0.6, 0.6],    # h5: dot products with h1, h2, h3 = 0, 0, 2
]


class DecoderWrites(BeatScene):
    """The decoder's turn: context in as the starting hidden state, one
    word out per time step, each word fed back as the next input."""

    def construct(self):
        self.camera.background_color = BG

        cells = VGroup(*[rnn_cell(x, color=GREEN) for x in BOX_XS])
        self.play(FadeIn(cells, lag_ratio=0.15))

        counter = step_counter(1)
        context = val_column(D_VALS[0], side=0.32, font_size=14)
        context.move_to([-6.5, 0, 0])
        ctx_lab = Text("context", font_size=22, color=BLUE,
                       font="Helvetica").next_to(context, DOWN, buff=0.2)
        self.play(FadeIn(counter),
                  VGroup(context, ctx_lab).animate.shift(RIGHT * 1.1),
                  run_time=0.9)
        self.wait(0.3)

        out_words = ["Я", "тебя", "люблю"]
        in_pos = [[x, -2.1, 0] for x in BOX_XS]
        out_pos = [[x, 2.1, 0] for x in BOX_XS]

        start_tok = Text("<start>", font_size=24, color=GREY_B,
                         font="Helvetica").move_to(in_pos[0])
        h = context
        prev_out = None
        for t in range(3):
            cell = cells[t]
            # This step's input arrives: <start> first, then the word
            # the decoder just produced.
            if t == 0:
                inp = start_tok
                self.play(FadeIn(inp, shift=UP * 0.2), run_time=0.5)
            else:
                arc = ArcBetweenPoints(
                    [BOX_XS[t - 1] + 0.5, 1.95, 0],
                    [BOX_XS[t] - 0.5, -1.85, 0],
                    angle=1.6,
                ).set_stroke(GREY_B, 2.5, opacity=0.7)
                inp = prev_out.copy()
                self.play(Create(arc), run_time=0.5)
                self.play(MoveAlongPath(inp, arc), run_time=0.9)
                self.play(inp.animate.move_to(in_pos[t]),
                          arc.animate.set_stroke(opacity=0.25), run_time=0.4)
            in_arrow = Arrow(inp.get_top(), cell[0].get_bottom(), buff=0.15,
                             color=GREY_B, stroke_width=3,
                             max_tip_length_to_length_ratio=0.25)
            self.play(GrowArrow(in_arrow), run_time=0.4)

            # Hidden state flows in, the cell computes.
            anims = [h.animate.move_to(cell[0].get_center()).set_opacity(0),
                     Indicate(cell[0], color=GREEN, scale_factor=1.04)]
            if t == 0:
                anims.append(FadeOut(ctx_lab))
            else:
                anims.append(Transform(counter, step_counter(t + 1)))
            self.play(*anims, run_time=0.8)

            # One output word comes out the top.
            out_arrow = Arrow(cell[0].get_top(), [BOX_XS[t], 1.75, 0],
                              buff=0.1, color=GREY_B, stroke_width=3,
                              max_tip_length_to_length_ratio=0.3)
            word = Text(out_words[t], font_size=30, font="Helvetica")
            word.move_to(out_pos[t])
            self.play(GrowArrow(out_arrow), FadeIn(word, shift=UP * 0.2),
                      run_time=0.6)
            prev_out = word

            # The updated hidden state emerges, headed for the next cell.
            if t < 2:
                h = val_column(D_VALS[t + 1], side=0.32, font_size=14)
                h.move_to(cell[0].get_center()).set_opacity(0)
                self.add(h)
                self.play(h.animate.move_to([H_XS[t + 1], 0, 0])
                          .set_opacity(1), run_time=0.6)
        self.wait(2.5)


class EndToEnd(BeatScene):
    """The whole run on one clock: encoder steps t = 1..3 build the
    context, decoder steps t = 4..6 spend it."""

    def construct(self):
        self.camera.background_color = BG

        E_XS = [-5.9, -3.7, -1.5]
        D_XS = [1.5, 3.7, 5.9]
        enc = VGroup(*[rnn_cell(x, BLUE, 1.5, 1.1, 20) for x in E_XS])
        dec = VGroup(*[rnn_cell(x, GREEN, 1.5, 1.1, 20) for x in D_XS])
        enc_lab = Text("Encoder", font_size=26, color=BLUE,
                       font="Helvetica").move_to([-3.7, 3.0, 0])
        dec_lab = Text("Decoder", font_size=26, color=GREEN,
                       font="Helvetica").move_to([3.7, 3.0, 0])
        self.play(FadeIn(enc, lag_ratio=0.1), FadeIn(enc_lab),
                  FadeIn(dec, lag_ratio=0.1), FadeIn(dec_lab))

        in_words = VGroup(
            *[
                Text(w, font_size=26, font="Helvetica").move_to([x, -1.9, 0])
                for w, x in zip(["I", "love", "you"], E_XS)
            ]
        )
        in_arrows = VGroup(
            *[
                Arrow(in_words[i].get_top(), enc[i][0].get_bottom(),
                      buff=0.12, color=GREY_B, stroke_width=2.5,
                      max_tip_length_to_length_ratio=0.25)
                for i in range(3)
            ]
        )
        counter = step_counter(1)
        self.play(FadeIn(in_words, lag_ratio=0.15),
                  *[GrowArrow(a) for a in in_arrows], FadeIn(counter))
        self.wait(0.3)

        # Encoder: t = 1..3, the memory filling up.
        h = None
        h_mids = [-4.8, -2.6, 0.0]
        for t in range(1, 4):
            cell = enc[t - 1]
            anims = [Transform(counter, step_counter(t)),
                     Indicate(cell[0], color=BLUE, scale_factor=1.05),
                     Indicate(in_words[t - 1], color=BLUE,
                              scale_factor=1.1)]
            if h is not None:
                anims.append(
                    h.animate.move_to(cell[0].get_center()).set_opacity(0))
            self.play(*anims, run_time=0.8)
            h = val_column(H_VALS[t], side=0.24, font_size=11)
            h.move_to(cell[0].get_center()).set_opacity(0)
            self.add(h)
            self.play(h.animate.move_to([h_mids[t - 1], 0, 0])
                      .set_opacity(1), run_time=0.6)

        # The handoff: the final memory is the context.
        ctx_lab = Text("context", font_size=22, color=BLUE,
                       font="Helvetica").next_to(h, DOWN, buff=0.2)
        self.play(FadeIn(ctx_lab), Indicate(h, color=BLUE,
                                            scale_factor=1.2))
        self.wait(0.6)

        # Decoder: t = 4..6, spending the context word by word.
        out_words = ["Я", "тебя", "люблю"]
        d_mids = [2.6, 4.8]
        start_tok = Text("<start>", font_size=20, color=GREY_B,
                         font="Helvetica").move_to([D_XS[0], -1.9, 0])
        prev_out = None
        for i in range(3):
            cell = dec[i]
            if i == 0:
                inp = start_tok
                self.play(FadeIn(inp, shift=UP * 0.2), run_time=0.4)
            else:
                arc = ArcBetweenPoints(
                    [D_XS[i - 1] + 0.4, 1.7, 0],
                    [D_XS[i] - 0.4, -1.65, 0],
                    angle=1.3,
                ).set_stroke(GREY_B, 2.5, opacity=0.7)
                inp = prev_out.copy()
                self.play(Create(arc), run_time=0.4)
                self.play(MoveAlongPath(inp, arc), run_time=0.7)
                self.play(inp.animate.move_to([D_XS[i], -1.9, 0]),
                          arc.animate.set_stroke(opacity=0.25),
                          run_time=0.3)
            in_arrow = Arrow(inp.get_top(), cell[0].get_bottom(), buff=0.12,
                             color=GREY_B, stroke_width=2.5,
                             max_tip_length_to_length_ratio=0.25)
            self.play(GrowArrow(in_arrow), run_time=0.3)

            anims = [h.animate.move_to(cell[0].get_center()).set_opacity(0),
                     Transform(counter, step_counter(i + 4)),
                     Indicate(cell[0], color=GREEN, scale_factor=1.05)]
            if i == 0:
                anims.append(FadeOut(ctx_lab))
            self.play(*anims, run_time=0.8)

            out_arrow = Arrow(cell[0].get_top(), [D_XS[i], 1.55, 0],
                              buff=0.1, color=GREY_B, stroke_width=2.5,
                              max_tip_length_to_length_ratio=0.3)
            word = Text(out_words[i], font_size=26, font="Helvetica")
            word.move_to([D_XS[i], 1.9, 0])
            self.play(GrowArrow(out_arrow), FadeIn(word, shift=UP * 0.2),
                      run_time=0.5)
            prev_out = word

            if i < 2:
                h = val_column(D_VALS[i + 1], side=0.24, font_size=11)
                h.move_to(cell[0].get_center()).set_opacity(0)
                self.add(h)
                self.play(h.animate.move_to([d_mids[i], 0, 0])
                          .set_opacity(1), run_time=0.5)
        self.wait(2.5)


ATT_W2 = [0.1, 0.1, 0.8]          # attention weights while writing "тебя"
CTX_STEP2 = [0.8, 0.6, 0.6, 0.6]  # .1 h1 + .1 h2 + .8 h3, rounded


class AttentionStep(BeatScene):
    """One decoding step with attention, math on screen: score, softmax,
    then the weighted sum assembled as an explicit equation."""

    def construct(self):
        self.camera.background_color = BG

        xs = [-5.7, -4.4, -3.1]
        cols = VGroup(
            *[
                val_column(H_VALS[t], side=0.3, font_size=13).move_to(
                    [x, 1.7, 0])
                for t, x in zip([1, 2, 3], xs)
            ]
        )
        labs = VGroup(
            *[h_label(t).next_to(c, UP, buff=0.15)
              for t, c in zip([1, 2, 3], cols)]
        )
        words = word_row(["I", "love", "you"], 0.68, font_size=20, xs=xs)
        words.set_color(GREY_B)
        cell = rnn_cell(4.8, GREEN).shift(UP * 1.7)
        cell_lab = Text("Decoder", font_size=22, color=GREEN,
                        font="Helvetica").next_to(cell, DOWN, buff=0.25)
        dstate = val_column(D_VALS[2], side=0.26, font_size=12,
                            stroke=GREEN, fill_color=GREEN)
        dstate.next_to(cell[0], LEFT, buff=0.35)
        dlab = Text("decoder state", font_size=16, color=GREY_B,
                    font="Helvetica").next_to(dstate, DOWN, buff=0.18)
        self.play(FadeIn(cols, lag_ratio=0.15), FadeIn(labs, lag_ratio=0.15),
                  FadeIn(words, lag_ratio=0.15), FadeIn(cell),
                  FadeIn(cell_lab), FadeIn(dstate), FadeIn(dlab))
        self.wait(0.4)

        # Score each snapshot for relevance to the word being written.
        # The score is a dot product, and the arithmetic goes on screen:
        # a copy of the decoder's state lands beside each snapshot, the
        # matching entries multiply, and the products add up.
        scores = VGroup(
            *[
                Text(t, font_size=22, color=GREY_A,
                     font="Helvetica").next_to(labs[i], UP, buff=0.25)
                for i, t in enumerate(["0", "0", "2"])
            ]
        )
        score_lab = Text("scores", font_size=20, color=GREY_B,
                         font="Helvetica").move_to([-6.5, scores[0].get_center()[1], 0])
        dot_lines = [
            ".6×.7  +  .7×(−.6)  +  .6×.6  +  .6×(−.6)   =   0",
            ".6×.5  +  .7×0  +  .6×(−.5)  +  .6×0   =   0",
            ".6×.9  +  .7×.8  +  .6×.7  +  .6×.8   =   2",
        ]
        for i, (line_str, sc, col) in enumerate(zip(dot_lines, scores, cols)):
            probe = dstate.copy().scale(0.9)
            self.add(probe)
            path = ArcBetweenPoints(
                dstate.get_top() + UP * 0.08,
                col.get_right() + RIGHT * 0.34,
                angle=-0.55,
            )
            self.play(MoveAlongPath(probe, path), run_time=0.65)
            line = Text(line_str, font_size=22, color=GREY_A,
                        font="Helvetica").move_to([0, -0.55, 0])
            extra = [FadeIn(score_lab)] if i == 0 else []
            self.play(FadeIn(line, shift=UP * 0.1), *extra, run_time=0.5)
            self.wait(1.1)
            self.play(FadeOut(probe, scale=0.5), FadeOut(line),
                      FadeIn(sc, shift=UP * 0.1),
                      Indicate(col, color=GREY_A, scale_factor=1.05),
                      run_time=0.45)
        self.wait(0.6)

        # Softmax the scores into weights.
        weights = VGroup(
            *[
                Text(t, font_size=22, color=WHITE,
                     font="Helvetica").move_to(scores[i])
                for i, t in enumerate([".1", ".1", ".8"])
            ]
        )
        w_lab = Text("softmax", font_size=20, color=WHITE,
                     font="Helvetica").move_to(score_lab)
        self.play(Transform(scores, weights), Transform(score_lab, w_lab))
        self.wait(0.4)

        # The weighted sum, written out as an actual equation.
        eq_ops = [
            Text(".1 ×", font_size=24, color=WHITE, font="Helvetica"),
            Text("+  .1 ×", font_size=24, color=WHITE, font="Helvetica"),
            Text("+  .8 ×", font_size=24, color=WHITE, font="Helvetica"),
            Text("=", font_size=26, font="Helvetica"),
        ]
        eq_cols = [c.copy() for c in cols]
        ctx = val_column(CTX_STEP2, side=0.32, font_size=14, fill=0.3)
        eq = VGroup(eq_ops[0], eq_cols[0], eq_ops[1], eq_cols[1],
                    eq_ops[2], eq_cols[2], eq_ops[3], ctx)
        eq.arrange(RIGHT, buff=0.22).move_to([0, -1.5, 0])
        self.play(
            *[TransformFromCopy(cols[i], eq_cols[i]) for i in range(3)],
            *[TransformFromCopy(scores[i], eq_ops[i]) for i in range(3)],
            run_time=1.2,
        )
        self.play(FadeIn(eq_ops[3]), FadeIn(ctx, scale=0.7), run_time=0.7)
        self.wait(0.3)

        # One row worked out digit by digit; every row works the same.
        rings = VGroup(
            *[
                SurroundingRectangle(col[0][0], color=WHITE, buff=0.05,
                                     stroke_width=2.5)
                for col in [*eq_cols, ctx]
            ]
        )
        arith = Text(".1 × .7  +  .1 × .5  +  .8 × .9  ≈  .8",
                     font_size=24, color=GREY_A, font="Helvetica")
        arith.move_to([0, -3.15, 0])
        self.play(Create(rings, lag_ratio=0.15), FadeIn(arith))
        self.wait(1.6)
        self.play(FadeOut(rings))

        ctx_lab = Text("context for this step", font_size=20, color=BLUE,
                       font="Helvetica").next_to(ctx, UP, buff=0.22)
        self.play(FadeIn(ctx_lab))
        self.wait(0.5)

        # Off to the decoder; the word comes out.
        flying = ctx.copy()
        self.add(flying)
        self.play(flying.animate.move_to(cell[0].get_center())
                  .set_opacity(0),
                  Indicate(cell[0], color=GREEN, scale_factor=1.05),
                  run_time=0.9)
        out_arrow = Arrow(cell[0].get_top(), [4.8, 2.95, 0], buff=0.1,
                          color=GREY_B, stroke_width=3,
                          max_tip_length_to_length_ratio=0.3)
        word = Text("тебя", font_size=30, font="Helvetica")
        word.move_to([4.8, 3.3, 0])
        self.play(GrowArrow(out_arrow), FadeIn(word, shift=UP * 0.2))
        self.wait(2.5)


class AttentionAlignment(BeatScene):
    """The learned attention weights, plotted: the crossed alignment
    from the start of the post falls out of training."""

    def construct(self):
        self.camera.background_color = BG

        in_xs = [-1.4, 0.4, 2.2]
        out_ys = [1.3, 0, -1.3]
        matrix = [
            ("Я", [0.8, 0.1, 0.1]),
            ("тебя", [0.1, 0.1, 0.8]),
            ("люблю", [0.1, 0.8, 0.1]),
        ]

        in_words = word_row(["I", "love", "you"], 2.5, font_size=26,
                            xs=in_xs)
        out_words = VGroup(
            *[
                Text(m[0], font_size=26, font="Helvetica").move_to(
                    [-3.6, y, 0])
                for m, y in zip(matrix, out_ys)
            ]
        )
        self.play(FadeIn(in_words, lag_ratio=0.15))
        self.play(FadeIn(out_words, lag_ratio=0.15))
        self.wait(0.3)

        rows = []
        for (out_w, ws), y in zip(matrix, out_ys):
            row = VGroup()
            for w, x in zip(ws, in_xs):
                sq = Square(1.0, stroke_color=GREY_C, stroke_width=2,
                            fill_color=BLUE,
                            fill_opacity=w * 0.85).move_to([x, y, 0])
                num = Text(fmt(w), font_size=20, font="Helvetica",
                           color=WHITE if w > 0.5 else GREY_B).move_to(sq)
                row.add(VGroup(sq, num))
            rows.append(row)
            self.play(FadeIn(row, lag_ratio=0.15), run_time=0.7)
        self.wait(0.5)

        # The bright cells are the alignment, crossings included.
        for row, ws in zip(rows, [m[1] for m in matrix]):
            best = ws.index(max(ws))
            self.play(Indicate(row[best], color=WHITE, scale_factor=1.12),
                      run_time=0.5)
        self.wait(2.5)


class Squash(BeatScene):
    """Activation functions at need-to-know depth: numbers get squashed
    into a workable range, and a squash between layers is what stops
    two multiplications collapsing into one."""

    def construct(self):
        self.camera.background_color = BG

        # Phase 1: the squash itself, numbers in, workable numbers out.
        ax = Axes(
            x_range=[-6, 6, 2],
            y_range=[-1.6, 1.6, 1],
            x_length=9,
            y_length=4,
            axis_config={"include_ticks": True, "color": GREY_C},
            tips=False,
        ).move_to([0, 0.4, 0])
        curve = ax.plot(lambda x: np.tanh(x), x_range=[-5.7, 5.7],
                        color=BLUE, stroke_width=4)
        name = Text("a squashing function", font_size=22, color=BLUE,
                    font="Helvetica").move_to([-3.9, 2.5, 0])
        self.play(Create(ax, run_time=0.9), Create(curve, run_time=1),
                  FadeIn(name))

        samples = [
            (4.0, "4 → ≈ 1", UP + RIGHT * 0.3),
            (-4.0, "−4 → ≈ −1", DOWN + LEFT * 0.3),
            (0.5, "0.5 → ≈ 0.5", RIGHT + DOWN * 0.4),
        ]
        marks = VGroup()
        for x0, lab_text, direction in samples:
            y0 = float(np.tanh(x0))
            v = DashedLine(ax.c2p(x0, 0), ax.c2p(x0, y0), color=GREY_B,
                           stroke_width=2)
            hl = DashedLine(ax.c2p(x0, y0), ax.c2p(0, y0), color=GREY_B,
                            stroke_width=2)
            dot = Dot(ax.c2p(x0, y0), radius=0.07, color=WHITE)
            lab = Text(lab_text, font_size=20, color=GREY_A,
                       font="Helvetica").next_to(dot, direction, buff=0.15)
            self.play(Create(v), Create(hl), FadeIn(dot), FadeIn(lab),
                      run_time=0.6)
            marks.add(v, hl, dot, lab)
        self.wait(1.2)
        self.play(FadeOut(VGroup(ax, curve, name, marks)))

        # Phase 2: without a squash, two layers collapse into one.
        def op_box(txt, color=BLUE, width=1.0):
            rect = RoundedRectangle(corner_radius=0.1, width=width,
                                    height=0.7, stroke_color=color,
                                    stroke_width=3, fill_color=color,
                                    fill_opacity=0.08)
            t = Text(txt, font_size=22, color=color, font="Helvetica")
            t.move_to(rect)
            return VGroup(rect, t)

        def num(txt):
            return Text(txt, font_size=24, font="Helvetica")

        def arr():
            return Arrow(ORIGIN, RIGHT * 0.55, buff=0,
                         color=GREY_B, stroke_width=2.5,
                         max_tip_length_to_length_ratio=0.4)

        row1 = VGroup(num("5"), arr(), op_box("× 3"), arr(), num("15"),
                      arr(), op_box("× 2"), arr(), num("30"))
        row1.arrange(RIGHT, buff=0.22).move_to([0.6, 1.5, 0])
        row1_lab = Text("no squash", font_size=20, color=GREY_B,
                        font="Helvetica").move_to([-5.6, 1.5, 0])
        self.play(FadeIn(row1, lag_ratio=0.1), FadeIn(row1_lab))
        self.wait(0.4)

        merged = op_box("× 6")
        merged.next_to(row1, DOWN, buff=0.5)
        merged_lab = Text("collapses into", font_size=20, color=GREY_B,
                          font="Helvetica").next_to(merged, LEFT, buff=0.3)
        self.play(TransformFromCopy(VGroup(row1[2], row1[6]), merged),
                  FadeIn(merged_lab))
        self.wait(0.8)

        row2 = VGroup(num("5"), arr(), op_box("× 3"), arr(), num("15"),
                      arr(), op_box("squash", color=GREEN, width=1.5),
                      arr(), num("1"), arr(), op_box("× 2"), arr(),
                      num("2"))
        row2.arrange(RIGHT, buff=0.22).move_to([0.6, -1.3, 0])
        row2_lab = Text("with a squash", font_size=20, color=GREY_B,
                        font="Helvetica").move_to([-5.9, -1.3, 0])
        self.play(FadeIn(row2, lag_ratio=0.1), FadeIn(row2_lab))
        self.wait(0.4)
        no_merge = Text("no single multiplication can replace this",
                        font_size=20, color=GREY_A, font="Helvetica")
        no_merge.next_to(row2, DOWN, buff=0.45)
        self.play(FadeIn(no_merge))
        self.wait(2.5)


H4 = D_VALS[1]                    # decoder hidden state at step 4
C4 = [0.7, -0.4, 0.5, -0.4]       # .8 h1 + .1 h2 + .1 h3, exact


def badge(n, pos):
    ring = Circle(radius=0.2, stroke_color=GREY_B, stroke_width=2)
    num = Text(str(n), font_size=18, color=GREY_A, font="Helvetica")
    b = VGroup(ring, num.move_to(ring)).move_to(pos)
    return b


class AttentionAnatomy(BeatScene):
    """One full attention-decoder time step, stages numbered 1-6 to
    match the list in the post, ending with the feedback loop."""

    def construct(self):
        self.camera.background_color = BG

        rnn = rnn_cell(-4.9, GREEN, 1.5, 1.1, 20)
        ffn_rect = RoundedRectangle(corner_radius=0.12, width=1.3,
                                    height=1.1, stroke_color=BLUE,
                                    stroke_width=3.5, fill_color=BLUE,
                                    fill_opacity=0.08).move_to([3.4, 0, 0])
        ffn_lab = Text("FFN", font_size=20, color=BLUE, font="Helvetica")
        ffn_lab.move_to(ffn_rect)
        ffn = VGroup(ffn_rect, ffn_lab)

        # 1: the artificial first input and the encoder's last snapshot.
        start = Text("<start>", font_size=20, color=GREY_B,
                     font="Helvetica").move_to([-4.9, -1.9, 0])
        start_arrow = Arrow(start.get_top(), rnn[0].get_bottom(), buff=0.12,
                            color=GREY_B, stroke_width=2.5,
                            max_tip_length_to_length_ratio=0.25)
        init_h = val_column(H_VALS[3], side=0.26, font_size=12)
        init_h.move_to([-6.5, 0, 0])
        init_lab = Text("from the encoder", font_size=16, color=GREY_B,
                        font="Helvetica").next_to(init_h, DOWN, buff=0.2)
        init_lab.shift(RIGHT * 0.55)
        self.play(FadeIn(rnn), FadeIn(badge(1, [-5.9, -1.75, 0])),
                  FadeIn(start, shift=UP * 0.2), GrowArrow(start_arrow),
                  FadeIn(init_h), FadeIn(init_lab))
        self.wait(0.5)

        # 2: the RNN computes h4; its own output gets discarded.
        self.play(init_h.animate.move_to(rnn[0].get_center())
                  .set_opacity(0), FadeOut(init_lab),
                  Indicate(rnn[0], color=GREEN, scale_factor=1.05),
                  run_time=0.8)
        discard = val_column([0.3, 0.5, 0.2], side=0.2, font_size=10,
                             stroke=GREY_B, fill=0.1)
        discard.move_to(rnn[0].get_center()).set_opacity(0)
        self.add(discard)
        self.play(discard.animate.move_to([-4.9, 1.6, 0]).set_opacity(0.6),
                  run_time=0.5)
        self.play(FadeOut(discard, shift=UP * 0.3), run_time=0.4)
        h4 = val_column(H4, side=0.26, font_size=12, stroke=GREEN,
                        fill_color=GREEN)
        h4.move_to(rnn[0].get_center()).set_opacity(0)
        self.add(h4)
        h4_lab = Text("h₄", font_size=22, color=GREEN, font="Helvetica")
        self.play(h4.animate.move_to([-3.5, 0, 0]).set_opacity(1),
                  run_time=0.6)
        h4_lab.next_to(h4, UP, buff=0.15)
        self.play(FadeIn(h4_lab), FadeIn(badge(2, [-3.5, -1.75, 0])))
        self.wait(0.3)

        # 3: the attention step with the math on screen: h4 scores the
        # snapshots, softmax makes weights, and the weighted sum that
        # builds c4 is written out as an equation.
        att_lab = Text("attention", font_size=20, color=WHITE,
                       font="Helvetica").move_to([-1.7, 3.85, 0])
        stack_xs = [-2.6, -1.7, -0.8]
        stack = VGroup(
            *[
                val_column(H_VALS[t], side=0.22, font_size=10).move_to(
                    [x, 2.35, 0])
                for t, x in zip([1, 2, 3], stack_xs)
            ]
        )
        stack_labs = VGroup(
            *[
                Text(f"h{'₁₂₃'[i]}", font_size=16, color=GREY_B,
                     font="Helvetica").move_to([stack_xs[i], 3.25, 0])
                for i in range(3)
            ]
        )
        self.play(FadeIn(stack, lag_ratio=0.15), FadeIn(stack_labs),
                  FadeIn(att_lab), FadeIn(badge(3, [0.3, -1.75, 0])))

        # h4 compares itself against every snapshot: fan out, score.
        fan = VGroup(
            *[
                DashedLine(h4.get_top() + UP * 0.05, [x, 1.5, 0],
                           color=GREY_C, stroke_width=2)
                for x in stack_xs
            ]
        )
        scores = VGroup(
            *[
                Text(t, font_size=20, color=GREY_A,
                     font="Helvetica").move_to([stack_xs[i], 1.22, 0])
                for i, t in enumerate(["2", "0", "0"])
            ]
        )
        self.play(Create(fan, lag_ratio=0.2), run_time=0.8)
        self.play(FadeIn(scores, lag_ratio=0.15), run_time=0.5)
        self.wait(0.4)

        # Softmax turns the scores into weights, in place.
        weights = VGroup(
            *[
                Text(t, font_size=20, color=WHITE,
                     font="Helvetica").move_to(scores[i])
                for i, t in enumerate([".8", ".1", ".1"])
            ]
        )
        sm_lab = Text("softmax", font_size=16, color=WHITE,
                      font="Helvetica").next_to(weights, DOWN, buff=0.2)
        self.play(Transform(scores, weights), FadeIn(sm_lab))
        self.wait(0.4)

        # The weighted sum, written out column by column.
        eq_ops = [
            Text(".8 ×", font_size=20, color=WHITE, font="Helvetica"),
            Text("+ .1 ×", font_size=20, color=WHITE, font="Helvetica"),
            Text("+ .1 ×", font_size=20, color=WHITE, font="Helvetica"),
            Text("=", font_size=22, font="Helvetica"),
        ]
        eq_cols = [c.copy() for c in stack]
        c4_eq = val_column(C4, side=0.22, font_size=10, fill=0.3)
        eq = VGroup(eq_ops[0], eq_cols[0], eq_ops[1], eq_cols[1],
                    eq_ops[2], eq_cols[2], eq_ops[3], c4_eq)
        eq.arrange(RIGHT, buff=0.18).move_to([3.4, 2.35, 0])
        self.play(
            *[TransformFromCopy(stack[i], eq_cols[i]) for i in range(3)],
            *[TransformFromCopy(scores[i], eq_ops[i]) for i in range(3)],
            run_time=1.1,
        )
        self.play(FadeIn(eq_ops[3]), FadeIn(c4_eq, scale=0.7),
                  run_time=0.6)
        self.wait(0.5)

        # c4 takes its place in the pipeline.
        c4 = val_column(C4, side=0.26, font_size=12, fill=0.3)
        c4.move_to([0.3, 0, 0])
        c4_lab = Text("c₄", font_size=22, color=BLUE, font="Helvetica")
        self.play(TransformFromCopy(c4_eq, c4), FadeOut(fan),
                  FadeOut(sm_lab), run_time=0.8)
        c4_lab.next_to(c4, UP, buff=0.15)
        self.play(FadeIn(c4_lab))
        self.wait(0.3)

        # 4: glue h4 and c4 end to end.
        h4_c = h4.copy()
        c4_c = c4.copy()
        self.add(h4_c, c4_c)
        concat_top = [1.7, 0.66, 0]
        concat_bot = [1.7, -0.66, 0]
        self.play(h4_c.animate.move_to(concat_top),
                  c4_c.animate.move_to(concat_bot),
                  FadeIn(badge(4, [1.7, -1.75, 0])), run_time=0.8)
        self.wait(0.4)

        # 5: through the feedforward network.
        glued = VGroup(h4_c, c4_c)
        self.play(FadeIn(ffn), run_time=0.4)
        self.play(glued.animate.move_to(ffn_rect.get_center())
                  .set_opacity(0),
                  Indicate(ffn_rect, color=BLUE, scale_factor=1.05),
                  FadeIn(badge(5, [3.4, -1.75, 0])), run_time=0.9)

        # 6: the output word for this time step.
        word = Text("Я", font_size=30, font="Helvetica").move_to([5.0, 0, 0])
        out_arrow = Arrow(ffn_rect.get_right(), word.get_left(), buff=0.15,
                          color=GREY_B, stroke_width=2.5,
                          max_tip_length_to_length_ratio=0.3)
        self.play(GrowArrow(out_arrow), FadeIn(word, shift=RIGHT * 0.2),
                  FadeIn(badge(6, [5.0, -1.75, 0])))
        self.wait(0.4)

        # 7: and around again, the word becomes the next input.
        loop_arc = ArcBetweenPoints([5.0, -0.5, 0], [-4.3, -2.0, 0],
                                    angle=-0.9)
        loop_arc.set_stroke(GREY_B, 2.5, opacity=0.7)
        rep = Text("next input", font_size=16, color=GREY_B,
                   font="Helvetica").move_to([0.4, -3.3, 0])
        self.play(Create(loop_arc), FadeIn(rep), run_time=0.9)
        self.wait(2.5)


class OneWordPerTick(BeatScene):
    """The bottleneck attention didn't fix: the RNN fires one cell per
    tick, each waiting on the last, while the attention look-back has
    no order in it at all."""

    def construct(self):
        self.camera.background_color = BG

        # The chain: each cell's input is the previous cell's memory,
        # so nothing can fire early.
        xs = [-4.4, -1.6, 1.2]
        cells = VGroup(*[rnn_cell(x, BLUE, 1.5, 1.1, 20) for x in xs])
        cells.shift(UP * 2.0)
        words = word_row(["I", "love", "you"], 0.95, font_size=22, xs=xs)
        words.set_color(GREY_B)
        top_lab = Text("each step waits on the last", font_size=20,
                       color=GREY_B, font="Helvetica").move_to([4.3, 2.0, 0])
        self.play(FadeIn(cells, lag_ratio=0.1), FadeIn(top_lab))
        counter = step_counter(1)
        self.add(counter)
        for t in range(3):
            anims = [Indicate(cells[t][0], color=BLUE, scale_factor=1.06),
                     FadeIn(words[t], shift=UP * 0.15)]
            if t:
                arrow = Arrow(cells[t - 1][0].get_right(),
                              cells[t][0].get_left(), buff=0.12,
                              color=GREY_B, stroke_width=3,
                              max_tip_length_to_length_ratio=0.3)
                anims.append(GrowArrow(arrow))
                anims.append(Transform(counter, step_counter(t + 1)))
            self.play(*anims, run_time=0.9)
            self.wait(0.35)
        self.wait(0.5)

        # The attention look: three dot products with no order between
        # them, so they all fire in one go.
        h_xs = [-4.8, -3.5, -2.2]
        cols = VGroup(
            *[
                val_column(H_VALS[t], side=0.26, font_size=12).move_to(
                    [x, -1.9, 0])
                for t, x in zip([1, 2, 3], h_xs)
            ]
        )
        labs = VGroup(*[h_label(t).scale(0.8).next_to(c, DOWN, buff=0.15)
                        for t, c in zip([1, 2, 3], cols)])
        dstate = val_column(D_VALS[2], side=0.26, font_size=12,
                            stroke=GREEN, fill_color=GREEN)
        dstate.move_to([2.6, -1.9, 0])
        d_lab = Text("decoder state", font_size=16, color=GREY_B,
                     font="Helvetica").next_to(dstate, DOWN, buff=0.15)
        bot_lab = Text("the look-back has no order", font_size=20,
                       color=GREY_B, font="Helvetica").move_to([5.1, -1.9, 0])
        self.play(FadeIn(cols), FadeIn(labs), FadeIn(dstate),
                  FadeIn(d_lab), FadeIn(bot_lab))
        scores = VGroup(
            *[
                Text(s, font_size=20, color=GREY_A,
                     font="Helvetica").next_to(c, UP, buff=0.2)
                for s, c in zip(["0", "0", "2"], cols)
            ]
        )
        looks = VGroup(
            *[
                DashedVMobject(
                    ArcBetweenPoints(
                        dstate.get_top() + UP * 0.08,
                        sc.get_top() + UP * 0.1,
                        angle=-0.55,
                    ),
                    num_dashes=40,
                ).set_stroke(GREY_C, 2)
                for sc in scores
            ]
        )
        self.play(Create(looks, lag_ratio=0), run_time=0.6)
        self.play(FadeIn(scores, lag_ratio=0),
                  *[Indicate(c, color=BLUE, scale_factor=1.06)
                    for c in cols],
                  run_time=0.7)
        self.wait(2.5)

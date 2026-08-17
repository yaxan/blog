---
title: "How gradient descent finds the minimum"
date: 2026-08-10
description: "A visual walk through the single idea powering nearly all of deep learning."
glyph: gradient-descent
draft: true
---

Nearly every neural network you've heard of was trained by the same humble
procedure: measure how wrong you are, figure out which direction makes you
less wrong, and take a small step that way. Repeat a few million times.

Formally, we have a loss function $L(w)$ that scores how bad our parameters
$w$ are, and we update them by stepping against the gradient:

$$
w_{t+1} = w_t - \eta \, \nabla L(w_t)
$$

where $\eta$ is the *learning rate* — the size of each
step.{{< sidenote >}}Too large and you leap clean across the valley; too
small and you crawl. Picking $\eta$ well is half the craft of training.{{< /sidenote >}}

{{< tangent "Wait — what exactly is a gradient?" >}}
With a single parameter, the gradient is just the slope: $\nabla L$ is the
derivative $dL/dw$, positive when the curve rises to the right. With many
parameters $w = (w_1, \ldots, w_n)$, the gradient collects every partial
slope into a vector,

$$
\nabla L = \left( \frac{\partial L}{\partial w_1}, \ldots, \frac{\partial L}{\partial w_n} \right)
$$

which points in the direction of *steepest increase* of the loss. That's the
entire reason for the minus sign in the update: stepping against the
gradient is the fastest local way downhill.
{{< /tangent >}}

Here's what that looks like on a simple one-dimensional loss:

{{< manim "GradientDescent" >}}
Each step moves against the slope. Steps shrink near the bottom because the
gradient itself shrinks — the ball settles into the minimum on its own.
{{< /manim >}}

Notice two things the equation doesn't make obvious:

1. **The steps shrink automatically.** Near the minimum the curve flattens,
   so $\nabla L$ is small and the update $-\eta \nabla L$ barely moves.
   Nobody schedules this — it falls out of the math.
2. **The gradient is local.** The ball only ever feels the slope under its
   feet. It has no idea whether a deeper valley exists elsewhere. That's why
   initialization and loss-surface shape matter so much in practice.

In code, the whole idea is three lines:

```python
for step in range(num_steps):
    grad = compute_gradient(loss, w)
    w = w - lr * grad
```

Everything else — momentum, Adam, learning-rate schedules — is a refinement
of this loop. We'll build up to those in later posts.

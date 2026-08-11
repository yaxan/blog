---
title: "How gradient descent finds the minimum"
date: 2026-08-10
description: "A visual walk through the single idea powering nearly all of deep learning."
---

Nearly every neural network you've heard of was trained by the same humble
procedure: measure how wrong you are, figure out which direction makes you
less wrong, and take a small step that way. Repeat a few million times.

Formally, we have a loss function $L(w)$ that scores how bad our parameters
$w$ are, and we update them by stepping against the gradient:

$$
w_{t+1} = w_t - \eta \, \nabla L(w_t)
$$

where $\eta$ is the *learning rate* — the size of each step. Here's what that
looks like on a simple one-dimensional loss:

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

---
title: "Intro"
date: 2026-08-17
description: "Why this blog exists, how to read it, and where it's headed."
glyph: intro
---

I'm hoping this blog can turn out to be a zero-to-hero kind of thing
for understanding modern AI systems from the ground up. I find there's
a whole lot of resources out there, and with how much everything is
changing, it's really hard to decide where to start. In the era of AI
agents and vibe coding, it's become really easy to give yourself the
illusion of learning without actually understanding what you're doing,
and quickly lose control of what's going on. I'll try to include
interactive notebooks to help solidify concepts. Ironically I'm a bit
lazy and will probably vibecode those to an extent, but I'll be sure
to at least run through them myself.

I want to start from simpler concepts and build my way towards LLM
inference and other real-world optimization techniques. Hopefully I'll
be able to make my way through the fundamentals of transformer
architectures, tokenization, attention, model families, autoregressive
generation, and KV caching, then build upward into GPU performance,
profiling, inference engines like vLLM and SGLang, batching,
scheduling, quantization, CUDA graphs, Triton kernels, ML compilers,
and hardware-aware optimization. The goal is to explain what modern
models are and develop a practical intuition to inspect an unfamiliar
model, understand how it runs on specific hardware, identify latency
and memory bottlenecks, and make evidence-based optimization decisions
across the full inference stack.

Everyone starts somewhere different and from all sorts of different
educational backgrounds. I try to explain in tangents what certain
things are without assuming prior familiarity, but the line needs to
be drawn somewhere. Some readers may find I over-explain certain
things, and others will probably feel I brush over topics that they
need explained further.

The important thing with learning here is stopping yourself at any
point you're confused, identifying the missing requisite knowledge,
and filling that gap before continuing. Be curious, ask yourself why
things work the way they do and why things are done the way they are.
If you read the first article and don't know how a neural network even
works and the RNN stuff goes right over your head, that's fine too.
The gap between you and an AI expert grows smaller with each one of
those requisite knowledge gaps you fill in.

I am by no means an expert. The whole reason I started this was to
brush up on the things I know and identify the knowledge I'm missing
and the concepts that I am incapable of explaining.

Some things to keep in mind: for every concept, ask what problem it
solves, what the input shape is, what the output shape is, where it
appears in the model, why it matters for inference, and try to find
one thing you still don't understand well enough to explain. If you
can't explain a concept with tensor shapes, you (probably?) don't
understand it yet.

For the most part, these come from my handwritten notes, some old,
some new. I don't really know where they all came from. So sorry if
sources are missing. Some of my notes suck too, so LLMs will
definitely be put to work on cleaning up and formatting stuff.

---
title: "Understanding Seq2Seq: RNNs, encoders, Decoders, & Attention"
date: 2026-08-10T22:41:52-07:00
description: "idk yet"
glyph: ""   # SVG glyph name for the home page; add a case in layouts/_partials/glyph.html
draft: true
---

Sequence-to-sequence (Seq2seq) models are a family of models that do exactly what they sound like they do: they take a sequence of items like words, and output another sequence of items. I think this is a good starting point on the road to understanding modern LLMs and AI models because the classic seq2seq architecture exposes several problems which motivate the Transformer. Most modern chat LLMs are not built as encoder-decoder (fine if you don't know what that is) seq2seq models, but understanding this architecture can help make it easier to see why Transformers were designed the way they were, and we can also use it to solidify other concepts along the way.
The canonical example is machine translation. Suppose we wanted to translate "I love you" → "Я тебя люблю". We can't translate each word independently because depending on the language word order can change, surrounding context can affect the translation, and sometimes the number of words can differ (i.e. "I am hungry" → "Я голоден").
The classic solution splits the model into two parts: the encoder and the decoder.
Encoder: read and understand the input sequence so we can turn it into a usable format
Decoder: Use that understanding to generate the output sequence
The encoder processes each item in the item in our input sequence, in our case each word and compiles it into a vector which we call the context. After processing the entire input sequence, the encoder then passes the context over to the decoder, which produces the output sequence item by item.
But wait why are we even encoding things into vectors instead of just passing our English words as input into our Russian language machine and letting it spit out a translation? Well, our goal is to take any arbitrary length sequence and turn it into another arbitrary length sequence. You can think of the decoder as the actual translator from one language to another, but it only understands inputs in one language. So we need to convert to the language it understands as an intermediary before we spit out our desired translation.
Anyways, the context is a vector, while the encoder and decoder both tend to be recurrent neural networks (RNNs). You can set the size of the context vector when you set up your model, it is essentially the number of hidden units in the encoder RNN.











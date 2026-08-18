---
title: "Understanding Seq2Seq: RNNs, Encoders, Decoders, & Attention"
date: 2026-08-17T14:56:54-07:00
description: "Encoders, decoders, and the problems that motivate the Transformer."
glyph: seq2seq
---

Sequence-to-sequence (seq2seq) models are a family of models that do exactly
what they sound like they do: they take a sequence of items like words, and
output another sequence of items. I think this is a good starting point on
the road to understanding modern LLMs and AI models because the classic
seq2seq architecture exposes several problems which motivate the
Transformer. Most modern chat LLMs are not built as
encoder-decoder{{< sidenote >}}Fine if you don't know what that is
yet.{{< /sidenote >}} seq2seq models, but understanding this architecture
can help make it easier to see why Transformers were designed the way they
were, and we can also use it to solidify other concepts along the way.

## Why not translate word by word?

The canonical example is machine translation. Suppose we wanted to translate
"I love you" → "Я тебя люблю". We can't translate each word independently
because depending on the language word order can change, surrounding context
can affect the translation, and sometimes the number of words can
differ.{{< sidenote >}}"I am hungry" → "Я голоден".{{< /sidenote >}}

{{< manim "WordByWord" >}}
Word-for-word translation fails twice: Russian wants "книгу Ивана",
literally "book of Ivan", so the lines cross; and "am" gets no line at all.
{{< /manim >}}

## The encoder and the decoder

The classic solution splits the model into two parts: the encoder and the
decoder.

- **Encoder**: read and understand the input sequence so we can turn it
  into a usable format
- **Decoder**: use that understanding to generate the output sequence

The encoder processes each item in our input sequence, in our case each
word, and compiles it into a vector which we call the **context**. After
processing the entire input sequence, the encoder then passes the context
over to the decoder, which produces the output sequence item by item.

{{< manim "Seq2SeqPipeline" >}}
The encoder reads the input word by word and compiles it into the context;
the decoder then produces the output word by word.
{{< /manim >}}

But wait — why are we even encoding things into vectors instead of just
passing our English words as input into our Russian language machine and
letting it spit out a translation? The boring answer first: a neural
network is just math. It multiplies its inputs by big matrices of weights,
and you can't multiply "hungry" by a matrix. So words have to become
numbers before the model can do anything with them.

That answers why vectors, but not why we squeeze the whole sentence into a
single one. Well, our goal is to take any arbitrary length sequence and
turn it into another arbitrary length sequence. Look at how the encoder
reads: it compiles words into a running summary one at a time, so by the
last word everything it understood is sitting in one vector of a fixed
size, no matter how long the sentence was. Reading ends in a fixed-size
vector whether we like it or not, and it turns out that's exactly what we
want: the decoder can unpack that vector into two words or ten, so the
output's length is cut loose from the input's. You can think of the
decoder as the actual translator from one language to another, but it only
understands inputs in one language. So we need to convert to the language
it understands as an intermediary before we spit out our desired
translation.

Anyways, the context is a vector, while the encoder and decoder both tend
to be recurrent neural networks (RNNs).

{{< tangent "Wait — what's an RNN?" >}}
An ordinary neural network is built from little **units**, each holding a
single number, stacked into **layers**, with each layer wired to the
next. The layers sitting between the input and the output are called
hidden layers. It takes a fixed number of inputs, all at once, and that's
a problem for us: sentences come in any length.

{{< manim "OrdinaryNet" >}}
Each circle is a unit holding one number; a column of units is a layer.
The middle one, neither input nor output, is the hidden layer. The input
numbers get transformed into new numbers at every layer, and the number of
input slots is fixed when the network is built.
{{< /manim >}}

A recurrent neural network (RNN) gets around this by reading the way you
do: one word at a time, keeping notes as it goes. The trick is one extra
wire: the hidden layer feeds back into itself, so whatever it computed for
the last word is still there when the next word arrives.

{{< manim "RNNLoop" >}}
At each time step $t$ the current word becomes numbers in the input layer,
the hidden layer's own numbers ride the loop back in, and the two combine
into the hidden layer's next values, the new hidden state. Each step gets
photographed. Unrolling is just lining the photos up: the same network at
$t = 1, 2, 3$.
{{< /manim >}}

The notes are called the **hidden state**: the numbers sitting in the
hidden layer at a given moment, collected into a vector. That vector is
the network's memory of everything it has read so far: it starts blank
(all zeros) and gets updated every time a word is read. Each of these
rounds of reading-and-updating is called a **time step**.

The update itself is small: combine the current word with the current
memory,

$$
h_t = f(W x_t + U h_{t-1})
$$

where $x_t$ is the word read at step $t$ (as a vector), $h_{t-1}$ is the
memory going in, $h_t$ is the memory coming out, and $f$ just squashes the
numbers into a workable range. The weights $W$ and $U$ are the same at
every step, one small network applied over and over, and that's what lets
it handle a sentence of any length.

Two things to hold onto for later. First, an RNN can also produce an
output at every time step, computed from the hidden state; that's how a
decoder RNN can emit one word per step. Second, notice there isn't one
hidden state but a trail of them, $h_1, h_2, h_3$, one snapshot per word.
Seq2seq keeps only the last one. The intermediate ones look like a
throwaway detail right now, but attention will dig them back up.

{{< manim "RNNTrail" >}}
Every step also produces an output (top) and leaves behind a snapshot of
the memory (h₁, h₂, h₃). Classic seq2seq throws all of it away except the
last snapshot.
{{< /manim >}}

I'm skipping the nitty gritty: how the weights get trained, and the
gated variants (LSTMs, GRUs) people actually used because plain RNNs are
forgetful. None of it is needed to follow along.
{{< /tangent >}}

First though, the words themselves have to become vectors. The vector a
word gets is called its **word embedding**.

{{< tangent "How does a word become a vector?" >}}
There's no clever formula, and no second model doing this job. The
dictionary of vectors is part of our seq2seq model itself: one entry per
word it knows, and each entry holds a list of numbers. Turning "hungry"
into a vector just means looking up its entry. The entries start out as
random numbers, and they get trained along with the rest of the model:
every sentence it gets wrong nudges the entries of the words in that
sentence, and over millions of sentences useful structure appears.

The right way to read that list is as coordinates. Two numbers pin down a
point on a map, three pin down a point in a room, and an embedding with
three hundred numbers pins down a point in a space with three hundred
axes. You can't picture that space, and you don't need to: the math works
the same as in two dimensions, so that's how I'll draw it.

Once words are points, "similar" means something literal: words that get
used in the same kinds of sentences end up near each other, so "hungry"
and "starving" sit close while "hungry" and "Tuesday" are far apart.
Directions mean something too: the step that takes you from "man" to
"woman" is nearly the same step that takes you from "king" to "queen".
That lets you do arithmetic with meanings: take the man → woman step,
start it at king instead, and you arrive near queen. Rearranged, that's
the famous king − man + woman ≈ queen. In real embeddings the landing is
not exact, queen is just the nearest word once you skip the three you
started with.

{{< manim "KingQueen" >}}
Each word's numbers are its coordinates, so every word is a point, and
also an arrow from the origin. Subtracting man means following its arrow
flipped, and adding woman means following its arrow as is. Take both
hops from king and you land on queen: together they're just the man →
woman step. Our toy numbers work out exactly; real embeddings only get
you near queen.
{{< /manim >}}

Nobody hand-picks what the axes mean; no single axis means anything
readable on its own, and meaning lives in directions, like the man →
woman step. If you've heard of word2vec or GloVe: those are separate
little models whose only job is producing word vectors, and the king and
queen result was discovered in word2vec's. You can borrow their vectors
as a starting point, but seq2seq doesn't need them; it learns its own
dictionary while learning to translate. Real embeddings run from a few
hundred numbers to a few thousand; ours are two or three so they fit on
screen.
{{< /tangent >}}

Now we can run the encoder. The first RNN step takes the first word's
vector and a blank starting hidden state (all zeros) and produces hidden
state #1. The next RNN step takes the second input vector and hidden
state #1 to produce hidden state #2. In each time step the RNN does some
processing and updates its hidden state based on its input and the
previous inputs. The last hidden state is actually the context we pass on
to the decoder.

{{< manim "RNNReads" >}}
One word per time step: the same network, drawn once per step, folds each
word into its memory. Whatever comes out after the last word has read the
whole sentence. In seq2seq, that's the context.
{{< /manim >}}

You can set the size of the context vector when you set up your model; it
is essentially the size of the encoder RNN's hidden state, i.e. how many
numbers long its memory is.{{< sidenote >}}Each of those numbers is what
papers call a **hidden unit**: one circle in the hidden layer, one square
in the blue columns. The classics used 256, 512, or 1024 of
them.{{< /sidenote >}}

## The decoder's turn

The decoder is another RNN. It also maintains a hidden state which gets
passed along each time step, and its starting value is the context
itself: the decoder picks up exactly where the encoder left off. At each
time step it produces one output word from its hidden state, updates the
hidden state, and feeds the word it just produced back in as the next
step's input. A special start marker kicks off the first step, and the
sentence ends when the decoder produces a special stop word.

{{< manim "DecoderWrites" >}}
The context becomes the decoder's starting hidden state. Every step emits
a word, and that word gets fed back in as the next step's input.
{{< /manim >}}

And that's the whole model. Here it is running start to finish:

{{< manim "EndToEnd" >}}
One clock for the whole run. Steps 1 through 3: the encoder folds "I love
you" into its memory. The final memory is the context. Steps 4 through 6:
the decoder starts from it and spends it, one output word per step, each
word fed back in as the next input.
{{< /manim >}}

## The bottleneck

The context vector turned out to be a bottleneck for these models. It
turns out that they are unable to deal with long sentences effectively,
because everything the decoder will ever know about the input has to fit
in that one fixed-size vector. A ten word sentence and a fifty word
sentence get squeezed into the same amount of space, and since the memory
fades a little with every update, by the end of a long sentence the early
words have mostly washed out.
## Attention

This is where the **attention mechanism** comes in: it allows the model
to focus on the relevant parts of the sentence as needed. The attention
model differs from classical seq2seq mainly in two ways:

1. The encoder passes a lot more info to the decoder: all of its hidden
   states, one per input word, instead of just the last one. Each state
   is a snapshot of the encoder's memory right after it read one word,
   so each is most associated with that word.
2. The attention decoder has an extra step before producing each output
   word, where it decides which of those snapshots matter right now.

Here's that extra step. At each decoding time step, the decoder looks at
the set of encoder hidden states and gives each one a score: one number
for how relevant that snapshot is to the word it's about to produce.
Relevant compared to what? To the decoder's own hidden state, its
summary of where the translation stands right now: each score comes from
comparing that state with one snapshot. And the comparing isn't some
black box: it's a **dot product**. Line the two vectors up, multiply
matching entries, add the products, and that sum is the score. A dot
product comes out big when two vectors point in a similar direction, and
remember from the embeddings that meaning lives in directions: a
snapshot scores high exactly when it points the same way as the
decoder's state.{{< sidenote >}}The original attention paper actually
did the comparing with a tiny neural network: feed it the two vectors,
one number comes out, trained with everything else. Later work found the
plain dot product works about as well, and that's the version
Transformers use.{{< /sidenote >}} Then the
scores go through a **softmax**, which turns them into weights: positive
numbers that add up to 1.

{{< tangent "Wait — what's a softmax?" >}}
Neural networks are full of little squashing functions called
**activation functions**. The sums inside a network can come out as any
number at all, huge or negative, so after each layer the numbers get
squashed back into a workable range; the squashing function $f$ from the
RNN update earlier is one of these. They also have a sneakier job: two
layers of pure multiplication collapse into one bigger multiplication,
so without a squash between the layers, depth would buy the network
nothing.

{{< manim "Squash" >}}
Any number in, a workable number out; this particular squash is called
tanh. Then the second job: ×3 then ×2 collapses into ×6, but with a
squash wedged between them, no single multiplication can replace the
chain. Depth survives.
{{< /manim >}}

The softmax is the activation function for making choices. It takes a
list of scores and turns them into shares of a whole: each share is
positive, they add up to 1, and bigger scores take much bigger shares.
Under the hood it raises $e$ to each score and divides by the total. For
our scores of 0, 0, and 2: $e^0 = 1$, $e^0 = 1$, $e^2 \approx 7.4$, and
dividing each by their sum gives the weights $.1, .1, .8$.

Why $e$? It keeps every share positive even when scores are negative,
and it exaggerates gaps: 2 is only two points ahead, but it took 80% of
the pie.
That's the point. A softmax is a softer version of just picking the
maximum, which is where the name comes from.
{{< /tangent >}}

Multiplying each hidden state by its weight amplifies the states with
high scores and drowns out the ones with low scores: a snapshot with
weight .8 comes through at almost full strength, one with weight .1
barely registers. Summing the weighted states gives a context vector
built specifically for this one time step. The decoder combines it with
its own hidden state to produce the word, and then does the whole thing
again, from scratch, for the next word.

{{< manim "AttentionStep" >}}
Writing "тебя": the decoder's current state visits each kept snapshot,
and each visit is one dot product, matching entries multiplied and
added, giving the scores 0, 0, 2. The softmax turns those into
weights .1, .1, .8, and this step's context is the weighted sum
$.1 h_1 + .1 h_2 + .8 h_3$, worked out row by row. "you"'s snapshot
dominates the sum.
{{< /manim >}}

So the bottleneck is gone. There is no single vector the whole sentence
has to squeeze through: the decoder gets a fresh context at every step,
weighted toward whatever part of the input it needs right now, and early
words no longer have to survive the entire squeeze, since the decoder
can reach straight back to their snapshots.

None of this scoring is set by hand: training shapes the states
themselves until the useful snapshots score high. And you can plot the weights: for
each output word, look at how much weight each input word got. Remember the crossed lines from the top of the post? Nobody told
the model that "тебя" is "you" and "люблю" is "love". Attention finds
the alignment on its own, crossings included.

{{< manim "AttentionAlignment" >}}
The attention weights, plotted per output word. Bright means heavily weighted: the crossed alignment we drew by hand at the start falls out
of training.
{{< /manim >}}

All together, one decoding time step looks like this:

1. The attention decoder takes in an artificial first input, because no
   previous outputs exist yet; you may see it referred to as \<START\>,
   \<BOS\>, etc. It also takes an initial decoder hidden state, the
   encoder's final snapshot.
2. The RNN processes its inputs and produces a new hidden state,
   $h_4$.{{< sidenote >}}Why $h_4$? The encoder's clock ended at $h_3$,
   and the decoder keeps counting.{{< /sidenote >}} It produces an
   output too, but that gets discarded: the actual word will come from
   the feedforward network below.
3. The attention step, the same recipe as before with $h_4$ doing the
   scoring: dot each encoder snapshot with $h_4$ for its score, softmax
   the scores into weights, and take the weighted sum of the snapshots.
   That sum is the context vector $c_4$ for this time step. Writing
   "Я", the weights come out .8, .1, .1, so nearly all of the attention
   lands on "I".
4. We concatenate $h_4$ and $c_4$ into a single vector, i.e. glue them
   end to end.
5. We pass this vector through a feedforward neural network, an ordinary
   network with no loop in it, trained jointly with the rest of the
   model.
6. The FFN's output picks the word for this time
   step.{{< sidenote >}}How does a vector pick a word? The FFN's last
   layer has one unit per word in the vocabulary, so its output is a
   score for every word the model knows. Softmax those scores into
   shares, same as before, and the biggest share wins.{{< /sidenote >}}
7. Repeat for the next time steps, feeding each output word back in,
   until the model produces the stop word.

{{< manim "AttentionAnatomy" >}}
One time step, numbered as above: \<start\> and the encoder's last
snapshot enter the RNN (1), and $h_4$ comes out while the RNN's own
output gets tossed (2). Then the attention step in full view: $h_4$
dots the snapshots for scores 2, 0, 0, softmax makes that .8, .1, .1, and their
weighted sum is $c_4$ (3). $h_4$ and $c_4$ get glued end to end (4) and
passed through the FFN (5), which picks "Я" (6). The word then rides
back around to become the next input.
{{< /manim >}}

## The road to the Transformer

So is that everything? Not quite. Attention got rid of the bottleneck,
but the model underneath is still an RNN: the encoder reads one word per
time step, the decoder writes one word per time step, and each step
needs the previous step's hidden state as its input, so no step can
start until the one before it finishes. A fifty word sentence means
fifty steps, one after another, and throwing more hardware at it doesn't
change that. It turns out the attention step is the only part of the
model that doesn't have this problem: the scores are just dot products,
and none of them needs to wait for any other.

{{< manim "OneWordPerTick" >}}
The leftover bottleneck. The chain on top can only fire in order, since
each cell needs the memory of the one before it. The look-back below has
no order in it: three independent dot products that could all happen at
once.
{{< /manim >}}

Which raises a natural question: if the attention step is doing this
much of the work, do we even need the RNN? The Transformer's answer is
no: throw away the recurrence, keep the attention, and let every word
score every other word directly, with the same recipe we just went
through: dot products, softmax, weighted sum. We'll get into how that
actually works, and what "queries" and "keys" are, in the next post.

If you want this in your hands and not just your head, there's a
[companion notebook](https://colab.research.google.com/github/yaxan/blog/blob/main/notebooks/seq2seq.ipynb)
you can run in the browser. The boring parts come prefilled; the
important ones — the RNN update, the encoder, the decoder, the
attention step — you fill in yourself, then watch the bottleneck and
its fix play out on a real model.

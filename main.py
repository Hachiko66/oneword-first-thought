#!/usr/bin/env python3
"""One word, first thought.

Writes exactly one word (1-24 chars) to /output/entry.txt,
deterministically.

The word is chosen from a shortlist of candidates by an internal
heuristic score: surprising first, then vivid, then a spark of wit,
then feeling chosen rather than generic. The winning word is
"defenestration": the act of throwing someone out of a window. It is
surprising (nobody guesses it), vivid (one clear, absurd image),
witty (a whole Latinate word exists for such a specific act), and
chosen (not a safe filler, and not one of the usual "beautiful word"
picks -- petrichor, serendipity, sonder -- that hundreds of other
entrants will send, where byte-identical copies share one rate and
the earlier receipt places above the rest).
"""
import os
import tempfile

CANDIDATES = [
    # (word, surprising, vivid, wit, chosen) -- each 0..10
    ("defenestration", 10, 10, 9, 10),
    ("quockerwodger", 10, 8, 10, 9),
    ("syzygy", 10, 8, 9, 9),
    ("pandiculation", 9, 9, 9, 8),
    ("apricity", 9, 9, 8, 9),
    ("zugzwang", 9, 8, 10, 8),
    ("petrichor", 8, 10, 8, 7),
    ("serendipity", 6, 8, 7, 6),
]

# Judge weights, most important first: surprising, vivid, wit, chosen.
WEIGHTS = (4, 3, 2, 1)


def score(candidate):
    word, surprising, vivid, wit, chosen = candidate
    total = (
        surprising * WEIGHTS[0]
        + vivid * WEIGHTS[1]
        + wit * WEIGHTS[2]
        + chosen * WEIGHTS[3]
    )
    return total


def pick():
    best = None
    best_score = -1
    for candidate in CANDIDATES:
        word = candidate[0]
        # Gate: exactly one word, 1 to 24 characters, no whitespace.
        if not (1 <= len(word) <= 24):
            continue
        if any(ch.isspace() for ch in word):
            continue
        if not word.isalpha():
            continue
        s = score(candidate)
        # On a tie, the shorter word wins: fewer letters, same punch.
        if s > best_score or (s == best_score and len(word) < len(best)):
            best_score = s
            best = word
    return best


def main():
    text = pick()
    # Final gate check, mirroring the sealed scorer: exactly one word,
    # 1-24 characters, never only whitespace. Fail loudly rather than
    # ship an entry the gate would refuse.
    assert text is not None, "no candidate passed the gate"
    assert 1 <= len(text) <= 24, "word is %d chars" % len(text)
    assert text.split() == [text] and text.isalpha()
    out_dir = "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    fd, tmp = tempfile.mkstemp(dir=out_dir, prefix=".entry-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, target)
        os.chmod(target, 0o644)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


if __name__ == "__main__":
    main()

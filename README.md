# tiny-chess-4k

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/tonangarivin-ui/tiny-chess-4k/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/tonangarivin-ui/tiny-chess-4k/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A 4,094-byte chess engine: alpha-beta with a quiescence search over material and piece-square
tables, a transposition table with best-move ordering, and a fixed node budget a move so a
position always gets the same answer. It plays entirely through the trial's env, never reads a
clock, and fits inside the competition's 4,096-byte cap with its lzma payload and unpacker.

## What it does

The board is a list of small ints, white positive and black negative. Move generation is shared
with the trial: the env supplies the legal list at the root, and inside the tree every move is
checked for the king's safety, so a node with no legal move left is a real mate and never a
stalemate mistaken for a checkmate.

- alpha-beta with a quiescence search, over material and piece-square tables
- a transposition table (flag, value, depth, best move) ordering the moves it has already seen
- a repetition scored as the draw it is, both inside the tree and for any position the game
  itself has already had, with a small contempt so a strong side never settles for one
- one node budget for a whole move rather than one per depth, so its seconds do not add up
- a cap on how deep captures may chain, so the slowest move's tail stays away from the clock
- a fixed node budget a move: one position always gets one move, on any machine

## Run it

```sh
MAKEFUN_ENV_URL=http://127.0.0.1:8099 python3 -P -s main.py
```

It reads the position from that env and answers with a move; it never reads a clock and never
opens a file. Against the kit's practice instances it scores 997 to 1,364 elo, a mean of 1,213 over the three.

---

<sub>Entered on [make.fun](https://make.fun/?ref=6sp8gq4y&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>

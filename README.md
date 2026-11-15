# tiny-chess-4k

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/tonangarivin-ui/tiny-chess-4k/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/tonangarivin-ui/tiny-chess-4k/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A 4,052-byte chess engine: alpha-beta with a quiescence search over material and piece-square
tables, a transposition table with best-move ordering, and a fixed node budget a move so a
position always gets the same answer. It plays entirely through the trial's env, never reads a
clock, and fits inside the competition's 4,096-byte cap with its lzma payload and unpacker.

## Run it

```sh
MAKEFUN_ENV_URL=http://127.0.0.1:8099 python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=6sp8gq4y&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>

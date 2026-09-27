# See The Odds

A transparent gambling-math education simulator built with Python and Pygame.

It exists to make one thing visible: what "50/50" actually means over many rounds, how a small house edge compounds into guaranteed long-run losses, and how patterns like "chasing losses" look in practice. Nothing here is hidden or secretly tuned — every probability is disclosed on screen.

## Modes

| Mode | True win chance | Purpose |
|---|---|---|
| **Fair 50/50** | 50% | A genuinely fair coin toss, for baseline comparison |
| **House Edge** | 46% | Mimics how a realistic house-edge game *feels* like 50/50 but isn't |
| **Player Favored** | 70% | For contrast only — no real platform offers this, since the house would lose money |

## Features

- Manual "Flip once" with a coin animation
- "Fast-forward 1,000 rounds" to instantly see the long-run trend
- Live stats: balance, win rate, rounds played, total wagered, net result, and true win chance
- A running balance-over-time chart with a baseline marker
- **Chasing-losses detection** — flags it when you raise your stake after a losing streak, a well-documented risk pattern in problem gambling

## Installation

```bash
git clone https://github.com/yourusername/see-the-odds.git
cd see-the-odds
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

**Controls:**
- Click **Fair 50/50** / **House Edge** / **Player Favored** to switch modes
- Click **HEAD** / **TAIL** to choose your call
- Click the stake box, type a number, press Enter (or click elsewhere) to confirm
- Click **Flip once** to play a single round
- Click **Fast-forward 1,000 rounds** to instantly simulate many rounds
- Click **Reset simulation** to start over
- Press `Q` or close the window to quit

## Why this exists

Real gambling platforms with a fixed, disclosed house edge are mathematically consistent, the odds don't change based on who you are or how much you bet. This project demonstrates that math honestly, using a coin toss as the simplest possible example, so the long-run outcome of "the odds are against you" is something you can actually *see* accumulate on a chart rather than just be told.

This is an educational tool, not a real-money gambling application. No real currency, wagering, or payment processing is involved.

## License

MIT

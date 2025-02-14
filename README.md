# Stacker (7×15) with Side Panel & Leaderboard

A **Python** (Pygame) implementation of the classic arcade **Stacker** game.

## Features

- **7×15** Grid: The main gameplay area is 280×600 pixels on the left.
- **Side Panel** (200 px wide): Displays an optional logo, game instructions, and a 5-entry leaderboard.
- **Smooth Movement**: Blocks slide fully off one side before coming back.
- **Score Display**:
  - **Current Score** (top-left of play area).
  - **High Score** (top-right of play area).
- **Leaderboards**:
  - Keeps **top 5** scores (score + 3-letter initials).
  - Enter initials if you beat or tie the best all-time score.
- **Flashing on Failure**: If you lock with no overlap, the row flashes red, then **Game Over**.
- **Restart / Quit**: Press **R** to restart, **Esc** to quit.

## Requirements

- **Python 3.7+** (earlier versions might work, but untested)
- **Pygame 2.0+** (install via `pip install pygame`)

## Setup & Installation

1. **Clone** or **download** this repository to your local machine.
2. (Optional) Place a **`stacker_logo.png`** file in the same folder as `stacker.py` if you want a logo displayed in the side panel. Otherwise, it’ll just show “STACKER.”
3. Ensure you have **Pygame** installed:
   ```bash
   pip install pygame
   ```
4. You’re ready to run the game!

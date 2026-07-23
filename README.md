# Key Door Puzzle

A puzzle game where you match keys to doors by shape. Built with pygame.

## Requirements

- Python 3.7+
- pygame

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd key_door_puzzle

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python key_door_puzzle.py
```

## Controls

| Input             | Action                        |
| ----------------- | ----------------------------- |
| Arrow keys / WASD | Move the key                  |
| Mouse             | Move the key (alternative)    |
| TAB               | Switch between mouse/keyboard |
| ESC               | Quit / Back to menu           |
| SPACE / ENTER     | Start game / Next level       |

## Features

- 4 key shapes: Square, Triangle, Circle, Star
- 10 progressive levels
- Timer with decreasing time per level
- Lives system (3 lives)
- Score with time bonus
- Mouse and keyboard controls
- Visual feedback for correct/incorrect matches

## How It Works

1. A key with a specific shape appears at the bottom
2. Doors with different shape keyholes appear at the top
3. Move the key to the matching door
4. Correct match = level complete + time bonus
5. Wrong match or timeout = lose a life
6. Complete all 10 levels to win

## Project Structure

```
key_door_puzzle/
├── key_door_puzzle.py  # Main game
├── requirements.txt    # Dependencies
├── .gitignore          # Excludes cache and venv
└── README.md           # This file
```

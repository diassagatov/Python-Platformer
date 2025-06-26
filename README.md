# Platformer Game

![image](https://github.com/user-attachments/assets/8c2b889a-cbba-4720-b0da-ebdc16ed7ad5)

A simple and fun platformer built with Pygame Zero. Jump on moving platforms, avoid enemies, and try to beat your best score!

## Features
- Randomized platforms and speed each game
- Three enemy types: bee, snail, and saw
- Health bar, score, and persistent best score
- Sound effects (jump, hurt, disappear) with mute option
- Simple, clean UI and menu

## Installation
1. **Install Python 3.8+**
2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Running the Game
Start the game with:
```
pgzrun main.py
```

## Controls
- **A/D**: Move left/right
- **W**: Jump
- **MENU**: Return to menu (bottom right in-game)
- **MUTE**: Toggle sound (in menu)
- **EXIT**: Quit the game (in menu or game over)

## Project Structure
```
images/      # All .png image files (player, enemies, backgrounds)
sounds/      # All .ogg/.wav sound files
main.py      # Main game logic
hero.py      # Hero/player class
platform.py  # Platform class
requirements.txt
README.md
```

## Notes
- All images should be in the `images/` folder, all sounds in `sounds/`.
- The game saves your best score in `best_score.txt` (auto-created).

Enjoy the game and feel free to fork or contribute!

![image](https://github.com/user-attachments/assets/d7129558-e96a-4e25-9952-ace15af94a0b)


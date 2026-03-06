#!/usr/bin/env python3
"""Entry point for PyScopone – run this file to start the game."""

from scopone.game import Game


def main() -> None:
    game = Game(target_score=11, ai_delay=0.6)
    game.play()


if __name__ == "__main__":
    main()

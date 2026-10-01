"""Verifica a janela sem abrir uma interface visível (SDL dummy)."""
import os
import sys
import threading
import time
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
raiz = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(raiz / ".test-deps"))
sys.path.insert(0, str(raiz))
import pygame
from snake_game import snake_game


def comandos():
    while not pygame.display.get_init() or pygame.display.get_surface() is None:
        time.sleep(.02)
    time.sleep(.3)
    pygame.image.save(pygame.display.get_surface(), str(raiz / "tests" / "menu.png"))
    for tecla in (pygame.K_3, pygame.K_m, pygame.K_RETURN, pygame.K_UP,
                  pygame.K_p, pygame.K_SPACE, pygame.K_r, pygame.K_ESCAPE):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla))
        time.sleep(.15)
    pygame.event.post(pygame.event.Event(pygame.QUIT))


if __name__ == "__main__":
    worker = threading.Thread(target=comandos, daemon=True)
    worker.start()
    snake_game()
    worker.join(timeout=3)
    assert not worker.is_alive(), "A sequência de comandos não terminou"
    assert not pygame.get_init(), "Pygame não foi encerrado"
    print("Interface: menu, partida, pausa, reinício e saída executados.")

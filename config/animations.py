"""Definições de animação por spritesheet (ver GDD seção 21 - Sprites).

Cada entrada aponta para um arquivo dentro de assets/sprites/<pasta>/.
Se o arquivo ainda não existir, systems/animation.py gera um placeholder
automaticamente — então dá pra adicionar a arte real aos poucos, uma
animação de cada vez, sem quebrar nada.

Formato esperado do arquivo: PNG com todos os frames lado a lado na
horizontal, todos do mesmo tamanho (frame_w x frame_h).
"""

# ---Jogador---

PLAYER_FRAME_SIZE = (48, 64)

PLAYER_ANIMATIONS = {
    "idle": dict(file="idle.png", frame_w=48, frame_h=64, frames=4, fps=6, loop=True),
    "run": dict(file="run.png", frame_w=48, frame_h=64, frames=6, fps=10, loop=True),
    "jump": dict(file="jump.png", frame_w=48, frame_h=64, frames=2, fps=8, loop=False),
    "fall": dict(file="fall.png", frame_w=48, frame_h=64, frames=2, fps=8, loop=True),
    "attack_sword": dict(file="attack_sword.png", frame_w=48, frame_h=64, frames=4, fps=20, loop=False),
    "attack_shuriken": dict(file="attack_shuriken.png", frame_w=48, frame_h=64, frames=3, fps=16, loop=False),
    "hurt": dict(file="hurt.png", frame_w=48, frame_h=64, frames=2, fps=10, loop=False),
    "death": dict(file="death.png", frame_w=48, frame_h=64, frames=6, fps=8, loop=False),
}

# ---Inimigos---

ENEMY_ANIMATIONS = {
    "basico": {
        "idle": dict(file="idle.png", frame_w=44, frame_h=75, frames=4, fps=5, loop=True),
        "walk": dict(file="walk.png", frame_w=44, frame_h=75, frames=6, fps=10, loop=True),
        "attack": dict(file="attack.png", frame_w=44, frame_h=75, frames=3, fps=14, loop=False),
        "hurt": dict(file="hurt.png", frame_w=44, frame_h=75, frames=2, fps=10, loop=False),
        "death": dict(file="death.png", frame_w=44, frame_h=75, frames=5, fps=8, loop=False),
    },
    "rapido": {
        "idle": dict(file="idle.png", frame_w=38, frame_h=46, frames=4, fps=6, loop=True),
        "walk": dict(file="walk.png", frame_w=38, frame_h=46, frames=6, fps=16, loop=True),
        "attack": dict(file="attack.png", frame_w=38, frame_h=46, frames=3, fps=18, loop=False),
        "hurt": dict(file="hurt.png", frame_w=38, frame_h=46, frames=2, fps=10, loop=False),
        "death": dict(file="death.png", frame_w=38, frame_h=46, frames=5, fps=10, loop=False),
    },
    "resistente": {
        "idle": dict(file="idle.png", frame_w=50, frame_h=62, frames=4, fps=4, loop=True),
        "walk": dict(file="walk.png", frame_w=50, frame_h=62, frames=6, fps=8, loop=True),
        "attack": dict(file="attack.png", frame_w=50, frame_h=62, frames=4, fps=10, loop=False),
        "hurt": dict(file="hurt.png", frame_w=50, frame_h=62, frames=2, fps=8, loop=False),
        "death": dict(file="death.png", frame_w=50, frame_h=62, frames=6, fps=6, loop=False),
    },
    "distancia": {
        "idle": dict(file="idle.png", frame_w=40, frame_h=50, frames=4, fps=5, loop=True),
        "walk": dict(file="walk.png", frame_w=40, frame_h=50, frames=6, fps=10, loop=True),
        "attack": dict(file="attack.png", frame_w=40, frame_h=50, frames=3, fps=12, loop=False),
        "hurt": dict(file="hurt.png", frame_w=40, frame_h=50, frames=2, fps=10, loop=False),
        "death": dict(file="death.png", frame_w=40, frame_h=50, frames=5, fps=8, loop=False),
    },
}

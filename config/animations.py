#---Jogador---
PLAYER_FRAME_SIZE = (48, 64)

PLAYER_ANIMATIONS = {
    "idle": dict(file="idle.png", frame_w=48, frame_h=64, frames=4, fps=6, loop=True),
    "run": dict(file="run.png", frame_w=48, frame_h=64, frames=6, fps=12, loop=True),
    "jump": dict(file="jump.png", frame_w=48, frame_h=64, frames=2, fps=8, loop=False),
    "fall": dict(file="fall.png", frame_w=48, frame_h=64, frames=2, fps=8, loop=True),
    "attack_sword": dict(file="attack_sword.png", frame_w=48, frame_h=64, frames=4, fps=20, loop=False),
    "attack_shuriken": dict(file="attack_shuriken.png", frame_w=48, frame_h=64, frames=3, fps=16, loop=False),
    "hurt": dict(file="hurt.png", frame_w=48, frame_h=64, frames=2, fps=10, loop=False),
    "death": dict(file="death.png", frame_w=48, frame_h=64, frames=6, fps=8, loop=False),
}

#---Inimigos---
ENEMY_ANIMATIONS = {
    "basico": {
        "idle": dict(file="idle.png", frame_w=44, frame_h=56, frames=4, fps=5, loop=True),
        "walk": dict(file="walk.png", frame_w=44, frame_h=56, frames=6, fps=10, loop=True),
        "attack": dict(file="attack.png", frame_w=44, frame_h=56, frames=3, fps=14, loop=False),
        "hurt": dict(file="hurt.png", frame_w=44, frame_h=56, frames=2, fps=10, loop=False),
        "death": dict(file="death.png", frame_w=44, frame_h=56, frames=5, fps=8, loop=False),
    },
    "rapido": {
        "idle": dict(file="idle.png", frame_w=48, frame_h=60, frames=4, fps=6, loop=True),
        "walk": dict(file="walk.png", frame_w=48, frame_h=60, frames=6, fps=12, loop=True),
        "attack": dict(file="attack.png", frame_w=48, frame_h=60, frames=3, fps=12, loop=False),
        "hurt": dict(file="hurt.png", frame_w=48, frame_h=60, frames=2, fps=9, loop=False),
        "death": dict(file="death.png", frame_w=48, frame_h=60, frames=6, fps=10, loop=False),
    },
    "resistente": {
        "idle": dict(file="idle.png", frame_w=72, frame_h=88, frames=4, fps=5, loop=True),
        "walk": dict(file="walk.png", frame_w=72, frame_h=88, frames=6, fps=8, loop=True),
        "attack": dict(file="attack.png", frame_w=72, frame_h=88, frames=4, fps=10, loop=False),
        "hurt": dict(file="hurt.png", frame_w=72, frame_h=88, frames=2, fps=8, loop=False),
        "death": dict(file="death.png", frame_w=72, frame_h=88, frames=6, fps=7, loop=False),
    },
    "distancia": {
        "idle": dict(file="idle.png", frame_w=96, frame_h=72, frames=5, fps=6, loop=True),
        "walk": dict(file="walk.png", frame_w=96, frame_h=72, frames=8, fps=11, loop=True),
        "attack": dict(file="attack.png", frame_w=96, frame_h=72, frames=6, fps=13, loop=False),
        "hurt": dict(file="hurt.png", frame_w=96, frame_h=72, frames=3, fps=10, loop=False),
        "death": dict(file="death.png", frame_w=96, frame_h=72, frames=5, fps=8, loop=False),
    },
}

ENEMY_ANIMATIONS["chefe"] = {
    "idle": dict(file="idle.png", frame_w=124, frame_h=136, frames=4, fps=5, loop=True),
    "walk": dict(file="walk.png", frame_w=124, frame_h=136, frames=4, fps=7, loop=True),
    "attack": dict(file="attack.png", frame_w=124, frame_h=136, frames=3, fps=10, loop=False),
    "hurt": dict(file="hurt.png", frame_w=124, frame_h=136, frames=2, fps=10, loop=False),
    "death": dict(file="death.png", frame_w=124, frame_h=136, frames=6, fps=8, loop=False),
}
ENEMY_ANIMATIONS["boss_basico"] = {
    "idle": dict(file="idle.png", frame_w=72, frame_h=90, frames=4, fps=5, loop=True),
    "walk": dict(file="walk.png", frame_w=72, frame_h=90, frames=6, fps=9, loop=True),
    "attack": dict(file="attack.png", frame_w=72, frame_h=90, frames=3, fps=12, loop=False),
    "hurt": dict(file="hurt.png", frame_w=72, frame_h=90, frames=2, fps=10, loop=False),
    "death": dict(file="death.png", frame_w=72, frame_h=90, frames=5, fps=8, loop=False),
}
ENEMY_ANIMATIONS["boss_distancia"] = {
    "idle": dict(file="idle.png", frame_w=120, frame_h=120, frames=5, fps=6, loop=True),
    "walk": dict(file="walk.png", frame_w=120, frame_h=120, frames=8, fps=10, loop=True),
    "attack": dict(file="attack.png", frame_w=120, frame_h=120, frames=6, fps=12, loop=False),
    "hurt": dict(file="hurt.png", frame_w=120, frame_h=120, frames=3, fps=10, loop=False),
    "death": dict(file="death.png", frame_w=120, frame_h=120, frames=5, fps=8, loop=False),
}
ENEMY_ANIMATIONS["boss_resistente"] = {
    "idle": dict(file="idle.png", frame_w=108, frame_h=132, frames=4, fps=4, loop=True),
    "walk": dict(file="walk.png", frame_w=108, frame_h=132, frames=6, fps=6, loop=True),
    "attack": dict(file="attack.png", frame_w=108, frame_h=132, frames=4, fps=8, loop=False),
    "hurt": dict(file="hurt.png", frame_w=108, frame_h=132, frames=2, fps=8, loop=False),
    "death": dict(file="death.png", frame_w=108, frame_h=132, frames=6, fps=6, loop=False),
}
# Quinto e último chefe: samurai sombrio enviado pelo usuário.
ENEMY_ANIMATIONS["boss_samurai"] = {
    "idle": dict(file="idle.png", frame_w=160, frame_h=170, frames=4, fps=5, loop=True),
    "walk": dict(file="walk.png", frame_w=160, frame_h=170, frames=6, fps=8, loop=True),
    "attack": dict(file="attack.png", frame_w=160, frame_h=170, frames=4, fps=10, loop=False),
    "hurt": dict(file="hurt.png", frame_w=160, frame_h=170, frames=2, fps=8, loop=False),
    "death": dict(file="death.png", frame_w=160, frame_h=170, frames=5, fps=7, loop=False),
}

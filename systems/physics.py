"""Funções de física básica: movimento horizontal, gravidade e salto
(ver GDD seção 5 - Física e Movimentação)."""

from config import settings


def apply_gravity(vy, dt):
    """vy = vy0 + g * dt, limitada à velocidade máxima de queda."""
    vy += settings.GRAVITY * dt
    if vy > settings.MAX_FALL_SPEED:
        vy = settings.MAX_FALL_SPEED
    return vy


def integrate_position(pos, vel, dt):
    """x = x0 + v * dt"""
    return pos + vel * dt


def apply_jump(jump_power=None):
    """vy = -Vp"""
    if jump_power is None:
        jump_power = settings.JUMP_POWER
    return -jump_power

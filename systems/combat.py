"""Cálculos de combate e vida"""

def calculate_damage(base_damage, multiplier=1.0):
    """Dano = DanoBase * MultiplicadorDeAtaque"""
    return base_damage * multiplier


def apply_damage(current_hp, damage):
    """VidaAtual = VidaAtual - DanoRecebido"""
    return max(0, current_hp - damage)

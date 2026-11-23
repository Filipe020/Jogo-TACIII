"""Colisões via Bounding Boxes retangularespara simplificar a plataforma: Jogador/Inimigo x Plataforma, Ataque/Shuriken x Inimigo."""

import pygame

from config import settings

def rects_collide(a: pygame.Rect, b: pygame.Rect) -> bool:
    return a.colliderect(b)

def resolve_horizontal(entity, platforms):
    """Impede que a entidade atravesse plataformas horizontalmente."""
    rect = entity.rect
    for plat in platforms:
        if rect.colliderect(plat):
            if entity.vx > 0:
                entity.x = plat.left - entity.width
            elif entity.vx < 0:
                entity.x = plat.right
            entity.vx = 0
            rect = entity.rect


def resolve_vertical(entity, platforms):
    """Resolve pouso sobre plataformas (chão) e colisão com o teto."""
    entity.on_ground = False
    rect = entity.rect
    for plat in platforms:
        if rect.colliderect(plat):
            if entity.vy > 0:  # caindo -> pousa em cima
                entity.y = plat.top - entity.height
                entity.vy = 0
                entity.on_ground = True
            elif entity.vy < 0:  # subindo -> bate a cabeça
                entity.y = plat.bottom
                entity.vy = 0
            rect = entity.rect

    TOLERANCIA_SNAP = 6
    if not entity.on_ground and entity.vy >= 0:
        for plat in platforms:
            sobrepoe_x = rect.right > plat.left and rect.left < plat.right
            distancia_ate_topo = plat.top - rect.bottom
            se_esta_logo_acima = 0 <= distancia_ate_topo <= TOLERANCIA_SNAP
            if sobrepoe_x and se_esta_logo_acima:
                entity.y = plat.top - entity.height
                entity.vy = 0
                entity.on_ground = True
                break

def resolve_vertical_one_way(entity, platforms, previous_bottom):
    """Pouso em plataformas atravessáveis por baixo (jogador).

    Aterrissa apenas durante a queda e quando os pés estavam em cima da
    superfície no frame anterior. Isso permite saltar debaixo de plataformas
    elevadas sem bater a cabeça ou ser bloqueado lateralmente.
    """
    entity.on_ground = False
    if entity.vy < 0:
        return

    rect = entity.rect
    tolerancia = 6
    pouso = None
    for plat in platforms:
        sobrepoe_x = rect.right > plat.left and rect.left < plat.right
        if not sobrepoe_x:
            continue
        # Plataformas elevadas deixam passar de baixo para cima. O chão
        # principal, porém, deve sempre recolocar o jogador sobre o terreno,
        # inclusive se um mapa antigo tiver um spawn salvo abaixo do piso.
        piso_principal = (plat.top == settings.GROUND_Y
                          and plat.bottom >= settings.SCREEN_HEIGHT)
        if previous_bottom > plat.top + 0.5 and not piso_principal:
            continue
        # Considera tanto o cruzamento da plataforma quanto o encaixe quando
        # o personagem já está parado no topo (diferenças de arredondamento).
        if rect.bottom >= plat.top - tolerancia:
            if pouso is None or plat.top < pouso:
                pouso = plat.top

    if pouso is not None:
        entity.y = pouso - entity.height
        entity.vy = 0
        entity.on_ground = True


def check_attack_hit(attack_rect, targets):
    """Retorna a lista de alvos atingidos por um retângulo de ataque"""
    hits = []
    for t in targets:
        if getattr(t, "alive", True) and attack_rect.colliderect(t.rect):
            hits.append(t)
    return hits

def clamp_to_bounds(entity, min_x, max_x):
    """Impede que a entidade saia dos limites do nível."""
    if entity.x < min_x:
        entity.x = min_x
        entity.vx = 0
    if entity.x + entity.width > max_x:
        entity.x = max_x - entity.width
        entity.vx = 0

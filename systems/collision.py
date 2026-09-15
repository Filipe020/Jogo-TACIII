"""Colisões via Bounding Boxes retangulares (ver GDD seção 6).
Resolve eixo horizontal e vertical separadamente para simplificar a
plataforma: Jogador/Inimigo x Plataforma, Ataque/Shuriken x Inimigo."""

import pygame


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

    # "Snap" ao chão: a cada frame a gravidade acelera vy um pouco (mesmo
    # com o personagem parado), então no frame seguinte ao pouso o
    # deslocamento pode ser pequeno demais para o rect ainda se sobrepor
    # à plataforma (bordas apenas encostando não contam como colisão em
    # colliderect). Sem isso, on_ground fica alternando True/False a cada
    # frame e a animação "pisca" entre idle e queda mesmo parado.
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


def check_attack_hit(attack_rect, targets):
    """Retorna a lista de alvos atingidos por um retângulo de ataque
    (Ataque x Inimigo / Shuriken x Inimigo)."""
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

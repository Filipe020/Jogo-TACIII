"""Inimigos: básico, rápido, resistente e à distância"""

import os
import random
from itertools import count

import pygame

from entities.entity import Entity
from entities.projectile import Projectile
from systems import physics, collision, combat
from systems.animation import AnimationController
from config import settings
from config.animations import ENEMY_ANIMATIONS

TIPOS = {
    "basico": dict(width=26, height=38, health=30, damage=10, speed=90,
                    cor=settings.ENEMY_COLORS["basico"]),
    "rapido": dict(width=22, height=30, health=16, damage=6, speed=190,
                    cor=settings.ENEMY_COLORS["rapido"]),
    "resistente": dict(width=34, height=46, health=70, damage=14, speed=55,
                        cor=settings.ENEMY_COLORS["resistente"]),
    "distancia": dict(width=24, height=34, health=20, damage=8, speed=60,
                       cor=settings.ENEMY_COLORS["distancia"]),
}


class Enemy(Entity):
    _ids = count(1)
    def __init__(self, x, y, tipo="basico"):
        info = TIPOS[tipo]
        super().__init__(x, y, info["width"], info["height"])
        self.uid = next(self._ids)
        self.tipo = tipo
        self.max_health = info["health"]
        self.health = self.max_health
        self.damage = info["damage"]
        self.speed = info["speed"]
        self.cor = info["cor"]
        self.ataque_cooldown = 1.1
        self.ataque_timer = random.uniform(0, self.ataque_cooldown)
        self.projectiles = []
        self.jump_cooldown = 0.0
        self.jump_target_x = None
        # Impulso maior que o do ninja para perseguir em plataformas altas.
        self.jump_power = {"rapido": 850, "resistente": 850, "basico": 870, "distancia": 820}[tipo]

        #---Animação---
        info_anim = ENEMY_ANIMATIONS[tipo]
        self.frame_size = (info_anim["idle"]["frame_w"], info_anim["idle"]["frame_h"])
        self.anim = AnimationController(
            info_anim,
            pasta_base=os.path.join(settings.BASE_DIR, "assets", "sprites", "enemies", tipo),
            cor_placeholder=self.cor,
        )
        self.anim.trocar_estado("idle")
        self.anim_ataque_timer = 0.0
        self.anim_hurt_timer = 0.0

    def _objetivo_plataforma(self, player, platforms):
        """Define degrau, local de decolagem (fora da parede) e pouso.

        As plataformas são sólidas: saltar por baixo causaria colisão no teto.
        """
        meus_pes = self.rect.bottom
        alvo_x, alvo_y = player.rect.centerx, player.rect.bottom
        max_subida = self.jump_power ** 2 / (2 * settings.GRAVITY) - 12
        candidatas = []
        for plat in platforms:
            subida = meus_pes - plat.top
            if not (20 < subida <= max_subida):
                continue
            # Aproximação em uma das duas bordas, sem entrar sob a plataforma.
            offset = self.width / 2 + 10
            pontos = (
                (plat.left - offset, plat.left + min(28, plat.width / 3)),
                (plat.right + offset, plat.right - min(28, plat.width / 3)),
            )
            for decolagem, pouso in pontos:
                distancia = abs(decolagem - self.rect.centerx)
                if distancia > 250:
                    continue
                if not (0 <= decolagem <= 12000):
                    continue
                # Preferir plataformas próximas da posição/altura do alvo.
                score = (abs(pouso - alvo_x) * 0.65 + abs(plat.top - alvo_y) * 1.1
                         + distancia * 0.28)
                candidatas.append((score, decolagem, pouso))
        return min(candidatas)[1:] if candidatas else None

    def _precisa_pular(self, player, platforms):
        if not self.on_ground or self.jump_cooldown > 0:
            return False
        meus_pes = self.rect.bottom
        # A plataforma do jogador precisa ser alcançável a partir da posição atual.
        # Um obstáculo à frente impede o deslocamento horizontal.
        if self.vx:
            frente = self.rect.move(12 if self.vx > 0 else -12, -6)
            for plat in platforms:
                if frente.colliderect(plat) and plat.top < meus_pes - 10:
                    return True
        return False

    def atualizar_ia(self, dt, player, platforms, level_bounds):
        if not self.alive:
            self.anim.trocar_estado("death")
            self.anim.atualizar(dt)
            for proj in self.projectiles:
                proj.update(dt)
            self.projectiles = [p for p in self.projectiles if p.alive]
            return

        self.jump_cooldown = max(0, self.jump_cooldown - dt)
        dist_x = player.rect.centerx - self.rect.centerx
        self.facing = 1 if dist_x >= 0 else -1
        meu_objetivo = None
        if player.rect.bottom < self.rect.bottom - 25 and self.on_ground:
            meu_objetivo = self._objetivo_plataforma(player, platforms)

        if not self.on_ground and self.jump_target_x is not None:
            delta = self.jump_target_x - self.rect.centerx
            self.vx = (1 if delta > 0 else -1) * self.speed if abs(delta) > 7 else 0
        elif meu_objetivo:
            decolagem_x, pouso_x = meu_objetivo
            diferenca = decolagem_x - self.rect.centerx
            self.vx = (1 if diferenca > 0 else -1) * self.speed if abs(diferenca) > 7 else 0
            if self.on_ground and self.jump_cooldown == 0 and abs(diferenca) < 12:
                self.vy = -self.jump_power
                self.on_ground = False
                self.jump_cooldown = 0.65
                self.jump_target_x = pouso_x
        elif self.tipo == "distancia":
            distancia_ideal = 260
            if abs(dist_x) < distancia_ideal - 20:
                self.vx = -self.facing * self.speed
            elif abs(dist_x) > distancia_ideal + 20:
                self.vx = self.facing * self.speed
            else:
                self.vx = 0
        else:
            self.vx = self.facing * self.speed if abs(dist_x) > 4 else 0

        if not meu_objetivo and self.jump_target_x is None and self._precisa_pular(player, platforms):
            self.vy = -self.jump_power
            self.on_ground = False
            self.jump_cooldown = 0.65

        self.ataque_timer += dt
        if self.tipo == "distancia":
            if self.ataque_timer >= self.ataque_cooldown and abs(dist_x) < 420 and abs(player.rect.centery - self.rect.centery) < 75:
                self._atirar()
                self.ataque_timer = 0
        else:
            if self.ataque_timer >= self.ataque_cooldown and self.rect.colliderect(player.rect.inflate(6, 6)):
                player.receber_dano(self.damage)
                self.ataque_timer = 0
                self.anim_ataque_timer = 0.25

        self.x = physics.integrate_position(self.x, self.vx, dt)
        collision.resolve_horizontal(self, platforms)
        collision.clamp_to_bounds(self, level_bounds[0], level_bounds[1])

        self.vy = physics.apply_gravity(self.vy, dt)
        self.y = physics.integrate_position(self.y, self.vy, dt)
        collision.resolve_vertical(self, platforms)
        if self.on_ground:
            self.jump_target_x = None

        for proj in self.projectiles:
            proj.update(dt)
        self.projectiles = [p for p in self.projectiles if p.alive]
        self._atualizar_animacao(dt)

    def _atualizar_animacao(self, dt):
        if self.anim_hurt_timer > 0:
            self.anim_hurt_timer -= dt
            estado = "hurt"
        elif self.anim_ataque_timer > 0:
            self.anim_ataque_timer -= dt
            estado = "attack"
        elif abs(self.vx) > 1:
            estado = "walk"
        else:
            estado = "idle"

        self.anim.trocar_estado(estado)
        self.anim.atualizar(dt)

    def _atirar(self):
        proj = Projectile(self.rect.centerx, self.rect.centery, self.facing,
                           speed=300, damage=self.damage, from_player=False)
        self.projectiles.append(proj)
        self.anim_ataque_timer = 0.2

    def receber_dano(self, dano, audio=None):
        if not self.alive:
            return
        self.health = combat.apply_damage(self.health, dano)
        if audio:
            audio.play("hit")
        if self.health <= 0:
            self.alive = False
            if audio:
                audio.play("enemy_death")
        else:
            self.anim_hurt_timer = 0.15

    def animacao_morte_terminou(self):
        return (not self.alive) and self.anim.animacao_terminou()

    def draw(self, surface, camera_x):
        frame_w, frame_h = self.frame_size
        draw_x = self.rect.centerx - camera_x - frame_w // 2
        draw_y = self.rect.bottom - frame_h
        self.anim.desenhar(surface, draw_x, draw_y, self.facing)

        if self.alive and self.health < self.max_health:
            rect = self.rect
            rect.x -= camera_x
            barra_bg = pygame.Rect(rect.x, rect.y - 8, rect.width, 4)
            pct = max(0, self.health / self.max_health)
            barra_fg = pygame.Rect(rect.x, rect.y - 8, int(rect.width * pct), 4)
            pygame.draw.rect(surface, settings.COLOR_HP_BG, barra_bg)
            pygame.draw.rect(surface, settings.COLOR_HP, barra_fg)

        for proj in self.projectiles:
            proj.draw(surface, camera_x)

"""Inimigos: básico, rápido, resistente e à distância (GDD seção 10)."""

import os
import random

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
    def __init__(self, x, y, tipo="basico"):
        info = TIPOS[tipo]
        super().__init__(x, y, info["width"], info["height"])
        self.tipo = tipo
        self.max_health = info["health"]
        self.health = self.max_health
        self.damage = info["damage"]
        self.speed = info["speed"]
        self.cor = info["cor"]
        self.ataque_cooldown = 1.1
        self.ataque_timer = random.uniform(0, self.ataque_cooldown)
        self.projectiles = []

        # --- Animação (GDD seção 21) ---
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

    def atualizar_ia(self, dt, player, platforms, level_bounds):
        if not self.alive:
            # Inimigo já morreu: só termina de tocar a animação de morte
            # e deixa os projéteis que ainda estejam no ar continuarem.
            self.anim.trocar_estado("death")
            self.anim.atualizar(dt)
            for proj in self.projectiles:
                proj.update(dt)
            self.projectiles = [p for p in self.projectiles if p.alive]
            return

        dist_x = player.rect.centerx - self.rect.centerx
        self.facing = 1 if dist_x > 0 else -1

        if self.tipo == "distancia":
            distancia_ideal = 260
            if abs(dist_x) < distancia_ideal - 20:
                self.vx = -self.facing * self.speed
            elif abs(dist_x) > distancia_ideal + 20:
                self.vx = self.facing * self.speed
            else:
                self.vx = 0
        else:
            self.vx = self.facing * self.speed if abs(dist_x) > 4 else 0

        self.ataque_timer += dt
        if self.tipo == "distancia":
            if self.ataque_timer >= self.ataque_cooldown and abs(dist_x) < 420:
                self._atirar()
                self.ataque_timer = 0
        else:
            if self.ataque_timer >= self.ataque_cooldown and self.rect.colliderect(player.rect.inflate(6, 6)):
                player.receber_dano(self.damage)
                self.ataque_timer = 0
                self.anim_ataque_timer = 0.25

        # Física (mesmas fórmulas do GDD seção 5)
        self.x = physics.integrate_position(self.x, self.vx, dt)
        collision.resolve_horizontal(self, platforms)
        collision.clamp_to_bounds(self, level_bounds[0], level_bounds[1])

        self.vy = physics.apply_gravity(self.vy, dt)
        self.y = physics.integrate_position(self.y, self.vy, dt)
        collision.resolve_vertical(self, platforms)

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

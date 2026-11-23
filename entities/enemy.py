"""Inimigos: básico, rápido, resistente, à distância e chefes."""

import os
import random
from itertools import count
from systems.display import sdim, spt, srect, sval

import pygame

from entities.entity import Entity
from entities.projectile import Projectile
from systems import physics, collision, combat
from systems.animation import AnimationController
from config import settings
from config.animations import ENEMY_ANIMATIONS

BOSS_TYPES = ("chefe", "boss_basico", "boss_distancia", "boss_resistente", "boss_samurai")
RANGED_TYPES = ("distancia", "chefe", "boss_distancia")

TIPOS = {
    "basico": dict(width=26, height=38, health=30, damage=10, speed=90,
                    cor=settings.ENEMY_COLORS["basico"]),
    "rapido": dict(width=22, height=30, health=16, damage=6, speed=190,
                    cor=settings.ENEMY_COLORS["rapido"]),
    "resistente": dict(width=34, height=46, health=70, damage=14, speed=55,
                        cor=settings.ENEMY_COLORS["resistente"]),
    "distancia": dict(width=24, height=34, health=20, damage=8, speed=60,
                       cor=settings.ENEMY_COLORS["distancia"]),
    "chefe": dict(width=76, height=94, health=300, damage=18, speed=85,
                   cor=settings.ENEMY_COLORS["chefe"]),
    "boss_basico": dict(width=56, height=80, health=340, damage=22, speed=88,
                          cor=settings.ENEMY_COLORS["boss_basico"]),
    "boss_distancia": dict(width=68, height=90, health=280, damage=12, speed=72,
                             cor=settings.ENEMY_COLORS["boss_distancia"]),
    "boss_resistente": dict(width=76, height=102, health=420, damage=20, speed=64,
                              cor=settings.ENEMY_COLORS["boss_resistente"]),
    "boss_samurai": dict(width=82, height=108, health=520, damage=24, speed=112,
                           cor=settings.ENEMY_COLORS["boss_samurai"]),
}

ENEMY_FOOT_OFFSETS = {
    "basico": 4, "rapido": 4, "resistente": 2,
    "distancia": 1, "chefe": 0, "boss_basico": 2, "boss_distancia": 2,
    "boss_resistente": 3, "boss_samurai": 2,
}

_ATTACK_COOLDOWNS = {
    "chefe": 1.6,
    "boss_basico": 1.25,
    "boss_distancia": 1.55,
    "boss_resistente": 1.35,
    "boss_samurai": 1.15,
}

_JUMP_POWER = {
    "rapido": 850, "resistente": 850, "basico": 870,
    "distancia": 820, "chefe": 960, "boss_basico": 940,
    "boss_distancia": 900, "boss_resistente": 900,
    "boss_samurai": 980,
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
        self.ataque_cooldown = _ATTACK_COOLDOWNS.get(tipo, 1.1)
        self.contato_timer = 0.0
        self.ataque_timer = random.uniform(0, self.ataque_cooldown)
        self.projectiles = []
        self.jump_cooldown = 0.0
        self.jump_target_x = None
        self.jump_power = _JUMP_POWER[tipo]
        self.pulso_cooldown = 2.2 if tipo == "boss_resistente" else 0.0
        self.pulso_carga = 0.0
        self.pulso_efeito = 0.0
        self.samurai_dash_cooldown = 1.4 if tipo == "boss_samurai" else 0.0
        self.samurai_dash_timer = 0.0
        self.samurai_dash_hit = False

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

    @property
    def is_boss(self):
        return self.tipo in BOSS_TYPES

    def _objetivo_plataforma(self, player, platforms):
        meus_pes = self.rect.bottom
        alvo_x, alvo_y = player.rect.centerx, player.rect.bottom
        max_subida = self.jump_power ** 2 / (2 * settings.GRAVITY) - 12
        candidatas = []
        for plat in platforms:
            subida = meus_pes - plat.top
            if not (20 < subida <= max_subida):
                continue
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
                score = (abs(pouso - alvo_x) * 0.65 + abs(plat.top - alvo_y) * 1.1
                         + distancia * 0.28)
                candidatas.append((score, decolagem, pouso))
        return min(candidatas)[1:] if candidatas else None

    def _precisa_pular(self, player, platforms):
        if not self.on_ground or self.jump_cooldown > 0:
            return False
        meus_pes = self.rect.bottom
        if self.vx:
            frente = self.rect.move(12 if self.vx > 0 else -12, -6)
            for plat in platforms:
                if frente.colliderect(plat) and plat.top < meus_pes - 10:
                    return True
        return False

    def _atingir_alvos(self, targets, dano, alcance_x, alcance_y=None):
        atingiu = False
        alcance_y = alcance_y if alcance_y is not None else max(self.height, 72)
        for alvo in targets:
            if alvo is None or getattr(alvo, "morto", False):
                continue
            if (abs(alvo.rect.centerx - self.rect.centerx) <= alcance_x
                    and abs(alvo.rect.centery - self.rect.centery) <= alcance_y
                    and self.rect.colliderect(alvo.rect.inflate(6, 6))):
                alvo.receber_dano(dano)
                atingiu = True
        return atingiu

    def atualizar_ia(self, dt, player, platforms, level_bounds, targets=None):
        if not self.alive:
            self.anim.trocar_estado("death")
            self.anim.atualizar(dt)
            for proj in self.projectiles:
                proj.update(dt)
            self.projectiles = [p for p in self.projectiles if p.alive]
            return

        targets = tuple(targets) if targets is not None else (player,)
        self.jump_cooldown = max(0, self.jump_cooldown - dt)
        self.contato_timer = max(0, self.contato_timer - dt)
        self.pulso_efeito = max(0.0, self.pulso_efeito - dt)
        if self.tipo == "boss_samurai":
            self.samurai_dash_cooldown = max(0.0, self.samurai_dash_cooldown - dt)
            self.samurai_dash_timer = max(0.0, self.samurai_dash_timer - dt)
        dist_x = player.rect.centerx - self.rect.centerx
        self.facing = 1 if dist_x >= 0 else -1
        meu_objetivo = None
        if player.rect.bottom < self.rect.bottom - 25 and self.on_ground:
            meu_objetivo = self._objetivo_plataforma(player, platforms)

        if self.samurai_dash_timer > 0:
            self.vx = self.facing * 420
            if not self.samurai_dash_hit and self._atingir_alvos(targets, self.damage + 6, 72, 82):
                self.samurai_dash_hit = True
                self.contato_timer = 0.55
        elif not self.on_ground and self.jump_target_x is not None:
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
        elif self.tipo in ("distancia", "boss_distancia"):
            distancia_ideal = 340 if self.tipo == "boss_distancia" else 260
            if abs(dist_x) < distancia_ideal - 20:
                self.vx = -self.facing * self.speed
            elif abs(dist_x) > distancia_ideal + 20:
                self.vx = self.facing * self.speed
            else:
                self.vx = 0
        else:
            self.vx = self.facing * self.speed if abs(dist_x) > 4 else 0

        if (self.tipo == "boss_samurai" and self.samurai_dash_timer == 0 and self.on_ground
                and self.samurai_dash_cooldown == 0 and 90 <= abs(dist_x) <= 320):
            self.samurai_dash_timer = 0.32
            self.samurai_dash_cooldown = 2.4
            self.samurai_dash_hit = False
            self.anim_ataque_timer = 0.4

        if not meu_objetivo and self.jump_target_x is None and self._precisa_pular(player, platforms):
            self.vy = -self.jump_power
            self.on_ground = False
            self.jump_cooldown = 0.65

        if self.tipo == "boss_resistente":
            self._atualizar_pulso_espectral(dt, targets)
            if self.pulso_carga > 0:
                self.vx = 0

        self.ataque_timer += dt
        if self.tipo in RANGED_TYPES:
            alcance = {"distancia": 420, "chefe": 540, "boss_distancia": 620}[self.tipo]
            diferenca_altura = {"distancia": 75, "chefe": 160, "boss_distancia": 170}[self.tipo]
            if (self.ataque_timer >= self.ataque_cooldown and abs(dist_x) < alcance
                    and abs(player.rect.centery - self.rect.centery) < diferenca_altura):
                self._atirar()
                self.ataque_timer = 0
            if (self.tipo == "chefe" and self.contato_timer == 0
                    and self.rect.colliderect(player.rect.inflate(8, 8))):
                player.receber_dano(self.damage)
                self.contato_timer = 1.2
        else:
            if (self.tipo == "boss_samurai" and self.samurai_dash_timer > 0):
                pass
            elif (self.pulso_carga <= 0 and self.ataque_timer >= self.ataque_cooldown
                    and self._atingir_alvos(targets, self.damage, 48 if not self.is_boss else 62, 72)):
                self.ataque_timer = 0
                self.anim_ataque_timer = 0.35 if self.is_boss else 0.25

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

    def _atualizar_pulso_espectral(self, dt, targets):
        if self.pulso_carga > 0:
            self.pulso_carga = max(0.0, self.pulso_carga - dt)
            if self.pulso_carga == 0:
                self.pulso_efeito = 0.42
                self.anim_ataque_timer = 0.45
                for alvo in targets:
                    if (alvo is not None and not getattr(alvo, "morto", False)
                            and abs(alvo.rect.centerx - self.rect.centerx) <= 165
                            and abs(alvo.rect.centery - self.rect.centery) <= 125):
                        alvo.receber_dano(16)
            return

        self.pulso_cooldown = max(0.0, self.pulso_cooldown - dt)
        if self.pulso_cooldown > 0:
            return
        if any(alvo is not None and not getattr(alvo, "morto", False)
               and abs(alvo.rect.centerx - self.rect.centerx) <= 220
               and abs(alvo.rect.centery - self.rect.centery) <= 140
               for alvo in targets):
            self.pulso_carga = 0.72
            self.pulso_cooldown = 3.8
            self.anim_ataque_timer = 0.72

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
        if self.tipo == "chefe":
            for altura in (-22, 22):
                self.projectiles.append(Projectile(
                    self.rect.centerx, self.rect.centery + altura,
                    self.facing, speed=360, damage=12, from_player=False,
                ))
            self.anim_ataque_timer = 0.35
        elif self.tipo == "boss_distancia":
            for altura in (-18, 0, 18):
                self.projectiles.append(Projectile(
                    self.rect.centerx, self.rect.centery + altura,
                    self.facing, speed=390, damage=10, from_player=False,
                ))
            self.anim_ataque_timer = 0.35
        else:
            self.projectiles.append(Projectile(
                self.rect.centerx, self.rect.centery, self.facing,
                speed=300, damage=self.damage, from_player=False,
            ))
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
            self.anim_hurt_timer = 0.18 if self.is_boss else 0.15

    def animacao_morte_terminou(self):
        return (not self.alive) and self.anim.animacao_terminou()

    def draw(self, surface, camera_x):
        frame_w, frame_h = self.frame_size
        draw_x = self.rect.centerx - camera_x - frame_w // 2
        padding_visual = ENEMY_FOOT_OFFSETS[self.tipo]
        draw_y = self.rect.bottom - frame_h - padding_visual

        frame_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        self.anim.desenhar(frame_surf, 0, 0, self.facing)
        scaled_frame = pygame.transform.scale(frame_surf, sdim(frame_w, frame_h))
        surface.blit(scaled_frame, spt(draw_x, draw_y))

        if self.tipo == "boss_resistente" and self.alive:
            centro = spt(int(self.rect.centerx - camera_x), int(self.rect.centery))
            if self.pulso_carga > 0:
                progresso = 1.0 - self.pulso_carga / 0.72
                raio = sval(int(75 + 100 * progresso))
                pygame.draw.circle(surface, (168, 206, 255), centro, raio, sval(3))
            elif self.pulso_efeito > 0:
                progresso = 1.0 - self.pulso_efeito / 0.42
                raio = sval(int(170 + 24 * progresso))
                pygame.draw.circle(surface, (229, 245, 255), centro, raio, sval(4))
        elif self.tipo == "boss_samurai" and self.alive and self.samurai_dash_timer > 0:
            cx, cy = int(self.rect.centerx - camera_x), int(self.rect.centery)
            pygame.draw.circle(surface, (244, 100, 137), spt(cx, cy), sval(58), sval(2))
            pygame.draw.line(
                surface,
                (255, 132, 161),
                spt(cx - 45, cy + 14),
                spt(cx + 45 * self.facing, cy - 12),
                sval(3),
            )

        if self.alive and not self.is_boss and self.health < self.max_health:
            rect = self.rect
            rect.x -= camera_x
            barra_bg = srect(rect.x, rect.y - 8, rect.width, 4)
            pct = max(0, self.health / self.max_health)
            barra_fg = srect(rect.x, rect.y - 8, int(rect.width * pct), 4)
            pygame.draw.rect(surface, settings.COLOR_HP_BG, barra_bg)
            pygame.draw.rect(surface, settings.COLOR_HP, barra_fg)

        for proj in self.projectiles:
            proj.draw(surface, camera_x)
"""Personagem principal"""

import os

import pygame

from entities.entity import Entity
from entities.projectile import Projectile
from weapons.sword import Sword
from weapons.shuriken import ShurikenWeapon
from systems import physics, collision, combat
from systems.animation import AnimationController
from config import settings
from config.animations import PLAYER_ANIMATIONS, PLAYER_FRAME_SIZE

class Player(Entity):
    WIDTH = 28
    HEIGHT = 44

    def __init__(self, x, y, progression):
        super().__init__(x, y, self.WIDTH, self.HEIGHT)
        self.progression = progression

        self.sword = Sword()
        self.shuriken_weapon = ShurikenWeapon()
        self.cooldown_espada_base = self.sword.cooldown
        self.cooldown_shuriken_base = self.shuriken_weapon.cooldown
        self.max_health = 100
        self.health = 100
        self.speed = settings.MOVE_SPEED
        self.shurikens_max = 5
        self.shurikens = 5
        self.shuriken_regen_time = 2.2
        self.shuriken_regen_timer = 0.0
        self.mult_dano_espada = 1.0
        self.mult_dano_shuriken = 1.0
        self.aplicar_melhorias()  # Aplica os níveis iniciais, se a opção foi Continuar.

        self.invulneravel_timer = 0.0
        self.ataque_visual_timer = 0.0
        self.atingidos_espada = set()
        self.projectiles = []

        self.morto = False

        #---Animação---
        self.anim = AnimationController(
            PLAYER_ANIMATIONS,
            pasta_base=os.path.join(settings.BASE_DIR, "assets", "sprites", "player"),
            cor_placeholder=settings.COLOR_PLAYER,
        )
        self.anim.trocar_estado("idle")
        self.anim_acao_timer = 0.0   #duração restante de uma animação de ação (ataque/dano)
        self.anim_acao_nome = None   # 'attack_sword' | 'attack_shuriken' | 'hurt'

    def aplicar_melhorias(self):
        """Atualiza imediatamente os atributos sem recriar o jogador.

        Não restaura toda a vida ou shurikens: concede apenas o aumento
        correspondente quando o máximo sobe.
        """
        nova_vida_max = 100 + self.progression.bonus_vida_maxima()
        delta_vida = nova_vida_max - self.max_health
        self.max_health = nova_vida_max
        self.health = max(0, min(self.max_health, self.health + max(0, delta_vida)))

        self.speed = settings.MOVE_SPEED * self.progression.multiplicador_velocidade()
        novo_max_shurikens = 5 + self.progression.bonus_shurikens()
        delta_shurikens = novo_max_shurikens - self.shurikens_max
        self.shurikens_max = novo_max_shurikens
        self.shurikens = max(0, min(novo_max_shurikens, self.shurikens + max(0, delta_shurikens)))

        self.mult_dano_espada = self.progression.multiplicador_dano_espada()
        self.mult_dano_shuriken = self.progression.multiplicador_dano_shuriken()
        mult = self.progression.multiplicador_velocidade_ataque()
        self.sword.cooldown = self.cooldown_espada_base * mult
        self.shuriken_weapon.cooldown = self.cooldown_shuriken_base * mult

    #---Entrada---
    def handle_input(self, keys, audio):
        """Lê comandos do computador local (modo solo ou anfitrião LAN)."""
        botoes = pygame.mouse.get_pressed()
        self.handle_actions({
            "left": bool(keys[pygame.K_a]),
            "right": bool(keys[pygame.K_d]),
            "jump": bool(keys[pygame.K_w] or keys[pygame.K_SPACE]),
            "sword": bool(botoes[0]),
            "shuriken": bool(botoes[2]),
        }, audio)

    def handle_actions(self, actions, audio):
        """Os mesmos comandos para jogadores locais e vindos da LAN."""
        if self.morto:
            self.vx = 0
            return
        move = int(bool(actions.get("right"))) - int(bool(actions.get("left")))
        self.vx = move * self.speed
        if move:
            self.facing = 1 if move > 0 else -1

        if actions.get("jump") and self.on_ground:
            self.vy = physics.apply_jump()
            self.on_ground = False
            audio.play("jump")

        if actions.get("sword") and self.sword.pode_atacar():
            self._atacar_espada()
            audio.play("sword")

        if actions.get("shuriken") and self.shuriken_weapon.pode_atacar() and self.shurikens > 0:
            self._lancar_shuriken()
            audio.play("shuriken")

    def _atacar_espada(self):
        self.atingidos_espada.clear()  # cada inimigo recebe somente um dano por golpe
        self.sword.resetar_cooldown()
        self.ataque_visual_timer = 0.12
        self.anim_acao_timer = 0.2
        self.anim_acao_nome = "attack_sword"

    def _lancar_shuriken(self):
        self.shuriken_weapon.resetar_cooldown()
        self.shurikens -= 1
        proj = Projectile(
            self.rect.centerx, self.rect.centery, self.facing,
            speed=520, damage=self._dano_shuriken(), from_player=True,
        )
        self.projectiles.append(proj)
        self.anim_acao_timer = 0.19
        self.anim_acao_nome = "attack_shuriken"

    def _dano_shuriken(self):
        return combat.calculate_damage(self.shuriken_weapon.dano_base, self.mult_dano_shuriken)

    def _dano_espada(self):
        return combat.calculate_damage(self.sword.dano_base, self.mult_dano_espada)

    #---Atualização---
    def update(self, dt, platforms, level_bounds):
        self.sword.atualizar(dt)
        self.shuriken_weapon.atualizar(dt)

        if self.ataque_visual_timer > 0:
            self.ataque_visual_timer -= dt
        if self.invulneravel_timer > 0:
            self.invulneravel_timer -= dt

        if self.shurikens < self.shurikens_max:
            self.shuriken_regen_timer += dt
            if self.shuriken_regen_timer >= self.shuriken_regen_time:
                self.shuriken_regen_timer = 0.0
                self.shurikens += 1

        #Movimento horizontal
        self.x = physics.integrate_position(self.x, self.vx, dt)
        collision.resolve_horizontal(self, platforms)
        collision.clamp_to_bounds(self, level_bounds[0], level_bounds[1])

        #Movimento vertical
        self.vy = physics.apply_gravity(self.vy, dt)
        self.y = physics.integrate_position(self.y, self.vy, dt)
        collision.resolve_vertical(self, platforms)

        for proj in self.projectiles:
            proj.update(dt)
        self.projectiles = [p for p in self.projectiles if p.alive]

        self._atualizar_animacao(dt)

    def _atualizar_animacao(self, dt):
        """Decide qual animação deve tocar agora, por prioridade:
        morte > dano/ataque em andamento > pulo/queda > correr > parado."""
        if self.morto:
            estado = "death"
        elif self.anim_acao_timer > 0:
            self.anim_acao_timer -= dt
            estado = self.anim_acao_nome
        elif not self.on_ground:
            estado = "jump" if self.vy < 0 else "fall"
        elif abs(self.vx) > 1:
            estado = "run"
        else:
            estado = "idle"

        self.anim.trocar_estado(estado)
        self.anim.atualizar(dt)

    def receber_dano(self, dano, audio=None):
        if self.invulneravel_timer > 0 or self.morto:
            return
        self.health = combat.apply_damage(self.health, dano)
        self.invulneravel_timer = 0.8
        if audio:
            audio.play("player_hurt")
        if self.health <= 0:
            self.morto = True
            if audio:
                audio.play("player_death")
        else:
            self.anim_acao_timer = 0.25
            self.anim_acao_nome = "hurt"

    def sword_hitbox(self):
        if self.ataque_visual_timer > 0:
            return self.sword.hitbox(self)
        return None

    #---Desenho---
    def draw(self, surface, camera_x):
        if self.invulneravel_timer > 0 and int(self.invulneravel_timer * 20) % 2 == 0:
            for proj in self.projectiles:
                proj.draw(surface, camera_x)
            return  # efeito de piscar ao tomar dano

        frame_w, frame_h = PLAYER_FRAME_SIZE
        # Ancora o sprite pelos "pés": centro horizontal e base do hitbox.
        draw_x = self.rect.centerx - camera_x - frame_w // 2
        draw_y = self.rect.bottom - frame_h
        self.anim.desenhar(surface, draw_x, draw_y, self.facing)

        hitbox = self.sword_hitbox()
        if hitbox:
            r = hitbox.copy()
            r.x -= camera_x
            pygame.draw.rect(surface, settings.COLOR_SWORD, r, 2, border_radius=3)

        for proj in self.projectiles:
            proj.draw(surface, camera_x)

# Shadow Rebirth

Protótipo jogável de **Shadow Rebirth**, um jogo de plataforma 2D com elementos de
**Run and Gun** e **Roguelite**, construído em **Python + Pygame**, seguindo o GDD do projeto.

Você controla um ninja que explora um cenário, combate inimigos com espada e
shuriken, e acumula um contador de inimigos derrotados durante cada **Run**.
Ao morrer, esse progresso vira pontos gastáveis na **Sala de Evolução**, onde
você compra melhorias permanentes antes de iniciar a próxima Run.

## Instalação

Requer **Python 3.10+**.

```bash
pip install -r requirements.txt
```

## Como executar

```bash
python main.py
```

## Controles

| Tecla       | Ação                          |
|-------------|-------------------------------|
| A           | Mover para a esquerda         |
| D           | Mover para a direita          |
| W / Espaço  | Pular                         |
| J           | Atacar com espada             |
| K           | Lançar shuriken                |
| ESC         | Pausar / voltar                |
| Enter       | Confirmar / comprar melhoria   |

## O que já está implementado

- Movimento, salto e gravidade seguindo as fórmulas de física do GDD (seção 5)
- Colisão por Bounding Boxes entre jogador, inimigos, plataformas e ataques (seção 6)
- Combate com espada (curto alcance, alto dano) e shuriken (longo alcance, menor dano, com recarga)
- 4 tipos de inimigo: básico, rápido, resistente e à distância (seção 10), com spawner que aumenta a dificuldade conforme o tempo de Run passa
- Sistema de vida do jogador e dos inimigos
- Contador de inimigos derrotados por Run (sem moedas, como especificado no GDD)
- Sala de Evolução com 6 melhorias permanentes (vida máxima, dano da espada,
  dano do shuriken, velocidade, quantidade de shurikens, velocidade de ataque),
  com custo crescente por nível
- Progresso salvo em `savegame.json` na raiz do projeto — as melhorias persistem
  entre execuções do jogo (RF14)
- HUD com vida, shurikens e contador de inimigos derrotados
- Menu inicial, pausa (ESC) e tela de "morte" antes de retornar à Sala de Evolução
- Efeitos sonoros básicos gerados por síntese (não dependem de arquivos de áudio)

## Sobre a arte e o áudio (importante)

O jogo já tem um **sistema de animação por spritesheet** completo
(`systems/animation.py` + `config/animations.py`), com estados de
idle/correndo/pulando/caindo/ataques/dano/morte para o jogador, e
idle/movimento/ataque/dano/morte para cada tipo de inimigo — exatamente
os sprites listados no GDD (seção 21).

Enquanto os arquivos `.png` reais não existem, cada animação usa um
**placeholder gerado automaticamente** (um retângulo colorido com um
traço que se move a cada frame), então o jogo já roda 100% jogável e
"animado" sem depender de nenhuma arte pronta.

### Formato esperado (é matricial/raster, não vetorial)

Cada spritesheet é um único `.png` com fundo transparente, com todos os
frames de uma ação lado a lado na horizontal e do mesmo tamanho. Pixel
Art feita no Piskel ou Aseprite já exporta nesse formato.

Onde colocar os arquivos (cada pasta já tem um `README.txt` com a lista
exata de arquivos, tamanhos e quantidade de frames esperados):

```
assets/sprites/player/idle.png, run.png, jump.png, fall.png,
                       attack_sword.png, attack_shuriken.png,
                       hurt.png, death.png

assets/sprites/enemies/basico/idle.png, walk.png, attack.png, hurt.png, death.png
assets/sprites/enemies/rapido/...
assets/sprites/enemies/resistente/...
assets/sprites/enemies/distancia/...
```

Basta soltar o `.png` com o nome certo na pasta certa — nenhum código
precisa mudar, o jogo detecta o arquivo e passa a usá-lo automaticamente
no lugar do placeholder. Dá pra ir substituindo uma animação de cada vez.

Se quiser ajustar tamanho de frame, número de frames ou velocidade (fps)
de qualquer animação, isso fica todo centralizado em `config/animations.py`.

### Problema comum: animação "piscando"/trocando rápido demais mesmo com fps baixo

Isso quase sempre é o **corte** errado, não a velocidade. Se `frame_w`/`frame_h`
em `config/animations.py` não bater exatamente com o tamanho de cada frame no
PNG exportado, cada corte pega um pedaço de um frame + um pedaço do vizinho —
e isso parece "flicker" mesmo em baixo fps, porque o conteúdo trocado entre
frames já está errado, independente do tempo que fica na tela.

Use a ferramenta de diagnóstico:

```bash
python debug_tools/export_frame_previews.py assets/sprites/player/run.png 48 64 6
```

Ela avisa se o tamanho da imagem não bate com o esperado e salva cada frame
cortado como um `.png` separado em `frame_preview_run/`, pra você ver
exatamente o que o jogo está lendo. Se um frame aparecer com um pedaço da
pose vizinha grudado nele, o `frame_w` (ou `frame_h`) declarado está
diferente do tamanho real de cada frame no arquivo — ajuste em
`config/animations.py`. Também vale conferir se o spritesheet foi exportado
como uma única tira horizontal (não em grade com várias linhas), sem
margem/espaçamento entre os frames.

Para adicionar áudio real (GDD seção 23-24):
1. Coloque os arquivos `.wav`/`.ogg` em `assets/sounds/` e `assets/music/`.
2. Chame `audio.carregar_arquivo("nome_do_evento", "assets/sounds/arquivo.wav")`
   em `game/game_manager.py`, após criar o `AudioManager`, para substituir o
   bipe gerado por um som real.

## Estrutura do projeto

A estrutura segue exatamente o que foi definido no GDD (seção 27), com pequenos
acréscimos (`entities/entity.py` como classe base, e `systems/audio.py`):

```
ShadowRebirth/
├── main.py
├── game/            # game_manager, game_state, level_manager
├── entities/         # entity (base), player, enemy, projectile
├── weapons/          # weapon (base), sword, shuriken
├── systems/          # physics, collision, combat, progression, audio
├── levels/            # level_01, rooms
├── ui/                # main_menu, hud, evolution_menu, game_over
├── config/            # settings
└── assets/            # sprites, sounds, music, fonts (placeholders)
```

## Próximos passos sugeridos (ver GDD seções 36 e 37)

- Trocar os placeholders geométricos por sprites reais em Pixel Art
- Adicionar animações (idle, correndo, pulando, atacando, morte)
- Adicionar chefe de fase e condição de vitória (GDD seção 33)
- Adicionar mais tipos de inimigo e novas salas/fases
- Music de fundo diferente para Run e Sala de Evolução

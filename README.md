# Shadow Rebirth Jogo desenvolvido pelos Alunos Filipe Zimmer Faganello e Guilherme Manfre de Barros

Primeiro protótipo jogável de **Shadow Rebirth**, um jogo de plataforma 2D com elementos de
**Run and Gun** e **Roguelite**, construído em **Python + Pygame**, seguindo o GDD do projeto passado pelo professor em aula.

Você controla um ninja que explora um cenário, combate inimigos com espada e
shuriken, e acumula um contador de inimigos derrotados durante cada **Run**.
Cada inimigo derrotado rende **1 ponto de habilidade imediatamente**. Use o botão
**Habilidades [H]** na partida para comprar melhorias de vida, armas e velocidade.
Os pontos restantes também podem ser gastos na **Sala de Evolução** após morrer.
**Novo Jogo sempre zera as habilidades e os pontos**; **Continuar** retoma a progressão
salva. Na LAN e no teste do editor, a evolução é temporária e não altera o save solo.

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

| Tecla / Botão       | Ação                           |
|---------------------|--------------------------------|
| A                   | Mover para a esquerda          |
| D                   | Mover para a direita           |
| W / Espaço          | Pular                          |
| Clique esquerdo     | Atacar com espada              |
| Clique direito      | Lançar shuriken                |
| ESC                 | Abrir/fechar o menu de pausa   |
| H ou botão HABILIDADES | Abrir/fechar evolução durante a partida |
| Enter               | Confirmar / comprar melhoria   |
#------------------------------------------------------|
## Editor de fases — integrado ao jogo

Abra `python main.py` e pressione **E no menu principal** para abrir o editor.
O editor vem com a fase original como referência e permite criar/alterar até **três fases**
sem mudar os arquivos `.py`.

| Controle | Ação |
|---|---|
| Clique nos botões laterais ou `V` | Selecionar e **arrastar** plataformas, inimigos e o início do jogador |
| `1` e arrastar mouse | Desenhar uma plataforma (solte para criar) |
| `2`, `3`, `4` e `5` | Adicionar inimigo básico, rápido, resistente ou à distância |
| `6` | Posicionar o início do jogador |
| `X` ou botão direito do mouse | Apagar plataforma/inimigo sob o cursor |
| `A` / `D`, setas ou rolagem | Deslocar a câmera horizontalmente |
| `G` | Mostrar/ocultar grade de 20 pixels |
| `B` | Ativar/desativar surgimento automático de inimigos durante a fase |
| `[` / `]` ou botões `-` / `+` | Diminuir/aumentar largura da fase (400 pixels) |
| `F1`, `F2`, `F3` | Alternar entre os três slots de fase |
| `Ctrl+S` | Salvar fase atual em JSON |
| `Ctrl+O` | Recarregar a fase salva do slot atual |
| `Ctrl+Z` / `Ctrl+Y` | Desfazer/refazer alterações |
| `N` | Criar mapa novo (mantém apenas chão e início do jogador) |
| `F5` | Testar a fase **mesmo sem salvar** |
| `ESC` durante o teste | Abrir pausa (opção **Voltar ao Editor**), sem registrar pontos de evolução |
| `ESC` no editor | Voltar ao menu, depois de salvar alterações |

### Onde ficam os mapas?

Os mapas são salvos automaticamente com os nomes:

- `levels/custom_level_01.json`
- `levels/custom_level_02.json`
- `levels/custom_level_03.json`

O programa cria esses arquivos ao pressionar **Ctrl+S**. Para jogar uma fase salva
fora do editor, selecione seu slot no editor, volte ao menu e escolha **Continuar** (que usa a fase salva).

**Diferença entre testar e jogar:** durante o teste iniciado com F5, você pode usar
uma versão ainda não salva do mapa, mas mortes e derrotas não mudam os pontos
permanentes. Na partida normal, a fase usada é a versão **salva** do slot selecionado.

A opção de surgimento automático de inimigos continua disponível, para que a fase
funcione como roguelite. Os inimigos que você posicionar também aparecerão no começo.

O cenário noturno `assets/backgrounds/templo_noite.png` acompanha o editor e o
jogo. Caso não seja encontrado, o jogo usa o fundo roxo simples original.

## Novidades — IA dos inimigos e multiplayer LAN

- **Inimigos podem saltar** e usar a borda das plataformas para chegar ao jogador em locais elevados. No modo cooperativo, perseguem o ninja vivo mais próximo.
- **Multiplayer LAN (2 jogadores):** menu `Multiplayer > Criar sala` no anfitrião; no outro computador, `Multiplayer > Entrar na sala` com o IP local dele. Usa TCP **porta 5050**. O host controla a física e envia o estado aos clientes.
- **Botão Voltar** nas telas de Configurações e Multiplayer (ESC também retorna).
- **Editor de fases:** mantido, com teste `F5` e salvamento `Ctrl+S`.

Consulte o [Guia de Multiplayer LAN](GUIA_MULTIPLAYER_LAN.md) para instruções no Windows, firewall, testes e limitações.

### Executar testes

```bash
python -m unittest discover -s tests -v
```

O teste de rede usa TCP local, e o teste de IA requer Pygame instalado.

## Menu de pausa (ESC)

Durante uma partida, pressione **ESC** para abrir o menu de pausa. É possível
escolher as opções pelo mouse ou por **↑ / ↓ e Enter**:

- **Continuar** — volta à partida (ou aperte ESC novamente).
- **Voltar ao menu** — encerra a partida atual e retorna ao menu principal.
- **Voltar ao editor** — aparece apenas no teste de fase iniciado com F5.

**Atenção:** voltar ao menu abandona a run atual; não equivale a salvar a partida.
Na **LAN**, abrir a pausa interrompe apenas os *controles locais*. A partida
continua acontecendo no computador anfitrião, para não interromper o outro
jogador. Ao escolher **Voltar ao menu**, a conexão LAN é encerrada.

## Novidades — melhorias durante a partida e botão Sair

- **Sair do Jogo:** botão no menu principal, com encerramento normal da janela e da conexão de rede.
- **Habilidades [H]:** novo botão no canto superior direito da partida. `H` abre/fecha o painel; `↑/↓` e `Enter` ou clique compram uma melhoria. `Esc` também fecha o painel.
- **Moeda:** cada inimigo derrotado rende **1 ponto** na hora. Os pontos são descontados ao melhorar uma habilidade. A morte **não concede esses mesmos pontos novamente**.
- **Bônus instantâneos:** vida máxima, velocidade, dano, limite de shurikens e velocidade de ataque são atualizados no personagem durante a partida, sem reiniciá-la.
- **Novo Jogo:** zera níveis, pontos, total de eliminações e recorde da progressão salva; começa com atributos básicos. **Atenção: sobrescreve o progresso anterior.**
- **Continuar:** utiliza os níveis e os pontos salvos anteriormente para iniciar uma nova run.
- **LAN cooperativa:** o servidor gerencia um conjunto de níveis e pontos *compartilhado pelos dois jogadores*. O cliente pode solicitar compras, validadas pelo servidor. Abrir o painel pausa somente os comandos locais; o outro jogador continua em movimento.
- **Editor (`F5`):** melhorias feitas em testes de fase não ficam salvas no perfil do jogo.
- **Sala de Evolução:** continua acessível após uma derrota; as compras feitas lá também persistem até selecionar Novo Jogo.

### Como testar

```bash
python -m unittest discover -s tests -v
python main.py
```

No menu principal clique em **Novo Jogo**, derrote inimigos e use `H` para evoluir.
Volte ao menu e clique em **Novo Jogo** para conferir o reinício dos níveis. A opção
**Continuar** preserva o estado salvo.

## Fantasma roxo e chefe espectral (atualização)

- Os inimigos **rápidos** (antes quadrados amarelos) agora usam a arte do fantasma roxo com animações de andar/flutuar, ataque, dano e morte. Os arquivos ficam em `assets/sprites/enemies/rapido/`.
- O chefe **Espectro Ancestral** possui 300 pontos de vida, contato perigoso, rajadas duplas e uma barra de vida no topo da tela. Ele utiliza `assets/sprites/enemies/chefe/`.
- **Nova arena do chefe:** a luta não acontece mais junto aos inimigos comuns. Um portal roxo aparece perto do fim da fase; atravesse-o para entrar em uma arena isolada. Os mobs normais ficam fora da luta e a fase retorna depois da vitória.
- **F8 durante a partida** entra diretamente na arena, para testes, sem precisar atravessar o portal. Não inicia uma segunda luta na mesma run; em LAN use F8 no anfitrião.
- **Editor de fases: tecla `7`** define a **posição do portal do chefe**, não o local de spawn do chefe na fase normal. `Ctrl+S` salva e `F5` testa.
- O chefe sempre aparece somente dentro da arena; não existe mais surgimento por tempo ou por quantidade de inimigos derrotados.

**Direitos da arte:** a imagem `Ghost2.jpg` fornecida pelo usuário exibe marcas de Dreamstime. Os sprites foram adaptados dessa imagem. Verifique a licença/autorização antes de distribuir ou publicar o jogo com esses recursos visuais.

## Atualização Full HD + robô atirador + arena exclusiva

- O jogo inicia em **tela cheia Full HD (1920×1080)** quando o monitor suporta essa resolução, ou em tela cheia na resolução nativa caso não suporte. A lógica continua em 960×540 e é ampliada, preservando o layout e os cliques nos menus. **F11** alterna entre janela e tela cheia.
- No editor, os botões **F1 FASE 1 / F2 FASE 2 / F3 FASE 3** foram ampliados para não cortar textos.
- O inimigo de tipo `distancia` agora usa as animações do robô do spritesheet `RoboAT1.jpg` (idle, walk, attack, hurt, death) em `assets/sprites/enemies/distancia/`.
- O chefe é enfrentado somente na sua **arena exclusiva**: basta chegar ao portal no fim da fase (ou apertar **F8** para testar). Os inimigos normais são separados durante a luta; ao derrotar o chefe você retorna à fase e o portal não reabre na mesma run.
- Em LAN o computador anfitrião determina a entrada na arena e sincroniza o cenário com o outro jogador.

Para instalar em um clone Git existente, utilize `ShadowRebirth_patch_fullhd_arena_robo.zip` e substitua somente os arquivos contidos nele. Mantenha `.git` e seus arquivos de save/fases personalizadas.

## Configurações de som e piso invisível

Em **Configurações**, clique no botão **Sons: LIGADOS / DESLIGADOS** ou pressione
**M** para ligar/desligar o áudio. A escolha é mantida no arquivo
`audio_settings.json` (ignorado pelo Git).

O piso da fase é uma colisão invisível na altura Y=460, alinhada à imagem de
fundo: **não existe mais um retângulo de chão desenhado**. As plataformas aéreas
permanecem visíveis. O editor cria fases sem piso explícito, e fases antigas com
o retângulo contínuo de chão são migradas automaticamente ao carregar; salve
com Ctrl+S para atualizar o arquivo JSON. O mesmo vale para a arena do chefe.

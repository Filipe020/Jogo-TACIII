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

**Atenção:** voltar ao menu abandona a run atual; não equivale a salvar a partida.
Na **LAN**, abrir a pausa interrompe apenas os *controles locais*. A partida
continua acontecendo no computador anfitrião, para não interromper o outro
jogador. Ao escolher **Voltar ao menu**, a conexão LAN é encerrada.

## Novidades — melhorias durante a partida e botão Sair

### Como testar

```bash
python -m unittest discover -s tests -v
python main.py
```

No menu principal clique em **Novo Jogo**, derrote inimigos e use `H` para evoluir.
Volte ao menu e clique em **Novo Jogo** para conferir o reinício dos níveis. A opção
**Continuar** preserva o estado salvo.

## Fantasma roxo e chefe espectral (atualização)

## Configurações de som e piso invisível

Em **Configurações**, clique no botão **Sons: LIGADOS / DESLIGADOS** ou pressione
**M** para ligar/desligar o áudio. A escolha é mantida no arquivo
`audio_settings.json` (ignorado pelo Git).
# Shadow Rebirth Jogo desenvolvido pelos Alunos Filipe Zimmer Faganello e Guilherme Manfre de Barros

Primeiro protótipo jogável de **Shadow Rebirth**, um jogo de plataforma 2D com elementos de
**Run and Gun** e **Roguelite**, construído em **Python + Pygame**, seguindo o GDD do projeto passado pelo professor em aula.

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

| Tecla / Botão       | Ação                           |
|---------------------|--------------------------------|
| A                   | Mover para a esquerda          |
| D                   | Mover para a direita           |
| W / Espaço          | Pular                          |
| Clique esquerdo     | Atacar com espada              |
| Clique direito      | Lançar shuriken                |
| ESC                 | Pausar / voltar                |
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
| `ESC` durante o teste | Voltar ao editor, sem registrar pontos de evolução |
| `ESC` no editor | Voltar ao menu, depois de salvar alterações |

### Onde ficam os mapas?

Os mapas são salvos automaticamente com os nomes:

- `levels/custom_level_01.json`
- `levels/custom_level_02.json`
- `levels/custom_level_03.json`

O programa cria esses arquivos ao pressionar **Ctrl+S**. Para jogar uma fase salva
fora do editor, selecione seu slot no editor, volte ao menu com **ESC** e use **ENTER**.

**Diferença entre testar e jogar:** durante o teste iniciado com F5, você pode usar
uma versão ainda não salva do mapa, mas mortes e derrotas não mudam os pontos
permanentes. Na partida normal, a fase usada é a versão **salva** do slot selecionado.

A opção de surgimento automático de inimigos continua disponível, para que a fase
funcione como roguelite. Os inimigos que você posicionar também aparecerão no começo.

O cenário noturno `assets/backgrounds/templo_noite.png` acompanha o editor e o
jogo. Caso não seja encontrado, o jogo usa o fundo roxo simples original.

# Shadow Rebirth — guia de multiplayer LAN

O jogo agora tem **multiplayer cooperativo para 2 pessoas**, via **TCP** na **mesma rede local** (roteador Wi-Fi ou cabo). O servidor/anfitrião executa a física, inimigos, dano e pontuação; o cliente envia comandos e recebe atualizações da partida. Não há necessidade de conta ou servidor externo.

## Preparação em ambos os computadores

1. Os dois jogadores precisam da **mesma versão** do projeto (mesmos arquivos Python e imagens).
2. Instale as dependências uma vez em cada computador: `pip install -r requirements.txt`.
3. Inicie o jogo em cada máquina: `python main.py`.
4. Conecte ambos na mesma rede local. **LAN não é multiplayer pela internet**.

## Criar a sala (anfitrião)

1. No menu inicial, clique em **Multiplayer → Criar sala**.
2. A tela mostrará o IP local do anfitrião e a porta **5050**.
3. Se houver mais de uma placa de rede, verifique o IPv4 correto com `ipconfig` no PowerShell. Use o endereço IPv4 da rede à qual os dois computadores estão conectados (exemplo: `192.168.0.15`).
4. Espere a segunda pessoa entrar. A partida começará automaticamente.

## Entrar na sala (cliente)

1. No outro computador, clique em **Multiplayer**.
2. Clique no campo de IP e escreva o endereço do computador anfitrião (exemplo: `192.168.0.15`). O padrão `127.0.0.1` serve **somente para testar duas janelas no mesmo computador**.
3. Clique em **Entrar na sala**.
4. O cliente recebe o mapa que o servidor estiver usando (slot selecionado no editor do anfitrião, caso tenha sido salvo, ou mapa padrão).

## Controles (ambos)

- `A / D`: mover à esquerda e à direita.
- `W / Espaço`: pular.
- Clique esquerdo: espada; clique direito: shuriken.
- `Esc`: desconectar e voltar ao menu (inclusive durante a partida LAN).
- O botão **Voltar** na tela de Configurações e Multiplayer retorna ao menu principal.

## Regras e observações

- Os jogadores estão no **mesmo mapa**, combatendo os mesmos inimigos. Cada um tem vida, movimento, espada e shurikens independentes.
- Mobs tentam alcançar o jogador mais próximo, inclusive com saltos sobre plataformas.
- A câmera de cada computador acompanha o próprio ninja. O servidor sincroniza vida, posições, inimigos, projéteis e pontuação compartilhada.
- A sala é encerrada quando **ambos** morrem, um jogador sai, ou ocorre desconexão. No multiplayer não são concedidos pontos para a Sala de Evolução; a progressão offline não é sobrescrita.
- O modo LAN foi desenvolvido para partidas locais cooperativas simples, **não** tem salas públicas, reconexão automática, autenticação, matchmaking nem interpolação avançada de movimento.

## Se não conseguir conectar

- No Windows, autorize o **Python** a usar a **rede privada** quando o Firewall perguntar. Se necessário, libere manualmente a porta **TCP 5050** de entrada no computador anfitrião.
- Confira se os dois computadores estão na **mesma rede** e que ela não bloqueia a comunicação entre dispositivos (isolamento de clientes / rede de convidados).
- Confira o IP com `ipconfig`, e não use o IP externo da internet.
- Verifique se a porta 5050 não está sendo usada por outro programa e se a sala ainda está aberta.
- Para testar localmente, execute `python main.py` **duas vezes**, crie uma sala na primeira janela e, na segunda, entre com IP `127.0.0.1`.

## Menu de pausa durante a LAN

Durante a partida, **ESC** abre um menu com **Continuar** e **Voltar ao menu**.
A pausa é **local**: o jogador pausado deixa de enviar controles, mas o outro
jogador e os inimigos continuam ativos. **Voltar ao menu** encerra a conexão
LAN, e a outra pessoa será avisada da desconexão. Se desejar sair sem encerrar,
escolha **Continuar** (ou pressione ESC de novo).


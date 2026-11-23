# Shadow Rebirth — quarto chefe (Espectro das Cinzas)

Esta atualização acrescenta o chefe baseado no fantasma branco/cinza usado no mob resistente.

## Ordem dos encontros

- 10 mobs: Espectro Ancestral (fantasma roxo)
- 20 mobs: Necrozumbi Titan (zumbi)
- 30 mobs: Sentinela Mecânico (robô)
- 40 mobs: Espectro das Cinzas (fantasma branco/cinza)
- 50, 60, 70, 80...: a sequência se repete a cada quatro encontros.

## Quarto chefe

- Mais robusto e lento: 420 de vida, 20 de dano de contato.
- Sprite 1,5 vez maior que o mob resistente, com as cinco animações.
- **Pulso espectral**: aviso visual circular por 0,72 segundo, seguido de dano em área (16 pontos) nos jogadores próximos. É possível se afastar antes de o ataque acontecer.
- Arena isolada: mobs comuns não surgem durante o combate.

## Teste

Execute `python main.py`. O portal surge com 10, 20, 30 e 40 mobs derrotados. Você pode usar F8 para entrar diretamente na próxima arena, sem precisar cumprir a meta, e derrotar cada chefe para avançar até o quarto. A tecla F8 não pula bosses; apenas abre o encontro atual.

Na LAN, o anfitrião determina o chefe da arena, a barra de vida e o pulso são enviados no snapshot.

## Instalação via patch

Extraia o ZIP da correção na raiz do projeto original, preservando `.git` e os arquivos de seus colegas. Teste o jogo antes de enviar ao GitHub.

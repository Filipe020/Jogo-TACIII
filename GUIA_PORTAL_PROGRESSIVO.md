# Atualização: alinhamento do chão e portal progressivo

- O piso invisível da fase e da arena passou de y=460 para y=486, para que os pés do personagem alcancem o caminho na arte de fundo. O chão não é desenhado como plataforma. Fases antigas continuam compatíveis.
- Ao iniciar uma nova partida, o portal está oculto.
- A cada **10 mobs comuns derrotados**, o portal passa a aparecer na entrada da arena (posição no fim da fase ou posicionada na ferramenta **7** do editor).
- O portal só transporta o jogador ao chegar perto dele, e só depois de cumprir a meta.
- Após vencer o chefe, a próxima meta aumenta: **10 → 20 → 30 → 40...** dentro da mesma partida.
- Os chefes não contam para as metas de mobs comuns, mas continuam rendendo pontos de evolução.
- No HUD, aparece o andamento da meta (por exemplo `PORTAL DO CHEFE: 7/10 MOBS`).
- **F8** continua como atalho de depuração para testar a arena sem cumprir a meta.
- O multiplayer LAN transmite a contagem de mobs comuns e a meta do próximo portal.

Para testar: `python main.py`. Derrote 10 inimigos comuns, alcance o portal, derrote o chefe, volte à fase e derrote mais 10. O próximo portal abre ao chegar a 20. Reinicie uma run para voltar à meta de 10.

Os testes no projeto podem ser executados com `python -m unittest discover -s tests -p 'test_*.py'` após instalar o Pygame.

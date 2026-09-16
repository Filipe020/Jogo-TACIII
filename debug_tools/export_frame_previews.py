"""Ferramenta de debug: Para conferir visualmente se
o corte (frame_w x frame_h x quantidade de frames) está certo.

Uso:
    python debug_tools/export_frame_previews.py <caminho_do_png> <frame_w> <frame_h> <num_frames>
"""

import os
import sys

import pygame


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        sys.exit(1)

    caminho, frame_w, frame_h, num_frames = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])

    if not os.path.exists(caminho):
        print(f"Arquivo não encontrado: {caminho}")
        sys.exit(1)

    pygame.init()
    pygame.display.set_mode((1, 1))  # necessário para convert_alpha() funcionar

    folha = pygame.image.load(caminho).convert_alpha()
    largura_real, altura_real = folha.get_size()
    largura_esperada = frame_w * num_frames

    print(f"Imagem carregada: {caminho}")
    print(f"  Tamanho real:     {largura_real}x{altura_real}px")
    print(f"  Tamanho esperado: {largura_esperada}x{frame_h}px  ({num_frames} frames de {frame_w}x{frame_h})")

    if largura_real != largura_esperada or altura_real != frame_h:
        print()
        print("  !! TAMANHO NÃO BATE !!")
        if largura_real % num_frames == 0:
            sugestao_w = largura_real // num_frames
            print(f"  Se a imagem realmente tem {num_frames} frames em 1 linha, cada frame "
                  f"tem {sugestao_w}px de largura (não {frame_w}px). Ajuste frame_w em "
                  f"config/animations.py para {sugestao_w}.")
        else:
            print("  A largura da imagem não é múltiplo do número de frames — confira se o "
                  "spritesheet foi exportado em uma única linha horizontal, sem margens/espaços "
                  "entre os frames, e sem múltiplas linhas (grade).")
        print(f"  Se a altura ({altura_real}px) for diferente de frame_h ({frame_h}px), ajuste "
              f"frame_h também.")
        print()

    nome_base = os.path.splitext(os.path.basename(caminho))[0]
    pasta_saida = f"frame_preview_{nome_base}"
    os.makedirs(pasta_saida, exist_ok=True)

    for i in range(num_frames):
        origem = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        frame.blit(folha, (0, 0), origem)
        destino = os.path.join(pasta_saida, f"frame_{i}.png")
        pygame.image.save(frame, destino)

    print(f"{num_frames} frames salvos em: {pasta_saida}/")
    print("Abra cada frame_N.png e confira se cada um mostra uma pose completa e correta.")


if __name__ == "__main__":
    main()

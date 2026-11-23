"""Confere dimensões dos sprites do inimigo atirador, sem dependências extras."""
import struct
import unittest
from pathlib import Path


class TestRobotSprites(unittest.TestCase):
    def test_sprites_png_com_quadros_corretos(self):
        base=Path(__file__).resolve().parents[1]
        from config.animations import ENEMY_ANIMATIONS
        for state,anim in ENEMY_ANIMATIONS['distancia'].items():
            with self.subTest(estado=state):
                file=base/'assets'/'sprites'/'enemies'/'distancia'/anim['file']
                data=file.read_bytes()[:24]
                self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n')
                width,height=struct.unpack('>II',data[16:24])
                self.assertEqual(width,anim['frame_w']*anim['frames'])
                self.assertEqual(height,anim['frame_h'])


if __name__=='__main__':
    unittest.main()

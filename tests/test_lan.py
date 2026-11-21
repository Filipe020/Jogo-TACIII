"""Teste real do transporte TCP local, sem precisar inicializar o Pygame."""
import socket
import time
import unittest

from network.lan import LANPeer


class TestLAN(unittest.TestCase):
    def test_host_cliente_trocam_mensagens(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tmp:
            tmp.bind(("127.0.0.1", 0))
            port = tmp.getsockname()[1]
        host = LANPeer("host", port=port)
        guest = LANPeer("client", "127.0.0.1", port=port)
        try:
            limit = time.monotonic() + 4
            while time.monotonic() < limit:
                if host.status == "conectado" and guest.status == "conectado":
                    break
                time.sleep(0.02)
            self.assertEqual(host.status, "conectado", host.error)
            self.assertEqual(guest.status, "conectado", guest.error)
            mapa = {"largura": 3600, "plataformas": [[0, 460, 3600, 40]]}
            host.send({"type": "welcome", "map": mapa})
            guest.send({"type": "input", "actions": {"jump": True}})
            host_msgs, guest_msgs = [], []
            limit = time.monotonic() + 4
            while time.monotonic() < limit and (not host_msgs or not guest_msgs):
                host_msgs += host.receive()
                guest_msgs += guest.receive()
                time.sleep(0.02)
            self.assertEqual(host_msgs[0]["actions"]["jump"], True)
            self.assertEqual(guest_msgs[0]["map"], mapa)
        finally:
            guest.close()
            host.close()


if __name__ == "__main__":
    unittest.main()

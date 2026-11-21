"""Rede TCP LAN (2 jogadores). Transporte em thread, sem bloquear o Pygame.

Protocolo: JSON delimitado por '\\n'. O servidor executa toda a física;
o cliente envia somente controles e recebe snapshots do mundo.
"""
import json
import queue
import select
import socket
import threading

PORT = 5050
MAX_PACKET = 512 * 1024


def local_ip():
    """IP preferencial da placa de rede; não envia pacotes pela internet."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as test:
            test.connect(("192.0.2.1", 1))
            return test.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "127.0.0.1"


class LANPeer:
    """Uma conexão host/cliente; comunicação segura por filas com a thread do jogo."""

    def __init__(self, role, address="127.0.0.1", port=PORT):
        if role not in ("host", "client"):
            raise ValueError("Papel LAN inválido")
        self.role = role
        self.address = address
        self.port = port
        self.status = "aguardando" if role == "host" else "conectando"
        self.error = ""
        self.incoming = queue.Queue(maxsize=64)
        self.outgoing = queue.Queue(maxsize=32)
        self._stop = threading.Event()
        self._listener = None
        self._socket = None
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def send(self, message):
        """Insere mensagem sem travar o frame; descarta mensagens mais antigas."""
        if self._stop.is_set():
            return
        try:
            self.outgoing.put_nowait(message)
        except queue.Full:
            try:
                self.outgoing.get_nowait()
            except queue.Empty:
                pass
            self.outgoing.put_nowait(message)

    def receive(self):
        messages = []
        while True:
            try:
                messages.append(self.incoming.get_nowait())
            except queue.Empty:
                return messages

    def close(self):
        self._stop.set()
        for sock in (self._socket, self._listener):
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    sock.close()
                except OSError:
                    pass
        self.status = "fechado"

    def _run(self):
        try:
            if self.role == "host":
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                    self._listener = listener
                    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    listener.bind(("0.0.0.0", self.port))
                    listener.listen(1)
                    listener.settimeout(0.2)
                    while not self._stop.is_set():
                        try:
                            conn, _ = listener.accept()
                            break
                        except socket.timeout:
                            continue
                    else:
                        return
                    self._serve(conn)
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                    self._socket = conn
                    conn.settimeout(6)
                    conn.connect((self.address, self.port))
                    self._serve(conn)
        except (OSError, ValueError) as exc:
            if not self._stop.is_set():
                self.error = str(exc)
                self.status = "erro"

    def _serve(self, conn):
        with conn:
            self._socket = conn
            conn.setblocking(False)
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.status = "conectado"
            incoming = bytearray()
            pending = bytearray()
            while not self._stop.is_set():
                if not pending:
                    try:
                        msg = self.outgoing.get_nowait()
                        pending.extend(json.dumps(msg, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n")
                    except queue.Empty:
                        pass
                readable, writable, _ = select.select([conn], [conn] if pending else [], [], 0.02)
                if readable:
                    try:
                        data = conn.recv(65536)
                    except BlockingIOError:
                        data = None
                    if data == b"":
                        self.status = "desconectado"
                        return
                    if data:
                        incoming.extend(data)
                        if len(incoming) > MAX_PACKET:
                            raise ValueError("Pacote de rede grande demais")
                        while b"\n" in incoming:
                            line, _, remain = incoming.partition(b"\n")
                            incoming = bytearray(remain)
                            if len(line) > MAX_PACKET:
                                raise ValueError("Pacote de rede grande demais")
                            try:
                                message = json.loads(line)
                                if isinstance(message, dict):
                                    try:
                                        self.incoming.put_nowait(message)
                                    except queue.Full:
                                        self.incoming.get_nowait()
                                        self.incoming.put_nowait(message)
                            except (ValueError, UnicodeDecodeError):
                                continue
                if writable and pending:
                    try:
                        sent = conn.send(pending)
                    except BlockingIOError:
                        sent = 0
                    if sent:
                        del pending[:sent]

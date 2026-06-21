import socket
import random
import threading
import queue
import uuid

BUFFER_SIZE = 4096
TIMEOUT = 1.5
CHANCE_DE_PERDA = 0.10
MAX_TENTATIVAS = 8
DEBUG_RDT = False

_estados = {}
_estados_lock = threading.Lock()


class EstadoRDT:
    def __init__(self, sock):
        self.sock = sock

        # Sequência usada para enviar para cada destino.
        self.sender_seq = {}

        # Sequência esperada ao receber de cada remetente.
        self.expected_seq = {}

        # Último pacote aceito de cada remetente.
        # Isso ajuda a diferenciar retransmissão real de cliente reiniciado na mesma porta.
        self.last_packet_id = {}

        # ACKs aguardados pelo transmissor.
        self.pending_acks = {}

        # Fila de pacotes entregues para a aplicação.
        self.inbox = queue.Queue()

        self.lock = threading.Lock()
        self.send_lock = threading.Lock()

        self.rodando = False
        self.thread = None


def deve_descartar_pacote():
    return random.random() < CHANCE_DE_PERDA


def iniciar_receptor(sock):
    estado = _get_estado(sock)

    if estado.rodando:
        return

    estado.rodando = True
    sock.settimeout(0.2)

    estado.thread = threading.Thread(
        target=_receiver_loop,
        args=(estado,),
        daemon=True
    )

    estado.thread.start()


def parar_receptor(sock):
    estado = _get_estado(sock)
    estado.rodando = False


def reset_peer(sock, addr):
    """
    Limpa o estado RDT associado a um cliente específico.
    Pode ser usado quando um cliente sai ou para evitar estado antigo preso.
    """
    estado = _get_estado(sock)

    with estado.lock:
        estado.sender_seq.pop(addr, None)
        estado.expected_seq.pop(addr, None)
        estado.last_packet_id.pop(addr, None)

        for chave in list(estado.pending_acks.keys()):
            destino, seq, packet_id = chave

            if destino == addr:
                estado.pending_acks.pop(chave, None)


def rdt_send(sock, payload, destino, tipo="DATA"):
    estado = _get_estado(sock)

    with estado.send_lock:
        seq_atual = estado.sender_seq.get(destino, 0)
        packet_id = uuid.uuid4().hex

        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        else:
            payload_bytes = payload

        cabecalho = f"{tipo}:{seq_atual}:{packet_id}:".encode("utf-8")
        pacote = cabecalho + payload_bytes

        ack_event = threading.Event()
        ack_key = (destino, seq_atual, packet_id)

        with estado.lock:
            estado.pending_acks[ack_key] = ack_event

        tentativas = 0

        while tentativas < MAX_TENTATIVAS:
            tentativas += 1

            if deve_descartar_pacote():
                _debug(f"[RDT SENDER] perda simulada de {tipo} SEQ={seq_atual}")
            else:
                _debug(f"[RDT SENDER] enviando {tipo} SEQ={seq_atual}")
                sock.sendto(pacote, destino)

            if ack_event.wait(TIMEOUT):
                _debug(f"[RDT SENDER] ACK correto recebido SEQ={seq_atual}")

                with estado.lock:
                    estado.sender_seq[destino] = 1 - seq_atual
                    estado.pending_acks.pop(ack_key, None)

                return True

            _debug(f"[RDT SENDER] timeout SEQ={seq_atual}. Retransmitindo...")

        with estado.lock:
            estado.pending_acks.pop(ack_key, None)

        return False


def rdt_recv(sock, timeout=None):
    estado = _get_estado(sock)
    return estado.inbox.get(timeout=timeout)


def _receiver_loop(estado):
    sock = estado.sock

    while estado.rodando:
        try:
            pacote, addr = sock.recvfrom(BUFFER_SIZE)

        except socket.timeout:
            continue

        except OSError:
            break

        resultado = _parse_packet(pacote)

        if resultado is None:
            continue

        tipo, seq_recebido, packet_id, conteudo = resultado

        if tipo == "ACK":
            ack_key = (addr, seq_recebido, packet_id)

            with estado.lock:
                ack_event = estado.pending_acks.get(ack_key)

            if ack_event:
                ack_event.set()

            continue

        expected_seq = estado.expected_seq.get(addr, 0)
        ultimo_packet_id = estado.last_packet_id.get(addr)

        if seq_recebido == expected_seq:
            _debug(f"[RDT RECEIVER] pacote esperado {tipo} SEQ={seq_recebido}")

            with estado.lock:
                estado.expected_seq[addr] = 1 - expected_seq
                estado.last_packet_id[addr] = packet_id

            _send_ack(sock, addr, seq_recebido, packet_id)
            estado.inbox.put((tipo, conteudo, addr))

        else:
            if packet_id == ultimo_packet_id:
                # Retransmissão real do mesmo pacote já entregue.
                # Reenvia ACK, mas não entrega novamente para a aplicação.
                _debug(f"[RDT RECEIVER] pacote duplicado SEQ={seq_recebido}")
                _send_ack(sock, addr, seq_recebido, packet_id)

            else:
                # Caso especial:
                # o cliente provavelmente foi fechado e reaberto usando a mesma porta.
                # O processo novo reiniciou a sequência em 0, mas o servidor ainda tinha estado antigo.
                # Como o packet_id é novo, aceitamos e ressincronizamos.
                _debug(
                    f"[RDT RECEIVER] ressincronizando cliente {addr}. "
                    f"Recebido SEQ={seq_recebido}, esperado={expected_seq}"
                )

                with estado.lock:
                    estado.expected_seq[addr] = 1 - seq_recebido
                    estado.last_packet_id[addr] = packet_id

                _send_ack(sock, addr, seq_recebido, packet_id)
                estado.inbox.put((tipo, conteudo, addr))


def _send_ack(sock, addr, seq, packet_id):
    ack = f"ACK:{seq}:{packet_id}:".encode("utf-8")

    if deve_descartar_pacote():
        _debug(f"[RDT RECEIVER] perda simulada de ACK={seq}")
        return

    sock.sendto(ack, addr)


def _parse_packet(pacote):
    try:
        idx1 = pacote.index(b":")
        idx2 = pacote.index(b":", idx1 + 1)
        idx3 = pacote.index(b":", idx2 + 1)

        tipo = pacote[:idx1].decode("utf-8")
        seq = int(pacote[idx1 + 1:idx2].decode("utf-8"))
        packet_id = pacote[idx2 + 1:idx3].decode("utf-8")
        conteudo = pacote[idx3 + 1:]

        return tipo, seq, packet_id, conteudo

    except (ValueError, IndexError, UnicodeDecodeError):
        return None


def _get_estado(sock):
    fileno = sock.fileno()

    with _estados_lock:
        if fileno not in _estados:
            _estados[fileno] = EstadoRDT(sock)

        return _estados[fileno]


def _debug(msg):
    if DEBUG_RDT:
        print(msg)
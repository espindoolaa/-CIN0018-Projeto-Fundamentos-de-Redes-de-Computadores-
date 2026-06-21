import socket
import os
import threading
import time

import rdt3
import protocol
from auction import AuctionSystem, TEXT_FILES_DIR
from contacts import HOST, SERVER_PORT, CONTATOS

BUFFER_SIZE = 1024


def enviar(serverSocket, auction, tipo, mensagem, addr):
    ok = rdt3.rdt_send(serverSocket, mensagem, addr, tipo=tipo)

    if not ok:
        print(f"Cliente {addr} não respondeu. Removendo da lista de usuários online.")
        auction.remove_address(addr)
        rdt3.reset_peer(serverSocket, addr)

    return ok


def broadcast(serverSocket, auction, mensagem):
    for addr in auction.get_online_addresses():
        enviar(serverSocket, auction, protocol.UPDATE, mensagem, addr)


def enviar_arquivo_item(serverSocket, auction, vencedor, addr, item_id, filename):
    if not addr:
        return

    caminho = os.path.join(TEXT_FILES_DIR, filename)

    if not os.path.exists(caminho):
        enviar(
            serverSocket,
            auction,
            protocol.UPDATE,
            f"Arquivo do item {filename} não foi encontrado no servidor.",
            addr
        )
        return

    print(f"Enviando o arquivo {filename} para o vencedor {vencedor}.")

    cabecalho = protocol.make_file_header(item_id, filename)

    ok = enviar(serverSocket, auction, protocol.FILE_BEGIN, cabecalho, addr)

    if not ok:
        return

    with open(caminho, "rb") as file:
        while True:
            chunk = file.read(BUFFER_SIZE)

            if not chunk:
                break

            ok = rdt3.rdt_send(serverSocket, chunk, addr, tipo=protocol.FILE_DATA)

            if not ok:
                print(f"Falha ao enviar parte do arquivo para {addr}.")
                auction.remove_address(addr)
                rdt3.reset_peer(serverSocket, addr)
                return

    enviar(serverSocket, auction, protocol.FILE_END, filename, addr)


def monitorar_tempos(serverSocket, auction):
    while True:
        time.sleep(1)

        broadcasts, arquivos = auction.close_expired_items()

        for mensagem in broadcasts:
            print(mensagem)
            broadcast(serverSocket, auction, mensagem)

        for vencedor, addr, item_id, filename in arquivos:
            enviar_arquivo_item(serverSocket, auction, vencedor, addr, item_id, filename)


def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind((HOST, SERVER_PORT))

    rdt3.iniciar_receptor(serverSocket)

    auction = AuctionSystem()

    print(f"Servidor AuctionCin escutando em {HOST}:{SERVER_PORT}...")
    print("\nLista de contatos sugerida para testes:")

    for nome, addr in CONTATOS.items():
        print(f"{nome} -> {addr[0]}:{addr[1]}")

    print()

    thread_monitor = threading.Thread(
        target=monitorar_tempos,
        args=(serverSocket, auction),
        daemon=True
    )

    thread_monitor.start()

    try:
        while True:
            tipo, conteudo, client_addr = rdt3.rdt_recv(serverSocket)

            if tipo != protocol.COMMAND:
                continue

            comando = conteudo.decode("utf-8")
            comando_limpo = comando.strip().lower()

            print(f"{client_addr} -> {comando}")

            resposta, broadcasts, arquivos = auction.handle_command(comando, client_addr)

            enviar(serverSocket, auction, protocol.RESPONSE, resposta, client_addr)

            if comando_limpo == "logout":
                rdt3.reset_peer(serverSocket, client_addr)

            for mensagem in broadcasts:
                print(mensagem)
                broadcast(serverSocket, auction, mensagem)

            for vencedor, addr, item_id, filename in arquivos:
                enviar_arquivo_item(serverSocket, auction, vencedor, addr, item_id, filename)

    except KeyboardInterrupt:
        print("\nServidor encerrado.")

    finally:
        rdt3.parar_receptor(serverSocket)
        serverSocket.close()


if __name__ == "__main__":
    main()
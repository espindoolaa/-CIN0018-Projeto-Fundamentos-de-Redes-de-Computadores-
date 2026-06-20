import socket
import os
import sys
import threading
import queue
import time

import rdt3
import protocol
from contacts import HOST, SERVER_PORT, CONTATOS

SERVER_ADDRESS = (HOST, SERVER_PORT)
TEXT_FILES_DIR = "text_files"

rodando = True
arquivo_atual = None
arquivo_atual_nome = None


# Escolhe a porta local a partir de cliente1, cliente2, cliente3 ou de uma porta manual.
def escolher_configuracao():
    if len(sys.argv) < 2:
        print("Uso correto:")
        print("python3 client.py cliente1")
        print("python3 client.py cliente2")
        print("python3 client.py cliente3")
        print("ou")
        print("python3 client.py <porta>")
        sys.exit(1)

    entrada = " ".join(sys.argv[1:]).strip()

    if entrada in CONTATOS:
        porta = CONTATOS[entrada][1]
        return porta, entrada

    if entrada.isdigit():
        return int(entrada), None

    print("Cliente não encontrado.")
    print("Use cliente1, cliente2, cliente3 ou informe uma porta manualmente.")
    sys.exit(1)


# Imprime mensagem recebida sem esconder o terminal.
def imprimir(mensagem):
    print(f"\n{mensagem}")
    print("> ", end="", flush=True)


# Valida os comandos antes de enviar ao servidor.
def comando_valido(comando):
    partes = comando.strip().split()

    if not partes:
        return False

    cmd = partes[0].lower()

    if cmd == "login":
        if len(partes) < 2:
            print("Uso correto: login <nome_do_usuario>")
            return False
        return True

    if cmd == "bid":
        if len(partes) != 3:
            print("Uso correto: bid <id_item> <valor>")
            return False
        return True

    if cmd in ("list", "status", "logout"):
        if len(partes) != 1:
            print(f"Uso correto: {cmd}")
            return False
        return True

    print("Comando inválido. Use: login, bid, list, status, logout ou exit.")
    return False


# Trata mensagens enviadas pelo servidor.
def tratar_mensagem(tipo, conteudo):
    global arquivo_atual
    global arquivo_atual_nome

    if tipo == protocol.RESPONSE:
        imprimir(conteudo.decode("utf-8"))

    elif tipo == protocol.UPDATE:
        imprimir("[ATUALIZAÇÃO] " + conteudo.decode("utf-8"))

    elif tipo == protocol.FILE_BEGIN:
        texto = conteudo.decode("utf-8")
        item_id, filename = protocol.parse_file_header(texto)

        os.makedirs(os.path.join(TEXT_FILES_DIR, "recebidos"), exist_ok=True)

        arquivo_atual_nome = "recebido_" + filename
        caminho = os.path.join(TEXT_FILES_DIR, "recebidos", arquivo_atual_nome)

        arquivo_atual = open(caminho, "wb")

        imprimir(f"Recebendo arquivo do item {item_id}: {filename}")

    elif tipo == protocol.FILE_DATA:
        if arquivo_atual:
            arquivo_atual.write(conteudo)

    elif tipo == protocol.FILE_END:
        if arquivo_atual:
            arquivo_atual.close()

        imprimir(f"Arquivo recebido e salvo em {TEXT_FILES_DIR}/recebidos/{arquivo_atual_nome}")

        arquivo_atual = None
        arquivo_atual_nome = None


# Thread que fica recebendo respostas e atualizações do servidor.
def receber_mensagens(clientSocket):
    global rodando

    while rodando:
        try:
            tipo, conteudo, server_addr = rdt3.rdt_recv(clientSocket, timeout=0.2)
        except queue.Empty:
            continue

        tratar_mensagem(tipo, conteudo)


# Envia logout antes de fechar o cliente.
def sair_com_logout(clientSocket):
    global rodando

    try:
        rdt3.rdt_send(clientSocket, "logout", SERVER_ADDRESS, tipo=protocol.COMMAND)
        time.sleep(1)
    except Exception:
        pass

    rodando = False


# Mostra as instruções iniciais do cliente.
def mostrar_inicio(cliente_id, porta_real):
    print("Cliente AuctionCin iniciado.")
    print(f"Identificador deste processo: {cliente_id if cliente_id else 'porta manual'}")
    print(f"Porta local deste cliente: {porta_real}")

    print("\nAtenção:")
    print("cliente1, cliente2 e cliente3 servem apenas para escolher portas diferentes.")
    print("O nome real do usuário é escolhido no comando login.")

    print("\nComandos disponíveis:")
    print("login <nome_do_usuario>")
    print("bid <id_item> <valor>")
    print("list")
    print("status")
    print("logout")
    print("exit\n")


def main():
    global rodando

    porta, cliente_id = escolher_configuracao()

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        clientSocket.bind((HOST, porta))
    except OSError:
        print(f"Erro: a porta {porta} já está em uso.")
        print("Provavelmente já existe outro terminal usando esse mesmo cliente.")
        print("Use outro identificador, por exemplo: cliente1, cliente2 ou cliente3.")
        sys.exit(1)

    porta_real = clientSocket.getsockname()[1]

    rdt3.iniciar_receptor(clientSocket)

    thread = threading.Thread(
        target=receber_mensagens,
        args=(clientSocket,),
        daemon=True
    )

    thread.start()

    mostrar_inicio(cliente_id, porta_real)

    try:
        while True:
            comando = input("> ").strip()

            if not comando:
                continue

            if comando.lower() in ("exit", "quit"):
                sair_com_logout(clientSocket)
                break

            if not comando_valido(comando):
                continue

            ok = rdt3.rdt_send(clientSocket, comando, SERVER_ADDRESS, tipo=protocol.COMMAND)

            if not ok:
                print("Servidor não respondeu. Tente novamente.")

    except KeyboardInterrupt:
        sair_com_logout(clientSocket)

    finally:
        rodando = False
        rdt3.parar_receptor(clientSocket)
        clientSocket.close()
        print("\nCliente encerrado.")


if __name__ == "__main__":
    main()
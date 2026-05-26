import socket 
import os
import  rdt3  # importa o protocolo RDT 3

BUFFER_SIZE = 1024
SERVER_NAME = "localhost" # 127.0.0.1
SERVER_PORT = 5005

# criação do socket UDP para o Server -> (AF_INET = IPv4, SOCK_DGRAM = UDP)
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((SERVER_NAME, SERVER_PORT)) # vínculo ao endereço

print(f"Servidor UDP com RDT 3.0 escutando na porta {SERVER_PORT}...");

while True:
    # recebe o nome do arquivo do cliente 
    expected_seq = 0  #arquivo começa esperando o SEQ 0

    # substituimos recvfrom por rdt_recv confiável
    tipo, conteudo, client_addr = rdt3.rdt_recv(serverSocket, expected_seq)
    filename = conteudo.decode()
    expected_seq = 1 - expected_seq  # passa a esperar SEQ 1

    print(f"\nRecebendo arquivo de nome: {filename}")

    # criação do novo nome com o prefixo exigido 
    new_name = "leilao_" + filename
    caminho = new_name  

    # abre o arquivo para escrita binária
    with open(caminho, "wb") as f:
        while True:
            tipo, chunk, client_addr = rdt3.rdt_recv(serverSocket, expected_seq)
            expected_seq = 1 - expected_seq  
            
            if tipo == "EOF": # checa o término do arquivo
                break 

            f.write(chunk) 

    print(f"Arquivo renomeado e armazenado localmente como: {new_name}")

    # devolve o arquivo ao cliente usando o RDT 3.0
    sender_seq = 0  
    
    print(f"Devolvendo o novo nome do arquivo ({new_name}) via RDT...")
    rdt3.rdt_send(serverSocket, new_name, client_addr, sender_seq, tipo="TEXT")
    sender_seq = 1 - sender_seq

    print("Devolvendo os bytes do arquivo processado...")

    # abre o arquivo salvo para leitura binária -> "rb"
    with open(caminho, "rb") as f:
        while True: 
            bytes_read = f.read(BUFFER_SIZE) # lê um pedaço de arquivo de até 1024 bytes por vez
            if not bytes_read: # como não há mais dados, finalizou o arquivo 
                break
    
            rdt3.rdt_send(serverSocket, bytes_read, client_addr, sender_seq, tipo="DATA")
            sender_seq = 1 - sender_seq

    # marca o fim do envio
    rdt3.rdt_send(serverSocket, b"EOF", client_addr, sender_seq, tipo="EOF")
    sender_seq = 1 - sender_seq

    print(f"Arquivo {new_name} totalmente devolvido ao cliente de forma confiável.\n")
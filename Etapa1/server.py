import socket 
import os

BUFFER_SIZE = 1024
SERVER_NAME = "127.0.0.1" # localhost
SERVER_PORT = 5005

# criação do socket UDP para o Server -> (AF_INET = IPv4, SOCK_DGRAM = UDP)
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverSocket.bind((SERVER_NAME, SERVER_PORT)) # vínculo ao IP e à porta 

print(f"Servidor UDP escutando na porta {SERVER_PORT}...");

while True:
    # recebe o primeiro pacote do cliente (nome do arquivo) 
    data, client_addr = serverSocket.recvfrom(BUFFER_SIZE)
    filename = data.decode()

    print(f"Recebendo arquivo de nome: {filename}")

    # criação do novo nome com o prefixo exigido 
    new_name = "leilao_" + filename
    caminho = new_name  

    # abre o arquivo para escrita binária
    with open(caminho, "wb") as f:
        while True:
            data, client_addr = serverSocket.recvfrom(BUFFER_SIZE) # recebe um pedaço do arquivo
            if data == b"EOF": # verficação de que a mensagem chegou ao fim ou não
                break 

            f.write(data) # escrita dos bytes recebidos no arquivo

    print(f"Arquivo salvo como {new_name}")

    # envia de volta ao cliente o novo nome do arquivo 
    serverSocket.sendto(novo_nome.encode(), client_addr)

    # abre o arquivo salvo para leitura binária -> "rb"
    with open(caminho, "rb") as f:
        while True: 
            bytes_read = f.read(BUFFER_SIZE) # lê um pedaço de arquivo de até 1024 bytes por vez
            if not bytes_read: # como não há mais dados, finalizou o arquivo 
                break
    
            serverSocket.sendto(bytes_read, client_addr) # envia pedaço para o cliente 

    # marca o fim do envio
    serverSocket.sendto(b"EOF", client_addr)

    print(f"Arquivo {new_name} devolvido ao cliente")


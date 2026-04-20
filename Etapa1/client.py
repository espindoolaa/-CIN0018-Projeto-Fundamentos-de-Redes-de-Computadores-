import socket 
import os

BUFFER_SIZE = 1024 
SERVER_NAME = "127.0.0.1" # localhost
SERVER_PORT = 5005
SERVER_ADDRESS = (SERVER_NAME, SERVER_PORT)

# criação do socket UDP para o Client
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # definição em IPv4 e UDP

# arquivo a ser enviado
file = input("Digite o nome do arquivo para envio:")

if not os.path.exists(file): # verificação
    print("Arquivo não encontrado no caminho mencionado!")
    exit()

# envio do nome do arquivo
clientSocket.sendto(file.encode(), SERVER_ADDRESS)

# envio dos pacotes (chunks) que compõem o arquivo enviado
with open(file, 'rb') as f:
    while True:
        chunk = f.read(BUFFER_SIZE) # leitura dos 1024 bytes por chunk.
        if not chunk: # leitura se encerra quando não houver mais conteúdo.
            break
        clientSocket.sendto(chunk, SERVER_ADDRESS) # envio do pacote para o server.

clientSocket.sendto(b"EOF", SERVER_ADDRESS) # end-of-file (EOF) enviado para o destino.

print("Transmissão do arquivo completa. Aguardando retorno...")

# recebe nome do arquivo renomeado
data, addr = clientSocket.recvfrom(BUFFER_SIZE)
name_received = data.decode()

# recebe o conteúdo do arquivo de volta
with open(file, 'wb') as f:
    while True:
        data, addr = clientSocket.recvfrom(BUFFER_SIZE) # o endereco do cliente não é necessário nessa etapa.
        if data == b"EOF": # recebe os pacotes até receber EOF, indicando encerramento do arquivo enviado pelo server.
            break
        f.write(data)

print(f"Arquivo recebido como: {name_received}") 

# fecha o socket
clientSocket.close()
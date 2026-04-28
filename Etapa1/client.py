import socket 
import os

BUFFER_SIZE = 1024 
SERVER_NAME = "localhost" # 127.0.0.1
SERVER_PORT = 5005
SERVER_ADDRESS = (SERVER_NAME, SERVER_PORT)

# criação do socket UDP para o Client
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # definição em IPv4 e UDP

# entrada do usuário com o nome do arquivo 
file_name = input("Digite o nome do arquivo: ").strip()

# caminho absoluto para leitura
base_dir = os.path.dirname(os.path.abspath(__file__))  
file = os.path.join(base_dir, "test_files", file_name) 

# verificação se o input encontrou o arquivo
if not os.path.exists(file): 
    print("Arquivo não encontrado no caminho mencionado!") 
    exit()  

# envio do nome do arquivo
clientSocket.sendto(file_name.encode(), SERVER_ADDRESS)

# envio dos pacotes (chunks) que compõem o arquivo enviado
with open(file, 'rb') as f:
    while True:
        chunk = f.read(BUFFER_SIZE) # leitura dos 1024 bytes por chunk.
        if not chunk: # leitura se encerra quando não houver mais conteúdo.
            break
        clientSocket.sendto(chunk, SERVER_ADDRESS) # envio do pacote para o server.

clientSocket.sendto(b"EOF", SERVER_ADDRESS) # end-of-file (EOF) enviado para o destino.

print("Transmissão do arquivo completa. Aguardando retorno...")

# recebe nome do arquivo renomeado e o endereço de quem enviou
data, server_addr = clientSocket.recvfrom(BUFFER_SIZE) 
name_received = data.decode()

# recebe o conteúdo do arquivo de volta 
with open(file, 'wb') as f:
    while True:
        data, server_addr = clientSocket.recvfrom(BUFFER_SIZE) # o endereco do cliente não é necessário nessa etapa.
        if data == b"EOF": # recebe os pacotes até receber EOF, indicando encerramento do arquivo enviado pelo server.
            break
        f.write(data)

print(f"Arquivo recebido como: {name_received}") 

# fecha o socket
clientSocket.close()
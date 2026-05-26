import socket 
import os
import rdt3  # importando o módulo com o protocolo RDt 3.0

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

# envio de arquivo para o servidor usando o protocolo RDT 3.0
sender_seq = 0  # inicializa a sequência de envio do cliente em 0

print("Enviando nome do arquivo via RDT 3.0...")

# substituição de sendto por rdt_send
# envio do nome do arquivo
rdt3.rdt_send(clientSocket, file_name, SERVER_ADDRESS, sender_seq, tipo="TEXT")
# alterna a sequência (0 -> 1) para o próximo envio
sender_seq = 1 - sender_seq  

print("Enviando os pacotes do arquivo...")

# envio dos pacotes (chunks) que compõem o arquivo enviado
with open(file, 'rb') as f:
    while True:
        chunk = f.read(BUFFER_SIZE) # leitura dos 1024 bytes por chunk.
        if not chunk: # leitura se encerra quando não houver mais conteúdo.
            break
        # substituição de sendto por rdt_send
        rdt3.rdt_send(clientSocket, chunk, SERVER_ADDRESS, sender_seq, tipo="DATA")
        sender_seq = 1 - sender_seq  # alterna a sequência a cada pacote com ACK confirmado

# envia o indicador de fim usando RDT confiável
rdt3.rdt_send(clientSocket, b"EOF", SERVER_ADDRESS, sender_seq, tipo="EOF")
sender_seq = 1 - sender_seq

print("Transmissão do arquivo completa. Aguardando retorno confiável do servidor...\n")

# recebendo om arquivo de volta do server
expected_seq = 0  #reinicia sequência esperada para o recebimento

# troca de recvfrom por rdt_recv
tipo, conteudo, server_addr = rdt3.rdt_recv(clientSocket, expected_seq)
name_received = conteudo.decode()
expected_seq = 1 - expected_seq  

#caminho_salvamento = os.path.join(base_dir, "test_files",name_received)

# recebe o conteúdo do arquivo de volta 

with open(file, 'wb') as f:
    while True:
        tipo, chunk, server_addr = rdt3.rdt_recv(clientSocket, expected_seq)
        expected_seq = 1 - expected_seq  
        
        if tipo == "EOF": #fica recebendo pacotes até o EOF
            break
        f.write(chunk)

print(f"\nArquivo recebido de volta e salvo com segurança.") 

# fecha o socket
clientSocket.close()
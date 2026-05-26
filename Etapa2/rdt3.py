import socket
import random
# esse módulo teve que ser criado, pois para implementar a lógica do RDT 3,
# ambos os servidor e cliente precisam usar as mesmas funções de envio e recebimento
# confiável. Assim, criamos o rdt3.py para centralizar essa lógica e evitar duplicação de código entre server.py e client.py

# nesse módulo, usamos o buffersize como 2048, pois no server.py e no client.py os pacotes são divididos como 
# tendo 1024 bytes, porém ainda serão acrescentados os cabeçalhos das outras camadas. Para evitar a perda 
# de dados, colocamos o tamanho de 2048, como uma margem de segurança


# nessa parte, definimos a chance de perda de pacotes para simular um ambiente realista onde o UDP pode perder pacotes
CHANCE_DE_PERDA = 0.15  #pode ser modificado pra aumentar ou diminuir a taxa de perda simulada

#função que define se o pacote será ou não descartado
def deve_descartar_pacote(): 
    """
    Retorna True se o pacote deve ser artificialmente descartado,
    simulando uma perda real na camada UDP/Internet.
    """
    return random.random() < CHANCE_DE_PERDA


# definição da função de envio confiável (rdt 3.0 sender)
def rdt_send(sock, payload, destino, seq_atual, tipo="DATA"):
    """
    Envia um pacote de dados ou controle para o destino de forma confiável.
    Aplicando a lógica Stop-and-Wait com temporizador e retransmissão.
    """
    # configura o tempo máximo de espera pelo ACK (Timeout de 1.5 segundos)>
    sock.settimeout(1.5)
    
    # construção do cabeçalho de aplicação (TIPO:SEQ:)
    # garante que strings (como texto/comandos) e bytes (como pedaços de imagem) coexistam.
    cabecalho = f"{tipo}:{seq_atual}:".encode()
    if isinstance(payload, str):
        pacote = cabecalho + payload.encode()
    else:
        pacote = cabecalho + payload

    # loop de parada e espera (Stop-and-Wait)
    while True:
        try:
            # simulação da perda
            if deve_descartar_pacote():
                print(f"[RDT SENDER] -> [SIMULAÇÃO DE PERDA] Pacote {tipo} com SEQ={seq_atual} foi 'perdido'.")
            else:
                print(f"[RDT SENDER] -> Enviando pacote {tipo} | SEQ={seq_atual}")
                sock.sendto(pacote, destino)
            
            # aguarda a resposta (ACK) do receptor
            ack_bytes, addr = sock.recvfrom(2048)
            
            # decodifica o ACK e ineterpretação do cabeçalho
            partes = ack_bytes.decode().split(":")
            
            #verifica se a mensagem recebida é de fato um ACK e se tem o SEQ esperado
            if partes[0] == "ACK" and int(partes[1]) == seq_atual:
                print(f"[RDT SENDER] <- Recebido ACK={seq_atual} correto. Avançando...")
                # desativa o timeout antes de retornar para não afetar outras operações padrão do socket
                sock.settimeout(None)
                return  # pacote recebido, encerra o loop e a função
            else:
                #deu algum problema: ou não é ACK ou o SEQ está errado (pode ser um ACK antigo ou um pacote malformado)
                print(f"[RDT SENDER] <- Recebeu ACK={partes[1]} incorreto (esperava {seq_atual}). Ignorando...")
                
        except socket.timeout:
            # Se o temporizador estourar antes de receber o ACK correto, entra aqui
            print(f"[RDT SENDER] !!! TIMEOUT !!! Estourou o tempo limite para SEQ={seq_atual}. Retransmitindo...")


# definição da função de recebimento confiável (rdt 3.0 receiver).
def rdt_recv(sock, expected_seq):
    """
    Fica escutando o socket até receber o pacote com o número de sequência esperado.
    Filtra duplicados e responde com ACKs automáticos.
    """
    # evitamos o timeout do receptor enquanto aguarda passivamente o cliente iniciar
    sock.settimeout(None)
    
    while True:
        packet, addr = sock.recvfrom(2048)
        
        # interptreatação dos dados binários separando os dois primeiros delimitadores ':'
        try:
            idx1 = packet.index(b':')
            idx2 = packet.index(b':', idx1 + 1)
            
            tipo = packet[:idx1].decode()
            seq_recebido = int(packet[idx1+1:idx2].decode())
            conteudo = packet[idx2+1:]
        except (ValueError, IndexError):
            # ignora pacotes malformados que não sigam a estrutura do cabeçalho
            continue

        # primeiro caso: o pacote recebido é o esperado
        if seq_recebido == expected_seq:
            print(f"[RDT RECEIVER] <- Recebido pacote esperado {tipo} | SEQ={seq_recebido}. Enviando ACK={expected_seq}.")
            
            # envia o ACK confirmando este pacote
            ack_msg = f"ACK:{expected_seq}".encode()
            sock.sendto(ack_msg, addr)
            
            # retorna os dados limpos para a aplicação tratar
            return tipo, conteudo, addr
            
        # segundo caso: o pacote recebido é duplicado (Seq antigo)
        else:
            # isso acontece se o nosso ACK anterior sumiu na rede e o transmissor deu timeout
            print(f"[RDT RECEIVER] <- Recebido pacote DUPLICADO SEQ={seq_recebido}. Reenviando ACK={seq_recebido} antigo.")
            
            # reenvia o ACK do pacote antigo para destravar o transmissor
            ack_msg = f"ACK:{seq_recebido}".encode()
            sock.sendto(ack_msg, addr)
            # o loop continua rodando até que o pacote com o SEQ correto de fato chegue

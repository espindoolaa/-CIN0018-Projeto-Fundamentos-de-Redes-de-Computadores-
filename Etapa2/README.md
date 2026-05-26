# Segunda Entrega: Implementando uma transferência confiável com RDT 3.0
## Objetivo da entrega
Esta segunda etapa tem como objetivo evoluir a comunicação UDP construída anteriormente, implementando o protocolo RDT 3.0 (Reliable Data Transfer) na camada de aplicação, conforme o modelo Stop-and-Wait apresentado no livro do Kurose. O sistema agora lida de forma robusta com canais não-confiáveis, tratando cenários de perda de pacotes e duplicações por meio de numeração de sequência alternada (0 e 1) e temporizadores (timeouts).
Os requisitos desta etapa exigem que:
**1.** Ocorra o envio, armazenamento e devolução de arquivos de formatos quaisquer (.txt, .jpg, etc.) de forma 100% confiável.
**2.** Cada passo do protocolo (envio de pacotes, recepção de ACKs, ocorrência de timeouts e retransmissões) seja explicitamente apresentado na linha de comando para fins de auditoria do fluxo.
**3.** Seja integrado um gerador de perdas aleatórias de pacotes na camada de transporte para testar e provar a eficiência e a resiliência do RDT 3.0 implementado.
Nota: Conforme orientação, a implementação de um checksum manual foi dispensada, visto que os protocolos subjacentes (UDP e camada de enlace) já realizam essa validação de integridade.
## Desenvolvedores do projeto
 * Lara Luchi (lvl)
 * Luiz Felipe Vicente da Silva (lfvs2)
 * Mateus Espíndola Batista (meb)
 * Victória Pessoa Barbosa Matos (vpbm)
## Funcionamento do sistema implementado
O sistema é composto por três módulos principais:
 * **RDT 3.0**
Centraliza a lógica de controle do protocolo.
Transmissor (Sender): Envia o pacote, inicia o timer e aguarda o ACK correto. Em caso de estouro de tempo (timeout), realiza a retransmissão automática.
Receptor (Receiver): Filtra pacotes duplicados para evitar corrupção de arquivos e garante o envio dos ACKs corretos.
Simulador de Perdas: Descarta pacotes de forma probabilística para forçar o acionamento dos mecanismos de recuperação do RDT 3.0.
 * **Cliente**
Solicita o arquivo local, fragmenta-o e utiliza o módulo rdt3.py para enviá-lo de forma confiável.
Inverte o papel para recepção e aguarda o retorno do arquivo modificado pelo servidor, também via RDT 3.0.
 * **Servidor**
Escuta a porta padrão e adota o papel de receptor via RDT 3.0 para remontar o arquivo original enviado pelo cliente.
Processa o arquivo, aplicando o prefixo leilao_.
Atua como transmissor via RDT 3.0 para devolver o arquivo e as confirmações de texto estruturado ao cliente.
## Fluxo da aplicação
Cliente inicializa a sequência de envio em 0 e envia o nome do arquivo de forma confiável.
Cliente envia os blocos de dados (de até 1024 bytes) alternando o bit de sequência (0 ou 1) a cada ACK recebido com sucesso.
Cliente envia o pacote indicador de fim de arquivo (EOF).
Servidor recebe os blocos sem duplicatas através da validação de sequência, reconstrói o arquivo e adiciona o prefixo leilao_.
Servidor assume o papel de transmissor (reiniciando sua sequência em 0) e envia o novo nome do arquivo e seus respectivos blocos de volta.
Servidor envia o indicador de término EOF via RDT 3.0.
Cliente valida o recebimento e armazena o arquivo modificado com sucesso.
## Estrutura do projeto
```text
Projeto/
└── Etapa2/
    ├── rdt3.py           # Núcleo do protocolo RDT 3.0 e gerador de perdas
    ├── client.py         # Código adaptado para transmissão e recepção confiável
    ├── server.py         # Servidor adaptado operando com controle de stop-and-wait
    ├── README.md         
    └── test_files/       # Pasta com os arquivos de testes de diferentes formatos
        ├── imagem.jpg    # Arquivo de imagem para validação binária
        └── mensagem.txt  # Arquivo de texto plano

```
## Instruções para execução(semelhantes às da entrega 1)
 1. Clonando o projeto para a sua máquina
```text
git clone https://github.com/espindoolaa/-CIN0018-Projeto-Fundamentos-de-Redes-de-Computadores-.git

```
 2. Executando servidor
```text
2.1 Primeiramente, abra um terminal que será exclusivo para o Server.

2.2 Dentro da pasta do projeto, transicione para a pasta Etapa2 (referente ao desenvolvimento dessa entrega) com o comando: cd Etapa2

2.3 Em seguida rode no terminal: python server.py

Observação: Lembrando que <nome_arquivo> pode assumir os valores: imagem.jpg ou mensagem.txt, os arquivos no contidos na pasta de testes (test_files).

```
 3. Executando cliente
```text
3.1 Para o cliente será necessário abrir outro terminal, o qual será exclusivo para ele.
3.2 Dentro da pasta do projeto, transicione para a pasta Etapa2 (referente ao desenvolvimento dessa entrega) com o comando: cd Etapa2
3.3 Agora, rode no terminal: python client.py
3.4 O terminal do client.py solicitará um input de arquivo, que deverá ser da forma: <arquivo>
3.5 Deverá ser iniciada a transmissão dos pacotes. Várias mensagens indicando a etapa e status da transmissão

Observação: Lembrando que <nome_arquivo> pode assumir os valores: imagem.jpg ou mensagem.txt, os arquivos no contidos na pasta de testes (test_files).


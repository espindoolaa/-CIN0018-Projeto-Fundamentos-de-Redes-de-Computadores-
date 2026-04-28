# 📡 Primeira Entrega: Transmissão de Arquivos com UDP
## Objetivo da entrega

Esta primeira etapa tem como objetivo implementar a comunicação entre **cliente** e **servidor** por meio do protocolo UDP, utilizando a biblioteca `socket` em Python 
e fragmentando a transferência em pacotes de até 1024 bytes. Os sistema solicitado pelo professor e monitores exigia que: <br/>

**1.** Ocorresse envio de arquivos de formatos quaisquer (.txt, .jpeg, .mp3, etc.) do cliente para o servidor. <br/>
**2.** Armazenasse do arquivo enviado pelo cliente no servidor, além de renomear o arquivo para o formato solicitado. <br/>
**3.** O servidor retornasse o arquivo para o cliente, já com o nome alterado. <br/>

## Desenvolvedores do projeto

* Lara Luchi (lvl)
* Luiz Felipe Vicente da Silva (lfvs2)
* Mateus Espíndola Batista (meb)
* Victória Pessoa Barbosa Matos (vpbm)

## Funcionamento do sistema implementado
O sistema construído pela equipe é composto por dois módulos:

* **Cliente**
  - Realiza o envio de arquivo com formato qualquer ao servidor.
  - Aguarda o retorno do arquivo renomeado pelo servidor.
  - Ao final do processo, recebe o arquivo renomeado.

* **Servidor**
  - Recebe o arquivo enviado pelo cliente.
  - Armazena o arquivo localmente.
  - Renomeia o arquivo com prefixo `leilao_` (padrão solicitado).
  - Devolve o arquivo ao cliente com a renomeação já realizada.
 
## Fluxo da aplicação

**1.** Cliente envia o nome do arquivo. <br/>
**2.** Cliente envia o conteúdo em pacotes de até 1024 bytes. <br/>
**3.** Cliente envia um marcador de fim (`EOF`). <br/>
**4.** Servidor recebe os pacotes enviados e reconstrói o arquivo. <br/>
**5.** Servidor renomeia o arquivo (`leilao_<nome>`). <br/>
**6.** Servidor envia o arquivo de volta. <br/>
**7.** Cliente recebe e salva o arquivo. <br/>

## Estrutura do projeto

```text
Projeto/
│
├── client.py (código relativo ao funcionamento do cliente)
├── server.py (código relativo ao funcionamento do servidor)
├── README.md
└── test_files/ (pasta dos arquivos de testes)
    ├── imagem.jpg (arquivo .jpg para teste)
    └── mensagem.txt (arquivo .txt para teste)
```
## Instruções para execução
1. Clonando o projeto para a sua máquina
```text
git clone https://github.com/espindoolaa/-CIN0018-Projeto-Fundamentos-de-Redes-de-Computadores-.git
```

2. Executando servidor
```text
2.1 Primeiramente, abra um terminal que será exclusivo para o Server.

2.2 Dentro da pasta do projeto, transicione para a pasta Etapa1 (referente ao desenvolvimento dessa entrega) com o comando: cd Etapa1

2.3 Em seguida rode no terminal: python server.py

2.4 Comportamento esperado: "Servidor UDP escutando na porta 5005..." --> "Recebendo arquivo de nome: <nome_arquivo>" (quando recebido arquivo do cliente) --> "Arquivo renomeado para: leilao_<nome_arquivo>" --> "Arquivo leilao_<nome_arquivo> devolvido ao cliente"

Observação: Lembrando que <nome_arquivo> pode assumir os valores: imagem.jpg ou mensagem.txt, os quais são os arquivos no contidos na pasta de testes (test_files).
```

3. Executando cliente
```text
3.1 Para o cliente será necessário abrir outro terminal, o qual será exclusivo para ele.
3.2 Dentro da pasta do projeto, transicione para a pasta Etapa1 (referente ao desenvolvimento dessa entrega) com o comando: cd Etapa1
3.3 Agora, rode no terminal: python client.py
3.4 O terminal do client.py solicitará um input de arquivo, que poderá deverá ser da forma: <arquivo>
3.5 Comportamento esperado: "Transmissão do arquivo completa. Aguardando retorno..." --> "Arquivo recebido como: leilao_<arquivo>

Observação: Lembrando que <nome_arquivo> pode assumir os valores: imagem.jpg ou mensagem.txt, os quais são os arquivos no contidos na pasta de testes (test_files).
```





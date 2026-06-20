# Projeto Fundamentos de Redes de Computadores - AuctionCin

## Visão geral

Este projeto foi desenvolvido para a disciplina de Fundamentos de Redes de Computadores e está dividido em três entregas incrementais.

A proposta geral é construir, em etapas, uma aplicação cliente-servidor utilizando sockets UDP. A cada entrega, a aplicação evolui em complexidade: primeiro com uma transferência básica de arquivos, depois com confiabilidade implementada na camada de aplicação e, por fim, com um sistema de leilão multiusuário chamado **AuctionCin**.

Cada etapa possui seu próprio diretório e um README específico com instruções detalhadas de execução.

## Desenvolvedores do projeto

Lara Luchi (lvl)
Luiz Felipe Vicente da Silva (lfvs2)
Mateus Espíndola Batista (meb)
Victória Pessoa Barbosa Matos (vpbm)

## Estrutura geral do repositório

```text
Projeto/
├── Etapa1/
│   ├── client.py
│   ├── server.py
│   ├── README.md
│   └── test_files/
│
├── Etapa2/
│   ├── client.py
│   ├── server.py
│   ├── rdt3.py
│   ├── README.md
│   └── test_files/
│
└── Etapa3/
    ├── auction.py
    ├── client.py
    ├── contacts.py
    ├── protocol.py
    ├── rdt3.py
    ├── server.py
    ├── README.md
    └── text_files/
```

## Etapa 1 - Transferência básica de arquivos com UDP

A primeira entrega implementa uma comunicação cliente-servidor simples utilizando sockets UDP.

Nessa etapa, o cliente envia um arquivo para o servidor. O servidor recebe esse arquivo, salva uma nova versão com o prefixo `leilao_` e devolve o arquivo modificado ao cliente.

O objetivo principal dessa etapa é compreender o uso básico de sockets UDP, incluindo:

* criação de sockets;
* envio de mensagens;
* recebimento de dados;
* fragmentação do arquivo em blocos;
* remontagem do arquivo no destino;
* comunicação entre cliente e servidor.

A Etapa 1 ainda não implementa mecanismos próprios de confiabilidade. Portanto, ela serve como base para a evolução feita na etapa seguinte.

Para instruções completas de execução, consulte:

```text
Etapa1/README.md
```

## Etapa 2 - Transferência confiável com RDT 3.0

A segunda entrega evolui a comunicação UDP da Etapa 1 por meio da implementação do protocolo **RDT 3.0** na camada de aplicação.

Como o UDP não garante entrega, ordenação ou ausência de duplicatas, essa etapa adiciona mecanismos de confiabilidade inspirados no modelo Stop-and-Wait apresentado no livro do Kurose.

O sistema passa a utilizar:

* ACKs;
* número de sequência alternado entre 0 e 1;
* temporizadores;
* timeout;
* retransmissão automática;
* descarte de pacotes duplicados;
* simulação de perda de pacotes.

Com isso, o cliente consegue enviar arquivos para o servidor de forma confiável, mesmo diante de perdas simuladas. O servidor recebe o arquivo, adiciona o prefixo `leilao_` e devolve o arquivo ao cliente também utilizando o RDT 3.0.

A implementação manual de checksum foi dispensada, pois os protocolos subjacentes já realizam verificação de integridade.

Para instruções completas de execução, consulte:

```text
Etapa2/README.md
```

## Etapa 3 - AuctionCin: Sistema de leilão multiusuário

A terceira entrega implementa a aplicação principal do projeto: o **AuctionCin**, um sistema de leilão online multiusuário executado em linha de comando.

Essa etapa reutiliza a comunicação UDP confiável construída na Etapa 2 e aplica essa base em uma aplicação completa de leilão.

O sistema possui um servidor central e múltiplos clientes. O servidor gerencia o estado do leilão, os usuários online, os itens disponíveis, os lances, os vencedores e o envio dos arquivos associados aos itens arrematados.

Entre as funcionalidades implementadas estão:

* múltiplos clientes simultâneos;
* associação de cada cliente a uma porta UDP diferente;
* login e logout de usuários;
* bloqueio de nomes repetidos;
* listagem de itens;
* consulta de status do leilão;
* envio de lances;
* validação de lances maiores que o valor atual;
* atualização automática para todos os usuários conectados;
* leilão de um item por vez;
* encerramento por tempo ou por limite de lances;
* envio do arquivo `.txt` do item ao vencedor.

Os itens leiloados são representados por arquivos de texto localizados na pasta `text_files`.

Para instruções completas de execução, comandos disponíveis, regras de negócio e sequência de testes, consulte:

```text
Etapa3/README.md
```

## Como clonar o projeto

```bash
git clone https://github.com/espindoolaa/-CIN0018-Projeto-Fundamentos-de-Redes-de-Computadores-.git
```

Depois de clonar, entre na pasta da etapa desejada:

```bash
cd Etapa1
```

ou:

```bash
cd Etapa2
```

ou:

```bash
cd Etapa3
```

Cada diretório possui um README próprio com as instruções específicas daquela entrega.

## Observação final

O projeto foi construído de forma incremental. Portanto, a Etapa 1 apresenta a base da comunicação UDP, a Etapa 2 adiciona confiabilidade por meio do RDT 3.0 e a Etapa 3 utiliza essa comunicação confiável para implementar o sistema final de leilão multiusuário.

# Terceira Entrega: AuctionCin - Sistema de Leilão Multiusuário com UDP e RDT 3.0

## Objetivo da entrega

Esta terceira etapa implementa o **AuctionCin**, um sistema de leilão online multiusuário executado em linha de comando, utilizando o paradigma **cliente-servidor**.

A comunicação entre cliente e servidor é feita com **sockets UDP**, mantendo a confiabilidade na camada de aplicação por meio do protocolo **RDT 3.0**, já utilizado na entrega anterior. Assim, mesmo usando UDP, o sistema possui controle de ACK, número de sequência, timeout, retransmissão e simulação de perda de pacotes.

Nesta etapa, o foco principal é a aplicação final do leilão: múltiplos clientes podem entrar no sistema, visualizar itens, dar lances, acompanhar quem está vencendo e receber o arquivo simbólico do item caso vençam o leilão.

## Desenvolvedores do projeto

Lara Luchi (lvl)
Luiz Felipe Vicente da Silva (lfvs2)
Mateus Espíndola Batista (meb)
Victória Pessoa Barbosa Matos (vpbm)

## Estrutura do projeto

```text
Projeto/
└── Etapa3/
    ├── auction.py          # Regras de negócio do leilão
    ├── client.py           # Cliente em linha de comando
    ├── contacts.py         # Associação cliente -> IP:PORTA
    ├── protocol.py         # Tipos de mensagens da aplicação
    ├── rdt3.py             # Implementação do RDT 3.0 sobre UDP
    ├── server.py           # Servidor principal do AuctionCin
    ├── README.md
    └── text_files/
        ├── carro.txt
        ├── celular.txt
        ├── drone.txt
        └── recebidos/      # Criada quando o cliente recebe um item vencido
```

## Módulos principais

### `rdt3.py`

Implementa o RDT 3.0 na camada de aplicação. O módulo cuida de:

* envio confiável sobre UDP;
* ACKs;
* número de sequência alternado;
* timeout;
* retransmissão;
* simulação de perda de pacotes;
* tratamento de pacotes duplicados.

### `server.py`

Executa o servidor do AuctionCin. Ele recebe comandos dos clientes, consulta as regras do leilão, envia respostas, envia atualizações para todos os usuários online e envia o arquivo `.txt` ao vencedor de cada item.

### `client.py`

Executa o cliente em linha de comando. O usuário digita comandos como `login`, `list`, `status`, `bid` e `logout`. O cliente também recebe atualizações automáticas do servidor e arquivos caso vença algum item.

### `auction.py`

Contém as regras do leilão: usuários online, nomes repetidos, item atual, lances, vencedor, cronômetro, limite de lances e encerramento dos itens.

### `contacts.py`

Define identificadores de processos clientes e suas portas:

```python
CONTATOS = {
    "cliente1": ("127.0.0.1", 5000),
    "cliente2": ("127.0.0.1", 5500),
    "cliente3": ("127.0.0.1", 6000),
}
```

Os nomes `cliente1`, `cliente2` e `cliente3` servem apenas para escolher a porta local. O nome real do usuário é escolhido no comando `login`.

## Regras de negócio

### Login

O usuário entra no sistema com:

```text
login <nome_do_usuario>
```

Exemplo:

```text
login Felipe
```

Resultado esperado:

```text
você está online
```

Dois usuários não podem estar online com o mesmo nome. Se outro cliente tentar usar um nome já logado, o servidor retorna:

```text
Erro: já existe um usuário online com esse nome.
```

### Logout

O usuário sai do sistema com:

```text
logout
```

Resultado esperado:

```text
Logout realizado.
```

Depois do logout, o usuário precisa fazer login novamente para usar `list`, `status` ou `bid`.

### Listagem de itens

O comando:

```text
list
```

mostra os itens disponíveis, seus identificadores, arquivos associados, lance atual e estado.

Exemplo esperado:

```text
Itens disponíveis no AuctionCin:
1 - Carro esportivo (carro.txt) | lance atual: R$ 0.00 | em leilão, aguardando primeiro lance
2 - Celular premium (celular.txt) | lance atual: R$ 0.00 | aguardando turno
3 - Drone autônomo (drone.txt) | lance atual: R$ 0.00 | aguardando turno
```

### Status

O comando:

```text
status
```

mostra o item atualmente em leilão, o cronômetro e quem está vencendo cada item.

Antes do primeiro lance, o cronômetro ainda não começa:

```text
Item em leilão no momento: 1 - Carro esportivo
Cronômetro: aguardando o primeiro lance deste item.
```

### Lance

O comando de lance é:

```text
bid <id_item> <valor>
```

Exemplo:

```text
bid 1 1000
```

O valor precisa ser maior que o lance atual. O sistema aceita valores com ponto ou vírgula:

```text
bid 1 1000.01
bid 1 1000,02
```

Se o lance for válido, o cliente recebe:

```text
Lance aceito.
```

E todos os usuários online recebem uma atualização:

```text
[ATUALIZAÇÃO] Novo lance no item 1 (Carro esportivo): Felipe deu R$ 1000.00. Cronômetro reiniciado para 60s.
```

### Ordem dos itens

Apenas um item é leiloado por vez. O item 2 só entra em leilão depois que o item 1 é encerrado. O item 3 só entra depois do item 2.

Se o item atual for o item 1 e alguém tentar:

```text
bid 2 500
```

o resultado esperado é:

```text
Erro: este item ainda não está em leilão. Item atual: 1 - Carro esportivo.
```

### Tempo e limite de lances

Cada item encerra quando uma destas condições acontece primeiro:

1. O item fica **60 segundos sem receber novo lance**.
2. O item atinge **5 lances totais**.

O cronômetro não começa quando o servidor inicia nem quando o usuário faz login. Ele começa apenas no primeiro lance válido do item atual. A cada novo lance válido, o cronômetro volta para 60 segundos.

O limite de 5 lances é **por item**, não por pessoa.

Exemplo:

```text
Felipe dá bid 1 100
Maria dá bid 1 150
Felipe dá bid 1 200
Maria dá bid 1 250
Felipe dá bid 1 300
```

No quinto lance, o item 1 é encerrado.

### Envio do item ao vencedor

Quando um item é encerrado, o servidor envia ao vencedor o arquivo `.txt` correspondente ao item.

Exemplo esperado no cliente vencedor:

```text
Recebendo arquivo do item 1: carro.txt
Arquivo recebido e salvo em text_files/recebidos/recebido_carro.txt
```

## Instruções para execução

### 1. Clonar o projeto

```bash
git clone https://github.com/espindoolaa/-CIN0018-Projeto-Fundamentos-de-Redes-de-Computadores-.git
```

### 2. Entrar na pasta da Etapa 3

```bash
cd Etapa3
```

### 3. Executar o servidor

Abra um terminal exclusivo para o servidor:

```bash
python3 server.py
```

Resultado esperado:

```text
Servidor AuctionCin escutando em 127.0.0.1:5005...

Lista de contatos sugerida para testes:
cliente1 -> 127.0.0.1:5000
cliente2 -> 127.0.0.1:5500
cliente3 -> 127.0.0.1:6000
```

### 4. Executar os clientes

Abra outro terminal para o primeiro cliente:

```bash
python3 client.py cliente1
```

Abra outro terminal para o segundo cliente:

```bash
python3 client.py cliente2
```

Opcionalmente, abra um terceiro:

```bash
python3 client.py cliente3
```

Cada cliente usa uma porta diferente. Portanto, dois terminais não devem ser abertos com o mesmo identificador, como `cliente2` e `cliente2`, pois isso causaria conflito de porta.

## Comandos disponíveis no cliente

```text
login <nome_do_usuario>
list
status
bid <id_item> <valor>
logout
exit
```

## Sequência sugerida de teste

### Cliente 1

```text
login Felipe
status
list
bid 1 100
status
```

Resultados esperados:

* Login retorna `você está online`.
* `status` mostra o item 1 como item atual.
* `list` mostra o item 1 em leilão e os itens 2 e 3 aguardando turno.
* `bid 1 100` é aceito.
* O cronômetro começa após o primeiro lance.

### Cliente 2

```text
login Maria
status
bid 1 150
status
```

Resultados esperados:

* Login retorna `você está online`.
* O lance de Maria é aceito porque é maior que R$ 100.00.
* Todos os clientes online recebem a atualização do novo lance.
* O cronômetro reinicia para 60 segundos.

### Teste de lance inválido

```text
bid 1 120
```

Resultado esperado:

```text
Erro: o lance precisa ser maior que o lance atual.
```

### Teste de item fora do turno

```text
bid 2 500
```

Resultado esperado:

```text
Erro: este item ainda não está em leilão. Item atual: 1 - Carro esportivo.
```

### Teste de encerramento por 5 lances

Continue dando lances no item 1 até completar 5 lances totais:

```text
bid 1 200
bid 1 250
bid 1 300
```

Resultado esperado:

```text
[ATUALIZAÇÃO] Leilão encerrado para o item 1 (Carro esportivo) por atingir o limite de 5 lances. Vencedor: Felipe com R$ 300.00.
[ATUALIZAÇÃO] Próximo item em leilão: 2 - Celular premium.
```

O vencedor recebe o arquivo `carro.txt`.

### Teste do segundo item

Depois que o item 1 encerrar:

```text
status
bid 2 1000
```

Resultado esperado:

```text
Item em leilão no momento: 2 - Celular premium
Cronômetro: aguardando o primeiro lance deste item.
```

Após o lance:

```text
Lance aceito.
```

### Teste de encerramento por tempo

Após um lance válido, espere 60 segundos sem novos lances.

Resultado esperado:

```text
[ATUALIZAÇÃO] Leilão encerrado para o item 2 (Celular premium) por ficar 60s sem novo lance. Vencedor: Felipe com R$ 1000.00.
[ATUALIZAÇÃO] Próximo item em leilão: 3 - Drone autônomo.
```

### Teste de logout

```text
logout
status
```

Resultado esperado:

```text
Logout realizado.
Erro: faça login antes de usar esse comando.
```

## Testando o RDT 3.0

No arquivo `rdt3.py`, é possível ativar o debug do protocolo:

```python
DEBUG_RDT = True
```

Também é possível ajustar a perda simulada:

```python
CHANCE_DE_PERDA = 0.10
```

Com o debug ativado, o terminal mostra mensagens de envio, ACK, timeout, retransmissão e perda simulada. Para o vídeo final, recomenda-se deixar:

```python
DEBUG_RDT = False
```

para manter a saída mais limpa.

## Possíveis erros

### Porta já está em uso

Ocorre quando dois terminais tentam usar o mesmo identificador, por exemplo:

```bash
python3 client.py cliente2
python3 client.py cliente2
```

Solução: use outro cliente ou encerre o processo antigo.

```bash
pkill -f client.py
```

### Nome já está online

Ocorre quando dois usuários tentam fazer login com o mesmo nome.

```text
Erro: já existe um usuário online com esse nome.
```

Solução: usar outro nome ou fazer `logout` no cliente que já está usando aquele nome.

### Comando inválido

Use apenas:

```text
login <nome_do_usuario>
list
status
bid <id_item> <valor>
logout
exit
```

## Encerrando o sistema

Para sair de um cliente:

```text
exit
```

ou:

```text
logout
exit
```

Para encerrar o servidor:

```text
Ctrl + C
```

Para garantir que todos os processos foram encerrados:

```bash
pkill -f server.py
pkill -f client.py
```

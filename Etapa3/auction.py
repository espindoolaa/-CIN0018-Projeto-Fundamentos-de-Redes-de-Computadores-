import os
import time
import math
import threading
from dataclasses import dataclass

TEXT_FILES_DIR = "text_files"
DURACAO_ITEM = 60
MAX_LANCES = 5

# Itens do leilão. Cada item aponta para um arquivo .txt.
ITENS_INICIAIS = [
    ("1", "Carro esportivo", "carro.txt"),
    ("2", "Celular premium", "celular.txt"),
    ("3", "Drone autônomo", "drone.txt"),
]


@dataclass
class AuctionItem:
    item_id: str
    nome: str
    filename: str
    maior_lance: float = 0.0
    vencedor: str = None
    vencedor_addr: tuple = None
    qtd_lances: int = 0

    # prazo_limite só é definido depois do primeiro lance.
    # A cada novo lance válido, ele é renovado.
    prazo_limite: float = None

    encerrado: bool = False
    arquivo_enviado: bool = False

    # Retorna o tempo restante desde o último lance válido.
    def tempo_restante(self):
        if self.encerrado:
            return 0

        if self.prazo_limite is None:
            return DURACAO_ITEM

        restante = self.prazo_limite - time.monotonic()
        return max(0, math.ceil(restante))

    # Diz se o item já passou do tempo após algum lance.
    def tempo_expirado(self):
        if self.encerrado:
            return False

        if self.prazo_limite is None:
            return False

        return time.monotonic() >= self.prazo_limite


class AuctionSystem:
    def __init__(self):
        self.usuarios = {}
        self.addr_para_usuario = {}
        self.itens = {}
        self.ordem_itens = []
        self.indice_item_atual = 0

        self.lock = threading.Lock()

        self._preparar_pasta()
        self._preparar_itens()

    # Garante que a pasta dos arquivos exista.
    def _preparar_pasta(self):
        os.makedirs(TEXT_FILES_DIR, exist_ok=True)

    # Cadastra os itens disponíveis no leilão.
    def _preparar_itens(self):
        for item_id, nome, filename in ITENS_INICIAIS:
            self.itens[item_id] = AuctionItem(item_id, nome, filename)
            self.ordem_itens.append(item_id)

    # Retorna o item que está sendo leiloado agora.
    def _item_atual(self):
        if self.indice_item_atual >= len(self.ordem_itens):
            return None

        item_id = self.ordem_itens[self.indice_item_atual]
        return self.itens[item_id]

    # Passa para o próximo item.
    def _avancar_item_locked(self):
        self.indice_item_atual += 1

        proximo = self._item_atual()

        if proximo:
            return f"Próximo item em leilão: {proximo.item_id} - {proximo.nome}."

        return "Todos os itens do leilão foram encerrados."

    # Recebe um comando do cliente e executa a ação correta.
    def handle_command(self, line, addr):
        with self.lock:
            broadcasts, arquivos = self._encerrar_expirados_locked()

            partes = line.strip().split()

            if not partes:
                return "Comando vazio.", broadcasts, arquivos

            comando = partes[0].lower()

            if comando == "login":
                resposta = self._login(partes, addr)

            elif comando == "logout":
                resposta, novos_broadcasts = self._logout(addr)
                broadcasts.extend(novos_broadcasts)

            elif comando == "list":
                resposta = self._list(addr)

            elif comando == "status":
                resposta = self._status(addr)

            elif comando == "bid":
                resposta, novos_broadcasts, novos_arquivos = self._bid(partes, addr)
                broadcasts.extend(novos_broadcasts)
                arquivos.extend(novos_arquivos)

            else:
                resposta = "Comando inválido. Use: login, bid, list, status ou logout."

            return resposta, broadcasts, arquivos

    # Faz login. O nome pode ser qualquer um, desde que não esteja repetido.
    def _login(self, partes, addr):
        if len(partes) < 2:
            return "Uso correto: login <nome_do_usuario>"

        nome = " ".join(partes[1:]).strip()

        if not nome:
            return "Erro: informe um nome de usuário."

        if nome in self.usuarios and self.usuarios[nome] != addr:
            return "Erro: já existe um usuário online com esse nome."

        if addr in self.addr_para_usuario and self.addr_para_usuario[addr] != nome:
            return "Erro: este cliente já está logado com outro nome. Use logout antes."

        self.usuarios[nome] = addr
        self.addr_para_usuario[addr] = nome

        return "você está online"

    # Remove o usuário da lista de online.
    def _logout(self, addr):
        nome = self.addr_para_usuario.get(addr)

        if not nome:
            return "Você não está online.", []

        self.addr_para_usuario.pop(addr, None)
        self.usuarios.pop(nome, None)

        return "Logout realizado.", [f"Usuário {nome} saiu do sistema."]

    # Verifica se o cliente já fez login.
    def _usuario_logado(self, addr):
        return self.addr_para_usuario.get(addr)

    # Retorna o estado textual de um item.
    def _estado_item(self, item):
        item_atual = self._item_atual()

        if item.encerrado:
            return "encerrado"

        if item_atual and item.item_id == item_atual.item_id:
            if item.prazo_limite is None:
                return "em leilão, aguardando primeiro lance"

            return f"em leilão, {item.tempo_restante()}s restantes"

        return "aguardando turno"

    # Lista os itens e seus preços atuais.
    def _list(self, addr):
        if not self._usuario_logado(addr):
            return "Erro: faça login antes de usar esse comando."

        linhas = ["Itens disponíveis no AuctionCin:"]

        for item in self.itens.values():
            estado = self._estado_item(item)

            linhas.append(
                f"{item.item_id} - {item.nome} ({item.filename}) | "
                f"lance atual: R$ {item.maior_lance:.2f} | {estado}"
            )

        return "\n".join(linhas)

    # Mostra o item atual e quem está ganhando.
    def _status(self, addr):
        if not self._usuario_logado(addr):
            return "Erro: faça login antes de usar esse comando."

        linhas = []

        item_atual = self._item_atual()

        if item_atual:
            linhas.append(f"Item em leilão no momento: {item_atual.item_id} - {item_atual.nome}")

            if item_atual.prazo_limite is None:
                linhas.append("Cronômetro: aguardando o primeiro lance deste item.")
            else:
                linhas.append(f"Cronômetro: {item_atual.tempo_restante()}s restantes desde o último lance.")
        else:
            linhas.append("Não há mais itens em leilão.")

        linhas.append("")
        linhas.append("Status atual dos leilões:")

        for item in self.itens.values():
            vencedor = item.vencedor if item.vencedor else "nenhum"
            estado = self._estado_item(item)

            linhas.append(
                f"Item {item.item_id} - {item.nome}: "
                f"maior lance R$ {item.maior_lance:.2f}, "
                f"vencedor atual: {vencedor}, "
                f"lances: {item.qtd_lances}/{MAX_LANCES}, "
                f"status: {estado}"
            )

        return "\n".join(linhas)

    # Processa um lance.
    def _bid(self, partes, addr):
        usuario = self._usuario_logado(addr)

        if not usuario:
            return "Erro: faça login antes de dar lance.", [], []

        if len(partes) != 3:
            return "Uso correto: bid <id_item> <valor>", [], []

        item_atual = self._item_atual()

        if item_atual is None:
            return "Erro: todos os itens já foram encerrados.", [], []

        item_id = partes[1]
        valor_texto = partes[2].replace(",", ".")

        try:
            valor = float(valor_texto)
        except ValueError:
            return "Erro: o valor do lance deve ser numérico.", [], []

        if item_id not in self.itens:
            return "Erro: item inexistente.", [], []

        item = self.itens[item_id]

        if item.encerrado:
            return "Erro: este item já foi encerrado.", [], []

        if item.item_id != item_atual.item_id:
            return (
                f"Erro: este item ainda não está em leilão. "
                f"Item atual: {item_atual.item_id} - {item_atual.nome}.",
                [],
                []
            )

        if item.tempo_expirado():
            msg, arquivo, msg_proximo = self._encerrar_item_locked(item)
            broadcasts = []

            if msg:
                broadcasts.append(msg)

            if msg_proximo:
                broadcasts.append(msg_proximo)

            arquivos = [arquivo] if arquivo else []
            return "Erro: este item já foi encerrado.", broadcasts, arquivos

        if valor <= item.maior_lance:
            return "Erro: o lance precisa ser maior que o lance atual.", [], []

        item.maior_lance = valor
        item.vencedor = usuario
        item.vencedor_addr = addr
        item.qtd_lances += 1

        # Aqui o cronômetro é reiniciado de verdade a cada lance válido.
        item.prazo_limite = time.monotonic() + DURACAO_ITEM

        broadcasts = [
            f"Novo lance no item {item.item_id} ({item.nome}): "
            f"{usuario} deu R$ {valor:.2f}. "
            f"Cronômetro reiniciado para {DURACAO_ITEM}s."
        ]

        arquivos = []

        if item.qtd_lances >= MAX_LANCES:
            msg, arquivo, msg_proximo = self._encerrar_item_locked(item)

            if msg:
                broadcasts.append(msg)

            if msg_proximo:
                broadcasts.append(msg_proximo)

            if arquivo:
                arquivos.append(arquivo)

        return "Lance aceito.", broadcasts, arquivos

    # Encerra o item atual e prepara o envio do arquivo ao vencedor.
    def _encerrar_item_locked(self, item):
        if item.encerrado:
            return "", None, None

        item.encerrado = True

        if item.vencedor:
            msg = (
                f"Leilão encerrado para o item {item.item_id} ({item.nome}). "
                f"Vencedor: {item.vencedor} com R$ {item.maior_lance:.2f}."
            )

            arquivo = None

            if not item.arquivo_enviado:
                item.arquivo_enviado = True
                arquivo = (item.vencedor, item.vencedor_addr, item.item_id, item.filename)

            msg_proximo = self._avancar_item_locked()

            return msg, arquivo, msg_proximo

        msg = f"Leilão encerrado para o item {item.item_id} ({item.nome}) sem lances."
        msg_proximo = self._avancar_item_locked()

        return msg, None, msg_proximo

    # Encerra o item atual se passaram 60 segundos desde o último lance.
    def _encerrar_expirados_locked(self):
        broadcasts = []
        arquivos = []

        item = self._item_atual()

        if item is None:
            return broadcasts, arquivos

        # Sem primeiro lance, o cronômetro não começa.
        if item.prazo_limite is None:
            return broadcasts, arquivos

        if item.tempo_expirado():
            msg, arquivo, msg_proximo = self._encerrar_item_locked(item)

            if msg:
                broadcasts.append(msg)

            if msg_proximo:
                broadcasts.append(msg_proximo)

            if arquivo:
                arquivos.append(arquivo)

        return broadcasts, arquivos

    # Usado pelo servidor para verificar o tempo dos itens.
    def close_expired_items(self):
        with self.lock:
            return self._encerrar_expirados_locked()

    # Retorna os endereços dos clientes online.
    def get_online_addresses(self):
        with self.lock:
            return list(self.addr_para_usuario.keys())

    # Remove um cliente que parou de responder.
    def remove_address(self, addr):
        with self.lock:
            nome = self.addr_para_usuario.pop(addr, None)

            if nome:
                self.usuarios.pop(nome, None)
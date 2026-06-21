# Tipos de mensagens usados pela aplicação AuctionCin.

COMMAND = "COMMAND"
RESPONSE = "RESPONSE"
UPDATE = "UPDATE"

FILE_BEGIN = "FILE_BEGIN"
FILE_DATA = "FILE_DATA"
FILE_END = "FILE_END"


# Monta a identificação do arquivo enviado ao cliente vencedor.
def make_file_header(item_id, filename):
    return f"{item_id}|{filename}"


# Separa id do item e nome do arquivo.
def parse_file_header(text):
    parts = text.split("|", 1)

    if len(parts) != 2:
        return None, None

    return parts[0], parts[1]
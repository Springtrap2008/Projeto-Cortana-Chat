import toml
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SECRETS_FILE = os.path.join(BASE, ".streamlit", "secrets.toml")

secrets = toml.load(SECRETS_FILE)
chave = secrets.get("vapid_private_key", "")

print("--- PRIMEIRAS 50 LETRAS DA CHAVE LIDA ---")
print(repr(chave[:50]))  # O repr() mostra espaços e quebras de linha escondidos
print("--- TAMANHO TOTAL ---")
print(len(chave))
# enviar_push.py — script para testar o Web Push lendo as chaves locais
import json, sys, os
import toml
from pywebpush import webpush, WebPushException

# Caminhos
BASE = os.path.dirname(os.path.abspath(__file__))
SECRETS_FILE = os.path.join(BASE, ".streamlit", "secrets.toml")
SUBSCRIPTION_FILE = os.path.join(BASE, "subscription.json")

def enviar_notificacao(titulo, mensagem):
    # 1. Ler a chave VAPID do secrets.toml
    if not os.path.exists(SECRETS_FILE):
        print(f"[ERRO] Arquivo {SECRETS_FILE} não encontrado. Crie o arquivo com sua chave privada.")
        sys.exit(1)
        
    try:
        secrets = toml.load(SECRETS_FILE)
        VAPID_PRIVATE_KEY = secrets.get("vapid_private_key", "")
        VAPID_SUBJECT = secrets.get("vapid_subject", "mailto:seu-email@exemplo.com")
    except Exception as e:
        print(f"[ERRO] Falha ao ler secrets.toml: {e}")
        sys.exit(1)

    if not VAPID_PRIVATE_KEY or "COLE_AQUI" in VAPID_PRIVATE_KEY:
        print("[ERRO] A chave vapid_private_key não está configurada corretamente no secrets.toml.")
        sys.exit(1)

    # 2. Ler a inscrição do iPhone
    try:
        with open(SUBSCRIPTION_FILE, "r", encoding="utf-8") as f:
            sub = json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo {SUBSCRIPTION_FILE} não encontrado.")
        print("Instale o PWA no iPhone e copie o JSON.")
        sys.exit(1)

    # 3. Enviar
    try:
        webpush(
            subscription_info=sub,
            data=json.dumps({"title": titulo, "body": mensagem}),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
        )
        print(f"[OK] Notificação enviada: {titulo} — {mensagem}")
    except WebPushException as ex:
        print(f"[ERRO] Falha ao enviar: {ex}")
        if ex.response is not None:
            print(f"  Status: {ex.response.status_code}")
            print(f"  Body: {ex.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    enviar_notificacao("Cortana", "Teste de Web Push com o nome Cortana, Chefe.")
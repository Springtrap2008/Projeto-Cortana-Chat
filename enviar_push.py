# enviar_push.py — script para testar o Web Push lendo a chave de um arquivo PEM
import json, sys, os
from pywebpush import webpush, WebPushException

BASE = os.path.dirname(os.path.abspath(__file__))
SUBSCRIPTION_FILE = os.path.join(BASE, "subscription.json")
VAPID_PRIVATE_KEY_FILE = os.path.join(BASE, "private_key.pem")

# Você pode colocar o seu e-mail aqui
VAPID_SUBJECT = "mailto:seu-email@exemplo.com"

def enviar_notificacao(titulo, mensagem):
    if not os.path.exists(VAPID_PRIVATE_KEY_FILE):
        print(f"[ERRO] Arquivo de chave não encontrado: {VAPID_PRIVATE_KEY_FILE}")
        print("Crie o arquivo private_key.pem e cole a chave privada dentro.")
        sys.exit(1)

    try:
        with open(SUBSCRIPTION_FILE, "r", encoding="utf-8") as f:
            sub = json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo {SUBSCRIPTION_FILE} não encontrado.")
        sys.exit(1)

    try:
        # Passamos o CAMINHO do arquivo em vez do texto da chave
        webpush(
            subscription_info=sub,
            data=json.dumps({"title": titulo, "body": mensagem}),
            vapid_private_key=VAPID_PRIVATE_KEY_FILE, 
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
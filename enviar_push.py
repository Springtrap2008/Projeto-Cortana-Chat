# enviar_push.py — script para testar o Web Push lendo a chave de um arquivo PEM
import json, sys, os
from pywebpush import webpush, WebPushException

BASE = os.path.dirname(os.path.abspath(__file__))
SUBSCRIPTION_FILE = os.path.join(BASE, "subscription.json")
VAPID_PRIVATE_KEY_FILE = os.path.join(BASE, "private_key.pem")

VAPID_SUBJECT = "mailto:seu-email@exemplo.com"

def enviar_notificacao(titulo, mensagem):
    if not os.path.exists(VAPID_PRIVATE_KEY_FILE):
        print(f"[ERRO] Arquivo de chave não encontrado: {VAPID_PRIVATE_KEY_FILE}")
        sys.exit(1)

    try:
        with open(SUBSCRIPTION_FILE, "r", encoding="utf-8") as f:
            sub = json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo {SUBSCRIPTION_FILE} não encontrado.")
        sys.exit(1)

    try:
        # Formato 'aps' que a Apple exige para não ignorar
        payload = {
            "aps": {
                "alert": {
                    "title": titulo,
                    "body": mensagem
                },
                "sound": "default",
                "interruption-level": "time-sensitive" # Fura o modo silencioso
            }
        }

        webpush(
            subscription_info=sub,
            data=json.dumps(payload),
            vapid_private_key=VAPID_PRIVATE_KEY_FILE, 
            vapid_claims={"sub": VAPID_SUBJECT},
            ttl=86400,
            headers={"Urgency": "high"}
        )
        print(f"[OK] Notificação enviada: {titulo}")
    except WebPushException as ex:
        print(f"[ERRO] Falha ao enviar: {ex}")
        if ex.response is not None:
            print(f"  Status: {ex.response.status_code}")
            print(f"  Body: {ex.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    enviar_notificacao("Cortana", "Teste de Web Push com o nome Cortana, Chefe.")
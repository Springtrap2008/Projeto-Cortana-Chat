# enviar_push.py — script para testar o Web Push sem abrir o Streamlit
import json, sys
from pywebpush import webpush, WebPushException

# --- CONFIGURAÇÃO ---
# Para testar rápido, cole os valores aqui direto:
VAPID_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
COLE_AQUI_A_CHAVE_PRIVADA
-----END PRIVATE KEY-----
"""
VAPID_SUBJECT = "mailto:seu-email@exemplo.com"
SUBSCRIPTION_FILE = "subscription.json"


def enviar_notificacao(titulo, mensagem):
    try:
        with open(SUBSCRIPTION_FILE, "r", encoding="utf-8") as f:
            sub = json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo {SUBSCRIPTION_FILE} não encontrado.")
        print("Instale o PWA no iPhone, toque em 'Ativar Notificações' e copie o JSON para subscription.json.")
        sys.exit(1)

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
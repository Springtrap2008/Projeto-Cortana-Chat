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
        sys.exit(1)

    try:
        with open(SUBSCRIPTION_FILE, "r", encoding="utf-8") as f:
            sub = json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo {SUBSCRIPTION_FILE} não encontrado.")
        sys.exit(1)

    try:
        # O SEGREDO PARA O iPHONE EXIBIR:
        # Mandamos um payload com 'title' e 'body' e forçamos a entrega imediata
        webpush(
            subscription_info=sub,
            data=json.dumps({
                "title": titulo,
                "body": mensagem
            }),
            vapid_private_key=VAPID_PRIVATE_KEY_FILE, 
            vapid_claims={"sub": VAPID_SUBJECT},
            ttl=86400, # Tenta entregar por até 24h se estiver offline
            headers={"Urgency": "high"} # Avisa a Apple que é uma notificação prioritária
        )
        print(f"[OK] Notificação enviada: {titulo} — {mensagem}")
        print("\n⚠️ ATENÇÃO: O iOS costuma entregar Web Push de forma SILENCIOSA.")
        print("Dê uma olhada na Central de Notificações (arraste de cima para baixo) e veja se ela está lá.")
    except WebPushException as ex:
        print(f"[ERRO] Falha ao enviar: {ex}")
        if ex.response is not None:
            print(f"  Status: {ex.response.status_code}")
            print(f"  Body: {ex.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    enviar_notificacao("Cortana", "Teste de Web Push com o nome Cortana, Chefe.")
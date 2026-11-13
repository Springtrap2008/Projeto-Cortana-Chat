import os
from py_vapid import Vapid
from cryptography.hazmat.primitives import serialization
import base64

v = Vapid()
v.generate_keys()

# 1. Salva a chave privada direto no arquivo .pem
with open("private_key.pem", "wb") as f:
    f.write(v.private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# 2. Gera a chave pública em base64url
pub_bytes = v.public_key.public_bytes(
    encoding=serialization.Encoding.X962,
    format=serialization.PublicFormat.UncompressedPoint
)
pub_b64 = base64.urlsafe_b64encode(pub_bytes).decode().rstrip('=')

print("✅ Arquivo private_key.pem criado com sucesso!")
print("\n⚠️ COPIE A CHAVE PÚBLICA ABAIXO E COLE NO index.html:")
print(pub_b64)
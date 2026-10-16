"""Hash de contraseñas y tokens HMAC simples para sesiones de API."""
import os, hmac, hashlib, base64, json, time
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET = os.getenv("TOKEN_SECRET", "CAMBIAR_POR_UN_SECRETO_LARGO_ALEATORIO")
if len(SECRET) < 32 or SECRET.startswith("CAMBIAR_"):
    # Permite iniciar en desarrollo, pero evita usar el valor por defecto en producción.
    if os.getenv("APP_ENV", "development").lower() == "production":
        raise RuntimeError("Configure TOKEN_SECRET con al menos 32 caracteres aleatorios.")

bearer = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return base64.b64encode(salt + digest).decode()

def verify_password(password: str, encoded: str) -> bool:
    try:
        raw = base64.b64decode(encoded.encode())
        salt, expected = raw[:16], raw[16:]
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False

def issue_token(subject: str, role: str, user_id: int | None = None, minutes: int = 45) -> str:
    payload = {"sub": subject, "role": role, "uid": user_id, "exp": int(time.time()) + minutes * 60}
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    sig = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).digest()
    signature = base64.urlsafe_b64encode(sig).decode().rstrip("=")
    return f"{body}.{signature}"

def decode_token(token: str) -> dict:
    try:
        body, signature = token.split(".", 1)
        expected = base64.urlsafe_b64encode(hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).digest()).decode().rstrip("=")
        if not hmac.compare_digest(signature, expected): raise ValueError()
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if int(payload["exp"]) < int(time.time()): raise ValueError()
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada.")

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if not credentials: raise HTTPException(status_code=401, detail="Debe iniciar sesión.")
    return decode_token(credentials.credentials)

def require_staff(user: dict = Depends(current_user)):
    if user.get("role") != "funcionario": raise HTTPException(status_code=403, detail="Acceso exclusivo para funcionarios autorizados.")
    return user

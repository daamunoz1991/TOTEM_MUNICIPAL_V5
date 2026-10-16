"""Autenticación LDAP opcional para Active Directory. Requiere LDAPS/puerto 636."""
import os

def autenticar_funcionario(usuario: str, password: str) -> bool:
    host = os.getenv("LDAP_HOST", "").strip()
    base_dn = os.getenv("LDAP_BASE_DN", "").strip()
    domain = os.getenv("LDAP_DOMAIN", "").strip()
    if not host or not base_dn or not domain:
        raise RuntimeError("Configure LDAP_HOST, LDAP_BASE_DN y LDAP_DOMAIN en el entorno del servidor.")
    if not password or not usuario:
        return False
    try:
        from ldap3 import Server, Connection, Tls, SIMPLE
        import ssl
        tls = Tls(validate=ssl.CERT_REQUIRED)
        server = Server(host, port=636, use_ssl=True, tls=tls, connect_timeout=5)
        # El formato de usuario debe adecuarse a la política del dominio municipal.
        principal = usuario if "@" in usuario else f"{usuario}@{domain}"
        conn = Connection(server, user=principal, password=password, authentication=SIMPLE, auto_bind=True, receive_timeout=5)
        conn.unbind()
        return True
    except Exception:
        return False

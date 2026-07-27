import base64, hashlib, hmac, json, time

class BadSignature(ValueError): pass
class SignatureExpired(BadSignature): pass

def _b64e(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")
def _b64d(value):
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as exc:
        raise BadSignature("malformed token") from exc

class URLSafeTimedSerializer:
    def __init__(self, secret_key, salt="featurelift", *, now=None):
        self.secret_key = str(secret_key).encode()
        self.salt = str(salt).encode()
        self._now = now or time.time
    def _sign(self, body):
        key = hmac.new(self.secret_key, self.salt, hashlib.sha256).digest()
        return _b64e(hmac.new(key, body.encode(), hashlib.sha256).digest())
    def dumps(self, obj):
        payload = _b64e(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
        body = f"{payload}.{int(self._now())}"
        return f"{body}.{self._sign(body)}"
    def loads(self, token, max_age=None, now=None):
        try:
            payload, timestamp, signature = str(token).rsplit(".", 2)
            created = int(timestamp)
        except Exception as exc:
            raise BadSignature("malformed token") from exc
        body = f"{payload}.{timestamp}"
        if not hmac.compare_digest(signature, self._sign(body)):
            raise BadSignature("signature does not match")
        current = int(self._now() if now is None else now)
        if max_age is not None and current - created > max_age:
            raise SignatureExpired("signature age exceeded")
        try:
            return json.loads(_b64d(payload).decode("utf-8"))
        except Exception as exc:
            if isinstance(exc, BadSignature): raise
            raise BadSignature("invalid payload") from exc

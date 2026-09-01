from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from urllib.parse import parse_qs, urlparse

from featurelifted import (
    AuthorizationCodeGrant,
    AuthorizationServer,
    ClientMixin,
    OAuth2Request,
)


class Payload:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.datalist = {key: [value] for key, value in data.items()}

    @property
    def client_id(self):
        return self.data.get("client_id")

    @property
    def response_type(self):
        return self.data.get("response_type")

    @property
    def grant_type(self):
        return self.data.get("grant_type")

    @property
    def redirect_uri(self):
        return self.data.get("redirect_uri")

    @property
    def scope(self):
        return self.data.get("scope")

    @property
    def state(self):
        return self.data.get("state")


class Client(ClientMixin):
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_client_id(self):
        return self.client_id

    def get_default_redirect_uri(self):
        return self.redirect_uri

    def get_allowed_scope(self, scope):
        return scope or ""

    def check_redirect_uri(self, redirect_uri):
        return redirect_uri == self.redirect_uri

    def check_client_secret(self, client_secret):
        return client_secret == self.client_secret

    def check_endpoint_auth_method(self, method, endpoint):
        return method in ("client_secret_post", "client_secret_basic")

    def check_response_type(self, response_type):
        return response_type == "code"

    def check_grant_type(self, grant_type):
        return grant_type in ("authorization_code", "refresh_token")


class Code:
    def __init__(self, code, client_id, redirect_uri, user, scope) -> None:
        self.code = code
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.user = user
        self.scope = scope

    def get_redirect_uri(self):
        return self.redirect_uri

    def get_scope(self):
        return self.scope


class MemoryServer(AuthorizationServer):
    def __init__(self) -> None:
        super().__init__(scopes_supported=["profile"])
        self.clients = {"cid": Client("cid", "secret", "https://client.test/cb")}
        self.codes = {}
        self.tokens = []
        self.register_token_generator(
            "default",
            lambda **kwargs: {"token_type": "Bearer", "access_token": "tok", "expires_in": 3600},
        )

    def query_client(self, client_id):
        return self.clients.get(client_id)

    def save_token(self, token, request):
        self.tokens.append(token)

    def send_signal(self, name, *args, **kwargs):
        return None

    def create_oauth2_request(self, request):
        if isinstance(request, OAuth2Request):
            return request
        method, uri, body, headers = request
        req = OAuth2Request(method, uri, body=body, headers=headers or {})
        data = {key: value[0] for key, value in parse_qs(urlparse(uri).query).items()}
        if isinstance(body, dict):
            data.update(body)
        req.payload = Payload(data)
        return req

    def handle_response(self, status, body, headers):
        return status, body, headers


class CodeGrant(AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = ["client_secret_post"]

    def save_authorization_code(self, code, request):
        item = Code(
            code,
            request.client.get_client_id(),
            request.payload.redirect_uri,
            request.user,
            request.payload.scope,
        )
        self.server.codes[code] = item
        return item

    def query_authorization_code(self, code, client):
        item = self.server.codes.get(code)
        if item and item.client_id == client.get_client_id():
            return item
        return None

    def delete_authorization_code(self, authorization_code):
        self.server.codes.pop(authorization_code.code, None)

    def authenticate_user(self, authorization_code):
        return authorization_code.user


def build_server():
    server = MemoryServer()
    server.register_grant(CodeGrant)
    return server


def test_authorization_code_redirect() -> None:
    server = build_server()
    uri = (
        "https://auth.test/authorize?response_type=code&client_id=cid"
        "&redirect_uri=https://client.test/cb&state=xyz&scope=profile"
    )
    status, _body, headers = server.create_authorization_response(
        request=("GET", uri, None, {}),
        grant_user={"id": 1},
    )
    assert status == 302
    location = dict(headers)["Location"]
    query = parse_qs(urlparse(location).query)
    assert query["state"] == ["xyz"]
    assert query["code"][0]


def test_token_response_issues_access_token() -> None:
    server = build_server()
    uri = (
        "https://auth.test/authorize?response_type=code&client_id=cid"
        "&redirect_uri=https://client.test/cb&state=xyz&scope=profile"
    )
    _status, _body, headers = server.create_authorization_response(
        request=("GET", uri, None, {}),
        grant_user={"id": 1},
    )
    code = parse_qs(urlparse(dict(headers)["Location"]).query)["code"][0]
    status, body, _headers = server.create_token_response(
        request=(
            "POST",
            "https://auth.test/token",
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "https://client.test/cb",
                "client_id": "cid",
                "client_secret": "secret",
            },
            {},
        )
    )
    assert status == 200
    assert body["access_token"] == "tok"
    assert body["token_type"] == "Bearer"

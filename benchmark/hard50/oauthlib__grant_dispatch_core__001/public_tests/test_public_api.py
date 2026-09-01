from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from featurelifted import RequestValidator, WebApplicationServer


class StubValidator(RequestValidator):
    def __init__(self) -> None:
        self.saved_codes: dict[str, dict] = {}
        self.saved_tokens: list[dict] = []

    def authenticate_client(self, request):
        request.client = type("Client", (), {"client_id": "cid"})()
        request.client_id = "cid"
        return True

    def authenticate_client_id(self, client_id, request):
        request.client = type("Client", (), {"client_id": client_id})()
        return client_id == "cid"

    def validate_client_id(self, client_id, request):
        return client_id == "cid"

    def validate_redirect_uri(self, client_id, redirect_uri, request):
        return redirect_uri == "https://example.com/cb"

    def get_default_redirect_uri(self, client_id, request):
        return "https://example.com/cb"

    def validate_scopes(self, client_id, scopes, client, request):
        return True

    def get_default_scopes(self, client_id, request):
        return ["profile"]

    def validate_response_type(self, client_id, response_type, client, request):
        return response_type == "code"

    def validate_grant_type(self, client_id, grant_type, client, request):
        return grant_type == "authorization_code"

    def save_authorization_code(self, client_id, code, request):
        self.saved_codes[code["code"]] = {
            "client_id": client_id,
            "redirect_uri": request.redirect_uri,
            "scopes": list(request.scopes or []),
        }

    def validate_code(self, client_id, code, client, request):
        saved = self.saved_codes.get(code)
        if not saved or saved["client_id"] != client_id:
            return False
        request.scopes = saved["scopes"]
        request.redirect_uri = saved["redirect_uri"]
        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request):
        saved = self.saved_codes.get(code)
        return bool(saved) and saved["redirect_uri"] == redirect_uri

    def save_bearer_token(self, token, request):
        self.saved_tokens.append(token)
        return token

    def invalidate_authorization_code(self, client_id, code, request):
        self.saved_codes.pop(code, None)


def test_authorization_code_grant_returns_code() -> None:
    server = WebApplicationServer(StubValidator())
    headers, _body, status = server.create_authorization_response(
        uri="https://example.com/authorize?response_type=code&client_id=cid&redirect_uri=https://example.com/cb",
        http_method="GET",
    )
    assert status == 302
    location = headers["Location"]
    code = parse_qs(urlparse(location).query)["code"][0]
    assert code


def test_token_exchange_returns_access_token() -> None:
    validator = StubValidator()
    server = WebApplicationServer(validator)
    headers, _body, _status = server.create_authorization_response(
        uri="https://example.com/authorize?response_type=code&client_id=cid&redirect_uri=https://example.com/cb",
        http_method="GET",
    )
    code = parse_qs(urlparse(headers["Location"]).query)["code"][0]
    _headers, body, status = server.create_token_response(
        uri="https://example.com/token",
        http_method="POST",
        body=(
            "grant_type=authorization_code&code="
            + code
            + "&redirect_uri=https://example.com/cb&client_id=cid"
        ),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert status == 200
    assert "access_token" in body


def test_unsupported_grant_type_is_rejected() -> None:
    server = WebApplicationServer(StubValidator())
    _headers, body, status = server.create_token_response(
        uri="https://example.com/token",
        http_method="POST",
        body="grant_type=password&username=u&password=p&client_id=cid",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert status == 400
    assert "unsupported_grant_type" in body

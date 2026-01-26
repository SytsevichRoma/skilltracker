import hashlib
import json
from typing import Any, Dict, Iterable, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from flask import current_app


REQUEST_SIGNATURE_ORDER: Iterable[str] = (
    "amount",
    "currency",
    "merchant_id",
    "order_desc",
    "order_id",
    "response_url",
    "sender_email",
    "server_callback_url",
)


def _signature_string(
    params: Dict[str, Any],
    secret_key: str,
    field_order: Optional[Iterable[str]] = None,
) -> str:
    pieces = []
    keys = list(field_order) if field_order else sorted(params.keys())
    for key in keys:
        if key in ("signature", "response_signature_string"):
            continue
        value = params.get(key)
        if value is None or value == "":
            continue
        pieces.append(str(value))
    return "|".join([secret_key] + pieces)


def generate_signature(
    params: Dict[str, Any],
    secret_key: str,
    field_order: Optional[Iterable[str]] = None,
) -> str:
    raw = _signature_string(params, secret_key, field_order=field_order)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def verify_signature(params: Dict[str, Any], secret_key: str) -> bool:
    signature = params.get("signature")
    if not signature:
        return False
    response_signature_string = params.get("response_signature_string")
    if response_signature_string:
        expected = hashlib.sha1(response_signature_string.encode("utf-8")).hexdigest()
    else:
        expected = generate_signature(params, secret_key)
    return signature.lower() == expected.lower()


def create_checkout_url(payload: Dict[str, Any]) -> str:
    api_url = current_app.config.get("FONDY_API_URL")
    secret_key = current_app.config.get("FONDY_SECRET_KEY")
    if not api_url or not secret_key:
        raise RuntimeError("Fondy configuration is missing")
    secret_key = str(secret_key).strip()

    payload = dict(payload)
    payload["signature"] = generate_signature(payload, secret_key, field_order=REQUEST_SIGNATURE_ORDER)
    request_body = json.dumps({"request": payload}).encode("utf-8")

    req = Request(
        api_url,
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Fondy request failed: {exc}") from exc

    response = data.get("response", {})
    if "signature" in response and not verify_signature(response, secret_key):
        raise RuntimeError("Fondy response signature invalid")

    if response.get("response_status") != "success":
        message = response.get("error_message") or response.get("response_description") or "Fondy error"
        raise RuntimeError(message)

    checkout_url = response.get("checkout_url")
    if not checkout_url:
        raise RuntimeError("Fondy response missing checkout_url")
    return checkout_url

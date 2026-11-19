import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import UUID

from django.conf import settings


class Unavailable(Exception):
    pass


def call(path, payload=None):
    if not settings.YOTI_KEY or not settings.YOTI_SDK:
        raise Unavailable
    request = Request("https://age.yoti.com/api/v1/sessions" + path,
                      data=json.dumps(payload).encode() if payload else None,
                      headers={"Authorization": "Bearer " + settings.YOTI_KEY,
                               "Yoti-SDK-Id": settings.YOTI_SDK, "Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=8) as response:
            result = json.load(response)
        if not isinstance(result, dict):
            raise ValueError
        return result
    except (URLError, OSError, ValueError) as exc:
        raise Unavailable from exc


def start(reference):
    result = call("", {"type": "OVER", "ttl": 600, "reference_id": reference,
                       "digital_id": {"allowed": False}, "credit_card": {"allowed": False},
                       "mobile": {"allowed": False},
                       "age_estimation": {"allowed": True, "threshold": 25, "level": "PASSIVE", "retry_limit": 2},
                       "doc_scan": {"allowed": True, "threshold": 18, "level": "PASSIVE", "authenticity": "AUTO"},
                       "callback": {"auto": True, "url": settings.ORIGIN + "/majorite/retour/"},
                       "cancel_url": settings.ORIGIN + "/compte/", "synchronous_checks": True})
    try:
        session = str(UUID(result["id"]))
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        raise Unavailable from exc
    return session, "https://age.yoti.com/?" + urlencode({"sessionId": session, "sdkId": settings.YOTI_SDK})


def passed(profile):
    result = call("/" + profile.age_session + "/result")
    method = result.get("method")
    threshold = {"AGE_ESTIMATION": 25, "DOC_SCAN": 18}.get(method) if isinstance(method, str) else None
    config = result.get(method.lower()) if threshold else None
    return (isinstance(config, dict) and config.get("threshold") == threshold
            and config.get("level") == "PASSIVE" and config.get("allowed") is True
            and result.get("status") == "COMPLETE" and result.get("type") == "OVER"
            and result.get("id") == profile.age_session and result.get("reference_id") == profile.age_ref
            and result.get("sdk_id") == settings.YOTI_SDK and type(result.get("age")) is int
            and result["age"] >= threshold)

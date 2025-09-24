import time
import requests
from django.conf import settings
from django.core.cache import cache


ESKIZ_BASE = getattr(settings, 'ESKIZ_BASE', 'https://notify.eskiz.uz')
ESKIZ_EMAIL = getattr(settings, 'ESKIZ_EMAIL', '')
ESKIZ_PASSWORD = getattr(settings, 'ESKIZ_PASSWORD', '')
ESKIZ_FROM = getattr(settings, 'ESKIZ_FROM', '4546')  # short code or sender name


def _get_eskiz_token(force=False) -> str:
    key = 'eskiz_token'
    if not force:
        tok = cache.get(key)
        if tok:
            return tok
    # If no credentials configured, raise to trigger fallback
    if not ESKIZ_EMAIL or not ESKIZ_PASSWORD:
        raise RuntimeError('Eskiz credentials missing')
    resp = requests.post(f"{ESKIZ_BASE}/api/auth/login", data={'email': ESKIZ_EMAIL, 'password': ESKIZ_PASSWORD}, timeout=10)
    resp.raise_for_status()
    token = resp.json().get('data', {}).get('token') or resp.json().get('data')
    if not token:
        raise RuntimeError('Eskiz: token missing in response')
    # cache for 9 hours (Eskiz tokens usually 10h)
    cache.set(key, token, 9 * 3600)
    return token


def send_otp_via_eskiz(phone: str, code: str) -> bool:
    # Local/dev fallback: if no creds or DEBUG, print to console and succeed
    if settings.DEBUG and (not ESKIZ_EMAIL or not ESKIZ_PASSWORD):
        print(f"[DEV] OTP to {phone}: {code}")
        return True

    try:
        token = _get_eskiz_token()
        headers = {'Authorization': f'Bearer {token}'}
        payload = {
            'mobile_phone': phone,
            'message': f"Fikrly tasdiqlash kodi: {code}",
            'from': ESKIZ_FROM,
            'callback_url': '',
        }
        resp = requests.post(f"{ESKIZ_BASE}/api/message/sms/send", headers=headers, data=payload, timeout=10)
        if resp.status_code == 401:
            # token expired; refresh once
            token = _get_eskiz_token(force=True)
            headers['Authorization'] = f'Bearer {token}'
            resp = requests.post(f"{ESKIZ_BASE}/api/message/sms/send", headers=headers, data=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        if settings.DEBUG:
            print(f"[DEV] Eskiz send failed: {e}. Fallback OTP to {phone}: {code}")
            return True
        return False

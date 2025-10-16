import os
import requests
import logging

PIXUP_API_KEY = os.getenv('PIXUP_API_KEY')
BASE_URL = 'https://api.pixup.com'  # placeholder; adapt to real PIXUP URL from docs

logger = logging.getLogger(__name__)

def create_charge(amount, description=None):
    """Create a PIX charge (cobrança) via PIXUP and return payment payload (qr code or code)
    Note: adapt endpoints and payload per PIXUP docs."""
    url = f"{BASE_URL}/charges"
    headers = {'Authorization': f'Bearer {PIXUP_API_KEY}', 'Content-Type': 'application/json'}
    payload = {
        'amount': str(amount),
        'description': description or 'Deposit',
    }
    resp = requests.post(url, json=payload, headers=headers)
    logger.info('create_charge status=%s', resp.status_code)
    resp.raise_for_status()
    return resp.json()

def get_charge_status(charge_id):
    url = f"{BASE_URL}/charges/{charge_id}"
    headers = {'Authorization': f'Bearer {PIXUP_API_KEY}'}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def request_withdrawal(amount, pix_key, recipient_name):
    """Request a PIX payout/repasse via PIXUP."""
    url = f"{BASE_URL}/payouts"
    headers = {'Authorization': f'Bearer {PIXUP_API_KEY}', 'Content-Type': 'application/json'}
    payload = {
        'amount': str(amount),
        'pix_key': pix_key,
        'recipient_name': recipient_name,
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

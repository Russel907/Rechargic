import requests
import os
import logging

logger = logging.getLogger(__name__)

INSPAY_BASE_URL = "https://inspay.in"
INSPAY_USERNAME = os.getenv('INSPAY_USERNAME')
INSPAY_TOKEN = os.getenv('INSPAY_TOKEN')


def initiate_recharge(opcode, number, amount, order_id, value1='', value2='', value3='', value4=''):
    params = {
        'username': INSPAY_USERNAME,
        'token': INSPAY_TOKEN,
        'opcode': str(opcode).strip(),
        'number': str(number).strip(),
        'amount': amount,
        'orderid': str(order_id).strip(),
        'value1': str(value1).strip(),
        'value2': str(value2).strip(),
        'value3': str(value3).strip(),
        'value4': str(value4).strip(),
        'format': 'json'
    }

    try:
        response = requests.get(
            f"{INSPAY_BASE_URL}/v3/recharge/api",
            params=params,
            timeout=30
        )
        print("INSPAY RESPONSE =", response.text)
        logger.info(f"Inspay recharge response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except requests.RequestException as e:
        logger.exception(f"Inspay recharge error: {str(e)}")
        return False, {"error": str(e)}


def check_recharge_status(order_id):
    params = {
        'username': INSPAY_USERNAME,
        'token': INSPAY_TOKEN,
        'orderid': str(order_id).strip(),
        'format': 'json'
    }

    try:
        response = requests.get(
            f"{INSPAY_BASE_URL}/v3/recharge/status",  # fixed URL
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except requests.RequestException as e:
        logger.exception(f"Inspay status check error: {str(e)}")
        return False, {"error": str(e)}


def check_inspay_balance():
    params = {
        'username': INSPAY_USERNAME,
        'token': INSPAY_TOKEN,
        'format': 'json'
    }

    try:
        response = requests.get(
            f"{INSPAY_BASE_URL}/v3/recharge/balance",  # fixed URL
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except requests.RequestException as e:
        logger.exception(f"Inspay balance check error: {str(e)}")
        return False, {"error": str(e)}


def fetch_electricity_bill(opcode, consumer_number, mobile, order_id):
    """
    Fetch electricity bill details before payment.
    Uses same recharge API — Inspay handles fetch internally for supported billers.
    """
    params = {
        'username': INSPAY_USERNAME,
        'token': INSPAY_TOKEN,
        'opcode': str(opcode).strip(),
        'number': str(consumer_number).strip(),
        'amount': 0,
        'orderid': str(order_id).strip(),
        'value1': str(mobile).strip(),
        'format': 'json'
    }

    try:
        response = requests.get(
            f"{INSPAY_BASE_URL}/v3/recharge/api",
            params=params,
            timeout=30
        )
        logger.info(f"Inspay electricity fetch response: {response.status_code} - {response.text}")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except requests.RequestException as e:
        logger.exception(f"Inspay electricity fetch error: {str(e)}")
        return False, {"error": str(e)}
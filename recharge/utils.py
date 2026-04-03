import requests
import os
import logging

logger = logging.getLogger(__name__)

INSPAY_BASE_URL = "http://www.connect.inspay.in"
INSPAY_USERNAME = os.getenv('INSPAY_USERNAME')
INSPAY_TOKEN = os.getenv('INSPAY_TOKEN')


def initiate_recharge(opcode, number, amount, order_id, value1='', value2='', value3='', value4=''):
    """
    Call InsPay API to initiate a recharge
    Returns the response dict from InsPay
    """
    params = {
        'username': INSPAY_USERNAME,
        'token': INSPAY_TOKEN,
        'opcode': opcode,
        'number': number,
        'amount': amount,
        'orderid': order_id,
        'value1': value1,
        'value2': value2,
        'value3': value3,
        'value4': value4,
        'format': 'json'
    }

    try:
        response = requests.get(
            f"{INSPAY_BASE_URL}/v3/recharge/api",
            params=params,
            timeout=30
        )
        logger.info(f"InsPay recharge response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}"}

    except requests.RequestException as e:
        logger.exception(f"InsPay recharge error: {str(e)}")
        return False, {"error": str(e)}


def check_recharge_status(order_id):
    """
    Check status of a recharge transaction
    """
    params = {
        'username': INSPAY_USERNAME,
        'token': INSPAY_TOKEN,
        'orderid': order_id,
        'format': 'json'
    }

    try:
        response = requests.get(
            f"https://www.connect.inspay.in/v3/recharge/status",
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}"}

    except requests.RequestException as e:
        logger.exception(f"InsPay status check error: {str(e)}")
        return False, {"error": str(e)}


def check_inspay_balance():
    """
    Check InsPay account balance
    """
    params = {
        'username': INSPAY_USERNAME,
        'token': INSPAY_TOKEN,
        'format': 'json'
    }

    try:
        response = requests.get(
            f"https://www.connect.inspay.in/v3/recharge/balance",
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}"}

    except requests.RequestException as e:
        logger.exception(f"InsPay balance check error: {str(e)}")
        return False, {"error": str(e)}
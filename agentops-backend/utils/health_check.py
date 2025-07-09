# utils/health_check.py

import requests
import logging

logger = logging.getLogger("agentops.health")

def ping_health(endpoint: str) -> str:
    """
    Pings the agent's health endpoint and returns its health status.

    Returns:
        - "OK" if status code is 200
        - "ERROR_<code>" for other HTTP errors
        - "UNREACHABLE" for connection/timeout issues
    """
    try:
        response = requests.get(endpoint, timeout=5)
        if response.status_code == 200:
            logger.debug(f"Health check OK for {endpoint}")
            return "OK"
        else:
            logger.warning(f"Health check ERROR for {endpoint}: HTTP {response.status_code}")
            return f"ERROR_{response.status_code}"
    except requests.exceptions.Timeout:
        logger.error(f"Health check TIMEOUT for {endpoint}")
        return "UNREACHABLE"
    except requests.exceptions.RequestException as e:
        logger.error(f"Health check FAILED for {endpoint}: {e}")
        return "UNREACHABLE"

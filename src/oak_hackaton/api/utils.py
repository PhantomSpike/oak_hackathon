import requests
from typing import Any
from oak_hackaton.settings import get_settings

settings = get_settings()

BASE_URL = settings.OAK_API_URL
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {settings.OAK_API_KEY}"
}

def api_get(endpoint: str) -> Any:
    """
    Make a GET request to the API and return the response as JSON.
    Redirect to an HTTP Cat image if there's an HTTP error.

    Args:
        endpoint (str): The API endpoint to call.

    Returns:
        dict: The JSON response.
    """

    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS)
    except requests.HTTPError as e:
        return print(f"HTTP error {e}")
    return response.json()

def get_units(key_stage: str) -> Any:
    endpoint = f"/key-stages/{key_stage}/subject/maths/units"
    response = api_get(endpoint)
    unit_list = [unit["unitTitle"] for unit in response]
    return unit_list

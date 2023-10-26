import requests
import json
import os
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IGAPIData:
    def __init__(self, api_key, username, password):
        self.api_key = api_key
        self.username = username
        self.password = password
        self.base_url = "https://demo-api.ig.com/gateway/deal"
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json; charset=utf-8",
            "X-IG-API-KEY": self.api_key,
            "Version": "2"
        }
        self._login()

    def _login(self):
        """Inicia sesión y actualiza las cabeceras con los tokens de seguridad."""
        url = f"{self.base_url}/session"
        data = json.dumps({"identifier": self.username, "password": self.password})
        try:
            response = requests.post(url, headers=self.headers, data=data)
            response.raise_for_status()
            self.headers["CST"] = response.headers["CST"]
            self.headers["X-SECURITY-TOKEN"] = response.headers["X-SECURITY-TOKEN"]
        except requests.RequestException as e:
            logger.error(f"Error al iniciar sesión: {e}")
            return None

    def get_accounts(self):
        """Obtiene la lista de cuentas."""
        url = f"{self.base_url}/accounts"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al obtener cuentas: {e}")
            return None

    def get_markets(self, epic):
        """Obtiene información del mercado para un EPIC específico."""
        url = f"{self.base_url}/markets/{epic}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al obtener datos del mercado: {e}")
            return None

    def get_price(self, epic):
        """Obtiene el precio de compra y venta para un EPIC específico."""
        market_data = self.get_markets(epic)
        if market_data and 'snapshot' in market_data:
            bid = market_data['snapshot']['bid']
            offer = market_data['snapshot']['offer']
            return bid, offer
        return None, None
    
    def get_historical_prices(self, epic, limit=100):
        """Obtiene los precios históricos para un EPIC específico."""
        url = f"{self.base_url}/prices/{epic}?limit={limit}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Suponiendo que la API devuelve los precios en una lista llamada 'prices'
            prices = [item['closePrice']['bid'] for item in data['prices']]
            return prices
        except requests.RequestException as e:
            logger.error(f"Error al obtener precios históricos: {e}")
            return []    

if __name__ == "__main__":
    api_key = os.environ.get("YOUR_API_KEY")
    username = os.environ.get("YOUR_USERNAME")
    password = os.environ.get("YOUR_PASSWORD")
    
    if not all([api_key, username, password]):
        logger.error("Por favor, establece las variables de entorno para API_KEY, USERNAME y PASSWORD.")
        exit()

    ig_data = IGAPIData(api_key, username, password)
    accounts = ig_data.get_accounts()
    logger.info(accounts)
    epic = "CS.D.EURUSD.MINI.IP"  # Reemplaza con el EPIC real que deseas rastrear
    bid, offer = ig_data.get_price(epic)
    if bid and offer:
        logger.info(f"Bid: {bid}, Offer: {offer}")
    else:
        logger.error(f"No se pudo obtener el precio para el EPIC: {epic}")

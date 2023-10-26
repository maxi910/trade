import logging
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datos import IGAPIData

logger = logging.getLogger(__name__)

class SupportResistanceStrategy:
    def __init__(self, ig_data):
        self.ig_data = ig_data

    def calculate_macd(self, prices, short_window=12, long_window=26, signal_window=9):
        """Calcula el MACD y la línea de señal."""
        prices_series = pd.Series(prices)
        short_ema = prices_series.ewm(span=short_window, adjust=False).mean()
        long_ema = prices_series.ewm(span=long_window, adjust=False).mean()
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
        return macd_line, signal_line

    def trade_strategy(self, epic, supports, resistances):
        """Estrategia de trading basada en niveles de soporte, resistencia y MACD."""
        market_data = self.ig_data.get_markets(epic)
        if not market_data:
            logger.error(f"No se pudo obtener datos del mercado para el EPIC: {epic}")
            return "HOLD"

        last_price = market_data['snapshot']['bid']
        prices = self.ig_data.get_historical_prices(epic)
        macd_line, signal_line = self.calculate_macd(prices)

        # Comprobar cruces MACD
        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
            return "BUY"
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
            return "SELL"

        # Comprobar niveles de soporte y resistencia
        for support in supports:
            if last_price > support:
                return "BUY"
        for resistance in resistances:
            if last_price < resistance:
                return "SELL"

        return "HOLD"  # Mantener la posición actual
        
    def plot_support_resistance(self, prices, supports, resistances):
        """Visualiza los niveles de soporte y resistencia en un gráfico."""
        plt.figure(figsize=(10, 6))
        plt.plot(prices, label='Precio', color='blue')
        
        # Dibujar múltiples niveles de soporte
        for support in supports:
            plt.axhline(y=support, color='green', linestyle='--', label=f'Soporte {support}')
        
        # Dibujar múltiples niveles de resistencia
        for resistance in resistances:
            plt.axhline(y=resistance, color='red', linestyle='--', label=f'Resistencia {resistance}')
        
        plt.title('Niveles de Soporte y Resistencia')
        plt.xlabel('Tiempo')
        plt.ylabel('Precio')
        plt.legend()
        plt.grid(True)
        plt.show()

    def identify_trend(self, prices):
        """Identifica si la tendencia es alcista o bajista."""
        # Calcula la pendiente entre el primer y el último precio
        slope = (prices[-1] - prices[0]) / len(prices)
        if slope > 0:
            return "alcista"
        elif slope < 0:
            return "bajista"
        else:
            return "lateral"
        
    def place_orders(self, prices, trend):
        """Coloca órdenes basadas en el canal identificado."""
        if trend == "alcista":
            # Coloca órdenes de compra en la línea de tendencia inferior
            # y órdenes de venta en la línea de tendencia superior
            # ... [código para colocar órdenes]
            pass
        elif trend == "bajista":
            # Coloca órdenes de venta en la línea de tendencia superior
            # y órdenes de compra en la línea de tendencia inferior
            # ... [código para colocar órdenes]
            pass
        else:
            # No colocar órdenes si la tendencia es lateral
            pass

if __name__ == "__main__":
    api_key = os.environ.get("YOUR_API_KEY")
    username = os.environ.get("YOUR_USERNAME")
    password = os.environ.get("YOUR_PASSWORD")

    ig_data = IGAPIData(api_key, username, password)
    strategy = SupportResistanceStrategy(ig_data)

    epic = "CS.D.EURUSD.MINI.IP"  # Reemplaza con el EPIC real que deseas rastrear
    support_level = 1.10
    resistance_level = 1.20

    # Suponiendo que tienes una lista de precios históricos
    prices = ig_data.get_historical_prices(epic)
    if not prices:
        logger.error(f"No se pudo obtener precios históricos para el EPIC: {epic}")
        exit()

    # Múltiples niveles de soporte y resistencia
    support_levels = [1.08, 1.09]
    resistance_levels = [1.12, 1.13]

    action = strategy.trade_strategy(epic, support_levels, resistance_levels)
    logger.info(f"Acción recomendada: {action}")

    # Consultar el contador
    counts = strategy.action_counter.get_counts()
    logger.info(f"Contador de acciones: {counts}")

    # Decidir si realizar una operación basada en el contador
    if counts["BUY"] > 5:  # Ejemplo: si se ha recomendado comprar más de 5 veces
        logger.info("Realizar operación de compra")
    elif counts["SELL"] > 5:  # Ejemplo: si se ha recomendado vender más de 5 veces
        logger.info("Realizar operación de venta")
    else:
        logger.info("Mantener posición actual")

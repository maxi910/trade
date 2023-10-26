import numpy as np
import pandas as pd
from datos import IGAPIData
import matplotlib.pyplot as plt
import pandas as pd
import pandas_ta as ta


class Indicators:
    def __init__(self, ig_data):
        self.ig_data = ig_data

    def calculate_macd(self, prices, short_window=12, long_window=26, signal_window=9):
        df = pd.DataFrame(prices, columns=["close"])
        macd = df.ta.macd(fast=short_window, slow=long_window, signal=signal_window)
        return macd["MACD_12_26_9"], macd["MACDs_12_26_9"]

    def calculate_rsi(self, prices, window=14):
        df = pd.DataFrame(prices, columns=["close"])
        rsi = df.ta.rsi(length=window)
        return rsi

class TrendIdentifier:
    def __init__(self, ig_data):
        self.ig_data = ig_data

    def identify_trend(self, prices):
        slope = (prices[-1] - prices[0]) / len(prices)
        if slope > 0:
            return "alcista"
        elif slope < 0:
            return "bajista"
        else:
            return "lateral"

class Visualizer:
    def plot_support_resistance(self, prices, supports, resistances):
        plt.figure(figsize=(10, 6))
        plt.plot(prices, label='Precio', color='blue')
        for support in supports:
            plt.axhline(y=support, color='green', linestyle='--', label=f'Soporte {support}')
        for resistance in resistances:
            plt.axhline(y=resistance, color='red', linestyle='--', label=f'Resistencia {resistance}')
        plt.title('Niveles de Soporte y Resistencia')
        plt.xlabel('Tiempo')
        plt.ylabel('Precio')
        plt.legend()
        plt.grid(True)
        plt.show()

class OrderCriteria:
    def __init__(self, ig_data, indicators):
        self.ig_data = ig_data
        self.indicators = indicators
        self.counter = {
            "BUY": 0,
            "SELL": 0,
            "HOLD": 0
        }

    def evaluate_criteria(self, epic, supports, resistances):
        prices = self.ig_data.get_historical_prices(epic)
        macd_line, signal_line = self.indicators.calculate_macd(prices)
        rsi = self.indicators.calculate_rsi(prices)
        
        # MACD criteria
        if macd_line[-1] > signal_line[-1]:
            macd_signal = "BUY"
        else:
            macd_signal = "SELL"
        
        # RSI criteria
        if rsi[-1] > 70:
            rsi_signal = "SELL"
        elif rsi[-1] < 30:
            rsi_signal = "BUY"
        else:
            rsi_signal = "HOLD"

        # Support and Resistance criteria
        last_price = prices[-1]
        if last_price in supports:
            sr_signal = "BUY"
        elif last_price in resistances:
            sr_signal = "SELL"
        else:
            sr_signal = "HOLD"

        # Update counter
        self.counter[macd_signal] += 1
        self.counter[rsi_signal] += 1
        self.counter[sr_signal] += 1

        # Decision
        if self.counter["BUY"] > 3:
            return "BUY"
        elif self.counter["SELL"] > 3:
            return "SELL"
        else:
            return "HOLD"

# Uso
ig_data = IGAPIData(api_key, username, password)
indicators = Indicators(ig_data)
order_criteria = OrderCriteria(ig_data, indicators)
decision = order_criteria.evaluate_criteria(epic, [1.08, 1.09], [1.12, 1.13])
print(f"Decision: {decision}")

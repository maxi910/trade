import logging
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datos import IGAPIData

logger = logging.getLogger(__name__)

class ActionCounter:
    def __init__(self):
        self.counts = {
            "BUY": 0,
            "HOLD": 0,
            "SELL": 0
        }

    def update(self, action):
        if action in self.counts:
            self.counts[action] += 1

    def get_counts(self):
        return self.counts

    def reset(self):
        for action in self.counts:
            self.counts[action] = 0

class OrderCriteria:
    def __init__(self, ig_data):
        self.ig_data = ig_data
        self.action_counter = ActionCounter()

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
    
    action = "HOLD"  # valor predeterminado
        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2]:
            action = "BUY"
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2]:
            action = "SELL"
        for support in supports:
            if last_price > support:
                action = "BUY"
        for resistance in resistances:
            if last_price < resistance:
                action = "SELL"
        
        self.action_counter.update(action)
        return action


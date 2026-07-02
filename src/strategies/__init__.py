from .pure_dca import pure_dca_strategy
from .dca_rsi import dca_rsi_strategy
from .value_averaging import value_averaging_strategy
from .grid_trading import grid_trading_strategy
from .hybrid import hybrid_strategy
from .fear_greed_dca import fear_greed_dca_strategy

ALL_STRATEGIES = {
    "Pure DCA": pure_dca_strategy,
    "DCA + RSI": dca_rsi_strategy,
    "Value Averaging": value_averaging_strategy,
    "Grid Trading": grid_trading_strategy,
    "Hybrid 80/15/5": hybrid_strategy,
    "Fear & Greed DCA": fear_greed_dca_strategy,
}

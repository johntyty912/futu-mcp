"""Pydantic models for input validation and output structuring."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from enum import Enum


# Enumerations for Futu API constants
class TrdMarket(str, Enum):
    """Trading market enumeration."""
    HK = "HK"
    US = "US"
    CN = "CN"
    HKCC = "HKCC"
    SG = "SG"
    JP = "JP"


class TrdSide(str, Enum):
    """Trading side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration."""
    NORMAL = "NORMAL"  # Limit order
    MARKET = "MARKET"  # Market order
    ABSOLUTE_LIMIT = "ABSOLUTE_LIMIT"  # Absolute limit order
    STOP = "STOP"  # Stop order
    STOP_LIMIT = "STOP_LIMIT"  # Stop limit order
    MARKET_IF_TOUCHED = "MARKET_IF_TOUCHED"  # MIT order
    LIMIT_IF_TOUCHED = "LIMIT_IF_TOUCHED"  # LIT order
    TRAILING_STOP = "TRAILING_STOP"  # Trailing stop order
    TRAILING_STOP_LIMIT = "TRAILING_STOP_LIMIT"  # Trailing stop limit order


class KLType(str, Enum):
    """K-line (candlestick) type enumeration."""
    K_1M = "K_1M"  # 1 minute
    K_5M = "K_5M"  # 5 minutes
    K_15M = "K_15M"  # 15 minutes
    K_30M = "K_30M"  # 30 minutes
    K_60M = "K_60M"  # 60 minutes
    K_DAY = "K_DAY"  # Daily
    K_WEEK = "K_WEEK"  # Weekly
    K_MON = "K_MON"  # Monthly


class AuType(str, Enum):
    """Adjustment type for K-line data."""
    QFQ = "qfq"  # Forward adjusted
    HFQ = "hfq"  # Backward adjusted
    NONE = "None"  # No adjustment


# Input Models
class StockQuoteInput(BaseModel):
    """Input model for get_stock_quote."""
    stock_codes: List[str] = Field(..., description="List of stock codes (e.g., ['HK.00700', 'US.AAPL'])")


class HistoricalKlineInput(BaseModel):
    """Input model for get_historical_kline."""
    stock_code: str = Field(..., description="Stock code (e.g., 'HK.00700')")
    start_date: str = Field(..., description="Start date in yyyy-MM-dd format")
    end_date: str = Field(..., description="End date in yyyy-MM-dd format")
    kl_type: KLType = Field(default=KLType.K_DAY, description="K-line type")
    autype: AuType = Field(default=AuType.QFQ, description="Adjustment type")
    max_count: int = Field(default=1000, description="Maximum number of K-lines to return")


class MarketSnapshotInput(BaseModel):
    """Input model for get_market_snapshot."""
    stock_codes: List[str] = Field(..., description="List of stock codes")


class OrderBookInput(BaseModel):
    """Input model for get_order_book."""
    stock_code: str = Field(..., description="Stock code")


class TickerInput(BaseModel):
    """Input model for get_rt_ticker."""
    stock_code: str = Field(..., description="Stock code")
    max_count: int = Field(default=1000, description="Maximum number of tickers to return")


class OptionChainInput(BaseModel):
    """Input model for get_option_chain."""
    stock_code: str = Field(..., description="Underlying stock code")
    start_date: Optional[str] = Field(None, description="Start expiration date (yyyy-MM-dd)")
    end_date: Optional[str] = Field(None, description="End expiration date (yyyy-MM-dd)")


class PlaceOrderInput(BaseModel):
    """Input model for place_order."""
    stock_code: str = Field(..., description="Stock code")
    trd_side: TrdSide = Field(..., description="Trading side (BUY or SELL)")
    order_type: OrderType = Field(..., description="Order type")
    qty: float = Field(..., description="Order quantity")
    price: Optional[float] = Field(None, description="Order price (required for limit orders)")
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")
    trd_market: Optional[TrdMarket] = Field(None, description="Trading market")
    remark: Optional[str] = Field(None, description="Order remark (max 64 bytes)")


class ModifyOrderInput(BaseModel):
    """Input model for modify_order."""
    order_id: str = Field(..., description="Order ID to modify")
    modify_op: Literal["CANCEL", "MODIFY", "ENABLE", "DISABLE"] = Field(..., description="Modification operation")
    qty: Optional[float] = Field(None, description="New quantity (for MODIFY operation)")
    price: Optional[float] = Field(None, description="New price (for MODIFY operation)")
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")


class CancelOrderInput(BaseModel):
    """Input model for cancel_order."""
    order_id: str = Field(..., description="Order ID to cancel")
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")


class OrderListInput(BaseModel):
    """Input model for get_order_list."""
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")
    trd_market: Optional[TrdMarket] = Field(None, description="Trading market filter")
    status_filter: Optional[List[str]] = Field(None, description="Order status filter list")


class DealListInput(BaseModel):
    """Input model for get_deal_list."""
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")
    trd_market: Optional[TrdMarket] = Field(None, description="Trading market filter")


class HistoryDealInput(BaseModel):
    """Input model for get_history_deal_list."""
    start_time: str = Field(..., description="Start time (YYYY-MM-DD HH:MM:SS)")
    end_time: str = Field(..., description="End time (YYYY-MM-DD HH:MM:SS)")
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")


class AccountInfoInput(BaseModel):
    """Input model for get_account_info."""
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")
    trd_market: Optional[TrdMarket] = Field(None, description="Trading market")


class PositionListInput(BaseModel):
    """Input model for get_positions."""
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")
    trd_market: Optional[TrdMarket] = Field(None, description="Trading market filter")


class CashFlowInput(BaseModel):
    """Input model for get_cash_flow."""
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")


class MaxTrdQtyInput(BaseModel):
    """Input model for get_max_trd_qtys."""
    stock_code: str = Field(..., description="Stock code")
    order_type: OrderType = Field(..., description="Order type")
    price: Optional[float] = Field(None, description="Order price")
    trd_side: TrdSide = Field(..., description="Trading side")
    trd_env: Literal["REAL", "SIMULATE"] = Field(default="SIMULATE", description="Trading environment")


class WatchlistInput(BaseModel):
    """Input model for get_watchlist."""
    group_name: Optional[str] = Field(None, description="Watchlist group name")


class PriceReminderInput(BaseModel):
    """Input model for set_price_reminder."""
    stock_code: str = Field(..., description="Stock code")
    operation: Literal["ADD", "DEL", "ENABLE", "DISABLE", "MODIFY", "DEL_ALL"] = Field(..., description="Operation type")
    reminder_type: Optional[str] = Field(None, description="Reminder type (e.g., PRICE_UP, PRICE_DOWN)")
    reminder_value: Optional[float] = Field(None, description="Reminder threshold value")
    note: Optional[str] = Field(None, description="Reminder note (max 64 bytes)")


class TradingDaysInput(BaseModel):
    """Input model for get_trading_days."""
    market: TrdMarket = Field(..., description="Trading market")
    start_date: str = Field(..., description="Start date (yyyy-MM-dd)")
    end_date: str = Field(..., description="End date (yyyy-MM-dd)")


class StaticInfoInput(BaseModel):
    """Input model for get_static_info."""
    stock_codes: List[str] = Field(..., description="List of stock codes")


class MarketStateInput(BaseModel):
    """Input model for get_market_state."""
    stock_codes: Optional[List[str]] = Field(None, description="Optional list of stock codes")


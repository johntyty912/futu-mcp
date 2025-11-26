"""Futu API client wrapper with connection management and error handling."""

import logging
from typing import Optional, Any, Dict
from contextlib import asynccontextmanager
from futu import (
    OpenQuoteContext,
    OpenSecTradeContext,
    RET_OK,
    TrdEnv,
    TrdMarket as FutuTrdMarket,
    TrdSide as FutuTrdSide,
    OrderType as FutuOrderType,
    KLType as FutuKLType,
    AuType as FutuAuType,
)
from .config import FutuConfig
from .models import TrdMarket, TrdSide, OrderType, KLType, AuType

logger = logging.getLogger(__name__)


class FutuClientError(Exception):
    """Base exception for Futu client errors."""
    pass


class FutuConnectionError(FutuClientError):
    """Raised when connection to FutuOpenD fails."""
    pass


class FutuAPIError(FutuClientError):
    """Raised when Futu API returns an error."""
    pass


class FutuClient:
    """Wrapper for Futu API with connection management and error handling."""

    def __init__(self, config: FutuConfig):
        """Initialize Futu client with configuration.
        
        Args:
            config: Futu configuration
        """
        self.config = config
        self.quote_ctx: Optional[OpenQuoteContext] = None
        self.trade_ctx: Optional[OpenSecTradeContext] = None
        self._connected = False

    def connect(self) -> None:
        """Connect to FutuOpenD gateway.
        
        Raises:
            FutuConnectionError: If connection fails
        """
        try:
            # Connect to quote context
            self.quote_ctx = OpenQuoteContext(
                host=self.config.host,
                port=self.config.port
            )
            logger.info(f"Connected to FutuOpenD at {self.config.host}:{self.config.port}")
            self._connected = True
        except Exception as e:
            logger.error(f"Failed to connect to FutuOpenD: {e}")
            raise FutuConnectionError(f"Failed to connect to FutuOpenD: {e}")

    def connect_trade(self, trd_env: str = "SIMULATE") -> None:
        """Connect to trade context.
        
        Args:
            trd_env: Trading environment ("REAL" or "SIMULATE")
            
        Raises:
            FutuConnectionError: If connection fails
        """
        try:
            env = TrdEnv.REAL if trd_env == "REAL" else TrdEnv.SIMULATE
            self.trade_ctx = OpenSecTradeContext(
                host=self.config.host,
                port=self.config.port
            )
            
            # Unlock trade if password is provided (required for both REAL and SIMULATE)
            if self.config.trade_pwd:
                ret, data = self.trade_ctx.unlock_trade(self.config.trade_pwd)
                if ret != RET_OK:
                    raise FutuConnectionError(f"Failed to unlock trade: {data}")
                logger.info(f"Trading unlocked for {trd_env} environment")
            
            logger.info(f"Connected to trade context ({trd_env})")
        except Exception as e:
            logger.error(f"Failed to connect to trade context: {e}")
            raise FutuConnectionError(f"Failed to connect to trade context: {e}")

    def disconnect(self) -> None:
        """Disconnect from FutuOpenD gateway."""
        if self.quote_ctx:
            self.quote_ctx.close()
            self.quote_ctx = None
            logger.info("Disconnected quote context")
        
        if self.trade_ctx:
            self.trade_ctx.close()
            self.trade_ctx = None
            logger.info("Disconnected trade context")
        
        self._connected = False

    def ensure_connected(self) -> None:
        """Ensure client is connected to FutuOpenD.
        
        Raises:
            FutuConnectionError: If not connected
        """
        if not self._connected or not self.quote_ctx:
            raise FutuConnectionError("Not connected to FutuOpenD. Call connect() first.")

    def ensure_trade_connected(self) -> None:
        """Ensure client is connected to trade context.
        
        Raises:
            FutuConnectionError: If not connected
        """
        if not self.trade_ctx:
            raise FutuConnectionError("Not connected to trade context. Call connect_trade() first.")

    @staticmethod
    def check_response(ret: int, data: Any, error_msg: str = "API call failed") -> Any:
        """Check Futu API response and raise exception if error.
        
        Args:
            ret: Return code from Futu API
            data: Data or error message from Futu API
            error_msg: Custom error message prefix
            
        Returns:
            data if successful
            
        Raises:
            FutuAPIError: If API call failed
        """
        if ret != RET_OK:
            raise FutuAPIError(f"{error_msg}: {data}")
        return data

    # Conversion helpers
    @staticmethod
    def convert_trd_market(market: Optional[TrdMarket]) -> Optional[Any]:
        """Convert TrdMarket enum to Futu TrdMarket."""
        if market is None:
            return None
        mapping = {
            TrdMarket.HK: FutuTrdMarket.HK,
            TrdMarket.US: FutuTrdMarket.US,
            TrdMarket.CN: FutuTrdMarket.CN,
            TrdMarket.HKCC: FutuTrdMarket.HKCC,
        }
        return mapping.get(market)

    @staticmethod
    def convert_trd_side(side: TrdSide) -> Any:
        """Convert TrdSide enum to Futu TrdSide."""
        mapping = {
            TrdSide.BUY: FutuTrdSide.BUY,
            TrdSide.SELL: FutuTrdSide.SELL,
        }
        return mapping.get(side)

    @staticmethod
    def convert_order_type(order_type: OrderType) -> Any:
        """Convert OrderType enum to Futu OrderType."""
        mapping = {
            OrderType.NORMAL: FutuOrderType.NORMAL,
            OrderType.MARKET: FutuOrderType.MARKET,
            OrderType.ABSOLUTE_LIMIT: FutuOrderType.ABSOLUTE_LIMIT,
            OrderType.STOP: FutuOrderType.STOP,
            OrderType.STOP_LIMIT: FutuOrderType.STOP_LIMIT,
            OrderType.MARKET_IF_TOUCHED: FutuOrderType.MARKET_IF_TOUCHED,
            OrderType.LIMIT_IF_TOUCHED: FutuOrderType.LIMIT_IF_TOUCHED,
            OrderType.TRAILING_STOP: FutuOrderType.TRAILING_STOP,
            OrderType.TRAILING_STOP_LIMIT: FutuOrderType.TRAILING_STOP_LIMIT,
        }
        return mapping.get(order_type)

    @staticmethod
    def convert_kl_type(kl_type: KLType) -> Any:
        """Convert KLType enum to Futu KLType."""
        mapping = {
            KLType.K_1M: FutuKLType.K_1M,
            KLType.K_5M: FutuKLType.K_5M,
            KLType.K_15M: FutuKLType.K_15M,
            KLType.K_30M: FutuKLType.K_30M,
            KLType.K_60M: FutuKLType.K_60M,
            KLType.K_DAY: FutuKLType.K_DAY,
            KLType.K_WEEK: FutuKLType.K_WEEK,
            KLType.K_MON: FutuKLType.K_MON,
        }
        return mapping.get(kl_type)

    @staticmethod
    def convert_au_type(au_type: AuType) -> str:
        """Convert AuType enum to Futu AuType."""
        mapping = {
            AuType.QFQ: FutuAuType.QFQ,
            AuType.HFQ: FutuAuType.HFQ,
            AuType.NONE: FutuAuType.NONE,
        }
        return mapping.get(au_type)

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


@asynccontextmanager
async def get_futu_client(config: FutuConfig):
    """Async context manager for Futu client.
    
    Args:
        config: Futu configuration
        
    Yields:
        FutuClient instance
    """
    client = FutuClient(config)
    try:
        client.connect()
        yield client
    finally:
        client.disconnect()


"""Tests for trading.place_order conditional-order forwarding and validation."""

import pandas as pd
import pytest
from futu import RET_OK
from futu import TimeInForce as FutuTimeInForce
from futu import TrailType as FutuTrailType
from futu import Session as FutuSession

from futu_mcp.config import FutuConfig
from futu_mcp.futu_client import FutuClient
from futu_mcp.tools import trading


class FakeTradeCtx:
    """Records the kwargs passed to place_order; returns a successful response."""

    def __init__(self):
        self.place_order_kwargs = None

    def place_order(self, **kwargs):
        self.place_order_kwargs = kwargs
        return RET_OK, pd.DataFrame([{"order_id": "ORD123"}])


def make_client():
    """Real FutuClient with the network boundary stubbed out."""
    client = FutuClient(FutuConfig())
    fake = FakeTradeCtx()
    client.trade_ctx = fake
    client.connect_trade = lambda trd_env="SIMULATE": None
    client.ensure_trade_connected = lambda: None
    return client, fake


def base_params(**overrides):
    params = {
        "stock_code": "HK.00700",
        "trd_side": "SELL",
        "order_type": "NORMAL",
        "qty": 100,
        "price": 350.0,
    }
    params.update(overrides)
    return params


def test_forwards_aux_price_for_stop_order():
    client, fake = make_client()
    trading.place_order(client, base_params(order_type="STOP", price=None, aux_price=320.0))
    assert fake.place_order_kwargs["aux_price"] == 320.0


def test_forwards_trailing_params_for_trailing_stop():
    client, fake = make_client()
    trading.place_order(
        client,
        base_params(order_type="TRAILING_STOP", price=None, trail_type="RATIO", trail_value=5.0, trail_spread=1.0),
    )
    kwargs = fake.place_order_kwargs
    assert kwargs["trail_type"] == FutuTrailType.RATIO
    assert kwargs["trail_value"] == 5.0
    assert kwargs["trail_spread"] == 1.0


def test_defaults_time_in_force_to_day():
    client, fake = make_client()
    trading.place_order(client, base_params())
    assert fake.place_order_kwargs["time_in_force"] == FutuTimeInForce.DAY


def test_forwards_gtc_time_in_force():
    client, fake = make_client()
    trading.place_order(client, base_params(time_in_force="GTC"))
    assert fake.place_order_kwargs["time_in_force"] == FutuTimeInForce.GTC


def test_does_not_forward_aux_price_when_absent():
    client, fake = make_client()
    trading.place_order(client, base_params())
    assert "aux_price" not in fake.place_order_kwargs


def test_stop_order_without_aux_price_raises():
    client, _ = make_client()
    with pytest.raises(ValueError, match="aux_price"):
        trading.place_order(client, base_params(order_type="STOP", price=None))


def test_trailing_stop_without_trail_params_raises():
    client, _ = make_client()
    with pytest.raises(ValueError, match="trail"):
        trading.place_order(client, base_params(order_type="TRAILING_STOP", price=None))


def test_defaults_fill_outside_rth_to_false():
    client, fake = make_client()
    trading.place_order(client, base_params())
    assert fake.place_order_kwargs["fill_outside_rth"] is False


def test_forwards_fill_outside_rth_when_true():
    client, fake = make_client()
    trading.place_order(client, base_params(fill_outside_rth=True))
    assert fake.place_order_kwargs["fill_outside_rth"] is True


def test_defaults_session_to_rth():
    client, fake = make_client()
    trading.place_order(client, base_params())
    assert fake.place_order_kwargs["session"] == FutuSession.RTH


def test_forwards_eth_session():
    client, fake = make_client()
    trading.place_order(client, base_params(session="ETH"))
    assert fake.place_order_kwargs["session"] == FutuSession.ETH


def test_forwards_all_session():
    client, fake = make_client()
    trading.place_order(client, base_params(session="ALL"))
    assert fake.place_order_kwargs["session"] == FutuSession.ALL

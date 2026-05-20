"""Tests for Pydantic input models."""

from futu_mcp.models import PlaceOrderInput, TimeInForce, TrailType


def test_place_order_input_time_in_force_defaults_to_day():
    order = PlaceOrderInput(
        stock_code="HK.00700",
        trd_side="BUY",
        order_type="NORMAL",
        qty=100,
        price=350.0,
    )
    assert order.time_in_force == TimeInForce.DAY


def test_place_order_input_accepts_aux_price_for_stop_orders():
    order = PlaceOrderInput(
        stock_code="HK.00700",
        trd_side="SELL",
        order_type="STOP",
        qty=100,
        aux_price=320.0,
    )
    assert order.aux_price == 320.0


def test_place_order_input_accepts_trailing_params():
    order = PlaceOrderInput(
        stock_code="HK.00700",
        trd_side="SELL",
        order_type="TRAILING_STOP",
        qty=100,
        trail_type="RATIO",
        trail_value=5.0,
        trail_spread=1.0,
    )
    assert order.trail_type == TrailType.RATIO
    assert order.trail_value == 5.0
    assert order.trail_spread == 1.0


def test_place_order_input_accepts_gtc_time_in_force():
    order = PlaceOrderInput(
        stock_code="HK.00700",
        trd_side="BUY",
        order_type="NORMAL",
        qty=100,
        price=350.0,
        time_in_force="GTC",
    )
    assert order.time_in_force == TimeInForce.GTC

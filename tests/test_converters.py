"""Tests for FutuClient enum conversion helpers."""

from futu import TimeInForce as FutuTimeInForce
from futu import TrailType as FutuTrailType

from futu_mcp.futu_client import FutuClient
from futu_mcp.models import TimeInForce, TrailType


def test_convert_time_in_force_day():
    assert FutuClient.convert_time_in_force(TimeInForce.DAY) == FutuTimeInForce.DAY


def test_convert_time_in_force_gtc():
    assert FutuClient.convert_time_in_force(TimeInForce.GTC) == FutuTimeInForce.GTC


def test_convert_trail_type_ratio():
    assert FutuClient.convert_trail_type(TrailType.RATIO) == FutuTrailType.RATIO


def test_convert_trail_type_amount():
    assert FutuClient.convert_trail_type(TrailType.AMOUNT) == FutuTrailType.AMOUNT


def test_convert_trail_type_none_returns_none():
    assert FutuClient.convert_trail_type(None) is None

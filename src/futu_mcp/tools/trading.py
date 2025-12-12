"""Trading tools for Futu MCP Server."""

import logging
from typing import Dict, Any
import pandas as pd
from futu import TrdEnv, ModifyOrderOp, RET_OK
from ..futu_client import FutuClient
from ..models import (
    PlaceOrderInput,
    ModifyOrderInput,
    CancelOrderInput,
    OrderListInput,
    DealListInput,
    HistoryDealInput,
    MaxTrdQtyInput,
)

logger = logging.getLogger(__name__)


def place_order(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Place a new order with full validation and safeguards.
    
    Args:
        client: Futu client instance
        params: Order parameters
        
    Returns:
        Dictionary with order placement result
    """
    input_data = PlaceOrderInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    # Convert enums
    trd_side = client.convert_trd_side(input_data.trd_side)
    order_type = client.convert_order_type(input_data.order_type)
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Validate price for limit orders
    if input_data.order_type in ["NORMAL", "STOP_LIMIT", "LIMIT_IF_TOUCHED"] and input_data.price is None:
        raise ValueError(f"{input_data.order_type} orders require a price")
    
    # Prepare order parameters
    order_params = {
        "price": input_data.price or 0,
        "qty": input_data.qty,
        "code": input_data.stock_code,
        "trd_side": trd_side,
        "order_type": order_type,
        "trd_env": trd_env,
    }
    
    # Only add trd_market if provided
    if input_data.trd_market is not None:
        order_params["trd_market"] = client.convert_trd_market(input_data.trd_market)
    
    # Add remark if provided
    if input_data.remark:
        order_params["remark"] = input_data.remark
    
    # Place order
    ret, data = client.trade_ctx.place_order(**order_params)
    result = client.check_response(ret, data, "Failed to place order")
    
    logger.info(f"Order placed: {input_data.stock_code} {input_data.trd_side} {input_data.qty} @ {input_data.price}")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        order_details = result.to_dict(orient='records')[0]
        order_id = result['order_id'][0] if 'order_id' in result else None
    elif isinstance(result, dict):
        order_details = result
        order_id = result.get('order_id')
    else:
        order_details = str(result)
        order_id = None
    
    return {
        "order_id": order_id,
        "order_details": order_details,
        "environment": input_data.trd_env
    }


def modify_order(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Modify an existing order.
    
    Args:
        client: Futu client instance
        params: Modification parameters
        
    Returns:
        Dictionary with modification result
    """
    input_data = ModifyOrderInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    # Convert operation
    op_mapping = {
        "CANCEL": ModifyOrderOp.CANCEL,
        "MODIFY": ModifyOrderOp.NORMAL,
        "ENABLE": ModifyOrderOp.ENABLE,
        "DISABLE": ModifyOrderOp.DISABLE,
    }
    modify_op = op_mapping.get(input_data.modify_op)
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Modify order
    ret, data = client.trade_ctx.modify_order(
        modify_order_op=modify_op,
        order_id=input_data.order_id,
        qty=input_data.qty or 0,
        price=input_data.price or 0,
        trd_env=trd_env
    )
    result = client.check_response(ret, data, "Failed to modify order")
    
    logger.info(f"Order modified: {input_data.order_id} - {input_data.modify_op}")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        result_data = result.to_dict(orient='records')[0]
    elif isinstance(result, dict):
        result_data = result
    else:
        result_data = str(result)
    
    return {
        "order_id": input_data.order_id,
        "operation": input_data.modify_op,
        "result": result_data
    }


def cancel_order(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Cancel an order.
    
    Args:
        client: Futu client instance
        params: Cancellation parameters
        
    Returns:
        Dictionary with cancellation result
    """
    input_data = CancelOrderInput(**params)
    
    # Use modify_order with CANCEL operation
    return modify_order(client, {
        "order_id": input_data.order_id,
        "modify_op": "CANCEL",
        "trd_env": input_data.trd_env
    })


def cancel_all_orders(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Cancel all orders for the account.
    
    Args:
        client: Futu client instance
        params: Parameters containing trd_env
        
    Returns:
        Dictionary with cancellation result
    """
    trd_env = params.get("trd_env", "SIMULATE")
    
    # Connect to trade context
    client.connect_trade(trd_env)
    client.ensure_trade_connected()
    
    env = TrdEnv.REAL if trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Cancel all orders
    ret, data = client.trade_ctx.cancel_all_order(trd_env=env)
    result = client.check_response(ret, data, "Failed to cancel all orders")
    
    logger.info(f"All orders cancelled in {trd_env}")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        details = result.to_dict(orient='records')
    elif isinstance(result, dict):
        details = [result]
    else:
        details = str(result)
    
    return {
        "message": "All orders cancelled successfully",
        "environment": trd_env,
        "details": details
    }


def get_order_list(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get list of orders.
    
    Args:
        client: Futu client instance
        params: Query parameters
        
    Returns:
        Dictionary with order list
    """
    input_data = OrderListInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Get order list
    # Note: order_list_query does not accept trd_market parameter.
    # Market filtering is done when creating OpenSecTradeContext via filter_trdmarket.
    # If needed, use order_market parameter for additional filtering (optional).
    query_params = {
        "trd_env": trd_env,
        "status_filter_list": input_data.status_filter or []
    }
    
    # Only add order_market if trd_market is specified (optional filter)
    if input_data.trd_market is not None:
        order_market = client.convert_trd_market(input_data.trd_market)
        if order_market is not None:
            query_params["order_market"] = order_market
    
    ret, data = client.trade_ctx.order_list_query(**query_params)
    result = client.check_response(ret, data, "Failed to get order list")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        orders = result.to_dict(orient='records')
        count = len(result)
    else:
        orders = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "orders": orders,
        "count": count,
        "environment": input_data.trd_env
    }


def get_deal_list(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get today's deal (transaction) list.
    
    Args:
        client: Futu client instance
        params: Query parameters
        
    Returns:
        Dictionary with deal list
    """
    input_data = DealListInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Get deal list
    # Note: deal_list_query does not accept trd_market parameter.
    # Market filtering is done when creating OpenSecTradeContext via filter_trdmarket.
    # If market filtering is needed, it should be set when creating the trade context.
    ret, data = client.trade_ctx.deal_list_query(
        trd_env=trd_env
    )
    result = client.check_response(ret, data, "Failed to get deal list")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        deals = result.to_dict(orient='records')
        count = len(result)
    else:
        deals = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "deals": deals,
        "count": count,
        "environment": input_data.trd_env
    }


def get_history_deal_list(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get historical deal list.
    
    Args:
        client: Futu client instance
        params: Query parameters with time range
        
    Returns:
        Dictionary with historical deal list
    """
    input_data = HistoryDealInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    
    # Get history deal list
    ret, data = client.trade_ctx.history_deal_list_query(
        start=input_data.start_time,
        end=input_data.end_time,
        trd_env=trd_env
    )
    result = client.check_response(ret, data, "Failed to get history deal list")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        deals = result.to_dict(orient='records')
        count = len(result)
    else:
        deals = [result] if isinstance(result, dict) else str(result)
        count = 1
    
    return {
        "deals": deals,
        "count": count,
        "start_time": input_data.start_time,
        "end_time": input_data.end_time,
        "environment": input_data.trd_env
    }


def get_max_trd_qtys(client: FutuClient, params: Dict[str, Any]) -> Dict[str, Any]:
    """Get maximum tradable quantities.
    
    Note: acctradinginfo_query does not accept trd_side parameter.
    The response contains separate fields for buy and sell max quantities.
    This function returns all max quantities and indicates which to use based on trd_side.
    
    Args:
        client: Futu client instance
        params: Query parameters
        
    Returns:
        Dictionary with max tradable quantities
    """
    input_data = MaxTrdQtyInput(**params)
    
    # Connect to trade context
    client.connect_trade(input_data.trd_env)
    client.ensure_trade_connected()
    
    trd_env = TrdEnv.REAL if input_data.trd_env == "REAL" else TrdEnv.SIMULATE
    order_type = client.convert_order_type(input_data.order_type)
    
    # Handle price parameter: API requires price > 0
    price = input_data.price
    
    # If price is not provided, try to fetch current market price for market orders
    if price is None:
        if input_data.order_type == "MARKET":
            # For market orders, fetch current price from market snapshot
            try:
                client.ensure_connected()
                # Subscribe and get market snapshot to get current price
                ret, data = client.quote_ctx.subscribe([input_data.stock_code], ['QUOTE'])
                if ret == RET_OK:
                    ret, data = client.quote_ctx.get_market_snapshot([input_data.stock_code])
                    if ret == RET_OK and isinstance(data, pd.DataFrame) and not data.empty:
                        # Use last_price or cur_price if available
                        if 'last_price' in data.columns:
                            price = float(data['last_price'].iloc[0])
                        elif 'cur_price' in data.columns:
                            price = float(data['cur_price'].iloc[0])
                        elif 'price' in data.columns:
                            price = float(data['price'].iloc[0])
                        
                        # Validate fetched price is valid
                        if price is not None and price > 0:
                            logger.info(f"Fetched current price {price} for {input_data.stock_code} (market order)")
                        else:
                            price = None  # Reset if invalid
            except Exception as e:
                logger.warning(f"Failed to fetch current price for market order: {e}")
        
        # If still no price, raise error with helpful message
        if price is None or price <= 0:
            if input_data.order_type == "MARKET":
                raise ValueError(
                    f"Price parameter is required for get_max_trd_qtys. "
                    f"For MARKET orders, provide a price estimate or the tool will attempt to fetch current price. "
                    f"Failed to fetch current price automatically. Please provide price parameter."
                )
            else:
                raise ValueError(
                    f"Price parameter is required for {input_data.order_type} orders. "
                    f"Please provide a price when calling get_max_trd_qtys."
                )
    
    # Validate price > 0
    if price <= 0:
        raise ValueError(f"Price must be greater than 0, got {price}")
    
    # Get max tradable quantities - note: no trd_side parameter
    ret, data = client.trade_ctx.acctradinginfo_query(
        order_type=order_type,
        code=input_data.stock_code,
        price=price,
        trd_env=trd_env
    )
    result = client.check_response(ret, data, "Failed to get max tradable quantities")
    
    # Handle DataFrame response
    if isinstance(result, pd.DataFrame):
        max_quantities = result.to_dict(orient='records')[0]
    elif isinstance(result, dict):
        max_quantities = result
    else:
        max_quantities = str(result)
    
    # Extract relevant max quantity based on trd_side
    # The response contains fields like max_cash_buy, max_sell, etc.
    relevant_max_qty = None
    if isinstance(max_quantities, dict):
        if input_data.trd_side == "BUY":
            # Prefer max_cash_and_margin_buy, fallback to max_cash_buy
            relevant_max_qty = max_quantities.get('max_cash_and_margin_buy') or max_quantities.get('max_cash_buy')
        elif input_data.trd_side == "SELL":
            # Prefer max_position_sell, fallback to max_sell
            relevant_max_qty = max_quantities.get('max_position_sell') or max_quantities.get('max_sell')
    
    return {
        "stock_code": input_data.stock_code,
        "trd_side": input_data.trd_side,
        "max_quantities": max_quantities,
        "relevant_max_qty": relevant_max_qty,  # Max qty for the specified trd_side
        "environment": input_data.trd_env
    }


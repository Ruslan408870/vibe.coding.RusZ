"""Order processing helpers."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class OrderValidationError(ValueError):
    """Raised when an order payload is invalid."""


def _require_mapping(order: Any) -> dict[str, Any]:
    if not isinstance(order, dict):
        raise OrderValidationError("Order must be a dictionary.")
    return order


def _normalize_id(order: dict[str, Any]) -> int:
    order_id = order.get("id", 0)
    try:
        order["id"] = int(order_id)
    except (TypeError, ValueError) as exc:
        raise OrderValidationError("Order id must be an integer value.") from exc
    return order["id"]


def _validate_items(order: dict[str, Any]) -> list[dict[str, Any]]:
    items = order.get("items")
    if not isinstance(items, list) or not items:
        raise OrderValidationError("Order items must be a non-empty list.")

    validated_items: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            raise OrderValidationError("Each item must be a dictionary.")
        if "price" not in item or "qty" not in item:
            raise OrderValidationError("Each item requires 'price' and 'qty'.")

        price = item["price"]
        qty = item["qty"]
        if not isinstance(price, (int, float)) or not isinstance(qty, (int, float)):
            raise OrderValidationError("Item price and qty must be numeric.")
        if price < 0:
            raise OrderValidationError("Item price cannot be negative.")
        if qty <= 0:
            raise OrderValidationError("Item quantity must be greater than zero.")

        validated_items.append({"price": float(price), "qty": float(qty)})

    order["items"] = validated_items
    return validated_items


def _validate_customer_type(order: dict[str, Any]) -> str:
    customer_type = order.get("customer_type")
    if customer_type is None:
        raise OrderValidationError("Order customer_type is required.")
    if not isinstance(customer_type, str):
        raise OrderValidationError("Order customer_type must be a string.")

    normalized = customer_type.lower()
    if normalized not in {"vip", "regular"}:
        raise OrderValidationError(f"Unsupported customer_type: {customer_type!r}")

    order["customer_type"] = normalized
    return normalized


def _validate_delivery(order: dict[str, Any]) -> str:
    delivery = order.get("delivery")
    if delivery is None:
        raise OrderValidationError("Order delivery is required.")
    if not isinstance(delivery, str):
        raise OrderValidationError("Order delivery must be a string.")

    normalized = delivery.lower()
    if normalized not in {"express", "standard"}:
        raise OrderValidationError(f"Unsupported delivery: {delivery!r}")

    order["delivery"] = normalized
    return normalized


def _calculate_total(items: list[dict[str, Any]]) -> float:
    return sum(float(item["price"]) * float(item["qty"]) for item in items)


def _apply_customer_discount(total: float, customer_type: str) -> float:
    if customer_type == "vip":
        return total * 0.8
    if customer_type == "regular":
        return total * 0.95
    return total


def _apply_delivery_charge(total: float, delivery: str) -> float:
    if delivery == "express":
        return total + 25
    if delivery == "standard":
        return total + 10
    return total


def _finalize_order(order: dict[str, Any], include_delivery: bool) -> dict[str, Any]:
    total = _calculate_total(order["items"])
    total = _apply_customer_discount(total, order["customer_type"])
    if total > 1000:
        total -= 50
    if include_delivery:
        total = _apply_delivery_charge(total, order["delivery"])

    order["total"] = round(total, 2)
    order["status"] = "processed" if order["total"] > 0 else "empty"
    logger.info("Processed order %s with total %.2f", order["id"], order["total"])
    return order


def process_order(order: dict[str, Any]) -> dict[str, Any]:
    normalized_order = _require_mapping(order)
    _normalize_id(normalized_order)
    _validate_items(normalized_order)
    _validate_customer_type(normalized_order)
    _validate_delivery(normalized_order)
    return _finalize_order(normalized_order, include_delivery=True)


def process_bulk_order(order: dict[str, Any]) -> dict[str, Any]:
    normalized_order = _require_mapping(order)
    _normalize_id(normalized_order)
    _validate_items(normalized_order)
    _validate_customer_type(normalized_order)
    return _finalize_order(normalized_order, include_delivery=False)
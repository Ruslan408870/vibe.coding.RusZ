import pytest

from orders import process_bulk_order, process_order


def make_order(**changes: object) -> dict[str, object]:
    order: dict[str, object] = {
        "id": 1,
        "items": [{"price": 100, "qty": 2}],
        "customer_type": "regular",
        "delivery": "standard",
    }
    order.update(changes)
    return order


INVALID_ORDERS = [
    pytest.param(make_order(items=[]), id="empty-items"),
    pytest.param(make_order(items=[{"price": 10, "qty": 0}]), id="zero-quantity"),
    pytest.param(make_order(items=[{"price": 10, "qty": -2}]), id="negative-quantity"),
    pytest.param(make_order(items=[{"price": -10, "qty": 1}]), id="negative-price"),
    pytest.param(make_order(customer_type="gold"), id="unknown-customer-type"),
    pytest.param(make_order(delivery="air"), id="unknown-delivery"),
    pytest.param(
        {"id": 1, "customer_type": "vip", "delivery": "standard"},
        id="missing-items",
    ),
]


@pytest.mark.parametrize(
    ("customer_type", "delivery", "expected_total"),
    [
        ("vip", "express", 185.0),
        ("vip", "standard", 170.0),
        ("regular", "express", 215.0),
        ("regular", "standard", 200.0),
    ],
)
def test_process_order_valid_orders(
    customer_type: str, delivery: str, expected_total: float
) -> None:
    result = process_order(make_order(customer_type=customer_type, delivery=delivery))

    assert result["total"] == expected_total
    assert result["status"] == "processed"


def test_process_order_large_order_gets_extra_discount() -> None:
    result = process_order(make_order(items=[{"price": 600, "qty": 2}]))

    assert result["total"] == 1100.0


def test_process_order_missing_id_defaults_to_zero() -> None:
    order = make_order()
    del order["id"]

    result = process_order(order)

    assert result["id"] == 0


@pytest.mark.parametrize("order", INVALID_ORDERS)
def test_process_order_rejects_invalid_orders(order: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        process_order(order)


@pytest.mark.parametrize(
    ("customer_type", "expected_total"),
    [("vip", 160.0), ("regular", 190.0)],
)
def test_process_bulk_order_valid_orders(
    customer_type: str, expected_total: float
) -> None:
    result = process_bulk_order(make_order(customer_type=customer_type))

    assert result["total"] == expected_total
    assert result["status"] == "processed"


@pytest.mark.parametrize(
    "order",
    [
        pytest.param(make_order(items=[]), id="empty-items"),
        pytest.param(make_order(items=[{"price": 10, "qty": 0}]), id="zero-quantity"),
        pytest.param(make_order(customer_type="gold"), id="unknown-customer-type"),
    ],
)
def test_process_bulk_order_rejects_invalid_orders(order: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        process_bulk_order(order)

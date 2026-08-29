from decimal import Decimal

from app.models import StockMovement
from app.services.pos_service import create_pos_sale


def test_pos_sale_creates_out_stock_movement(app, inventory_context):
    organization, store, product, stock, session = inventory_context
    sale = create_pos_sale(
        organization_id=organization.id,
        session_id=session.id,
        lines=[{"product_id": product.id, "quantity": 2, "unit_price": "50.00"}],
        payments=[{"method": "cash", "amount": "100.00"}],
    )

    movement = StockMovement.query.filter_by(
        organization_id=organization.id,
        reference_type="POS",
        reference_id=sale.id,
    ).one()
    assert movement.movement_type == "OUT"
    assert Decimal(str(movement.quantity)) == Decimal("2")
    assert Decimal(str(stock.quantity)) == Decimal("8")

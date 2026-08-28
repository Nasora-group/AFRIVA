from app.models import ProductBatch

                reference_type="sale_refund",
                reference_id=sale.id,
                note="POS sale refund",
            )

            prefix = "FEFO batch "
            for movement in movements_by_product.get(item.product_id, []):
                if not movement.note or not movement.note.startswith(prefix):
                    continue
                batch_id = int(movement.note[len(prefix):])
                batch = ProductBatch.query.filter_by(
                    id=batch_id,
                    product_id=item.product_id,
                    store_id=sale.store_id,
                    organization_id=organization_id,
                ).with_for_update().first()
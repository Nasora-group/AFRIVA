# Phase 9 — POS and Inventory integration

## Behavior

A confirmed POS sale consumes stock from the store attached to the active cash register.

- Stock is locked before decrementing to prevent overselling under concurrent checkouts.
- If batches exist, only non-expired batches are eligible.
- Batch consumption follows FEFO: earliest expiry first, then batch id.
- If stock or eligible batch stock is insufficient, the sale is rejected.
- The POS route rolls back the transaction on validation failure.

## Compatibility

The existing POS endpoints and models remain unchanged. Store ownership is derived from the cash session's register, so no duplicate `store_id` is required on `POSSale`.

## Validation

The Phase 9 tests cover successful stock consumption and rejection of insufficient stock. The existing Phase 6 POS behavior remains the base contract.

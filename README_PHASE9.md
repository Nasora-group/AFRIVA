# Phase 9 — POS / Inventory

POS checkout now decrements inventory from the store attached to its cash register. Stock rows are locked for concurrent checkout safety. When batches exist, non-expired batches are consumed FEFO. Validation errors roll back the POS transaction.

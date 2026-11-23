# osrs-owned-item-repurchase-gate

**Type:** Post-check on reply text
**Enforcement:** `contracts/osrs_owned_item_repurchase_gate.py:OsrsOwnedItemRepurchaseGate`

On an OSRS turn, blocks a reply line that recommends buying an item recorded as
owned in `state/osrs_loadout.json`, unless the line says the item is already
owned, skipped or kept.

**Limits:** Ownership is only as current as the saved loadout. Buy lines are found
by wording and table headers, so an unusual phrasing can pass.

**Recovery:** Remove the owned item from the purchase plan or mark it as owned.

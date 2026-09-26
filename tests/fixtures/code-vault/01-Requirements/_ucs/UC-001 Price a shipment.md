---
id: UC-001
type: use-case
title: "Price a shipment"
status: draft
version: 1.0
synced: true
level: user-goal
scope: Acme Grants Portal
primary_feature: rates
features: [rates]
brs: []
entities: []
pain_points: []
sources: [INT-001]
links: []
attachments: []
absorbs: []
owner: team
updated: 2026-09-20
---

# `UC-001 Price a shipment`

## 1. Context & Metadata

* **Primary Actor:** Consumer
* **Secondary Actor(s):** none
* **Business Need / Goal:** See the price of a move
* **Trigger:** The consumer asks for a quote
* **Pre-conditions:**
  * A tariff exists for the lane
* **Post-conditions (success):**
  * A price is shown
* **Post-conditions (failure):**
  * No price is shown
    
## 2. Main Success Scenario

| Step | Actor Action | System Response & Validation |
| :--- | :--- | :--- |
| **S1** | Consumer asks for a quote for a shipment. | System prices it as weight in hundredweight times the lane tariff (`XR-CALC-001`), never below the lane minimum (`XR-CALC-002`). |
| **S2** | — | System adds the fuel surcharge percentage from settings (`XR-CALC-003`). |

## 3. Alternative & Exception Flows

## 4. Business Rules & Compliance Constraints

| Rule | Statement (short) | Enforced at |
| :--- | :--- | :--- |

## 5. Open Questions & Decision Log

**Still open**

**Decision log**

| # | Topic | Raised by / source | Decision | Date |
| :--- | :--- | :--- | :--- | :--- |

## 6. Special Requirements & Related Information

## Discussion

## Changelog
- 1.0 (2026-09-20) — created from INT-001

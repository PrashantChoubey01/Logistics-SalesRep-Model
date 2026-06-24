# Business Rules

The rules the workflow enforces when extracting data, validating shipments,
merging thread state, and deciding the next action.

## Mandatory fields by shipment type

### FCL (Full Container Load)
- Origin (a specific port, not just a country)
- Destination (a specific port, not just a country)
- Container type (e.g. 40HC, 20GP)
- Container count
- Shipment date
- Commodity

### LCL (Less than Container Load)
- Origin (a specific port, not just a country)
- Destination (a specific port, not just a country)
- Weight
- Volume
- Shipment date
- Commodity

Container count is **not** required for LCL.

### Unknown shipment type
If the shipment type is not stated, it is **never assumed**. The workflow asks
for the type (FCL/LCL) along with the fields needed to disambiguate (container
type, weight, volume).

## Cumulative merge rules

Data is preserved across the thread and merged with recency priority:

1. A new non-empty value replaces the old value.
2. A missing field keeps the existing value.
3. An empty string means "no update" and never overwrites existing data.
4. Switching shipment type clears the fields specific to the other type
   (LCL clears FCL-only fields, and vice versa).

## Routing / next actions

| Condition | Next action |
| --- | --- |
| Mandatory fields missing | `send_clarification_request` |
| All data complete | `send_confirmation_request` |
| Customer confirmed | `booking_details_confirmed_assign_forwarders` |
| Forwarder rates received | `collate_rates_and_send_to_sales` |

## Standardization

- Ports are enriched to `Name (CODE)` form, e.g. `Shanghai` → `Shanghai (CNSHG)`.
- Container descriptions are normalized, e.g. `40 footer` → `40HC`.
- Country names are distinguished from port names; a country alone is not a
  valid origin or destination.

## Rate recommendation

- A rate is recommended from the origin/destination/container lookup.
- A market range is computed as ±10% around the market average, floored at a
  minimum value, and surfaced alongside the underlying market figures.

## Invariants

1. Never assume shipment type — ask for FCL/LCL when it is not stated.
2. Origin and destination must be specific ports, not just countries.
3. Empty strings never delete existing values.
4. When a forwarder sends an email, its content is included in the sales
   notification.
5. Sales notifications use port/city names, not country information.

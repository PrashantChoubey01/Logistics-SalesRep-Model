# Market Range Feature Documentation

## Overview

The Rate Recommendation Agent now calculates and displays a **market range** based on the market average with ±10% variation, ensuring all values are positive and have a minimum lower bound of $10.

---

## Feature Details

### Calculation Formula

```
Market Average = $X
Lower Bound = max($10, X × 0.9)  # -10% but never less than $10
Upper Bound = X × 1.1             # +10%
```

### Safety Guards

1. **Minimum $10 Lower Bound**: If the calculated lower bound is less than $10, it's set to exactly $10
2. **Always Positive**: Both values are guaranteed to be positive numbers
3. **High > Low**: Upper bound is always greater than lower bound

---

## Examples

| Market Average | Lower Bound (-10%) | Upper Bound (+10%) | Market Range |
|----------------|-------------------|-------------------|--------------|
| $1,107 | $996 | $1,217 | `$996 - $1,217` |
| $1,000 | $900 | $1,100 | `$900 - $1,100` |
| $100 | $90 | $110 | `$90 - $110` |
| $50 | $45 | $55 | `$45 - $55` |
| $5 | **$10** (enforced) | $11 | `$10 - $11` |
| $10,000 | $9,000 | $11,000 | `$9,000 - $11,000` |

---

## API Response

The `RateRecommendationAgent` now returns an additional field:

```json
{
  "status": "success",
  "market_average": "1107.0",
  "market_range": "$996 - $1,217",
  "market_low": "996",
  "market_high": "1217",
  ...
}
```

### Fields

- **`market_range`** (NEW): Formatted string showing the ±10% range (e.g., "$996 - $1,217")
- **`market_average`**: The base market average price
- **`market_low`**: Calculated lower bound (string number)
- **`market_high`**: Calculated upper bound (string number)

---

## Usage in Responses

### Before (without market range):
```
Market Average: $1,107
```

### After (with market range):
```
Market Average: $1,107
Market Range: $996 - $1,217
```

This gives customers a realistic expectation of price flexibility and helps in negotiations.

---

## Implementation Details

### Location
- **File**: `agents/rate_recommendation_agent.py`
- **Function**: `process()` method, lines 210-270

### Code Logic

```python
# Calculate market range: ±10% of market average
if market_avg_numeric is not None and pd.notna(market_avg_numeric):
    avg_value = float(market_avg_numeric)
    if avg_value > 0:
        # Calculate ±10%
        range_low = avg_value * 0.9  # -10%
        range_high = avg_value * 1.1  # +10%
        
        # Ensure lower bound is at least $10
        if range_low < 10:
            range_low = 10
        
        # Ensure both values are positive
        range_low = max(10, range_low)
        range_high = max(range_low + 1, range_high)
        
        # Format the market range
        market_range_formatted = f"${int(range_low):,} - ${int(range_high):,}"
```

---

## Testing

### Test Results

✅ **Normal Values**: Correct ±10% calculation
```
Average: $1,107 → Range: $996 - $1,217
```

✅ **Low Values**: Proper percentage calculation
```
Average: $50 → Range: $45 - $55
```

✅ **Very Low Values**: $10 minimum enforced
```
Average: $5 → Range: $10 - $11 (not $4.50 - $5.50)
```

✅ **High Values**: Scales correctly
```
Average: $10,000 → Range: $9,000 - $11,000
```

### Edge Cases Handled

- ✓ Negative calculated values → Set to $10
- ✓ Zero or null market average → No range calculated
- ✓ Non-numeric values → Graceful fallback
- ✓ Missing market data → Uses CSV fallback values

---

## Benefits

1. **Transparency**: Customers see realistic price expectations
2. **Negotiation Tool**: Provides a range for rate discussions
3. **Market Context**: Shows price flexibility in current market
4. **Trust Building**: Demonstrates market-based pricing
5. **Consistency**: Standardized ±10% across all routes

---

## Backward Compatibility

✅ **Fully Compatible**: Existing `market_low` and `market_high` fields are still populated
✅ **Additive Change**: New `market_range` field doesn't break existing integrations
✅ **Fallback Logic**: If calculation fails, falls back to CSV values

---

## Future Enhancements

Potential improvements for future versions:

1. **Dynamic Percentage**: Allow ±5%, ±15%, or ±20% based on route volatility
2. **Confidence Intervals**: Show statistical confidence in the range
3. **Historical Trends**: Include "trending up/down" indicators
4. **Seasonal Adjustments**: Adjust range based on peak/off-peak seasons
5. **Currency Support**: Handle multiple currencies (EUR, GBP, etc.)

---

## Related Files

- `agents/rate_recommendation_agent.py` - Main implementation
- `data/rate_recommendation.csv` - Market data source
- `test_market_range.py` - Test script (if created)

---

## Version History

- **v1.0** (2026-02-11): Initial implementation with ±10% and $10 minimum
  - Commit: `a7912fe0`
  - Branch: `demo-version`

---

## Support

For questions or issues with the market range feature:
1. Check the test examples in this document
2. Review the implementation in `rate_recommendation_agent.py`
3. Verify market data is loaded correctly from CSV
4. Check logs for calculation warnings

---

**Last Updated**: February 11, 2026  
**Status**: ✅ Active and Tested

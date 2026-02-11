#!/usr/bin/env python3
"""
Test Market Range Calculation
Verify that market range is calculated correctly with ±10% and minimum $10 lower bound
"""

from agents.rate_recommendation_agent import RateRecommendationAgent

def test_market_range_calculation():
    """Test various market average values"""
    
    print("=" * 70)
    print("TESTING MARKET RANGE CALCULATION (±10% with $10 minimum)")
    print("=" * 70)
    
    agent = RateRecommendationAgent()
    
    if not agent.data_loaded:
        print("❌ Rate data not loaded. Cannot test.")
        return
    
    # Test with a real route
    test_cases = [
        {
            "name": "Standard Route (AEAUH → AUBNE, 20DC)",
            "origin": "AEAUH",
            "destination": "AUBNE",
            "container_type": "20DC"
        },
        {
            "name": "High Value Route (if available)",
            "origin": "CNSHG",
            "destination": "USLAX",
            "container_type": "40HC"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'='*70}")
        
        result = agent.process(test_case)
        
        if result.get("status") == "success" or result.get("market_average"):
            print(f"\n✅ Route: {result['origin_code']} → {result['destination_code']}")
            print(f"   Container: {result['container_type']}")
            print(f"\n📊 Market Data:")
            
            market_avg = result.get("market_average")
            market_range = result.get("market_range")
            market_low = result.get("market_low")
            market_high = result.get("market_high")
            
            if market_avg:
                try:
                    avg_val = float(market_avg)
                    print(f"   Market Average: ${avg_val:,.2f}")
                    
                    if market_range:
                        print(f"   Market Range (±10%): {market_range}")
                    
                    if market_low and market_high:
                        low_val = float(market_low)
                        high_val = float(market_high)
                        
                        # Verify calculations
                        expected_low = max(10, avg_val * 0.9)
                        expected_high = avg_val * 1.1
                        
                        print(f"\n🔍 Verification:")
                        print(f"   Lower Bound: ${low_val:,.2f}")
                        print(f"   Expected: ${expected_low:,.2f} (max of $10 or -10%)")
                        print(f"   ✓ Correct" if abs(low_val - expected_low) < 1 else f"   ✗ Mismatch!")
                        
                        print(f"\n   Upper Bound: ${high_val:,.2f}")
                        print(f"   Expected: ${expected_high:,.2f} (+10%)")
                        print(f"   ✓ Correct" if abs(high_val - expected_high) < 1 else f"   ✗ Mismatch!")
                        
                        # Check minimum $10 rule
                        if low_val >= 10:
                            print(f"\n   ✅ Lower bound is ≥ $10 (${low_val:,.2f})")
                        else:
                            print(f"\n   ❌ Lower bound is < $10 (${low_val:,.2f})")
                        
                        # Check positive values
                        if low_val > 0 and high_val > 0:
                            print(f"   ✅ Both values are positive")
                        else:
                            print(f"   ❌ Negative values detected!")
                            
                except (ValueError, TypeError) as e:
                    print(f"   ⚠️ Could not parse values: {e}")
            else:
                print(f"   ⚠️ No market average available")
        else:
            print(f"\n⚠️ No data found for this route")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
    
    print(f"\n{'='*70}")
    print("EDGE CASE TESTS")
    print(f"{'='*70}")
    
    # Test edge cases manually
    edge_cases = [
        {"avg": 1000, "expected_low": 900, "expected_high": 1100, "name": "Normal case ($1000)"},
        {"avg": 50, "expected_low": 45, "expected_high": 55, "name": "Low value ($50)"},
        {"avg": 5, "expected_low": 10, "expected_high": 5.5, "name": "Very low ($5 - should enforce $10 minimum)"},
        {"avg": 100, "expected_low": 90, "expected_high": 110, "name": "Round number ($100)"},
        {"avg": 10000, "expected_low": 9000, "expected_high": 11000, "name": "High value ($10,000)"},
    ]
    
    for case in edge_cases:
        avg = case["avg"]
        range_low = avg * 0.9
        range_high = avg * 1.1
        
        # Apply minimum $10 rule
        if range_low < 10:
            range_low = 10
        
        # Ensure positive
        range_low = max(10, range_low)
        range_high = max(range_low + 1, range_high)
        
        print(f"\n{case['name']}:")
        print(f"   Average: ${avg:,.2f}")
        print(f"   Calculated Range: ${int(range_low):,} - ${int(range_high):,}")
        print(f"   ✓ Lower ≥ $10: {range_low >= 10}")
        print(f"   ✓ Both positive: {range_low > 0 and range_high > 0}")
        print(f"   ✓ High > Low: {range_high > range_low}")


if __name__ == "__main__":
    test_market_range_calculation()

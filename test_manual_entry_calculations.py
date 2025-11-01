"""
Test manual entry price calculations
Verify all fields update correctly
"""

print("="*70)
print("TESTING MANUAL ENTRY PRICE CALCULATIONS")
print("="*70)
print()

# Simulated values
btc_amount = 0.00004323
current_price = 109839.76
manual_entry_price = 70000.00

# Settings
profit_target_pct = 1.5
buy_fee_pct = 0.6
sell_fee_pct = 0.6

print("📊 Input Values:")
print(f"   BTC Amount:          {btc_amount:.8f} BTC")
print(f"   Current Price:       ${current_price:,.2f}")
print(f"   Manual Entry Price:  ${manual_entry_price:,.2f}")
print()

# Calculate cost basis (Initial Investment)
cost_basis = btc_amount * manual_entry_price
print("="*70)
print("STEP 1: INITIAL INVESTMENT (Cost Basis)")
print("="*70)
print(f"   Formula: BTC Amount × Manual Entry Price")
print(f"   Calculation: {btc_amount:.8f} × ${manual_entry_price:,.2f}")
print(f"   ✅ Initial Investment: ${cost_basis:.2f}")
print()

# Calculate TARGET PRICE
print("="*70)
print("STEP 2: TARGET PRICE")
print("="*70)
print(f"   Formula: Entry Price × (1 + (Profit% + BuyFee% + SellFee%) / 100)")
target_price = manual_entry_price * (1 + (profit_target_pct + buy_fee_pct + sell_fee_pct) / 100)
print(f"   Calculation: ${manual_entry_price:,.2f} × (1 + ({profit_target_pct} + {buy_fee_pct} + {sell_fee_pct}) / 100)")
print(f"   Calculation: ${manual_entry_price:,.2f} × 1.027")
print(f"   ✅ Target Price: ${target_price:,.2f}")
print()

# Calculate STOP LOSS
print("="*70)
print("STEP 3: STOP LOSS")
print("="*70)
stop_loss_pct = 1.0
stop_price = manual_entry_price * (1 - stop_loss_pct / 100)
print(f"   Formula: Entry Price × (1 - Stop Loss % / 100)")
print(f"   Calculation: ${manual_entry_price:,.2f} × (1 - {stop_loss_pct} / 100)")
print(f"   ✅ Stop Price: ${stop_price:,.2f}")
print()

# Calculate VALUE AT TARGET
print("="*70)
print("STEP 4: VALUE AT TARGET")
print("="*70)
value_at_target = cost_basis * (1 + profit_target_pct / 100)
print(f"   Formula: Cost Basis × (1 + Profit Target % / 100)")
print(f"   Calculation: ${cost_basis:.2f} × (1 + {profit_target_pct} / 100)")
print(f"   ✅ Value at Target: ${value_at_target:.2f}")
print()

# Calculate SELL FEE
print("="*70)
print("STEP 5: SELL FEE")
print("="*70)
sell_fee = value_at_target * (sell_fee_pct / 100)
print(f"   Formula: Value at Target × Sell Fee % / 100")
print(f"   Calculation: ${value_at_target:.2f} × {sell_fee_pct} / 100")
print(f"   ✅ Sell Fee: ${sell_fee:.2f}")
print()

# Calculate FINAL PROFIT
print("="*70)
print("STEP 6: FINAL PROFIT")
print("="*70)
final_profit = value_at_target - cost_basis - sell_fee
print(f"   Formula: Value at Target - Cost Basis - Sell Fee")
print(f"   Calculation: ${value_at_target:.2f} - ${cost_basis:.2f} - ${sell_fee:.2f}")
print(f"   ✅ Final Profit: ${final_profit:+.2f}")
print()

# Calculate CURRENT P/L
print("="*70)
print("STEP 7: CURRENT P/L (if sold now)")
print("="*70)
current_value = btc_amount * current_price
current_sell_fee = current_value * (sell_fee_pct / 100)
current_pl = current_value - cost_basis - current_sell_fee
current_pl_pct = (current_pl / cost_basis) * 100
print(f"   Current BTC Value: {btc_amount:.8f} × ${current_price:,.2f} = ${current_value:.2f}")
print(f"   Sell Fee if sold now: ${current_sell_fee:.2f}")
print(f"   Current P/L: ${current_value:.2f} - ${cost_basis:.2f} - ${current_sell_fee:.2f}")
print(f"   ✅ Current P/L: ${current_pl:+.2f} ({current_pl_pct:+.2f}%)")
print()

# Summary
print("="*70)
print("SUMMARY - ALL FIELDS")
print("="*70)
print()
print(f"📊 Position:")
print(f"   BTC Amount:              {btc_amount:.8f} BTC")
print(f"   Entry Price:             ${manual_entry_price:,.2f}")
print(f"   Current Price:           ${current_price:,.2f}")
print()
print(f"💰 Investment:")
print(f"   Initial Investment:      ${cost_basis:.2f} ✅")
print(f"   Buy Fee (0.6%):          $0.00 ✅")
print(f"   Actual BTC Purchase:     ${cost_basis:.2f} ✅")
print()
print(f"📈 Current Status:")
print(f"   Current BTC Value:       ${current_value:.2f}")
print(f"   Current P/L:             ${current_pl:+.2f} ({current_pl_pct:+.2f}%) ✅")
print()
print(f"🎯 At Target:")
print(f"   Target Price:            ${target_price:,.2f} ✅")
print(f"   Value at Target:         ${value_at_target:.2f} ✅")
print(f"   Sell Fee (0.6%):         ${sell_fee:.2f} ✅")
print(f"   Final Profit:            ${final_profit:+.2f} ✅")
print()
print(f"🛑 Stop Loss:")
print(f"   Stop Price:              ${stop_price:,.2f} ✅")
print()
print("="*70)
print()

# Test with different entry prices
print("="*70)
print("TESTING WITH DIFFERENT ENTRY PRICES")
print("="*70)
print()

test_entries = [50000, 70000, 90000, 109839.76]

for entry in test_entries:
    cost = btc_amount * entry
    target = entry * (1 + (profit_target_pct + buy_fee_pct + sell_fee_pct) / 100)
    stop = entry * (1 - stop_loss_pct / 100)
    value_target = cost * (1 + profit_target_pct / 100)
    fee = value_target * (sell_fee_pct / 100)
    profit = value_target - cost - fee
    
    current_val = btc_amount * current_price
    current_fee = current_val * (sell_fee_pct / 100)
    current_profit = current_val - cost - current_fee
    current_profit_pct = (current_profit / cost) * 100
    
    print(f"Entry Price: ${entry:,.2f}")
    print(f"  Initial Investment:  ${cost:.2f}")
    print(f"  Target Price:        ${target:,.2f}")
    print(f"  Stop Loss:           ${stop:,.2f}")
    print(f"  Final Profit:        ${profit:+.2f}")
    print(f"  Current P/L:         ${current_profit:+.2f} ({current_profit_pct:+.2f}%)")
    print()

print("="*70)
print("✅ ALL CALCULATIONS COMPLETE")
print("="*70)

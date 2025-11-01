"""
Trading Helper Functions
Simplified interfaces for buy, sell, and average entry price calculations
"""
from coinbase_complete_api import CoinbaseCompleteAPI
from config import Config
import uuid


class TradingHelpers:
    """Helper functions for trading operations"""
    
    def __init__(self):
        self.api = CoinbaseCompleteAPI()
    
    def buy_btc_market(self, usd_amount):
        """
        Buy BTC with USD at market price
        
        Args:
            usd_amount (float): Amount of USD to spend
            
        Returns:
            dict: Order response or error
        """
        try:
            client_order_id = str(uuid.uuid4())
            
            # Market order configuration
            order_configuration = {
                "market_market_ioc": {
                    "quote_size": str(usd_amount)
                }
            }
            
            # Create buy order
            response = self.api.create_order(
                client_order_id=client_order_id,
                product_id="BTC-USD",
                side="BUY",
                order_configuration=order_configuration
            )
            
            if response.get('success'):
                print(f"\n✅ BUY ORDER EXECUTED")
                print(f"   Amount: ${usd_amount:.2f}")
                print(f"   Order ID: {response.get('order_id', 'N/A')}")
                return {
                    'success': True,
                    'order_id': response.get('order_id'),
                    'response': response
                }
            else:
                error_msg = response.get('error_response', {}).get('message', 'Unknown error')
                print(f"\n❌ BUY ORDER FAILED: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'response': response
                }
                
        except Exception as e:
            print(f"\n❌ Error creating buy order: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def sell_btc_market(self, btc_amount):
        """
        Sell BTC for USD at market price
        
        Args:
            btc_amount (float): Amount of BTC to sell
            
        Returns:
            dict: Order response or error
        """
        try:
            client_order_id = str(uuid.uuid4())
            
            # Market order configuration
            order_configuration = {
                "market_market_ioc": {
                    "base_size": str(btc_amount)
                }
            }
            
            # Create sell order
            response = self.api.create_order(
                client_order_id=client_order_id,
                product_id="BTC-USD",
                side="SELL",
                order_configuration=order_configuration
            )
            
            if response.get('success'):
                print(f"\n✅ SELL ORDER EXECUTED")
                print(f"   BTC Amount: {btc_amount:.8f}")
                print(f"   Order ID: {response.get('order_id', 'N/A')}")
                return {
                    'success': True,
                    'order_id': response.get('order_id'),
                    'response': response
                }
            else:
                error_msg = response.get('error_response', {}).get('message', 'Unknown error')
                print(f"\n❌ SELL ORDER FAILED: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'response': response
                }
                
        except Exception as e:
            print(f"\n❌ Error creating sell order: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_average_entry_price(self, product_id='BTC-USD', limit=100):
        """
        Calculate average entry price from historical fills
        
        Args:
            product_id (str): Product ID (default: BTC-USD)
            limit (int): Number of fills to retrieve
            
        Returns:
            dict: {
                'average_price': float,
                'total_btc_bought': float,
                'total_usd_spent': float,
                'buy_count': int,
                'fills': list
            }
        """
        try:
            print(f"\n🔄 Calculating average entry price for {product_id}...")
            
            # Get historical fills
            fills_response = self.api.list_fills(product_id=product_id, limit=limit)
            
            if not fills_response.get('fills'):
                print("❌ No fills found")
                return {
                    'average_price': 0,
                    'total_btc_bought': 0,
                    'total_usd_spent': 0,
                    'buy_count': 0,
                    'fills': []
                }
            
            fills = fills_response.get('fills', [])
            
            # Calculate weighted average for BUY orders
            total_btc_bought = 0.0
            total_usd_spent = 0.0
            buy_count = 0
            buy_fills = []
            
            for fill in fills:
                side = fill.get('side')
                size = float(fill.get('size', 0))
                price = float(fill.get('price', 0))
                
                if side == 'BUY':
                    cost = size * price
                    total_btc_bought += size
                    total_usd_spent += cost
                    buy_count += 1
                    buy_fills.append(fill)
                    
                    print(f"  BUY: {size:.8f} BTC @ ${price:,.2f} = ${cost:,.2f}")
            
            if total_btc_bought > 0:
                average_price = total_usd_spent / total_btc_bought
                
                print(f"\n✅ Average Entry Price Calculated:")
                print(f"   Total BTC Bought: {total_btc_bought:.8f}")
                print(f"   Total USD Spent:  ${total_usd_spent:,.2f}")
                print(f"   Number of Buys:   {buy_count}")
                print(f"   ⭐ AVERAGE PRICE: ${average_price:,.2f}")
                
                return {
                    'average_price': average_price,
                    'total_btc_bought': total_btc_bought,
                    'total_usd_spent': total_usd_spent,
                    'buy_count': buy_count,
                    'fills': buy_fills
                }
            else:
                print("❌ No BUY orders found")
                return {
                    'average_price': 0,
                    'total_btc_bought': 0,
                    'total_usd_spent': 0,
                    'buy_count': 0,
                    'fills': []
                }
                
        except Exception as e:
            print(f"❌ Error calculating average entry price: {e}")
            return {
                'average_price': 0,
                'total_btc_bought': 0,
                'total_usd_spent': 0,
                'buy_count': 0,
                'fills': [],
                'error': str(e)
            }
    
    def get_break_even_price(self, average_entry_price, sell_fee_rate=0.006):
        """
        Calculate break-even price (price needed to not lose money)
        
        Args:
            average_entry_price (float): Average price you bought at
            sell_fee_rate (float): Sell fee rate (default: 0.6% = 0.006)
            
        Returns:
            dict: {
                'break_even_price': float,
                'average_entry': float,
                'sell_fee_rate': float
            }
        """
        # Break-even is entry price adjusted for sell fee
        # Price = Entry / (1 - sell_fee)
        break_even = average_entry_price / (1 - sell_fee_rate)
        
        return {
            'break_even_price': break_even,
            'average_entry': average_entry_price,
            'sell_fee_rate': sell_fee_rate,
            'fee_impact': break_even - average_entry_price
        }
    
    def analyze_position(self, current_price, average_entry_price, btc_amount):
        """
        Analyze current position profitability
        
        Args:
            current_price (float): Current BTC price
            average_entry_price (float): Your average entry price
            btc_amount (float): Amount of BTC you hold
            
        Returns:
            dict: Complete position analysis
        """
        # Current value
        current_value = btc_amount * current_price
        
        # Cost basis
        cost_basis = btc_amount * average_entry_price
        
        # Break-even analysis
        break_even_info = self.get_break_even_price(average_entry_price)
        break_even_price = break_even_info['break_even_price']
        
        # P/L if sold now
        sell_fee = current_value * 0.006
        net_proceeds = current_value - sell_fee
        profit_loss = net_proceeds - cost_basis
        profit_loss_pct = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0
        
        # Status
        if current_price < break_even_price:
            status = "🔴 LOSS ZONE"
            recommendation = "Don't sell - you'll lose money"
        elif current_price == break_even_price:
            status = "⚖️  BREAK-EVEN"
            recommendation = "Selling now breaks even (no profit/loss)"
        else:
            status = "🟢 PROFIT ZONE"
            recommendation = "Safe to sell - you'll make profit"
        
        return {
            'current_price': current_price,
            'average_entry': average_entry_price,
            'break_even_price': break_even_price,
            'btc_amount': btc_amount,
            'current_value': current_value,
            'cost_basis': cost_basis,
            'profit_loss': profit_loss,
            'profit_loss_pct': profit_loss_pct,
            'status': status,
            'recommendation': recommendation,
            'is_profitable': current_price > break_even_price
        }


def main():
    """Example usage"""
    helpers = TradingHelpers()
    
    # Calculate average entry price from fills
    avg_data = helpers.calculate_average_entry_price()
    
    if avg_data['average_price'] > 0:
        # Analyze position
        current_price = 109000  # Example
        analysis = helpers.analyze_position(
            current_price=current_price,
            average_entry_price=avg_data['average_price'],
            btc_amount=avg_data['total_btc_bought']
        )
        
        print("\n" + "="*70)
        print("POSITION ANALYSIS")
        print("="*70)
        print(f"Status: {analysis['status']}")
        print(f"Break-Even Price: ${analysis['break_even_price']:,.2f}")
        print(f"Current Price: ${analysis['current_price']:,.2f}")
        print(f"P/L: ${analysis['profit_loss']:+,.2f} ({analysis['profit_loss_pct']:+.2f}%)")
        print(f"Recommendation: {analysis['recommendation']}")


if __name__ == '__main__':
    main()

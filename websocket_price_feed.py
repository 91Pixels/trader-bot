"""
WebSocket Price Feed for Coinbase
Real-time price updates with latency monitoring
"""
import json
import time
import threading
import websocket
from datetime import datetime


class CoinbaseWebSocketFeed:
    """WebSocket connection to Coinbase for real-time price updates"""
    
    def __init__(self, product_id="BTC-USD"):
        self.product_id = product_id
        self.ws = None
        self.is_connected = False
        self.last_price = 0.0
        self.last_update_time = 0
        self.latency_ms = 0
        self.price_callback = None
        self.error_callback = None
        self.thread = None
        self.should_run = False
        
        # Latency tracking
        self.ping_sent_time = 0
        self.last_message_time = 0
        
    def on_message(self, ws, message):
        """Handle incoming WebSocket message"""
        try:
            receive_time = time.time()
            data = json.loads(message)
            
            # Calculate latency (time since last ping or message)
            if self.last_message_time > 0:
                self.latency_ms = int((receive_time - self.last_message_time) * 1000)
            
            self.last_message_time = receive_time
            
            # Handle ticker updates
            if data.get('type') == 'ticker':
                price_str = data.get('price')
                if price_str:
                    self.last_price = float(price_str)
                    self.last_update_time = receive_time
                    
                    # Call callback if registered
                    if self.price_callback:
                        self.price_callback(self.last_price, self.latency_ms)
                        
        except Exception as e:
            print(f"❌ WebSocket message error: {e}")
            if self.error_callback:
                self.error_callback(str(e))
    
    def on_error(self, ws, error):
        """Handle WebSocket error"""
        print(f"❌ WebSocket error: {error}")
        if self.error_callback:
            self.error_callback(str(error))
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"🔌 WebSocket closed: {close_status_code} - {close_msg}")
        self.is_connected = False
    
    def on_open(self, ws):
        """Handle WebSocket open"""
        print(f"✅ WebSocket connected to Coinbase")
        self.is_connected = True
        self.last_message_time = time.time()
        
        # Subscribe to ticker channel
        subscribe_message = {
            "type": "subscribe",
            "product_ids": [self.product_id],
            "channels": ["ticker"]
        }
        ws.send(json.dumps(subscribe_message))
        print(f"📡 Subscribed to {self.product_id} ticker")
    
    def connect(self, price_callback=None, error_callback=None):
        """Start WebSocket connection in a separate thread"""
        if self.is_connected:
            print("⚠️ WebSocket already connected")
            return
        
        self.price_callback = price_callback
        self.error_callback = error_callback
        self.should_run = True
        
        def run_websocket():
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(
                "wss://ws-feed.exchange.coinbase.com",
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # Run with reconnect
            while self.should_run:
                try:
                    self.ws.run_forever(ping_interval=20, ping_timeout=10)
                except Exception as e:
                    print(f"❌ WebSocket connection error: {e}")
                    if self.error_callback:
                        self.error_callback(str(e))
                
                if self.should_run:
                    print("🔄 Reconnecting WebSocket in 5 seconds...")
                    time.sleep(5)
        
        self.thread = threading.Thread(target=run_websocket, daemon=True)
        self.thread.start()
        print("🚀 WebSocket thread started")
    
    def disconnect(self):
        """Disconnect WebSocket"""
        print("🔌 Disconnecting WebSocket...")
        self.should_run = False
        if self.ws:
            self.ws.close()
        self.is_connected = False
    
    def get_price(self):
        """Get last received price"""
        return self.last_price
    
    def get_latency(self):
        """Get current latency in milliseconds"""
        return self.latency_ms
    
    def is_price_stale(self, max_age_seconds=2):
        """Check if price data is stale"""
        if self.last_update_time == 0:
            return True
        age = time.time() - self.last_update_time
        return age > max_age_seconds


# Test the WebSocket feed
if __name__ == "__main__":
    print("🧪 Testing Coinbase WebSocket Feed...")
    
    def on_price_update(price, latency):
        print(f"💰 Price: ${price:,.2f} | Latency: {latency}ms")
    
    def on_error(error):
        print(f"❌ Error: {error}")
    
    feed = CoinbaseWebSocketFeed()
    feed.connect(price_callback=on_price_update, error_callback=on_error)
    
    try:
        # Run for 30 seconds
        print("\n📊 Receiving price updates for 30 seconds...")
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n⏹️ Stopping...")
    finally:
        feed.disconnect()
        print("✅ Test complete")

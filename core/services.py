# In core/services.py
import random

class WalmartClient:
    def __init__(self):
        # Placeholder for API key and base URL
        self.api_key = "your_api_key"
        self.base_url = "https://mock-walmart-api.com"

    def place_order(self, order_data):
        # Simulate order placement with a randomized confirmation
        if random.choice([True, False]):
            return {"status": "success", "confirmation_number": "WM" + str(random.randint(1000, 9999))}
        else:
            return {"status": "failed", "message": "Order could not be processed"}

# In core/services.py (continuation)
class VesselPositionService:
    def __init__(self):
        self.base_url = "https://mock-vessel-tracking.com"

    def get_vessel_position(self, vessel_id):
        # Simulate vessel position data
        return {
            "vessel_id": vessel_id,
            "latitude": round(random.uniform(-90, 90), 6),
            "longitude": round(random.uniform(-180, 180), 6)
        }

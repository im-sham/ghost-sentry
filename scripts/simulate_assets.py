import httpx
import time
import random
import sys

def run_simulation():
    print("Starting Asset Telemetry Simulation...")
    asset_ids = ["drone-alpha", "drone-beta", "ugv-sierra"]
    
    # Initial locations around LAX
    locs = {
        "drone-alpha": [33.94, -118.41],
        "drone-beta": [33.95, -118.40],
        "ugv-sierra": [33.93, -118.42]
    }
    
    # Initial telemetry
    telemetry = {aid: {"battery": 1.0, "signal": 1.0} for aid in asset_ids}

    try:
        while True:
            for aid in asset_ids:
                # Random drift for location
                locs[aid][0] += random.uniform(-0.0001, 0.0001)
                locs[aid][1] += random.uniform(-0.0001, 0.0001)
                
                # Slowly drain battery
                telemetry[aid]["battery"] = max(0, telemetry[aid]["battery"] - 0.001)
                
                # Fluctuate signal
                telemetry[aid]["signal"] = max(0.2, min(1.0, telemetry[aid]["signal"] + random.uniform(-0.05, 0.05)))
                
                try:
                    params = {
                        "asset_id": aid,
                        "lat": locs[aid][0],
                        "lon": locs[aid][1],
                        "battery": telemetry[aid]["battery"],
                        "signal": telemetry[aid]["signal"]
                    }
                    response = httpx.post("http://localhost:8000/assets/telemetry", params=params)
                    if response.status_code == 200:
                        print(f"[{time.strftime('%H:%M:%S')}] Pushed telemetry for {aid}: {locs[aid]} Bat: {telemetry[aid]['battery']:.2f}")
                    else:
                        print(f"Error pushing telemetry for {aid}: {response.status_code}")
                except Exception as e:
                    print(f"Failed to connect to backend: {e}")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nSimulation stopped.")

if __name__ == "__main__":
    run_simulation()

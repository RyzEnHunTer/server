import os
import pytz
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import Optional

app = FastAPI(title="Hunter License Server")

# 🔐 MongoDB Configuration - Use environment variables for production
# Fallback to the provided URI for development/initial setup
DEFAULT_MONGO_URI = "mongodb+srv://ryzen_hunter:Ryzhunteryt098%24%40@hunterbot.beaj4bf.mongodb.net/?retryWrites=true&w=majority&appName=hunterbot"
MONGO_URI = os.getenv("MONGODB_URI", DEFAULT_MONGO_URI)

# Initialize MongoDB Connection
try:
    client = MongoClient(MONGO_URI)
    db = client["hunter_bot"]
    licenses_collection = db["licenses"]
    # Test connection
    client.admin.command('ping')
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

class LicenseRequest(BaseModel):
    license_key: str
    device_id: str

class VerifyResponse(BaseModel):
    valid: bool
    reason: Optional[str] = None

@app.get("/")
def home():
    return {"status": "Hunter License Server Running 🚀", "server_time": datetime.now(pytz.UTC).isoformat()}

@app.post("/verify", response_model=VerifyResponse)
def verify_license(data: LicenseRequest):
    try:
        # 1. Check if license exists
        license_doc = licenses_collection.find_one({"license_key": data.license_key})
        
        if not license_doc:
            return {"valid": False, "reason": "Invalid license key"}

        # 2. Check status (active, inactive, banned)
        status = license_doc.get("status", "inactive")
        if status == "banned":
            return {"valid": False, "reason": "License has been banned"}
        if status != "active":
            return {"valid": False, "reason": "License is inactive"}

        # 3. Expiry check (Always use UTC for server-side dates)
        try:
            expiry_str = license_doc.get("expiry")
            if not expiry_str:
                return {"valid": False, "reason": "Missing expiry date"}
            
            expiry_date = datetime.fromisoformat(expiry_str)
            if expiry_date.tzinfo is None:
                expiry_date = pytz.UTC.localize(expiry_date)
            
            if datetime.now(pytz.UTC) > expiry_date:
                return {"valid": False, "reason": "License has expired"}
        except ValueError:
            return {"valid": False, "reason": "System error: Invalid expiry format"}

        # 4. 🔐 Device binding
        stored_device_id = license_doc.get("device_id")
        
        if not stored_device_id:
            # First success - Bind current device_id
            licenses_collection.update_one(
                {"license_key": data.license_key},
                {"$set": {"device_id": data.device_id}}
            )
            return {"valid": True, "reason": "Device bound and verified"}
        
        elif stored_device_id != data.device_id:
            return {"valid": False, "reason": "Device mismatch - This license belongs to another PC"}

        return {"valid": True, "reason": "Verified"}

    except Exception as e:
        print(f"Error during verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
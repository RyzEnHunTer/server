from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime, timedelta
import os
import pytz

IST = pytz.timezone('Asia/Kolkata')
# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://ryzen_hunter:Ryzhunteryt098%24%40@hunterbot.beaj4bf.mongodb.net/hunter_bot?retryWrites=true&w=majority&appName=hunterbot")
client = MongoClient(MONGO_URI)
db = client.hunter_bot
licenses = db.licenses

app = FastAPI()

class VerifyRequest(BaseModel):
    license_key: str
    device_id: str

@app.get("/")
def home():
    return {"status": "Hunter Bot License Server Online"}

@app.post("/verify")
def verify_license(req: VerifyRequest):
    license = licenses.find_one({"key": req.license_key})
    
    if not license:
        return {"valid": False, "reason": "Invalid license key"}
    
    if license.get("status") == "revoked":
        return {"valid": False, "reason": "License has been revoked"}
        
    # Check if key is already bound to a different device
    if license.get("device_id") and license.get("device_id") != req.device_id:
        return {"valid": False, "reason": "Key bound to another device"}
        
    # Bind device if not bound
    if not license.get("device_id"):
        licenses.update_one({"key": req.license_key}, {"$set": {"device_id": req.device_id, "activated_at": datetime.now(IST)}})
        
    # Check expiry
    expiry = license.get("expires_at")
    if expiry:
        # Ensure expiry is timezone aware for comparison
        if expiry.tzinfo is None:
            expiry = IST.localize(expiry)
            
        if datetime.now(IST) > expiry:
            return {"valid": False, "reason": f"License expired on {expiry.strftime('%Y-%m-%d %H:%M')}"}
            
    nickname = license.get("nickname", "Premium User")
    return {"valid": True, "reason": f"Welcome, {nickname}!", "expires_at": expiry}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

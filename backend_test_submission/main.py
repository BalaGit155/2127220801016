import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from logging_middleware import logger



app = FastAPI()

db = {} # for in-memory storage

# for short url request
class urlRequest(BaseModel): 
    url: str
    validity: Optional[int] = 30 
    shortcode: Optional[str] = None


# to craeate short url
@app.post("/shorturls")
def create_short_url(data:urlRequest):
    code = data.shortcode 
    if code in db:
        raise HTTPException(status_code=400, detail="Shortcode already exists")
    
    expiry = datetime.utcnow()+timedelta(minutes=data.validity)

    db[code] = {
        "url": data.url,
        "expiry": expiry,
        "created": datetime.utcnow(),
    }

    logger.log("backend", "info", "controller", f"short code created: {code} for url: {data.url}")

    return {
        "shortlink":f"http://localhost:8000/{code}",
        "expiry": expiry.isoformat(),
    }
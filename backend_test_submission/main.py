import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from logging_middleware import logger
from fastapi.responses import RedirectResponse



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
        "clicks":[]
    }

    logger.log("backend", "info", "controller", f"short code created: {code} for url: {data.url}")

    return {
        "shortlink":f"http://localhost:8000/{code}",
        "expiry": expiry.isoformat(),
    }

# to redirect to original url
@app.get("/{shortcode}")
def redirect(shortcode:str, request: Request):
    if shortcode not in db:
        logger.log("backend","error","db",f"{shortcode} not found")
        raise HTTPException(status_code=404, detail="Shortcode not found")
    
    if datetime.utcnow() > db[shortcode]["expiry"]:
        logger.log("backend","error","db",f"{shortcode} expired")
        raise HTTPException(status_code=410, detail="Shortcode expired")
       
    db[shortcode]["clicks"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "referrer": request.headers.get("referer", "unknown"),
        "location": "unkonwn"
    })

    RedirectResponse(url=db[shortcode]["url"])

    return {"redirect": db[shortcode]["url"]}

# to get statistics
@app.get("/shorturls/{shortcode}")
def stats(shortcode: str):
    if shortcode not in db:
        logger.log("backend", "error", "controller", f"Stats failed: {shortcode}")
        raise HTTPException(status_code=404, detail="Shortcode not found")

    entry = db[shortcode]
    return {
        "url": entry["url"],
        "created": entry["created"],
        "expiry": entry["expiry"],
        "clicks": entry["clicks"],
        "clickCount": len(entry["clicks"])
    }
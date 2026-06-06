from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "telemetry.json"

with open(DATA_FILE, "r") as f:
    telemetry = json.load(f)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.post("/")
def metrics(data: RequestBody):

    result = {}

    for region in data.regions:

        rows = [
            r for r in telemetry
            if r["region"] == region
        ]

        latencies = [
            r["latency_ms"]
            for r in rows
        ]

        uptimes = [
            r["uptime_pct"]
            for r in rows
        ]

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(
                1 for x in latencies
                if x > data.threshold_ms
            )
        }

    return result
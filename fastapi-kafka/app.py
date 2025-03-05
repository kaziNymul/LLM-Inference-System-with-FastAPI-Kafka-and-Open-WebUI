from fastapi import FastAPI, Request
import requests
import json
import os
import random
from confluent_kafka import Producer

app = FastAPI()

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka.kafka.svc.cluster.local:9092")
producer_conf = {'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS}
producer = Producer(producer_conf)

# LLM endpoints (override via env vars if needed)
LLM_ENDPOINTS = [
    os.environ.get("LLM_ENDPOINT_1", "http://ollama-service.llm.svc.cluster.local:80/api/generate"),
    os.environ.get("LLM_ENDPOINT_2", "http://ollama-service.llm.svc.cluster.local:80/api/generate")
]

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    if not prompt:
        return {"error": "Prompt is required"}

    # Publish prompt to Kafka topic "prompt-requests"
    prompt_message = json.dumps({"prompt": prompt})
    producer.produce("prompt-requests", prompt_message)
    producer.flush()

    # Randomly select one LLM endpoint
    endpoint = random.choice(LLM_ENDPOINTS)

    # We'll accumulate the streamed text in partial_text
    partial_text = ""
    try:
        # Use stream=True to handle NDJSON streaming
        with requests.post(endpoint,
                           json={"model": "llama3.2:1b", "prompt": prompt},
                           timeout=30,
                           stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if line:  # Each line is a small JSON chunk
                    chunk = json.loads(line)
                    partial_text += chunk.get("response", "")
                    # If chunk indicates it's done, break out of the loop
                    if chunk.get("done"):
                        break

        result = partial_text if partial_text else "No response"
    except Exception as e:
        result = f"Error calling LLM: {str(e)}"

    # Publish the result to Kafka topic "inference-results"
    result_message = json.dumps({"prompt": prompt, "result": result})
    producer.produce("inference-results", result_message)
    producer.flush()

    return {"response": result}

@app.get("/status")
async def status():
    return {"status": "FastAPI Kafka Inference API is running"}


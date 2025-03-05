from fastapi import FastAPI, Request
import ray
import requests
from random import choice

# Initialize FastAPI
app = FastAPI()

# Initialize Ray Cluster (update <RAY_HEAD_IP> with your head node's IP or service name)
ray.init(address="ray://localhost:10001")

# List of endpoints for your Ollama instances running on worker nodes.
# Make sure these endpoints are accessible from the FastAPI pod.
OLLAMA_ENDPOINTS = [
    "http://10.244.1.5/api/generate",
    "http://10.244.2.5/api/generate"
]

# Ray remote function that sends the prompt to one Ollama endpoint.
@ray.remote(num_cpus=0.25)
def generate_text(prompt: str):
    # For load balancing, choose one endpoint randomly.
    endpoint = choice(OLLAMA_ENDPOINTS)
    response = requests.post(endpoint, json={"model": "llama3.2:1b", "prompt": prompt})
    return response.json()["response"]

@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    # In this example, we send the prompt to all endpoints and then pick one response.
    # Alternatively, you could send to all workers and then combine or select based on some logic.
    futures = [generate_text.remote(prompt) for _ in OLLAMA_ENDPOINTS]
    responses = ray.get(futures)
    # For example, simply choose the first response:
    return {"response": responses[0]}

# To run the FastAPI service, use Uvicorn:
# uvicorn app:app --host 0.0.0.0 --port 8000


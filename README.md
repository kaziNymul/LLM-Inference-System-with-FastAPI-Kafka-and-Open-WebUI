# LLM Inference System with FastAPI, Kafka, and Open WebUI

## Overview
This repository contains an **LLM (Large Language Model) inference system** deployed in **Kubernetes** using **FastAPI, Kafka, and Open WebUI**. The system is designed to distribute **prompt requests** across multiple LLM pods efficiently. It uses **Kafka** as a message broker for decoupling the request-response cycle and can optionally support **KubeRay** for distributing single prompts across multiple LLM pods.

## Components and Flow

### 1. **User (Web Interface)**
- Users interact with **Open WebUI** (or **Gradio WebUI**, if used).
- They input a **prompt** which is then submitted to FastAPI.

### 2. **FastAPI Kafka (Producer & Consumer)**
- Acts as an **API Gateway**.
- Receives prompt requests from **WebUI**.
- Produces prompt requests into the **Kafka** topic `prompt-requests`.
- Randomly selects one LLM Pod to send the request.
- Optionally, with **KubeRay**, a single prompt can be distributed across multiple LLM pods.
- Once the response is available, it consumes messages from the Kafka topic `inference-results` and forwards them back to WebUI.

### 3. **Kafka Broker**
- Manages the distribution of **prompt-requests** to available **LLM Pods**.
- Stores generated responses in the **inference-results** topic.

### 4. **LLM Pods (Ollama Instances)**
- Each **LLM Pod** runs an instance of **Ollama**.
- Listens for Kafka messages on `prompt-requests`.
- Generates responses and sends them to `inference-results`.

### 5. **KubeRay (Optional)**
- Allows **single prompt** to be split across multiple **LLM pods** for parallel inference.
- Useful for **large models** and resource-heavy inference tasks.

### 6. **Response Flow**
- Once the LLM inference is complete, the response is published to **Kafka (`inference-results`)**.
- FastAPI consumes the result and sends it back to WebUI.
- WebUI displays the response to the user.

## Deployment Guide

### 1. Deploy **Kafka & Zookeeper**
Ensure **Kafka** and **Zookeeper** are running in Kubernetes.

```sh
kubectl create namespace kafka
kubectl apply -f kafka-deployment.yaml
```

### 2. Deploy **LLM Pods (Ollama)**
Apply the Ollama deployment and service:
```sh
kubectl create namespace llm
kubectl apply -f ollama-deployment.yaml
kubectl apply -f ollama-service.yaml
```

### 3. Deploy **FastAPI Kafka**
```sh
kubectl apply -f fastapi-deployment.yaml
kubectl apply -f fastapi-service.yaml
```

### 4. Deploy **Open WebUI**
```sh
kubectl create namespace open-webui
kubectl apply -f open-webui-deployment.yaml
kubectl apply -f open-webui-service.yaml
```

### 5. Access the Web Interface
Find the node's public IP and access Open WebUI at:
```
http://<PUBLIC_NODE_IP>:30081
```
## Open WebUI Integration
### Change LLM Service Endpoint in Open WebUI Deployment
Modify the `OLLAMA_BASE_URL` to:
```yaml
env:
- name: OLLAMA_BASE_URL
  value: "http://ollama-service.llm.svc.cluster.local"
```

## Scaling LLM Pods with **KubeRay**
If **KubeRay** is installed, you can enable **distributed inference** across multiple LLM pods:
```sh
kubectl apply -f kuberay-deployment.yaml
```
This will **distribute a single prompt** across multiple pods for faster inference.

## Debugging
### 1. Check if LLM Pods are Running
```sh
kubectl get pods -n llm
```

### 2. Check Kafka Topics
```sh
kubectl exec -it kafka-<pod-name> -n kafka -- kafka-topics.sh --list --bootstrap-server kafka.kafka.svc.cluster.local:9092
```

### 3. Check Open WebUI Logs
```sh
kubectl logs -f open-webui-deployment-<pod-name> -n open-webui
```

### 4. Flow Diagram
![diagram](https://github.com/user-attachments/assets/6b7bb2d4-e654-4849-9db9-e8fb5bfedf9f)



## Conclusion
This **LLM inference system** provides a **scalable, distributed, and efficient** way to handle **AI inference workloads** using **FastAPI, Kafka, Open WebUI, and KubeRay**. 

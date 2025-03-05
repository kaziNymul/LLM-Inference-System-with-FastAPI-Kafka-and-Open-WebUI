
import gradio as gr
import requests

def submit_prompt(prompt):
    # Replace <NODE_IP> with the external IP of one of your nodes.
    url = "http://fastapi-service.llm.svc.cluster.local:80/generate"
    try:
        response = requests.post(url, json={"prompt": prompt}, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "No response")
    except Exception as e:
        return f"Error: {str(e)}"

iface = gr.Interface(
    fn=submit_prompt,
    inputs=gr.Textbox(label="Enter Prompt"),
    outputs=gr.Textbox(label="Response"),
    title="LLM Inference WebUI"
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=8501)


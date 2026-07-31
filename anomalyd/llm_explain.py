import requests

class LLMExplainer:
    def __init__(self, config):
        self.enabled = config.get("enabled", False)
        self.model = config.get("model", "llama3")
        self.url = config.get("base_url", "http://localhost:11434")

    def explain_batch(self, events, table):
        if not self.enabled or not events:
            return events
        prompt = "Anomalies in " + table + ": "
        for e in events[:3]:
            prompt += e.anomaly_type + "=" + str(e.observed_value) + " "
        prompt += "Explain causes."
        r = requests.post(self.url + "/api/generate", json={"model": self.model, "prompt": prompt, "stream": False}, timeout=30)
        if r.status_code == 200:
            text = r.json().get("response", "")
            for e in events:
                e.explanation = text[:200]
        return events
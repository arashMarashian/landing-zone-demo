import os
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("AI_API_KEY")

GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GROQ_API_KEY:
    print("Warning: No Groq API key found in env (AI_API_KEY / GROQ_API_KEY).")


def call_groq_chat(prompt: str) -> str:
    """
    Simple helper that calls Groq chat completions and returns the text answer.
    """
    if not GROQ_API_KEY:
        raise RuntimeError("Groq API key is not configured.")

    url = f"{GROQ_API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=30)

    try:
        resp.raise_for_status()
    except requests.HTTPError as http_err:
        error_detail = ""
        try:
            err_json = resp.json()
            error_detail = err_json.get("error") or err_json

            if isinstance(err_json, dict):
                err_code = err_json.get("code") or err_json.get("error", {}).get("code")
                if err_code == "model_decommissioned":
                    error_detail = (
                        f"Model '{GROQ_MODEL}' is decommissioned. "
                        "Please update GROQ_MODEL to a supported option from "
                        "https://console.groq.com/docs/deprecations."
                    )
        except Exception:
            error_detail = resp.text

        raise requests.HTTPError(f"{http_err} | Detail: {error_detail}") from http_err

    data = resp.json()

    return data["choices"][0]["message"]["content"]

@app.route("/")
def home():
    vnet_enabled = os.getenv("VNET_ENABLED", "false")
    app_mode = os.getenv("APP_MODE")
    region = os.getenv("DEPLOY_REGION")
    log_level = os.getenv("LOG_LEVEL")
    ai_key_set = GROQ_API_KEY is not None

    ai_key_preview = None
    if ai_key_set:
        if len(GROQ_API_KEY) >= 4:
            ai_key_preview = f"{GROQ_API_KEY[:2]}...{GROQ_API_KEY[-2:]}"
        else:
            ai_key_preview = "**masked**"

    return render_template(
        "index.html",
        app_mode=app_mode,
        region=region,
        log_level=log_level,
        vnet_enabled=vnet_enabled,
        ai_key_set=ai_key_set,
        ai_key_preview=ai_key_preview,
    )

@app.route("/ai-test", methods=["GET", "POST"])
def ai_test():
    ai_response = None

    if request.method == "POST":
        user_prompt = (request.form.get("prompt") or "").strip()

        if not user_prompt:
            ai_response = "Please enter a prompt so I can send it to the model."
        elif not GROQ_API_KEY:
            ai_response = "The Groq API key is missing from the environment settings."
        else:
            try:
                answer = call_groq_chat(user_prompt)
                ai_response = answer
            except Exception as e:
                ai_response = f"There was a problem calling Groq: {e}"

    return render_template("ai_test.html", ai_response=ai_response)

@app.route("/api/openai-test")
def openai_test():
    question = request.args.get("q", "Say hello in exactly one word: OK")

    if not GROQ_API_KEY:
        return jsonify({
            "status": "error",
            "error": "Groq API key is not configured in environment variables."
        }), 500

    try:
        answer = call_groq_chat(question)
        return jsonify({
            "status": "ok",
            "question": question,
            "answer": answer,
            "provider": "groq-llama3"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
        }), 500

@app.route("/health")
def health():
    return {
        "status": "healthy",
        "app": "landing-zone-demo",
        "provider": "groq-llama3"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

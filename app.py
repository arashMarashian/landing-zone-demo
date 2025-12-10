import os
import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ============================
#   Groq Client (OpenAI-compatible)
# ============================

GROQ_API_KEY = (
    os.getenv("GROQ_API_KEY")
)

GROQ_API_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # مدل پیش‌فرض

if not GROQ_API_KEY:
    print("⚠️ WARNING: No Groq API key found in env (AI_API_KEY / GROQ_API_KEY).")


def call_groq_chat(prompt: str) -> str:
    """
    یه هلسپر ساده که به Groq chat completions وصل میشه
    و متن جواب رو برمی‌گردونه.
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
    resp.raise_for_status()
    data = resp.json()

    # ساختار مثل OpenAIه
    return data["choices"][0]["message"]["content"]


# ============================
#   Home Page  (/)
# ============================

@app.route("/")
def home():
    vnet_enabled = os.getenv("VNET_ENABLED", "false")
    app_mode = os.getenv("APP_MODE")
    region = os.getenv("DEPLOY_REGION")
    log_level = os.getenv("LOG_LEVEL")
    ai_key_set = GROQ_API_KEY is not None

    return render_template(
        "index.html",
        app_mode=app_mode,
        region=region,
        log_level=log_level,
        vnet_enabled=vnet_enabled,
        ai_key_set=ai_key_set,
    )


# ============================
#   /ai-test  (فرم HTML)
# ============================

@app.route("/ai-test", methods=["GET", "POST"])
def ai_test():
    ai_response = None

    if request.method == "POST":
        user_prompt = (request.form.get("prompt") or "").strip()

        if not user_prompt:
            ai_response = "⚠️ لطفاً یک متن وارد کن."
        elif not GROQ_API_KEY:
            ai_response = "⚠️ Groq API Key در محیط (App Settings) پیدا نشد."
        else:
            try:
                answer = call_groq_chat(user_prompt)
                ai_response = answer
            except Exception as e:
                ai_response = f"⚠️ Error calling Groq: {e}"

    return render_template("ai_test.html", ai_response=ai_response)


# ============================
#   /api/openai-test  (حالا در واقع Groq تست میشه)
# ============================

@app.route("/api/openai-test")
def openai_test():  # اسم رو نگه داشتیم
    question = request.args.get("q", "سلام، فقط با یک کلمه جواب بده: OK")

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


# ============================
#   Health Probe
# ============================

@app.route("/health")
def health():
    return {
        "status": "healthy",
        "app": "landing-zone-demo",
        "provider": "groq-llama3"
    }


# ============================
#   Local Run
# ============================

if __name__ == "__main__":
    # برای تست لوکال
    app.run(host="0.0.0.0", port=8000, debug=True)

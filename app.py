import os
from flask import Flask, render_template, jsonify, request
from openai import OpenAI

app = Flask(__name__)

# ============================
#   OpenAI Client
# ============================
API_KEY = os.getenv("AI_API_KEY")

if not API_KEY:
    print("⚠️ WARNING: AI_API_KEY is NOT set in environment variables!")

client = OpenAI(api_key=API_KEY)


# ============================
#   Home Page
# ============================
@app.route("/")
def home():
    return render_template(
        "index.html",
        app_mode=os.getenv("APP_MODE"),
        region=os.getenv("DEPLOY_REGION"),
        log_level=os.getenv("LOG_LEVEL"),
        vnet_enabled=os.getenv("VNET_ENABLED"),
    )


# ============================
#   HTML OpenAI Test Page
# ============================
@app.route("/ai-test", methods=["GET", "POST"])
def ai_test():
    ai_response = None

    if request.method == "POST":
        user_prompt = request.form.get("prompt")

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": user_prompt}],
            )

            ai_response = completion.choices[0].message.content

        except Exception as e:
            ai_response = f"⚠️ Error: {str(e)}"

    return render_template("ai_test.html", ai_response=ai_response)


# ============================
#   JSON API Test Endpoint
# ============================
@app.route("/api/openai-test")
def openai_test():
    question = request.args.get("q", "سلام، فقط بگو OK")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
        )

        answer = response.choices[0].message.content

        return jsonify({
            "status": "ok",
            "question": question,
            "answer": answer,
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
    return {"status": "healthy", "app": "landing-zone-demo"}


# ============================
#   Run Local
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

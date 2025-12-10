import os
from flask import Flask, render_template, jsonify, request
import google.generativeai as genai

app = Flask(__name__)

# ============================
#   Gemini / Google AI Client
# ============================

# اول از AI_API_KEY استفاده می‌کنیم (همونی که تو Azure گذاشتی)
API_KEY = (
    os.getenv("AI_API_KEY")
    or os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if not API_KEY:
    print("⚠️ WARNING: No Gemini API key found in env (AI_API_KEY / GEMINI_API_KEY / GOOGLE_API_KEY).")

# تنظیم کتابخونه گوگل
if API_KEY:
    genai.configure(api_key=API_KEY)
    GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash")
else:
    GEMINI_MODEL = None


# ============================
#   Home Page  (/)
# ============================

@app.route("/")
def home():
    vnet_enabled = os.getenv("VNET_ENABLED", "false")
    app_mode = os.getenv("APP_MODE")
    region = os.getenv("DEPLOY_REGION")
    log_level = os.getenv("LOG_LEVEL")
    ai_key_set = API_KEY is not None

    return render_template(
        "index.html",
        app_mode=app_mode,
        region=region,
        log_level=log_level,
        vnet_enabled=vnet_enabled,
        ai_key_set=ai_key_set,
    )


# ============================
#   /ai-test  (صفحه‌ی فرم HTML)
# ============================

@app.route("/ai-test", methods=["GET", "POST"])
def ai_test():
    ai_response = None

    if request.method == "POST":
        user_prompt = (request.form.get("prompt") or "").strip()

        if not user_prompt:
            ai_response = "⚠️ لطفاً یک متن وارد کن."
        elif not GEMINI_MODEL:
            ai_response = "⚠️ Gemini API Key در محیط (App Settings) پیدا نشد."
        else:
            try:
                result = GEMINI_MODEL.generate_content(user_prompt)
                ai_response = result.text
            except Exception as e:
                ai_response = f"⚠️ Error calling Gemini: {e}"

    return render_template("ai_test.html", ai_response=ai_response)


# ============================
#   /api/openai-test  (الان در واقع Gemini تست می‌کند)
# ============================

@app.route("/api/openai-test")
def openai_test():  # اسم رو نگه داشتیم، زیرش Gemini است 😉
    question = request.args.get("q", "سلام، فقط با یک کلمه جواب بده: OK")

    if not GEMINI_MODEL:
        return jsonify({
            "status": "error",
            "error": "Gemini API key is not configured in environment variables."
        }), 500

    try:
        result = GEMINI_MODEL.generate_content(question)
        answer = result.text

        return jsonify({
            "status": "ok",
            "question": question,
            "answer": answer,
            "provider": "google-gemini"
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
        "provider": "google-gemini"
    }


# ============================
#   Local Run
# ============================

if __name__ == "__main__":
    # برای تست لوکال
    app.run(host="0.0.0.0", port=8000, debug=True)

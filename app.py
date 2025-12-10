import os
from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("AI_API_KEY"))


@app.route("/")
def home():
    return render_template("index.html",
                           app_mode=os.getenv("APP_MODE"),
                           region=os.getenv("DEPLOY_REGION"),
                           log_level=os.getenv("LOG_LEVEL"),
                           vnet_enabled=os.getenv("VNET_ENABLED"))


@app.route("/ai-test", methods=["GET", "POST"])
def ai_test():
    ai_response = None

    if request.method == "POST":
        user_prompt = request.form.get("prompt")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_prompt}]
        )

        ai_response = completion.choices[0].message.content

    return render_template("ai_test.html", ai_response=ai_response)


@app.route("/health")
def health():
    return {"status": "healthy", "app": "landing-zone-demo"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

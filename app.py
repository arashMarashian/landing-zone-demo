import os
import socket
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Arash Landing Zone Dashboard</title>
  <style>
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #020617;
      color: #e5e7eb;
      margin: 0;
      padding: 40px;
    }
    h1 { margin-bottom: 4px; }
    h2 { margin-top: 32px; margin-bottom: 12px; }
    .subtitle { color: #9ca3af; margin-bottom: 28px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 16px;
    }
    .card {
      background: #020617;
      border-radius: 16px;
      padding: 14px 16px;
      border: 1px solid #1f2937;
    }
    .label {
      font-size: 11px;
      color: #9ca3af;
      text-transform: uppercase;
      letter-spacing: .1em;
    }
    .value {
      font-size: 16px;
      margin-top: 3px;
    }
    .pill {
      display: inline-block;
      margin-top: 6px;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 11px;
      background: #111827;
      color: #9ca3af;
    }
    .ok { color: #4ade80; }
    .warn { color: #facc15; }
    .fail { color: #f97373; }
    a { color: #60a5fa; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .footer {
      margin-top: 32px;
      font-size: 12px;
      color: #6b7280;
    }
    code {
      background: #020617;
      padding: 2px 4px;
      border-radius: 4px;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <h1>Arash Landing Zone</h1>
  <div class="subtitle">Azure Landing Zone demo – App Service + VNet Integration + App Settings</div>

  <h2>Metadata</h2>
  <div class="grid">
    <div class="card">
      <div class="label">App mode</div>
      <div class="value">{{ app_mode }}</div>
      <div class="pill">LOG_LEVEL={{ log_level }}</div>
    </div>
    <div class="card">
      <div class="label">Region</div>
      <div class="value">{{ deploy_region }}</div>
      <div class="pill">{{ hostname }}</div>
    </div>
    <div class="card">
      <div class="label">VNet integration</div>
      {% if vnet_enabled %}
        <div class="value ok">Enabled</div>
      {% else %}
        <div class="value warn">Not enabled</div>
      {% endif %}
      <div class="pill"><a href="/health">/health</a></div>
    </div>
    <div class="card">
      <div class="label">AI API key</div>
      <div class="value">
        {% if ai_key_masked %}
          {{ ai_key_masked }}
        {% else %}
          <span class="warn">Not configured</span>
        {% endif %}
      </div>
    </div>
  </div>

  <h2>Raw settings</h2>
  <div class="card">
    <pre style="margin:0; font-size:13px; line-height:1.4;">
APP_MODE       = {{ app_mode }}
DEPLOY_REGION  = {{ deploy_region }}
LOG_LEVEL      = {{ log_level }}
VNET_ENABLED   = {{ vnet_enabled|lower }}
AI_API_KEY     = {{ ai_key_masked or "None" }}
    </pre>
  </div>

  <div class="footer">
    Built as a hands-on Azure Landing Zone demo (governance, network, and app layer in one place).
  </div>
</body>
</html>
"""

def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)

@app.route("/")
def index():
    app_mode = get_env("APP_MODE", "landing-zone-demo")
    deploy_region = get_env("DEPLOY_REGION", "northeurope")
    log_level = get_env("LOG_LEVEL", "debug")
    vnet_enabled_raw = get_env("VNET_ENABLED", "false")
    ai_key = get_env("AI_API_KEY")

    vnet_enabled = str(vnet_enabled_raw).lower() in ("1", "true", "yes", "y")

    if ai_key and len(ai_key) > 3 and ai_key.lower() != "xxxx":
        ai_key_masked = ai_key[:3] + "***"
    elif ai_key:
        ai_key_masked = "(set, masked)"
    else:
        ai_key_masked = None

    hostname = socket.gethostname()

    return render_template_string(
        TEMPLATE,
        app_mode=app_mode,
        deploy_region=deploy_region,
        log_level=log_level,
        vnet_enabled=vnet_enabled,
        ai_key_masked=ai_key_masked,
        hostname=hostname,
    )

@app.route("/health")
def health():
    return jsonify(
        status="ok",
        app="arash-lz-webapp",
        mode=get_env("APP_MODE", "landing-zone-demo"),
        region=get_env("DEPLOY_REGION", "northeurope"),
    )

if __name__ == "__main__":
    # لو لوکال اجرا می‌کنی
    app.run(host="0.0.0.0", port=8000, debug=True)

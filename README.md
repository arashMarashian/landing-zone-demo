# Landing Zone Demo

A compact Flask app that demonstrates key Azure Landing Zone concepts: App Service deployment, managed identity, governance policies, VNet integration, and CI/CD with GitHub Actions. The home page surfaces runtime metadata, links to a simple AI test form, and lists the topics covered while building the project.

## Running locally
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables as needed (e.g., `APP_MODE`, `DEPLOY_REGION`, `LOG_LEVEL`, `VNET_ENABLED`, `AI_API_KEY`).
3. Start the server: `python app.py` and open http://localhost:8000.

## Notes
- The AI test route (`/ai-test`) uses a Groq API key from `AI_API_KEY` or `GROQ_API_KEY`.
- Metadata on the landing page masks the key while still showing a short preview for verification.

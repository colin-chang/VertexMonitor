import os
from google.cloud import aiplatform

# Set the path to your service account key JSON file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex-key.json"
aiplatform.init(project="your-gcp-project-id", location="global")

from vertexai.generative_models import GenerativeModel
model = GenerativeModel("gemini-3.1-flash-lite")

response = model.generate_content("Hello, please respond briefly")
print(response.text)

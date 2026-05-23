import os
from google.cloud import aiplatform

# 替换为你下载的 JSON 文件路径
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vertex-key.json"
aiplatform.init(project="ai-project-384207", location="global")

from vertexai.generative_models import GenerativeModel
model = GenerativeModel("gemini-3.1-flash-lite")

response = model.generate_content("你好，请简短回答")
print(response.text)
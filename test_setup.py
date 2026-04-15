import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import azure.ai.projects
from dotenv import load_dotenv

load_dotenv()

# Check the SDK version
print(f"Azure AI Projects SDK version: {azure.ai.projects.__version__}")


# Test that you can connect to your project
project = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"], 
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP_NAME"], 
    project_name=os.environ["AZURE_PROJECT_NAME"], 
    credential=DefaultAzureCredential()
)

print("✓ Setup verified! Ready to getenvbuild your RAG app.")
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

vector_store = client.vector_stores.create(
    name="Benefits Service Copilot Knowledge Base"
)

with open("knowledge_base.md", "rb") as knowledge:
    uploaded_file = client.vector_stores.files.upload_and_poll(
        vector_store_id=vector_store.id,
        file=knowledge
    )
print(f"Vector store ID: {vector_store.id}")
print(f"Upload status: {uploaded_file.status}")
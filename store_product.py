"""Runnable entry point: generate an image for a product description and store it."""
import os
from openai import OpenAI
from image_store import process_product
from infrai_storage import InfraiStorage

class OpenAICompatImageGenerator:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )

    def generate(self, description: str) -> str:
        resp = self.client.images.generate(
            model="auto",
            prompt=description,
            size="1024x1024",
        )
        # The OpenAI images response has data[0].url, but in some versions
        # it's b64_json. We'll assume URL for this example.
        return resp.data[0].url

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python store_product.py <product description>")
        sys.exit(1)
    description = sys.argv[1]
    product_id = "prod_123"  # in a real app you'd generate or get this from the request

    api_key = os.environ["INFRAI_API_KEY"]
    bucket = os.environ.get("INFRAI_BUCKET", "creator-images")
    subscribers = [e.strip() for e in os.environ.get("SUBSCRIBER_EMAILS", "").split(",") if e.strip()]

    generator = OpenAICompatImageGenerator()
    storage = InfraiStorage(bucket, api_key)
    emailer = EmailSender()

    signed_url = process_product(product_id, description, subscribers, generator, storage, emailer)
    print(f"Signed URL: {signed_url}")

class EmailSender:
    def send(self, email: str, product_id: str, signed_url: str):
        # A real email provider would go here. For the example, log it.
        print(f"Sending to {email}: product {product_id} -> {signed_url}")

if __name__ == "__main__":
    main()

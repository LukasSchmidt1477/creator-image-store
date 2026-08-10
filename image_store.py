"""Core store-and-notify workflow."""

def process_product(product_id: str, description: str, subscribers: list[str], image_generator, storage, emailer) -> str:
    """Generate, store, and notify. Returns the signed download URL."""
    # 1. Generate the image using the OpenAI-compatible client.
    image_url = image_generator.generate(description)

    # 2. Store it and get a signed URL.
    signed_url = storage.store_and_get_signed_url(product_id, image_url)

    # 3. Notify subscribers if there are any.
    if subscribers:
        for email in subscribers:
            emailer.send(email, product_id, signed_url)
    else:
        print("No subscribers to notify; skipping email.")

    return signed_url

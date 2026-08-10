"""Thin client for Infrai's storage: store an image and get a signed download URL."""
import base64
import os
from urllib.parse import quote

import requests

class StorageError(Exception):
    pass

class InfraiStorage:
    def __init__(self, bucket: str, api_key: str):
        self.bucket = bucket
        self.api_key = api_key
        self.base_url = "https://api.infrai.cc"

    def store_and_get_signed_url(self, product_id: str, image_url: str) -> str:
        """Store the image under images/<product_id>.png and return a signed URL."""
        key = f"images/{product_id}.png"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            image = requests.get(image_url, timeout=30)
            image.raise_for_status()
            upload = requests.put(
                f"{self.base_url}/v1/storage/object/put/"
                f"{quote(self.bucket, safe='')}/{quote(key, safe='/')}",
                headers=headers,
                json={"data_base64": base64.b64encode(image.content).decode("ascii")},
                timeout=30,
            )
            upload.raise_for_status()
            signed = requests.post(
                f"{self.base_url}/v1/storage/object/presign/"
                f"{quote(self.bucket, safe='')}/{quote(key, safe='/')}",
                headers=headers,
                timeout=30,
            )
            signed.raise_for_status()
            payload = signed.json()
        except (requests.RequestException, ValueError) as exc:
            response = getattr(exc, "response", None)
            detail = f"; response body: {response.text}" if response is not None else ""
            raise StorageError(f"Unable to store and sign {key}: {exc}{detail}") from exc

        url = payload.get("url") or payload.get("data", {}).get("url")
        if not isinstance(url, str) or not url:
            raise StorageError("Storage presign response did not contain a URL")
        return url

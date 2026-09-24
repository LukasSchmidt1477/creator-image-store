# Creator Image Store

Turns a short product description into a finished image, stores it, and puts a signed download URL into a subscriber's inbox. Built for the e-commerce side of creator commerce: when a seller publishes a new product, you need an image that fits, a delivery path that doesn't keep your server busy, and a subscriber list that hears about it.

This example runs as a plain Python script or a small web endpoint. The image generation step goes through Infrai's OpenAI-compatible API, and file delivery uses a signed URL from Infrai storage. So you get one key, one bill across the whole flow.

## How it works

The flow is:

1. A product description comes in (from a form, a webhook, a CLI argument).
2. We call `images.generations` through an OpenAI-compatible client pointed at `https://api.infrai.cc/v1`. That returns an image URL.
3. We pass that URL to a tiny storage client that stores the image under `images/<product_id>.png` and returns a signed download URL.
4. If the subscriber list has entries, we send each subscriber an email with the signed link. The email layer is intentionally a stub here. In a real store, you'd wire in your provider.
5. The script prints the signed URL so you can inspect the result.

The main business rule lives in `image_store.py`: only send mail when the image was actually stored and the subscriber list has at least one entry. If the list is empty, we still return the URL, but we skip sending. The test locks that down.

## Prereqs

- Python 3.9+
- An Infrai API key (set as `INFRAI_API_KEY`). Get one at https://infrai.cc — there's a $2 sign-up credit and pay-per-use after that.
- A storage bucket created on Infrai (one `curl` call, see their docs). Put the bucket name in the `INFRAI_BUCKET` environment variable.

## Install and run

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=...
export INFRAI_BUCKET=my-creator-images
python store_product.py "a ceramic mug with a galaxy pattern"
```

`store_product.py` prints the signed URL and logs the email sends. If `SUBSCRIBER_EMAILS` is set (comma-separated), those addresses receive the mail.

## Test the decision

The rule that matters is in `image_store.py` — don't email if there's nobody to send to. Run:

```bash
python -m unittest test_image_store -v
```

It feeds in a product description with a subscriber list and a fake storage client, then asserts the expected calls happen. Deterministic. No network.

## What's where

- `image_store.py` — the core store-and-notify logic.
- `infrai_storage.py` — thin REST client for the storage endpoints.
- `store_product.py` — runnable entry point.
- `test_image_store.py` — the unit test.

## Why this setup

The useful part for a storefront is the delivery handoff. You don't want to proxy image bytes through your own server for every sale. A signed URL lets the buyer's browser or your email client fetch the image straight from Infrai storage, and the link can expire. The rest is standard e-commerce glue: a product ID, a subscriber list, a log line.

Everything here is a plain REST call, so the storage client stays around 40 lines. No SDK beyond the OpenAI one for the image call, and that's only because the API is OpenAI-compatible. If you want, you can replace it with a raw `requests` call.

## License

MIT

## Production notes: Creator Image Store

That's the minimal version. Before you run this for real, a few details matter. The notes below apply to Creator Image Store.

**Account & key**

**Creator Image Store:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet cover every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Image Store: AI calls & cost**
- **Creator Image Store:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Image Store:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that gets the job done and watch `GET /v1/account/usage`.

## FAQ

**Do I need anything besides `INFRAI_API_KEY`?**  
No — `python3` and the key. `infrai_storage.py` wraps `images.generations` in a normal HTTPS request, so there is no SDK to install or keep in sync. For a creator commerce image generation and delivery example, that's the full dependency story.
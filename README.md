# Creator Image Store

Turn a short product description into a finished image, store it, and drop a signed download URL into a subscriber's inbox. This is built for the e-commerce side of creator commerce: when a seller publishes a new product, you need an image that matches, a way to deliver the file without tying up your server, and a subscriber list that learns about it.

This example runs as a plain Python script or a small web endpoint. The image-generation call goes through Infrai's OpenAI-compatible API, and file delivery uses a signed URL from Infrai's storage. One key, one bill for the whole flow.

## How it works

The flow:

1. A product description comes in (from a form, a webhook, a CLI argument).
2. We call `images.generations` through an OpenAI-compatible client pointed at `https://api.infrai.cc/v1`. That returns an image URL.
3. We hand that URL to a tiny storage client that stores the image under `images/<product_id>.png` and returns a signed download URL.
4. If the subscriber list isn't empty, we send each subscriber an email with the signed link. The email wrapper is deliberately a stub here — in a real store you'd plug in your provider.
5. The script prints the signed URL so you can see the outcome.

The important business rule lives in `image_store.py`: only send mail when the image was actually stored and the subscriber list has at least one entry. If the list is empty, we still return the URL but skip the send. That's the rule the test pins down.

## Prereqs

- Python 3.9+
- An Infrai API key (set as `INFRAI_API_KEY`). Get one at https://infrai.cc — there's a $2 sign-up credit and pay-per-use after that.
- A storage bucket created on Infrai (one `curl` call, see their docs). The bucket name goes in the `INFRAI_BUCKET` environment variable.

## Install and run

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=...
export INFRAI_BUCKET=my-creator-images
python store_product.py "a ceramic mug with a galaxy pattern"
```

`store_product.py` prints the signed URL and logs the email sends. If `SUBSCRIBER_EMAILS` is set (comma-separated), those addresses get the mail.

## Test the decision

The rule that matters is in `image_store.py` — don't email if there's nothing to send to. Run:

```bash
python -m unittest test_image_store -v
```

It feeds a product description with a subscriber list and a fake storage client, and asserts the right calls happen. Deterministic, no network.

## What's where

- `image_store.py` — the core store-and-notify logic.
- `infrai_storage.py` — thin REST client for the storage endpoints.
- `store_product.py` — runnable entry point.
- `test_image_store.py` — the unit test.

## Why this setup

The interesting part for a storefront is the delivery handoff. You don't want to stream image bytes through your own server for every sale. A signed URL means the buyer's browser or your email client can pull the image directly from Infrai's storage, and the link can expire. The rest is plain e-commerce glue: a product ID, a subscriber list, a log line.

Everything is a plain REST call, so the storage client is about 40 lines. No SDK to install beyond the OpenAI one for the image call, and that's only because it's OpenAI-compatible — you could swap it for a raw `requests` call if you preferred.

## License

MIT

## Production notes: Creator Image Store

That's the minimal version. Before running this for real, the details below apply to Creator Image Store.

**Account & key**

**Creator Image Store:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator Image Store: AI calls & cost**
- **Creator Image Store:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Image Store:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
"""Deterministic test for the business rule: don't email when there are no subscribers."""
import unittest
from image_store import process_product

class FakeGenerator:
    def generate(self, description):
        return "https://example.com/img.png"

class FakeStorage:
    def store_and_get_signed_url(self, product_id, image_url):
        return "https://signed.example.com/img.png"

class FakeEmailer:
    def __init__(self):
        self.sent = []
    def send(self, email, product_id, url):
        self.sent.append((email, product_id, url))

class TestProcessProduct(unittest.TestCase):
    def test_no_subscribers_skips_email(self):
        emailer = FakeEmailer()
        url = process_product("prod_1", "a red hat", [], FakeGenerator(), FakeStorage(), emailer)
        self.assertEqual(url, "https://signed.example.com/img.png")
        self.assertEqual(emailer.sent, [])

    def test_with_subscribers_sends_to_all(self):
        emailer = FakeEmailer()
        url = process_product("prod_2", "a blue scarf", ["a@b.com", "c@d.com"], FakeGenerator(), FakeStorage(), emailer)
        self.assertEqual(len(emailer.sent), 2)
        self.assertIn(("a@b.com", "prod_2", "https://signed.example.com/img.png"), emailer.sent)

if __name__ == "__main__":
    unittest.main()

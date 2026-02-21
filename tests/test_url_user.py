"""
API-level tests for the URL-to-user linking and /my-urls endpoint.
"""


class TestShortenWithAuth:
    def test_anonymous_shorten(self, client):
        """Shortened URL works without authentication."""
        resp = client.post("/shorten", json={"original_url": "https://example.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["short_code"]
        assert data["short_url"]

    def test_authenticated_shorten(self, client, auth_headers):
        """Shortened URL is linked to user when authenticated."""
        resp = client.post(
            "/shorten",
            json={"original_url": "https://linked.com"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

        # Should appear in /my-urls
        my = client.get("/my-urls", headers=auth_headers)
        assert my.status_code == 200
        urls = my.json()
        assert len(urls) == 1
        assert urls[0]["original_url"] == "https://linked.com/"


class TestMyUrls:
    def test_requires_auth(self, client):
        resp = client.get("/my-urls")
        assert resp.status_code == 401

    def test_empty_list(self, client, auth_headers):
        resp = client.get("/my-urls", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_lists_only_own_urls(self, client, auth_headers, second_auth_headers):
        """Each user only sees their own shortened URLs."""
        client.post("/shorten", json={"original_url": "https://user1.com"}, headers=auth_headers)
        client.post("/shorten", json={"original_url": "https://user1b.com"}, headers=auth_headers)
        client.post("/shorten", json={"original_url": "https://user2.com"}, headers=second_auth_headers)

        user1_urls = client.get("/my-urls", headers=auth_headers).json()
        user2_urls = client.get("/my-urls", headers=second_auth_headers).json()

        assert len(user1_urls) == 2
        assert len(user2_urls) == 1

    def test_anonymous_urls_not_in_my_urls(self, client, auth_headers):
        """URLs created without auth don't appear in any user's list."""
        client.post("/shorten", json={"original_url": "https://anon.com"})
        client.post("/shorten", json={"original_url": "https://mine.com"}, headers=auth_headers)

        my = client.get("/my-urls", headers=auth_headers).json()
        assert len(my) == 1
        assert my[0]["original_url"] == "https://mine.com/"

    def test_newest_first(self, client, auth_headers):
        """URLs are returned in newest-first order."""
        client.post("/shorten", json={"original_url": "https://first.com"}, headers=auth_headers)
        client.post("/shorten", json={"original_url": "https://second.com"}, headers=auth_headers)

        urls = client.get("/my-urls", headers=auth_headers).json()
        assert urls[0]["original_url"] == "https://second.com/"
        assert urls[1]["original_url"] == "https://first.com/"

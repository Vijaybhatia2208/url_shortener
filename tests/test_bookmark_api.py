"""
API-level integration tests for the bookmark endpoints.
Tests use FastAPI TestClient with JWT-authenticated requests.
"""


class TestCreateBookmark:
    def test_create_success(self, client, auth_headers):
        resp = client.post(
            "/bookmarks",
            json={"url": "https://example.com", "title": "Example", "tags": ["dev"]},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["url"] == "https://example.com"
        assert data["title"] == "Example"
        assert data["tags"] == ["dev"]
        assert "id" in data

    def test_create_minimal(self, client, auth_headers):
        resp = client.post(
            "/bookmarks",
            json={"url": "https://minimal.com"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["title"] is None
        assert resp.json()["tags"] is None

    def test_create_requires_auth(self, client):
        resp = client.post("/bookmarks", json={"url": "https://nope.com"})
        assert resp.status_code == 401


class TestListBookmarks:
    def _seed(self, client, headers):
        for bm in [
            {"url": "https://python.org", "title": "Python", "tags": ["python"]},
            {"url": "https://fastapi.tiangolo.com", "title": "FastAPI", "tags": ["python", "api"]},
            {"url": "https://react.dev", "title": "React", "tags": ["frontend"]},
        ]:
            client.post("/bookmarks", json=bm, headers=headers)

    def test_list_all(self, client, auth_headers):
        self._seed(client, auth_headers)
        resp = client.get("/bookmarks", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_list_isolates_users(self, client, auth_headers, second_auth_headers):
        self._seed(client, auth_headers)
        client.post("/bookmarks", json={"url": "https://other.com"}, headers=second_auth_headers)

        assert len(client.get("/bookmarks", headers=auth_headers).json()) == 3
        assert len(client.get("/bookmarks", headers=second_auth_headers).json()) == 1

    def test_search_by_title(self, client, auth_headers):
        self._seed(client, auth_headers)
        resp = client.get("/bookmarks", params={"search": "fastapi"}, headers=auth_headers)
        results = resp.json()
        assert len(results) == 1
        assert results[0]["title"] == "FastAPI"

    def test_filter_by_tag(self, client, auth_headers):
        self._seed(client, auth_headers)
        resp = client.get("/bookmarks", params={"tag": "python"}, headers=auth_headers)
        assert len(resp.json()) == 2

    def test_list_requires_auth(self, client):
        resp = client.get("/bookmarks")
        assert resp.status_code == 401


class TestUpdateBookmark:
    def _create(self, client, headers):
        resp = client.post(
            "/bookmarks",
            json={"url": "https://old.com", "title": "Old Title", "tags": ["old"]},
            headers=headers,
        )
        return resp.json()["id"]

    def test_update_title(self, client, auth_headers):
        bid = self._create(client, auth_headers)
        resp = client.put(f"/bookmarks/{bid}", json={"title": "New Title"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["title"] == "New Title"
        assert resp.json()["url"] == "https://old.com"  # unchanged

    def test_update_tags(self, client, auth_headers):
        bid = self._create(client, auth_headers)
        resp = client.put(f"/bookmarks/{bid}", json={"tags": ["new", "tags"]}, headers=auth_headers)
        assert resp.json()["tags"] == ["new", "tags"]

    def test_update_nonexistent(self, client, auth_headers):
        resp = client.put("/bookmarks/9999", json={"title": "X"}, headers=auth_headers)
        assert resp.status_code == 404

    def test_cannot_update_others_bookmark(self, client, auth_headers, second_auth_headers):
        bid = self._create(client, auth_headers)
        resp = client.put(f"/bookmarks/{bid}", json={"title": "Hack"}, headers=second_auth_headers)
        assert resp.status_code == 404

    def test_update_requires_auth(self, client, auth_headers):
        bid = self._create(client, auth_headers)
        resp = client.put(f"/bookmarks/{bid}", json={"title": "X"})
        assert resp.status_code == 401


class TestDeleteBookmark:
    def _create(self, client, headers):
        resp = client.post(
            "/bookmarks",
            json={"url": "https://delete-me.com"},
            headers=headers,
        )
        return resp.json()["id"]

    def test_delete_success(self, client, auth_headers):
        bid = self._create(client, auth_headers)
        resp = client.delete(f"/bookmarks/{bid}", headers=auth_headers)
        assert resp.status_code == 204

        # Verify it's gone
        assert len(client.get("/bookmarks", headers=auth_headers).json()) == 0

    def test_delete_nonexistent(self, client, auth_headers):
        resp = client.delete("/bookmarks/9999", headers=auth_headers)
        assert resp.status_code == 404

    def test_cannot_delete_others_bookmark(self, client, auth_headers, second_auth_headers):
        bid = self._create(client, auth_headers)
        resp = client.delete(f"/bookmarks/{bid}", headers=second_auth_headers)
        assert resp.status_code == 404

    def test_delete_requires_auth(self, client, auth_headers):
        bid = self._create(client, auth_headers)
        resp = client.delete(f"/bookmarks/{bid}")
        assert resp.status_code == 401

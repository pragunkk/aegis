"""Tests for Product Catalog and Semantic Discovery."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_products_excludes_price_floor(async_client: AsyncClient):
    """Test that public catalog lists products without exposing internal price floors."""
    response = await async_client.get("/api/v1/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0

    for p in products:
        assert "id" in p
        assert "name" in p
        assert "mrp" in p
        assert "stock" in p
        # Price floor MUST NOT be exposed in public API
        assert "price_floor" not in p


@pytest.mark.asyncio
async def test_discover_products_semantic_search(async_client: AsyncClient):
    """Test agent semantic discovery endpoint returns relevant products."""
    response = await async_client.post(
        "/api/v1/agent/discover",
        json={"query": "stealth drone surveillance", "limit": 2},
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    # Top match should be the Recon Drone
    assert "Drone" in results[0]["name"]
    assert "price_floor" not in results[0]


@pytest.mark.asyncio
async def test_get_product_by_id(async_client: AsyncClient):
    """Test fetching a single product by ID."""
    product_id = "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
    response = await async_client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Neural Interface Cyber-Deck X9"
    assert "price_floor" not in data

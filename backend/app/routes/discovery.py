"""Product catalog and semantic discovery endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, Query, status

from backend.app.database import db
from backend.app.models.schemas import (
    ProductPublicResponse,
    DiscoveryQueryRequest,
)
from backend.app.services.audit_service import audit_service

router = APIRouter(prefix="/api/v1", tags=["Discovery"])


@router.get("/products", response_model=List[ProductPublicResponse])
async def list_products():
    """Returns the merchant catalog. Confidential price floors are stripped."""
    products = await db.list_products()
    return [
        ProductPublicResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            mrp=p.mrp,
            stock=p.stock,
        )
        for p in products
    ]


@router.get("/products/{product_id}", response_model=ProductPublicResponse)
async def get_product_details(product_id: str):
    """Fetches details for a specific product."""
    product = await db.get_product(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found",
        )
    return ProductPublicResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        mrp=product.mrp,
        stock=product.stock,
    )


@router.post("/agent/discover", response_model=List[ProductPublicResponse])
async def discover_products(req: DiscoveryQueryRequest):
    """
    Semantic & keyword discovery endpoint for AI buyer agents.
    Searches product catalog matching buyer intent while protecting confidential margins.
    """
    results = await db.search_products(query=req.query, limit=req.limit)

    await audit_service.log_event(
        event_type="DISCOVERY_QUERY",
        payload={
            "query": req.query,
            "results_count": len(results),
            "matched_ids": [p.id for p in results],
        }
    )

    return [
        ProductPublicResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            mrp=p.mrp,
            stock=p.stock,
        )
        for p in results
    ]

"""
Product service — business logic for product management.
"""
import uuid
import logging
from typing import Optional

from sqlalchemy import select, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product, SellingAngle
from app.schemas.product import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


async def create_product(
    db: AsyncSession, data: ProductCreate, user_id: uuid.UUID
) -> Product:
    """Create a new product."""
    product = Product(
        name=data.name,
        source_url=data.source_url,
        description=data.description,
        category=data.category,
        created_by=user_id,
        status="draft",
    )
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


async def get_product(db: AsyncSession, product_id: uuid.UUID) -> Optional[Product]:
    """Get a product by ID with selling angles."""
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.selling_angles))
        .where(Product.id == product_id)
    )
    return result.scalar_one_or_none()


async def list_products(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[list[Product], int]:
    """List products with pagination and filters."""
    query = select(Product).options(selectinload(Product.selling_angles))

    if status:
        query = query.where(Product.status == status)
    if category:
        query = query.where(Product.category == category)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    # Count total
    count_query = select(sql_func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.order_by(Product.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return list(result.scalars().all()), total


async def update_product(
    db: AsyncSession, product_id: uuid.UUID, data: ProductUpdate
) -> Optional[Product]:
    """Update a product."""
    product = await get_product(db, product_id)
    if not product:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.flush()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product_id: uuid.UUID) -> bool:
    """Soft-delete a product by setting status to archived."""
    product = await get_product(db, product_id)
    if not product:
        return False
    product.status = "archived"
    await db.flush()
    return True


async def save_analysis_results(
    db: AsyncSession,
    product_id: uuid.UUID,
    analysis: dict,
) -> Product:
    """Save AI analysis results and create selling angles."""
    product = await get_product(db, product_id)
    if not product:
        raise ValueError(f"Product {product_id} not found")

    product.ai_analysis = analysis
    product.status = "analyzed"

    # Create selling angles from analysis
    angles_data = analysis.get("selling_angles", [])
    for angle_data in angles_data:
        angle = SellingAngle(
            product_id=product_id,
            angle_type=angle_data.get("type", "benefit"),
            title=angle_data.get("title", ""),
            description=angle_data.get("description", ""),
            score=angle_data.get("score"),
        )
        db.add(angle)

    await db.flush()
    await db.refresh(product)
    return product

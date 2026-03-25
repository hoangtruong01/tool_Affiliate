"""
Seed data script — populate the database with a clean MVP demo state.
"""
import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_factory, engine, Base
from app.models.user import User
from app.models.product import Product, SellingAngle
from app.models.script import Script
from app.models.asset import Asset
from app.models.video_job import VideoJob, VideoJobAsset
from app.utils.security import hash_password

async def seed_data():
    async with async_session_factory() as db:
        # 1. Create Admin User
        admin_email = "admin@example.com"
        admin = await db.get(User, uuid.uuid4()) # dummy check
        # Actually check by email
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == admin_email))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                email=admin_email,
                hashed_password=hash_password("admin123"),
                full_name="MVP Admin",
                role="admin",
                is_active=True
            )
            db.add(admin)
            await db.flush()
            print(f"Created admin user: {admin_email}")
        else:
            admin.hashed_password = hash_password("admin123")
            admin.role = "admin"
            print(f"Updated admin user: {admin_email} (role → admin)")
        
        # 2. Create Demo Product
        product_name = "Cool AI Gadget"
        result = await db.execute(select(Product).where(Product.name == product_name))
        product = result.scalar_one_or_none()
        
        if not product:
            product = Product(
                name=product_name,
                description="A futuristic gadget that uses AI to solve your problems.",
                status="analyzed",
                created_by=admin.id,
                ai_analysis={
                    "target_audience": "Tech enthusiasts",
                    "pain_points": ["Complexity", "Boredom"],
                    "benefits": ["Ease of use", "Innovation"]
                }
            )
            db.add(product)
            await db.flush()
            print(f"Created demo product: {product_name}")
        
        # 3. Create Selling Angle
        result = await db.execute(select(SellingAngle).where(SellingAngle.product_id == product.id))
        angle = result.scalar_one_or_none()
        
        if not angle:
            angle = SellingAngle(
                product_id=product.id,
                angle_type="benefit",
                title="AI Magic at Your Fingertips",
                description="Experience the future of personal tech with AI magic.",
                score=0.95
            )
            db.add(angle)
            await db.flush()
            print(f"Created selling angle: {angle.title}")

        # 4. Create Approved Script
        result = await db.execute(select(Script).where(Script.product_id == product.id))
        script = result.scalar_one_or_none()
        
        if not script:
            script = Script(
                product_id=product.id,
                angle_id=angle.id,
                created_by=admin.id,
                hook="Ready for the future?",
                body="This gadget uses AI to automate your life.",
                cta="Check link in bio!",
                status="approved",
                platform="tiktok"
            )
            db.add(script)
            await db.flush()
            print(f"Created approved script: {script.id}")
            
        # 5. Create Demo Asset
        result = await db.execute(select(Asset).where(Asset.filename == "demo_image.png"))
        asset = result.scalar_one_or_none()
        
        if not asset:
            asset = Asset(
                filename="demo_image.png",
                file_path="/app/data/assets/demo_image.png",
                asset_type="image",
                file_size=1024,
                uploaded_by=admin.id
            )
            db.add(asset)
            await db.flush()
            print(f"Created demo asset: {asset.filename}")

        # 6. Create Video Job in needs_review status
        result = await db.execute(select(VideoJob).where(VideoJob.script_id == script.id))
        job = result.scalar_one_or_none()
        
        if not job:
            job = VideoJob(
                script_id=script.id,
                created_by=admin.id,
                status="needs_review",
                output_path="http://localhost:8000/media/renders/demo_video.mp4",
                duration_seconds=15,
                started_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc)
            )
            db.add(job)
            await db.flush()
            
            # Link asset
            job_asset = VideoJobAsset(
                job_id=job.id,
                asset_id=asset.id,
                sequence_order=0
            )
            db.add(job_asset)
            print(f"Created needs_review video job: {job.id}")

        await db.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_data())

from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
# MongoDB Atlas will use database in URL, if not specified we fall back to fake_detector
db = client.get_default_database()

# Fallback database name if not resolved from URI
if db is None or db.name == 'admin':
    db = client['fake_detector']

async def init_db():
    # Create indexes for user registration
    await db.users.create_index("username", unique=True)
    await db.users.create_index("email", unique=True)
    # Index for scan history sorting/filtering
    await db.history.create_index("scanned_at")
    await db.history.create_index("user_id")

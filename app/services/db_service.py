from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from datetime import datetime
import logging
from typing import List, Optional, Dict, Any

from app.core.config import settings
from app.models.schemas import UserInDB, FeedbackResponse

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_mongodb(self):
        """Connect to MongoDB database"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DB_NAME]
            # Ping the database to verify connection
            await self.client.admin.command('ping')
            logger.info("Connected to MongoDB")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close_mongodb_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")

    # User operations
    async def create_user(self, user_data: dict) -> str:
        """Create a new user in the database"""
        user_data["created_at"] = datetime.utcnow()
        result = await self.db.users.insert_one(user_data)
        return str(result.inserted_id)

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by email"""
        user = await self.db.users.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
            return UserInDB(**user)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get a user by ID"""
        try:
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                return UserInDB(**user)
        except Exception as e:
            logger.error(f"Error retrieving user by ID: {e}")
        return None

    # Feedback operations
    async def save_feedback(self, feedback: FeedbackResponse) -> str:
        """Save feedback to the database"""
        feedback_dict = feedback.model_dump()
        feedback_dict["created_at"] = datetime.utcnow()
        
        # Convert user_id to ObjectId if it exists
        if feedback_dict.get("user_id"):
            try:
                feedback_dict["user_id"] = ObjectId(feedback_dict["user_id"])
            except Exception as e:
                logger.error(f"Error converting user_id to ObjectId: {e}")
        
        result = await self.db.feedback.insert_one(feedback_dict)
        return str(result.inserted_id)

    async def get_user_feedback_history(self, user_id: str) -> List[FeedbackResponse]:
        """Get feedback history for a user"""
        try:
            cursor = self.db.feedback.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
            feedback_list = []
            async for feedback in cursor:
                feedback["id"] = str(feedback["_id"])
                # Convert ObjectId to string for user_id
                if feedback.get("user_id"):
                    feedback["user_id"] = str(feedback["user_id"])
                feedback_list.append(FeedbackResponse(**feedback))
            return feedback_list
        except Exception as e:
            logger.error(f"Error retrieving user feedback history: {e}")
            return []

# Create a database instance
db = Database()

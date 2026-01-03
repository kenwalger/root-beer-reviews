"""MongoDB database connection and utilities.

This module manages the MongoDB connection lifecycle and provides
a singleton database instance for use throughout the application.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from typing import Optional


class Database:
    """Database connection manager.
    
    Singleton class that holds the MongoDB client and database instances.
    """
    
    client: Optional[AsyncIOMotorClient] = None  #: MongoDB client instance
    database: Optional[AsyncIOMotorDatabase] = None  #: MongoDB database instance


db = Database()


async def connect_to_mongo() -> None:
    """Connect to MongoDB.
    
    Initializes the MongoDB client and database connection using
    settings from the configuration.
    
    :raises Exception: If connection fails
    """
    db.client = AsyncIOMotorClient(settings.mongodb_uri)
    db.database = db.client[settings.database_name]
    print(f"Connected to MongoDB database: {settings.database_name}")


async def close_mongo_connection() -> None:
    """Close MongoDB connection.
    
    Safely closes the MongoDB client connection if it exists.
    """
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")


def get_database() -> Optional[AsyncIOMotorDatabase]:
    """Get database instance.
    
    :returns: MongoDB database instance, or None if not connected
    :rtype: Optional[AsyncIOMotorDatabase]
    """
    return db.database


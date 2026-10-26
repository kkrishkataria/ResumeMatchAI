"""Optional MongoDB history. The app works fully without it."""
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId


def _collection():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    client = MongoClient(uri, serverSelectionTimeoutMS=1200)
    client.admin.command("ping")
    return client[os.getenv("MONGODB_DATABASE", "resumematch_ai")]["analyses"]


def save_analysis(score: float, matched_skills: list[str], missing_skills: list[str], job_description: str) -> tuple[bool, str | None]:
    try:
        collection = _collection()
        if collection is None:
            return False, "History is unavailable: MONGODB_URI is not configured."
        summary = " ".join(job_description.split())[:180]
        collection.insert_one({"timestamp": datetime.now(timezone.utc), "score": score, "score_type": "skill", "matched_skills": matched_skills, "missing_skills": missing_skills, "job_summary": summary})
        return True, None
    except PyMongoError:
        return False, "History could not be saved because MongoDB is unavailable."


def get_history(limit: int = 20) -> tuple[list[dict], bool, str | None]:
    try:
        collection = _collection()
        if collection is None:
            return [], False, "History is unavailable: MONGODB_URI is not configured."
        records = list(collection.find({}).sort("timestamp", -1).limit(limit))
        for record in records:
            record["id"] = str(record.pop("_id"))
        return records, True, None
    except PyMongoError:
        return [], False, "History is unavailable because MongoDB cannot be reached."


def delete_analysis(analysis_id: str) -> tuple[bool, str | None]:
    """Delete one saved analysis; resume text is never stored in these records."""
    try:
        collection = _collection()
        if collection is None:
            return False, "History is unavailable: MONGODB_URI is not configured."
        try:
            object_id = ObjectId(analysis_id)
        except InvalidId:
            return False, "The selected history record is invalid."
        result = collection.delete_one({"_id": object_id})
        if not result.deleted_count:
            return False, "The selected history record no longer exists."
        return True, None
    except PyMongoError:
        return False, "History could not be deleted because MongoDB cannot be reached."


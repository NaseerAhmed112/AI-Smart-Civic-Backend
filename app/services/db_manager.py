from typing import Generic, List, Optional, Type, TypeVar

from pymongo.database import Database

T = TypeVar("T")


class DatabaseManager(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def collection(self, db: Database):
        return db[self.model.collection_name]

    def get_by_id(self, db: Database, id_val: str) -> Optional[T]:
        document = self.collection(db).find_one({"complaint_id": id_val})
        return self.model.from_document(document) if document else None

    def get_all(self, db: Database, skip: int = 0, limit: int = 100) -> List[T]:
        cursor = self.collection(db).find({}).sort("created_at", -1).skip(skip).limit(limit)
        return [self.model.from_document(document) for document in cursor]

    def create(self, db: Database, obj_in: dict) -> T:
        db_obj = self.model(**obj_in)
        self.collection(db).insert_one(db_obj.to_document())
        return db_obj

    def update(self, db: Database, db_obj: T, update_data: dict) -> T:
        values = {field: value for field, value in update_data.items() if value is not None and hasattr(db_obj, field)}
        if values:
            self.collection(db).update_one({"complaint_id": db_obj.complaint_id}, {"$set": values})
            for field, value in values.items():
                setattr(db_obj, field, value)
        return db_obj

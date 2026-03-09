from sqlalchemy.orm import Session
import models, schemas, auth

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def add_friend(db: Session, user_id: int, friend_username: str):
    friend = get_user_by_username(db, friend_username)
    if not friend:
        return None
    # 检查是否已经是好友
    existing = db.query(models.Friendship).filter(
        models.Friendship.user_id == user_id, 
        models.Friendship.friend_id == friend.id
    ).first()
    if existing:
        return friend # 已经是好友
    
    friendship = models.Friendship(user_id=user_id, friend_id=friend.id)
    db.add(friendship)
    db.commit()
    return friend

def get_friends(db: Session, user_id: int):
    # 返回 User 对象列表
    friendships = db.query(models.Friendship).filter(models.Friendship.user_id == user_id).all()
    return [f.friend for f in friendships]

def create_record(db: Session, record: schemas.RecordCreate, user_id: int):
    db_record = models.TrainingRecord(**record.dict(), user_id=user_id)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

from typing import List

def get_records(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.TrainingRecord).filter(models.TrainingRecord.user_id == user_id).order_by(models.TrainingRecord.date.desc()).offset(skip).limit(limit).all()

def get_records_by_users(db: Session, user_ids: List[int], skip: int = 0, limit: int = 100):
    return db.query(models.TrainingRecord).filter(models.TrainingRecord.user_id.in_(user_ids)).order_by(models.TrainingRecord.date.desc()).offset(skip).limit(limit).all()

def delete_record(db: Session, record_id: int, user_id: int):
    record = db.query(models.TrainingRecord).filter(models.TrainingRecord.id == record_id, models.TrainingRecord.user_id == user_id).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

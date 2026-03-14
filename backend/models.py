from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, JSON
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    records = relationship("TrainingRecord", back_populates="owner")
    study_records = relationship("StudyRecord", back_populates="owner")
    
    # Friendship: user_id 指向当前用户，friend_id 指向好友
    friends = relationship("Friendship", foreign_keys="[Friendship.user_id]", back_populates="user")

class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    friend_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", foreign_keys=[user_id], back_populates="friends")
    # friend 关系不需要反向引用到 User 的某个特定字段，因为我们只关心从 User 查好友
    friend = relationship("User", foreign_keys=[friend_id])

class TrainingRecord(Base):
    __tablename__ = "training_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, index=True)
    type = Column(String)  # 'jogging', 'interval', 'quality'
    
    # 存储详情，根据 type 不同结构不同
    # jogging: {distance: float, pace: str, heart_rate: int, note: str}
    # interval: {sets: [{distance: float, count: int}], note: str}
    # quality: {content: str}
    details = Column(JSON) 
    
    owner = relationship("User", back_populates="records")

class StudyRecord(Base):
    __tablename__ = "study_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, index=True)
    
    # List of {text: str, completed: bool}
    todos = Column(JSON, default=list)
    review = Column(String, nullable=True)

    owner = relationship("User", back_populates="study_records")

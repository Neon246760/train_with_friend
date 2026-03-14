from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional

import crud, models, schemas, auth, database
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user

# 注册接口（可选，主要由管理员添加）
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/friends/", response_model=schemas.Friend)
def add_friend(friend: schemas.FriendCreate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_friend = crud.add_friend(db, user_id=current_user.id, friend_username=friend.friend_username)
    if not db_friend:
        raise HTTPException(status_code=404, detail="User not found")
    return db_friend

@app.get("/friends/", response_model=List[schemas.Friend])
def read_friends(db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.get_friends(db, user_id=current_user.id)

@app.post("/records/", response_model=schemas.Record)
def create_record(record: schemas.RecordCreate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_record(db=db, record=record, user_id=current_user.id)

@app.get("/records/", response_model=List[schemas.Record])
def read_records(
    user_id: Optional[int] = None, 
    friend_id: Optional[int] = None, # 如果提供了，则同时查看自己和该好友的记录
    db: Session = Depends(auth.get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    # 如果指定了 user_id，则查看该用户的记录（需是好友或自己）
    # 注意：user_id 优先级高于 friend_id，如果指定了 user_id，friend_id 将被忽略
    if user_id:
        # 简单权限检查：如果是查自己，直接通过
        if user_id == current_user.id:
             return crud.get_records(db, user_id=user_id)
        
        # 如果是查别人，检查是否是好友
        friends = crud.get_friends(db, user_id=current_user.id)
        is_friend = any(f.id == user_id for f in friends)
        if not is_friend:
             raise HTTPException(status_code=403, detail="Not a friend")
        
        return crud.get_records(db, user_id=user_id)
    
    # 如果没有指定 user_id，但指定了 friend_id
    if friend_id:
        friends = crud.get_friends(db, user_id=current_user.id)
        is_friend = any(f.id == friend_id for f in friends)
        if not is_friend:
             raise HTTPException(status_code=403, detail="Not a friend")
        
        # 同时返回自己和好友的记录
        return crud.get_records_by_users(db, user_ids=[current_user.id, friend_id])

    return crud.get_records(db, user_id=current_user.id)

@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    success = crud.delete_record(db, record_id=record_id, user_id=current_user.id)
    if not success:
         raise HTTPException(status_code=404, detail="Record not found or permission denied")
    return {"ok": True}

# --- Study Records Endpoints ---

@app.post("/study_records/", response_model=schemas.StudyRecord)
def create_study_record(record: schemas.StudyRecordCreate, db: Session = Depends(auth.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    return crud.create_or_update_study_record(db=db, record=record, user_id=current_user.id)

@app.get("/study_records/", response_model=List[schemas.StudyRecord])
def read_study_records(
    user_id: Optional[int] = None, 
    friend_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(auth.get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    if user_id:
        if user_id == current_user.id:
             return crud.get_study_records(db, user_id=user_id, limit=limit)
        
        friends = crud.get_friends(db, user_id=current_user.id)
        is_friend = any(f.id == user_id for f in friends)
        if not is_friend:
             raise HTTPException(status_code=403, detail="Not a friend")
        
        return crud.get_study_records(db, user_id=user_id, limit=limit)
    
    if friend_id:
        friends = crud.get_friends(db, user_id=current_user.id)
        is_friend = any(f.id == friend_id for f in friends)
        if not is_friend:
             raise HTTPException(status_code=403, detail="Not a friend")
        
        return crud.get_study_records_by_users(db, user_ids=[current_user.id, friend_id], limit=limit)

    return crud.get_study_records(db, user_id=current_user.id, limit=limit)

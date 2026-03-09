from database import SessionLocal, engine
import models, auth
import sys

models.Base.metadata.create_all(bind=engine)

def create_user(username, password):
    db = SessionLocal()
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        print(f"User {username} already exists.")
        return
    
    hashed_password = auth.get_password_hash(password)
    user = models.User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    print(f"User {username} created successfully.")
    db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <password>")
    else:
        create_user(sys.argv[1], sys.argv[2])

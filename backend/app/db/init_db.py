from app.db.session import Base, engine
from app.models import User, ChatRoom, ChatRoomMember, Message  # noqa: F401

def main():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    main()

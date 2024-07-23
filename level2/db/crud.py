import uuid
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.exc import IntegrityError

database_url = "sqlite:///./database.db"
engine = create_engine(database_url)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base=sqlalchemy.orm.declarative_base()

class UserChatSession(Base):
    __tablename__ = "user_chat_sessions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True)
    chat_history = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
     db = SessionLocal()
     try:
         yield db
     finally:
         db.close()


def create_session(db: Session):
    while True:
        session_id = str(uuid.uuid4())
        user_session = UserChatSession(session_id=session_id, chat_history="[]")
        db.add(user_session)
        try:
            db.commit()
            db.refresh(user_session)
            return session_id
        except IntegrityError:
            db.rollback()  # Rollback the transaction on IntegrityError
            continue  # Retry generating a new session_id


def get_current_session(session_id: str, db: Session):
    session=db.query(UserChatSession).filter(UserChatSession.session_id == session_id).first()
    print(session)
    return session



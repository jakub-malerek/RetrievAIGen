from .db import Base, engine
from .models import ChatSession, Message

Base.metadata.create_all(bind=engine)

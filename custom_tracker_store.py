import logging
import datetime
import json
import traceback
from rasa.core.tracker_store import TrackerStore
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import (Any,Dict,Optional)
from rasa.shared.core.trackers import DialogueStateTracker, Dialogue

logger = logging.getLogger(__name__)
Base = declarative_base()

class ConversationTracker(Base):
  __tablename__ = 'rasa_conversation_trackers'

  id = Column(Integer, primary_key=True)
  sender_id = Column('sender_id',String(255))
  conversation_data = Column(Text)
  message = Column(Text)
  created = Column(DateTime, default=datetime.datetime.utcnow)
  updated = Column(DateTime, default=datetime.datetime.utcnow)
  deleted = Column(Boolean, unique=False, default=True)

class CustomTrackerStore(TrackerStore):
  def __init__(self, domain, event_broker, **kwargs: Dict[Text, Any]):
    super().__init__(domain, event_broker, **kwargs)
    host = kwargs.get('host')
    port = kwargs.get('port')
    username = kwargs.get('username')
    password = kwargs.get('password')
    dbname = kwargs.get('dbname')
    url = "mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(username, password, host, port, dbname)
    logger.info("======= BEGIN =======")
    logger.info(url)
    logger.info("======= END =======")
    # Initialize database connection
    self.engine = create_engine(url)
    Base.metadata.create_all(self.engine)
    self.Session = sessionmaker(bind=self.engine)

  def save(self, tracker: DialogueStateTracker) -> None:
    # Serialize tracker data
    latest_message = tracker.latest_message.text;
    logger.info("======= BEGIN =======")
    logger.info("custom_tracker_store#save")
    logger.info("=======")
    for e in tracker.events:
      print(e)
    logger.info("=======")
    if self.event_broker:
      self.stream_events(tracker)
    conversation_data = tracker.as_dialogue().as_dict()
    conversation_data = json.dumps(conversation_data)
    logger.info("latest_message: %s", latest_message)
    logger.info("conversation_data: %s", conversation_data)
    logger.info("======= END =======")
    #conversation_data = json.dumps(tracker.current_state())
    conversation_tracker = ConversationTracker(sender_id=tracker.sender_id, conversation_data=conversation_data, message=latest_message)
    # Save conversation tracker to the database
    with self.Session() as session:
      session.add(conversation_tracker)
      session.commit()

  def retrieve(self, sender_id) -> Optional[DialogueStateTracker]:
    logger.info("======= BEGIN =======")
    logger.info("custom_tracker_store#retrieve")
    logger.info("sender_id: %s", sender_id)
    logger.info("=======")
    # Retrieve conversation tracker from the database
    with self.Session() as session:
      conversation = session.query(ConversationTracker).filter_by(sender_id=sender_id).order_by(ConversationTracker.id.desc()).first()
      if conversation:
        try:
          events_json = json.loads(conversation.conversation_data)
          logger.info("id: %s", conversation.id)
          logger.info("latest_message: %s", conversation.message)
          logger.info(type(events_json))
          logger.info(events_json)
          logger.info("======= END =======")
          tracker = DialogueStateTracker.from_dict(sender_id, [events_json], self.domain.slots)
          return tracker
        except Exception as e:
          logging.error(traceback.format_exc())
          logger.info("======= END =======")
          return None
      else:
        logger.info("======= END =======")
        return None

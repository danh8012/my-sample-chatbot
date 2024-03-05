import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted

logger = logging.getLogger(__name__)

class ActionSaveConversation(Action):

  def name(self) -> Text:
    return "action_save_conversation"

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    logging.info("======")
    logging.info("action_save_conversation")
    logging.info("send_id: %s", tracker.sender_id)
    for e in tracker.events:
      if e['event'] in ('bot', 'user'):
        #logger.info("%s: %s", e['event'], e['text'])
        logger.info("")
        logger.info(e)
    logging.info("======")
    dispatcher.utter_message(text="stored conversations")
    return [Restarted()]

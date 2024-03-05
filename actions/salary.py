import logging
import requests
import json
import cachetools
from datetime import datetime, timedelta
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

logger = logging.getLogger(__name__)
my_cache = cachetools.TTLCache(maxsize=1,ttl=timedelta(hours=12), timer=datetime.now)

class ActionFindSalaryForm(Action):
  
  def name(self) -> Text:
    return "action_find_salary_form"
  
  @cachetools.cached(my_cache)
  @staticmethod
  def salary_data(key):
    logger.info("====")
    logger.info("[my-debug]\tsalary.py#ActionFindSalaryForm#salary_data")
    logger.info("====")
    headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }
    response_API = requests.get('https://reqres.in/api/users?page=0', headers=headers)
    status = response_API.status_code
    if status==200:
      data = response_API.content
      return json.loads(data)
    return json.loads({})

  def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
    logger.info("====")
    logger.info("[my-debug]\tsalary.py#ActionFindSalaryForm#run")
    employee_name = tracker.get_slot("employee_name")
    logger.info("employee_name: %s", employee_name)
    logger.info("====")
    if employee_name:
      parse_json = self.salary_data()
      salary = 0
      for em in parse_json['data']:
        if em['email']==employee_name:
          salary = em['first_name'] + " " + em['last_name']
      dispatcher.utter_message(text="Full name: " + str(salary))
    else:
        dispatcher.utter_message(text="Sorry! Not found your salary.")
    return []

class ValidateFindSalaryForm(FormValidationAction):

  def name(self) -> Text:
    return "validate_find_salary_form"
  
  def extract_employee_name(
    self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
  ) -> Dict[Text, Any]:
    logger.info("====")
    logger.info("[my-debug]\tsalary.py#ValidateFindSalaryForm#extract_employee_name")
    employee_name = tracker.latest_message.get("text")
    slot_name = tracker.slots["requested_slot"]
    logger.info("employee_name: %s", employee_name)
    logger.info("slot_name: %s", slot_name)
    logger.info("====")
    if slot_name=="employee_name":
      return {"employee_name": employee_name}
    return {"employee_name": None}

  def validate_employee_name(
    self,
    slot_value: Any,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
  ) -> Dict[Text, Any]:
    logger.info("====")
    logger.info("[my-debug]\tsalary.py#ValidateFindSalaryForm#validate_employee_name")
    logger.info("slot_value: %s", slot_value)
    logger.info("====")
    return {"employee_name": slot_value}

import copy
from datetime import datetime, timezone, timedelta
import string
import sys
import time
import typing
from behave import *
import logging

import requests
from APIAutomation.common.cache import cache
from APIAutomation.config.config import *
import random

global cacheObj
logging.basicConfig(
    filename="result.log",
    filemode="w",
    format="%(asctime)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logging.basicConfig(level=logging.DEBUG)
dict = []
cacheObj = cache(dict)

@given('I get details for current user logged into the system and save details in {user_details_cache}')
def user_details(context, user_details_cache):
  try:
    user = get_user_details()
    logging.info(f"Details of user:") 
    logging.info(f"     {user}")
    details = {
            "id": user["_id"],
            "first_name" : user["firstName"],
            "last_name" : user["lastName"],
            "email": user["email"],
            "__v" : user["__v"]
          }
    if len(user) == 0:
      logging.info(f"No user details provided")
      raise(Exception("Missing user"))
    else:
      cache.__setitem__(cacheObj, user_details_cache, details)
  except Exception as e:
      stopWorkflow(str(e))

@step('I add new user {first_name}, {last_name} with password {password} into the system and save details in {new_user_details_cache}')
def add_user(context, first_name, last_name, password, new_user_details_cache):
  try:
    import random
    # Random string of length 5
    first_part_mail = ''.join((random.choice('Abcdefgh') for i in range(5)))
    second_part_mail = ''.join((random.choice('Ijklmnop') for i in range(5)))
    
    email = (f"{first_part_mail}.{second_part_mail}@mail.com")
    
    user = add_new_user(first_name, last_name, email, password)
    logging.info(f"Details of user:") 
    logging.info(f"     {user}")
    details = {
            "id": user["user"]["_id"],
            "first_name" : user["user"]["firstName"],
            "last_name" : user["user"]["lastName"],
            "email": user["user"]["email"],
            "__v" : user["user"]["__v"],
            "token" : user["token"]
          }
    if len(user) == 0:
      logging.info(f"User was not created!")
      raise(Exception("Create of user FAILED!"))
    else:
      cache.__setitem__(cacheObj, new_user_details_cache, details)
  except Exception as e:
        stopWorkflow(str(e))

@step('I want to login as user using details from {new_user_cache} with password {password} into the system and save details in {logged_user_details_cache}')
def user_login(context, new_user_cache, password, logged_user_details_cache):
  try:
    new_user_details = cache.__getitem__(cacheObj, new_user_cache)   
    email = new_user_details["email"]
    user = login_user(email, password)
    logging.info(f"Details of user:") 
    logging.info(f"     {user}")
    details = {
            "id": user["user"]["_id"],
            "first_name" : user["user"]["firstName"],
            "last_name" : user["user"]["lastName"],
            "email": user["user"]["email"],
            "__v" : user["user"]["__v"],
            "token" : user["token"]
          }
    if len(user) == 0:
      logging.info(f"User LOGGED IN!")
      raise(Exception("Login of user FAILED!"))
    else:
      cache.__setitem__(cacheObj, logged_user_details_cache, details)
  except Exception as e:
        stopWorkflow(str(e))

@then('I want to add new contact with details: {first_name}, {last_name}, {phone}, {street1}, {street2}, {city}, {country}, to Contact List and save details in {added_contact_details_cache}')
def add_contact(context, first_name, last_name, phone, street1, street2, city, country, added_contact_details_cache):
  try:
    email = (f"{first_name}.{last_name}@mail.com")
    birthdate = datetime.today().strftime('%Y-%m-%d')
    phone = ''.join(random.choice(string.digits) for _ in range(10))
    state_province = 'StateP'
    postal_code = 1234
    contact = add_new_contact(first_name, last_name, birthdate, email, phone, street1, street2, city, state_province, postal_code, country)
    logging.info(f"Details of contact:") 
    logging.info(f"     {contact}")
    details = {
            "id": contact["_id"],
            "first_name" : contact["firstName"],
            "last_name" : contact["lastName"],
            "birthdate" : contact["birthdate"],
            "email" : contact["email"],
            "phone" : contact["phone"],
            "street1" : contact["street1"],
            "street2" : contact["street2"],
            "city" : contact["city"],
            "state_province" : contact["stateProvince"],
            "postal_code" : contact["postalCode"],
            "country": contact["country"],
            "owner" : contact["owner"],
            "__v": contact["__v"]
          }
    if len(contact) == 0:
      logging.info(f"Contact was not added!")
      raise(Exception("Addinf of new contact FAILED!"))
    else:
      cache.__setitem__(cacheObj, added_contact_details_cache, details)
  except Exception as e:
        stopWorkflow(str(e))

@given('I get details for contacts from Contact List and save details in {contact_list_details_cache}')
def contact_details(context, contact_list_details_cache):
  try:
    resource_details = []                
    for contact in get_contact_list_details():
        details = {
            "id": contact["_id"],
            "first_name" : contact["firstName"],
            "last_name" : contact["lastName"],
            "birthdate" : contact["birthdate"],
            "email" : contact["email"],
            "phone" : contact["phone"],
            "street1" : contact["street1"],
            "street2" : contact["street2"],
            "city" : contact["city"],
            "state_province" : contact["stateProvince"],
            "postal_code" : contact["postalCode"],
            "country": contact["country"],
            "owner" : contact["owner"],
            "__v": contact["__v"]
        }
        resource_details.append(details)
    if len(resource_details) == 0:
      logging.info(f"No contact found")
      raise(Exception("Missing contacts"))
    else:
      logging.info(f"Details of contact:") 
      logging.info(f"     {resource_details}")
      cache.__setitem__(cacheObj, contact_list_details_cache, resource_details)
  except Exception as e:
      stopWorkflow(str(e))

@step('Validate that contact from {added_contact_details_cache} is added to Contact List in {contact_list_details_cache}')
def validate_contacts(context, added_contact_details_cache, contact_list_details_cache):
    details_added = cache.__getitem__(cacheObj, added_contact_details_cache)   
    details_contact_list = cache.__getitem__(cacheObj, contact_list_details_cache)
    # Deep copy was needed because any changes to local variables will affect data stored in cache
    details_contact_list = copy.deepcopy(details_contact_list)    
    found_match = ''
    if len(details_contact_list) != 0:         
        try: 
            for item in details_contact_list:
                added = validate_contact_details(details_added, item)
                if added:
                    found_match = copy.deepcopy(item)
                    break
            if found_match:
                logging.info(f"Contact is found in contact list!")
            else:
                logging.info(f"Contact is MISSING from contact list")
                raise(Exception("Missing contact from contact list"))
        except Exception as e:
            stopWorkflow(str(e))
    
def get_user_details():
  url = f"{settings['Contact_List']['api_url']}{settings['Users_Endpoints']['users']}{settings['Users_Endpoints']['current_user']}"
  header = {
      "Authorization": settings["Contact_List"]["authorization_token"],
      "Content-Type": "application/json",
      "Accept": "application/json" 
  }  
  response = getContactListEndpointResponse("get", url, header)
  json_response = response.json()  
  return json_response

def get_contact_list_details():
  url = f"{settings['Contact_List']['api_url']}{settings['Contact_Endpoints']['contacts']}"
  header = {
      "Authorization": settings["Contact_List"]["authorization_token"],
      "Content-Type": "application/json",
      "Accept": "application/json" 
  }  
  response = getContactListEndpointResponse("get", url, header)
  json_response = response.json()
  return json_response

def add_new_user(first_name, last_name, email, password):
    url = f"{settings['Contact_List']['api_url']}{settings['Users_Endpoints']['users']}"
    header = {
        "Authorization": settings["Contact_List"]["authorization_token"],
        "Content-Type": "application/json",
        "Accept": "application/json" 
    }
    data = json.dumps({
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "password": password   
            })
    response = getContactListEndpointResponse("post", url, header, data)
    json_response = response.json()  
    return json_response

def login_user(email, password):
    url = f"{settings['Contact_List']['api_url']}{settings['Users_Endpoints']['users']}{settings['Users_Endpoints']['login_user']}"
    header = {
        "Authorization": settings["Contact_List"]["authorization_token"],
        "Content-Type": "application/json",
        "Accept": "application/json" 
    }
    data = json.dumps({
                "email": email,
                "password": password   
            })
    response = getContactListEndpointResponse("post", url, header, data)
    json_response = response.json()  
    return json_response

def add_new_contact(first_name, last_name, birthdate, email, phone, street1, street2, city, state_province, postal_code, country):
    url = f"{settings['Contact_List']['api_url']}{settings['Contact_Endpoints']['contacts']}"
    header = {
        "Authorization": settings["Contact_List"]["authorization_token"],
        "Content-Type": "application/json",
        "Accept": "application/json" 
    }
    data = json.dumps({
                "firstName": first_name,
                "lastName": last_name,
                "birthdate": birthdate,
                "email": email,
                "phone": phone,
                "street1": street1,
                "street2": street2,
                "city": city,
                "stateProvince": state_province,
                "postalCode": postal_code,
                "country": country
            })
    response = getContactListEndpointResponse("post", url, header, data)
    json_response = response.json()  
    return json_response

def validate_contact_details(details_before, details_after):      
    if (
        details_after["id"] == details_before["id"]
        and details_after["first_name"] == details_before["first_name"]
        and details_after["last_name"] == details_before["last_name"]
        and details_after["birthdate"] == details_before["birthdate"]
        and details_after["email"] == details_before["email"]
        and details_after["phone"] == details_before["phone"]
        and details_after["street1"] == details_before["street1"]
        and details_after["street2"] == details_before["street2"]
        and details_after["city"] == details_before["city"]
        and details_after["state_province"] == details_before["state_province"]
        and details_after["postal_code"] == details_before["postal_code"]
        and details_after["country"] == details_before["country"]
        and details_after["owner"] == details_before["owner"]
    ):
        return True
    return False

#Methods defined below I would usually put to separate class under common folder(i.e. GlobalUtil),
# but for this purpose I've left it in the same file
def stopWorkflow(value) :
    logging.error(value)
    print("---------------ERROR----------------")
    print(value)
    sys.exit(1)


def getContactListEndpointResponse(httpMethod, url, headers, data = "", params = "", files = "", *args, verify=True):
    response = ""
    counter = 8 #limitation in case API call fails for 8 times in the row
    try:
        while counter > 0:
            if httpMethod == "get" and params == "" and data == "":
                response = requests.request(
                httpMethod,
                url = url, 
                verify=verify,
                headers = headers           
                )
            elif httpMethod == "get" and params != "" and data == "":
                response = requests.request(
                httpMethod,
                url = url,           
                headers = headers,
                verify=verify,
                params = params           
                )
            elif httpMethod == "delete" and params == "" and data == "":
                response = requests.request(
                httpMethod,           
                url = url,
                verify=verify,       
                headers = headers           
                )
            elif httpMethod == "post" and data != "":
                response = requests.request(
                httpMethod,
                url = url,
                verify=verify,   
                headers = headers,
                data = data           
                )
            if response.status_code != 200 and response.status_code != 201:
                time.sleep(20) #20 seconds between retry
                counter -= 1
                continue
            else:
                break
    except requests.HTTPError as e:
        logging.error(f"Error: {e}")
        return False
    if response.status_code != 200 and response.status_code != 201:
        logging.error("Unexpected response, with text")
        logging.info(response.text)
    return response

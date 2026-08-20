import time
from bs4 import BeautifulSoup
import bs4
from tqdm import tqdm
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from datetime import date
import random
import string
import json
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import requests
from configparser import ConfigParser
import psycopg2
import validators
import phonenumbers
options = Options()
options.add_argument('--headless')
HEADLESS_OPTIONS = {'chrome_options': options}
import logging
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from eld import LanguageDetector

logger = logging.getLogger(__name__)

def validate_mobile_number(mobile_number):
	pattern = re.compile(r'^\+((?:9[679]|8[035789]|6[789]|5[90]|42|3[578]|2[1-689])|9[0-58]|8[1246]|6[0-6]|5[1-8]|4[013-9]|3[0-469]|2[70]|7|1)(?:\W*\d){0,13}\d$')
	return bool(pattern.match(mobile_number))

def connect():
	""" Connect to the PostgreSQL database server """
	conn = None
	try:
		# read connection parameters
		params = config(filename='database.ini', section='postgresql')

		# connect to the PostgreSQL server
		print('Connecting to the PostgreSQL database...')
		conn = psycopg2.connect(**params)
		
		# create a cursor
		cur = conn.cursor()
		
	# execute a statement
		print('PostgreSQL database version:')
		cur.execute('SELECT version()')

		# display the PostgreSQL database server version
		db_version = cur.fetchone()
		print(db_version)
	   
	# close the communication with the PostgreSQL
		cur.close()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if conn is not None:
			return conn

			
def config(filename='database.ini', section='postgresql'):
	# create a parser
	parser = ConfigParser()
	# read config file
	parser.read(filename)
	print("Filename:" + filename)
	# get section, default to postgresql
	db = {}
	if parser.has_section(section):
		params = parser.items(section)
		for param in params:
			db[param[0]] = param[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))

	return db
SELECT_CONTRACT_BUTTON_SELECTOR = "#main > div > div > div:nth-child(3) > form > div > ul > li:nth-child(1) > div > div.contract-list__item-buttons > button"


def login_crm():
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	jsondata = {}
	login_api = "https://crm.fitech.com.vn/Api/access_token"
	
	jsondata["grant_type"] = "client_credentials"
	jsondata["client_id"] = "ccfd00e1-307e-e56f-1e06-6592d6c95397"
	jsondata["client_secret"] = "apiuser@Fitech#vn"
	print(type(jsondata))
	data = requests.post(login_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["access_token"]

def get_min_sale():
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/leads/find-minimum-sale"
	data = requests.get(check_api,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
		return json_object["data"]
	
	
def check_company_existed(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/accounts/check"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object
		
def check_lead_existed(title, account_name, contact):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/leads/check"
	jsondata = {"title":title,
				"last_name" : account_name,
				"first_name" : contact
	}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object

def getAccountSentMessageToday():
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/getAccountSentMessageToday"
	data = requests.post(check_api,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object


def add_new_account(access_token,name,phone,website,address, des):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Accounts",
	"attributes": {
	  "name": name,
	  "account_type": "Customer",
   	  "phone_office": phone,
	  "phone_alternate": phone,
	  "website": website,
	  "billing_address_country" : address,
	  "assigned_user_id": "62b60dd0-9ab9-735e-e291-65d2cd0ab68e",
	  "description" : des
	}
  }
}
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)

def edit_account(access_token,account_id,name,phone,website,address, des):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Accounts",
 	"id": account_id,
	"attributes": {
	  "name": name,
	  "account_type": "Customer",
   	  "phone_office": phone,
	  "phone_alternate": phone,
	  "website": website,
	  "billing_address_country" : address,
	  "assigned_user_id": "62b60dd0-9ab9-735e-e291-65d2cd0ab68e",
	  "description" : des
	}
  }
}
	time.sleep(2)
	data = requests.patch(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
	 
	 
def add_new_lead(access_token,company_name,company_id,title,address,other_address,phone_company,hirer_phone,hirer_email,website,content,assigned_user_id, lead_status, job_phone, hirer_name, refer, contact_id, status_des):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	assigned_user = ""
	if(len(assigned_user_id)):
		assigned_user = assigned_user_id
	jsondata =  {
  "data": {
	"type": "Leads",
	"attributes": {
	  "first_name": hirer_name,
	  "last_name": company_name,
	  "phone_work": phone_company,
	  "phone_mobile": hirer_phone,
	  "phone_other": job_phone,
	  "phone_home": hirer_phone,
	  "website": website,
	  "account_name": company_name,
	  "account_id" : company_id,
	  "status" : lead_status,
	  "primary_address_country": address,
	  "alt_address_street": other_address,
	  "description": content,
	  "title": title,
	  "email1": hirer_email,
	   "assigned_user_id" : assigned_user,
	  "refered_by" : "",
	  "contact_id" : contact_id,
	  "status_description": status_des
	}
  }
}
	# Ha cmt
	#print(jsondata)
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print('fail')
		print(data.status_code)
		print(data.reason)
	else:
		print('done')
		json_object = data.json()
		print(json_object)
		
def edit_new_lead(access_token,lead_id,job_id,company_name,company_id,title,address,other_address,phone_company,hirer_phone,hirer_email,website,content, lead_status, job_phone, assigned_user_id, hirer_name, refer, contact_id, status_des):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	assigned_user = ""
	if(len(assigned_user_id)):
		assigned_user = assigned_user_id
	jsondata =  {
  "data": {
	"type": "Leads",
	"id" : lead_id,
	"attributes": {
	  "first_name": hirer_name,
	  "last_name": company_name,
	  "phone_work": phone_company,
	  "phone_mobile": hirer_phone,
	  "phone_other": job_phone,
	  "phone_home": hirer_phone,
	  "website": website,
	  "account_name": company_name,
	  "account_id" : company_id,
	  "status" : lead_status,
	  "primary_address_country": address,
	  "alt_address_street": other_address,
	  "title": title,
	  "description": content,
	  "email1" : hirer_email,
	  "assigned_user_id": assigned_user,
	  "refered_by" : "",
	  "contact_id": contact_id,
	  "status_description": status_des
	}
  }
}
	# Ha cmt
	#print(jsondata)
	time.sleep(2)
	data = requests.patch(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print('fail')
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)


def check_contact(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/contact/check"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\ncheck_contact" + data.reason)
	else:
		json_object = data.json()
		return json_object


def add_contact(access_token,title, name, email, phone, des, link, account_id):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Contacts",
	"attributes": {
	  "last_name": name,
	  "title": title,
	  "description" : des,
	  "email" : email,
	  "phone_work" : phone,
	  "created_by_link" : link,
	  "account_id" : account_id,
	  "created_by": "1",
	  "assigned_user_id": "62b60dd0-9ab9-735e-e291-65d2cd0ab68e"
	}
  }
}
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print('fail')
		print(data.status_code)
		print(data.reason)
	else:
		print('done')
		json_object = data.json()
		print(json_object)

def edit_contact(access_token, contact_id , title, name, email, phone, des, link, account_id):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "Contacts",
	"id" : contact_id,
	"attributes": {
	  "last_name": name,
	  "title": title,
	  "description" : des,
	  "email" : email,
	  "phone_work" : phone,
	  "created_by_link" : link,
	  "account_id" : account_id
	}
  }
}
	# Ha cmt
	#print(jsondata)
	time.sleep(2)
	data = requests.patch(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print('fail')
		print(data.status_code)
		print(data.reason)
	else:
		print('done')
		json_object = data.json()
		print(json_object)


def check_email_existed(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/emails/check"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["data"]  

def check_email_lead(lead_id):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/email_lead/check"
	jsondata = {"name":lead_id}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object
def add_email_lead(access_token, email_id, lead_id, bean_type):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "email_addr_bean_rel",
	"attributes": {
		 "email_address_id": email_id,
		 "bean_id": lead_id,
		 "bean_module" : bean_type
	}
	}
	}
	time.sleep(2)
	data = requests.post(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)
		
def edit_email_lead(access_token,email_lead_id,email_id):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module"
	jsondata =  {
  "data": {
	"type": "email_addr_bean_rel",
	"id": email_lead_id,
	"attributes": {
		 "email_address_id": email_id
	}
	}
	}
	time.sleep(2)
	data = requests.patch(module_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		print(json_object)

def get_contact_assigned_user(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/lead/getassigneduserbycontact"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\ncontact_assigned" + data.reason)
	else:
		json_object = data.json()
		return json_object["data"]

def get_account_assigned_user(name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/lead/getassigneduserbyaccount"
	jsondata = {"name":name}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\naccount_assigned" + data.reason)
	else:
		json_object = data.json()
		return json_object["data"]

def get_account_email_assigned_user(name,email):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/lead/getassigneduserbyaccountandemail"
	jsondata = {"param_1":name,
			 "param_2":email}
	# Ha cmt
	#print(jsondata)

	data = requests.post(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print("\naccount_assigned" + data.reason)
	else:
		json_object = data.json()
		return json_object["data"]

def get_num_mess_sent_lead(access_token):
	headers = {'Content-Type': "application/json", 'Accept': "application/json", "Authorization": "Bearer " + access_token}
	module_api = "https://crm.fitech.com.vn/Api/V8/module/Leads?filter[mess_sent_c][eq]=1"
	time.sleep(2)
	data = requests.get(module_api,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["data"]

def get_lead_count_one_year(company_name):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/getLeadCountByCompany"
	jsondata = {"name":company_name}
	data = requests.get(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object

def check_email_expired(email):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/getactivelead"
	jsondata = {"name":email}
	data = requests.get(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["email_expired"]
	

def check_lead_status_with_email(email):
	headers = {'Content-Type': "application/json", 'Accept': "application/json"}
	check_api = "http://68.183.189.171:9999/get_lead_status_with_email"
	jsondata = {"name":email}
	data = requests.get(check_api,json=jsondata,headers=headers)
	if data.status_code != 200:
		print(data.status_code)
		print(data.reason)
	else:
		json_object = data.json()
		return json_object["status_count"]

def get_job_href(driver,job_id,access_token,address, country, linkedin_acc):	
	root_window = driver.window_handles[0]
	print("\n job_id",job_id)
	#1 job detail window 
	driver.execute_script("window.open('');")
	job_detail_window = driver.window_handles[1]
	driver.switch_to.window(job_detail_window)
	

	job_detail_url = 'https://www.linkedin.com/jobs/view/' + job_id
	driver.get(job_detail_url)
	time.sleep(10)
	# company_element_ = driver.find_element(By.TAG_NAME,"a")
	company_element_urls = driver.find_elements(By.CSS_SELECTOR,"a")
	print(len(company_element_urls))
	for company_element_url in company_element_urls:
		company_url = company_element_url.get_attribute("href")
		company_url_name = company_element_url.text
		print(company_url)
		print("company_url_name: ", company_url_name)
  
def add_job_facebook(profile_link,access_token, profile_name):
	contact_info = check_contact(profile_name)
	if(contact_info["data"] == ""):
		add_contact(access_token = access_token,title = "" , name = profile_name, email = "", phone = "", des = "", link = profile_link, account_id= "")
		add_new_lead(access_token=access_token, company_name="from fb", company_id = "",title="from fb",address="Vietnam",other_address="Vietnam",phone_company="",hirer_phone = "",hirer_email = "",website= profile_link,content="",assigned_user_id="d6ea87ac-8c7e-a4ed-ba81-65f500a98e58", lead_status = "New", job_phone = "", hirer_name = profile_name, refer= "", contact_id = "", status_des = "")


def get_lk_credentials(path="./lk_credentials.json"):
	f = open(path)
	data = json.load(f)
	f.close()
	return data

def enter_ids_on_lk_signin(driver, email, password):
	time.sleep(10)
 
	# usernameInputElement = driver.find_element(By.ID, "username")
	# usernameInputElement.send_keys(email)
	# passwordInputElement = driver.find_element(By.ID, "password")
	# passwordInputElement.send_keys(password)
	# submitElement = driver.find_element(
	# 	By.CSS_SELECTOR,
	# 	"#organic-div > form > div.login__form_action_container > button",
	# )
	
	# usernameInputElement = driver.find_elements(By.ID, "«r3»")[-1]
	# usernameInputElement.send_keys(email)
	# passwordInputElement = driver.find_elements(By.ID, "«r4»")[-1]
	# passwordInputElement.send_keys(password)    
	usernameInputElement = driver.find_elements(By.ID, "_R_1h6kqsqppb6amH1_")[-1]  # _r_2_, _R_1h6kqsqppb6amH1_
	usernameInputElement.send_keys(email)
	passwordInputElement = driver.find_elements(By.ID, "_R_1hmkqsqppb6amH1_")[-1]  # _r_d_, _R_1hmkqsqppb6amH1_
	passwordInputElement.send_keys(password)
	submitElement = driver.find_elements(By.CLASS_NAME,"xc8cyl1")[0]  
 
	# usernameInputElement = driver.find_element(By.ID, "session_key")
	# # print(len(usernameInputElement))
	# usernameInputElement.send_keys(email)
	# passwordInputElement = driver.find_element(By.ID, "session_password")
	# passwordInputElement.send_keys(password)
	# submitElement = driver.find_element(By.CSS_SELECTOR, "[data-id='sign-in-form__submit-btn']")
	time.sleep(2)
	submitElement.click()
	time.sleep(60)

# -*- coding: utf-8 -*-
def isEnglish(s):
	try:
		s.encode(encoding='utf-8').encode('ascii')
	except UnicodeEncodeError:
		return False
	else:
		return True
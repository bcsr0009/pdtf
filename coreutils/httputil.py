import logging
import requests
from coreutils.logdecorator import logwrap

@logwrap
def post_call(username, password, url, payloadlocation):
	'''
	post_call --> interact with nso-server to create resource
	'''
	logging.debug("username is:%s"% username)
	logging.debug("password is:%s"% password)
	logging.debug("url is:%s"% url)
	logging.debug("payloadlocation is:%s"% payloadlocation)
	s = requests.Session()
	s.auth = (username, password)
	headers = {"Content-Type":"application/vnd.yang.data+json"}
	s.headers = headers
	json_str = ""
	with open(payloadlocation, 'r') as json_file_obj:
		response =s.post(url, data=json_file_obj)
		logging.debug("response code is: %s"% response.status_code)
		logging.debug("response text is: %s"% response.text)
		if response.status_code == 200:
		    logging.debug("Created Resource Successfully")
		    return True
		else:
		    logging.debug("Resource Not Created, Please check logs with string 'response text is:' to find the reason of failure !!!")
		    return False

@logwrap
def patch_call(username, password, url, payloadlocation):
	'''
	patch_call --> interact with nso-server to append resource
	'''
	logging.debug("username is:%s"% username)
	logging.debug("password is:%s"% password)
	logging.debug("url is:%s"% url)
	logging.debug("payloadlocation is:%s"% payloadlocation)
	s = requests.Session()
	s.auth = (username, password)
	headers = {"Content-Type":"application/vnd.yang.data+json"}
	s.headers = headers
	json_str = ""
	with open(payloadlocation, 'r') as json_file_obj:
		response =s.patch(url, data=json_file_obj)
		logging.debug("response code is: %s"% response.status_code)
		logging.debug("response text is: %s"% response.text)
		if response.status_code == 204:
		    logging.debug("Created Resource Successfully")
		    return True
		else:
		    logging.debug("Resource Not Created, Please check logs with string 'response text is:' to find the reason of failure !!!")
		    return False

@logwrap
def delete_call(username, password, url):
	'''
	delete_call --> interact with nso-server to delete resource
	'''
	logging.debug("username is:%s"% username)
	logging.debug("password is:%s"% password)
	logging.debug("url is:%s"% url)
	s = requests.Session()
	s.auth = (username, password)
	headers = {"Content-Type":"application/vnd.yang.data+json"}
	s.headers = headers
	response =s.delete(url)
	logging.debug("response code is: %s"% response.status_code)
	logging.debug("response text is: %s"% response.text)
	if response.status_code == 204:
	    logging.debug("Resource Deleted Successfully")
	    return True
	else:
	    logging.debug("Resource Not Deleted Successfully, Please check logs with string 'response text is:' to find the reason of failure !!!")
	    return False

@logwrap
def get_call(username, password, get_url):
	'''
	get_call --> interact with nso-server to get resource
	'''
	logging.debug("username is:%s"% username)
	logging.debug("password is:%s"% password)
	logging.debug("url is:%s"% url)
	s = requests.Session()
	s.auth = (username, password)
	headers = {"Content-Type":"application/vnd.yang.data+json"}
	s.headers = headers
	response = s.get(get_url)
	logging.debug("response code is: %s"% response.status_code)
	logging.debug("response text is: %s"% response.text)


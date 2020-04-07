# coding: utf-8
import requests

import json
import paramiko
import time
import logging
import os
import difflib

from coreutils.logdecorator import logwrap

from coreutils import get_delta_from_expected_and_generated_configs

@logwrap
def execute_command(ssh_connection_handler):
	'''
	This method provides execute_command option on device
	'''
	stdin,stdout,stderr=ssh_connection_handler.exec_command('enable\nshow running-config')
	return stdin,stdout,stderr

@logwrap
def build_show_config_from_stdout(stdout, file):
	'''
	This method redirects stdout from execute command of device to file
	'''
	with open(file, "w") as rcbsp:
		for line in stdout.readlines():
			rcbsp.write(line)

@logwrap
def connect_to_nso_device(username, password, device_ip, port):
	'''
	This method provides ssh_handler to interact with device
	'''
	ssh_client = None
	try:
		ssh_client=paramiko.SSHClient()
		logging.info("ssh_client %s"% ssh_client)
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		logging.info("username %s"% username)
		logging.info("password %s"% password)
		logging.info("device_ip %s"% device_ip)
		logging.info("port %s"% port)
		ssh_client.connect(hostname=device_ip, username=username, password=password, port= port, allow_agent=False, look_for_keys=False)
	except Exception as e:
		logging.debug("Exception in SSH Connetion to Device is:%s"%e)
	return ssh_client

@logwrap
def get_running_config_from_device_before_service_push(ssh_connection_handler, before_service_push_config_file):
	'''
	This method provides running config before service create
	'''
	execute_command_result = execute_command(ssh_connection_handler)
	build_show_config_from_stdout(execute_command_result[1], before_service_push_config_file)
	
@logwrap
def get_running_config_from_device_before_service_delete(ssh_connection_handler, before_service_delete_config_file):
	'''
	This method provides running config before service delete
	'''
	execute_command_result = execute_command(ssh_connection_handler)
	build_show_config_from_stdout(execute_command_result[1], before_service_delete_config_file)

@logwrap
def get_running_config_from_device_after_service_push(ssh_connection_handler, after_service_push_config_file):
	'''
	This method provides running config after service create
	'''
	execute_command_result = execute_command(ssh_connection_handler)
	build_show_config_from_stdout(execute_command_result[1], after_service_push_config_file)

@logwrap
def get_running_config_from_device_after_service_delete(ssh_connection_handler, after_service_delete_config_file):
	'''
	This method provides running config after service delete
	'''
	execute_command_result = execute_command(ssh_connection_handler)
	build_show_config_from_stdout(execute_command_result[1], after_service_delete_config_file)

@logwrap
def get_generated_config_from_service_create(before_service_push, after_service_push, generated_service_config):
	'''
	This method provides generated config out of (before and after running configs )
	'''
	import difflib

	with open(before_service_push, 'r') as before_service_push_file_obj, open(after_service_push, 'r') as after_service_push_file_obj:
		before_service_push_file_content = before_service_push_file_obj.readlines()
		after_service_push_file_content = after_service_push_file_obj.readlines()

	with open(generated_service_config, 'w') as generated_service_config_obj:
		for line in after_service_push_file_content:
			if line in before_service_push_file_content:
				continue
			generated_service_config_obj.write(line)

@logwrap
def get_generated_config_from_service_delete(before_service_push, after_service_push, generated_service_config):
	'''
	This method provides generated config out of (before and after running configs )
	'''
	import difflib

	with open(before_service_push, 'r') as before_service_push_file_obj, open(after_service_push, 'r') as after_service_push_file_obj:
		before_service_push_file_content = before_service_push_file_obj.readlines()
		after_service_push_file_content = after_service_push_file_obj.readlines()

	with open(generated_service_config, 'w') as generated_service_config_obj:
		for line in before_service_push_file_content:
			if line in after_service_push_file_content:
				continue
			generated_service_config_obj.write(line)

@logwrap
def file_len(fname):
	'''
	file_len method to take file name and provide filelen
	'''
	i = 0
	with open(fname) as f:
		for i, l in enumerate(f):
			pass
		return i + 1

@logwrap
def validate_config(expected_config_file, generated_config_file, testcase,create = None,delete = None):
	'''
	validates create and delete generated configs against expected configs
	'''
	validate_create_flag = False
	validate_delete_flag = False
	if create == True:
		
		expected_config_file_exists = os.path.isfile(expected_config_file)
		if expected_config_file_exists:
			logging.debug("create expected config file exists")
		else:
			with open(expected_config_file, "w") as expected_config_file_obj, open(generated_config_file) as generated_config_file_obj:
				for line in generated_config_file_obj:
					expected_config_file_obj.write(line)
		expected_file_lines = file_len(expected_config_file)
		generated_file_lines = file_len(generated_config_file)
	
		logging.debug("create_expected_file_lines is:%s"% expected_file_lines)
		logging.debug("create_generated_file_lines is:%s"% generated_file_lines)
		if expected_file_lines == generated_file_lines:
			logging.debug("in if block-create")
			validate_flag_create = True
			with open(expected_config_file) as f1, open(generated_config_file) as f2:
			    
			    for line1, line2 in zip(f1, f2):
			        if line1.strip() == line2.strip():
			        	continue
			        validate_flag_create = False
			        logging.info("create_expected_line is: %s"% line1)
			        logging.info("create_generated_line is: %s"% line2)
			        break
			    if validate_flag_create == False:
			    	logging.debug("Below Are The Details OF Delta OF Expected & Generated Create Configs")
			    	get_delta_from_expected_and_generated_configs.get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)

			    if validate_flag_create == True:
			    	validate_create_flag = True
	
			    assert (validate_flag_create == True), "CREATE VALIDATION FAILED: Expected & Generated Configs Not Matched!! for : "+testcase
			    logging.debug("CREATE VALIDATION SUCCESS: Expected & Generated Configs Exactly Matched!! for : "+testcase)
		else:
			logging.debug("in else block-create")
			logging.debug("CREATE VALIDATION FAILED: Expected & Generated Configs Not Matched!! for : "+testcase)
			logging.debug("Below Are The Details OF Delta OF Expected & Generated Create Configs")
			#with open(expected_config_file) as f1, open(generated_config_file) as f2:
			get_delta_from_expected_and_generated_configs.get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
	elif delete == True:
		
		expected_config_file_exists = os.path.isfile(expected_config_file)
		if expected_config_file_exists:
			logging.debug("delete expected config file exists")
		else:
			with open(expected_config_file, "w") as expected_config_file_obj, open(generated_config_file) as generated_config_file_obj:
				for line in generated_config_file_obj:
					expected_config_file_obj.write(line)
		expected_file_lines = file_len(expected_config_file)
		generated_file_lines = file_len(generated_config_file)
	
		logging.debug("delete_expected_file_lines is:%s"% expected_file_lines)
		logging.debug("delete_generated_file_lines is:%s"% generated_file_lines)
		
		
		if expected_file_lines == generated_file_lines:
			logging.debug("in if block-delete")
			validate_flag_delete = True
			with open(expected_config_file) as f1, open(generated_config_file) as f2:
			    
			    for line1, line2 in zip(f1, f2):
			        if line1.strip() == line2.strip():
			        	continue
			        validate_flag_delete = False
			        logging.info("delete_expected_line is: %s"% line1)
			        logging.info("delete_generated_line is: %s"% line2)
			        break
			    if validate_flag_delete == False:
			    	logging.debug("Below Are The Details OF Delta OF Expected & Generated Delete Configs")
			    	get_delta_from_expected_and_generated_configs.get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
	

			    assert (validate_flag_delete == True), "DELETE VALIDATION FAILED: Expected & Generated Configs Not Matched!! for : "+testcase
			    
			    if validate_flag_delete == True:
			    	validate_delete_flag = True
			    logging.debug("DELETE VALIDATION SUCCESS: Expected & Generated Configs Exactly Matched!! for : "+testcase)
		else:
			logging.debug("in else block-delete")
			logging.debug("DELETE VALIDATION FAILED: Expected & Generated Configs Not Matched!! for : "+testcase)
			logging.debug("Below Are The Details OF Delta OF Expected & Generated Delete Configs")
			#with open(expected_config_file) as f1, open(generated_config_file) as f2:
			get_delta_from_expected_and_generated_configs.get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
		
		
	if create == True:
		return validate_create_flag
	else:
		return validate_delete_flag  
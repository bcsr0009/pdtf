# coding: utf-8
import paramiko
import logging
import os

from coreutils.logdecorator import logwrap

@logwrap
def connect_to_device(username, password, device_ip, port):
	'''
	This method provides ssh_handler to interact with device
	'''
	ssh_client = None
	try:
		ssh_client=paramiko.SSHClient()
		logging.info("Device ssh_client %s"% ssh_client)
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		logging.info("Device username %s"% username)
		logging.info("Device password %s"% password)
		logging.info("Device device_ip %s"% device_ip)
		logging.info("device port %s"% port)
		ssh_client.connect(hostname=device_ip, username=username, password=password, port= port, allow_agent=False, look_for_keys=False)
	except Exception as e:
		logging.debug("Exception in SSH Connetion to Device is:%s"%e)
	return ssh_client


@logwrap
def connect_to_ncs(username, password, device_ip, port):
	'''
	This method provides ssh_handler to interact with device
	'''
	ssh_client = None
	try:
		ssh_client=paramiko.SSHClient()
		logging.info("NCS ssh_client %s"% ssh_client)
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		logging.info("NCS username %s"% username)
		logging.info("NCS password %s"% password)
		logging.info("NCS device_ip %s"% device_ip)
		logging.info("NCS port %s"% port)
		ssh_client.connect(hostname=device_ip, username=username, password=password, port= port, allow_agent=False, look_for_keys=False)
	except Exception as e:
		logging.debug("Exception in SSH Connetion to NCS is:%s"%e)
	return ssh_client
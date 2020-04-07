# coding: utf-8
import requests
import json
import paramiko
import time
import logging
import os
import difflib
import pdb

from coreutils.logdecorator import logwrap

@logwrap
def execute_command(ssh_connection_handler, cmd):
    '''
    This method provides execute_command option on device
    '''
    stdin,stdout,stderr=ssh_connection_handler.exec_command(cmd)
    return stdin,stdout,stderr

@logwrap
def build_show_config_from_stdout(stdout, file):
    '''
    This method redirects stdout from execute command of device to file
    '''
    with open(file, "w") as rcbsp:
        for line in stdout.readlines():
            rcbsp.write(line)

def get_running_config(ssh_connection_handler, config_file, cmd):
    execute_command_result = execute_command(ssh_connection_handler, cmd)
    build_show_config_from_stdout(execute_command_result[1], config_file)

@logwrap
def get_running_config_from_ncs_before_service_push(ssh_connection_handler, before_service_push_config_file, cmd):
    '''
    This method provides NCS running config before service create
    '''
    get_running_config(ssh_connection_handler, before_service_push_config_file, cmd)


@logwrap
def get_running_config_from_ncs_before_service_delete(ssh_connection_handler, before_service_delete_config_file, cmd):
    '''
    This method provides running config before service delete
    '''
    get_running_config(ssh_connection_handler, before_service_delete_config_file, cmd)

@logwrap
def get_running_config_from_device_before_service_push(ssh_connection_handler, before_service_push_config_file, cmd):
    '''
    This method provides running config before service create
    '''
    get_running_config(ssh_connection_handler, before_service_push_config_file, cmd)
    
@logwrap
def get_running_config_from_device_before_service_delete(ssh_connection_handler, before_service_delete_config_file, cmd):
    '''
    This method provides running config before service delete
    '''
    get_running_config(ssh_connection_handler, before_service_delete_config_file, cmd)

@logwrap
def get_running_config_from_device_after_service_push(ssh_connection_handler, after_service_push_config_file, cmd):
    '''
    This method provides running config after service create
    '''
    get_running_config(ssh_connection_handler, after_service_push_config_file, cmd)


@logwrap
def get_running_config_from_ncs_after_service_push(ssh_connection_handler, after_service_push_config_file, cmd):
    '''
    This method provides NCS running config after service create
    '''
    get_running_config(ssh_connection_handler, after_service_push_config_file, cmd)

@logwrap
def get_running_config_from_ncs_after_service_delete(ssh_connection_handler, after_service_delete_config_file, cmd):
    '''
    This method provides running config after service delete
    '''
    get_running_config(ssh_connection_handler, after_service_delete_config_file, cmd)

@logwrap
def get_running_config_from_device_after_service_delete(ssh_connection_handler, after_service_delete_config_file, cmd):
    '''
    This method provides running config after service delete
    '''
    get_running_config(ssh_connection_handler, after_service_delete_config_file, cmd)

@logwrap
def get_generated_config_from_service_create(before_service_push, after_service_push, generated_service_config):
    '''
    This method provides generated config out of (before and after running configs )
    '''

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

    with open(before_service_push, 'r') as before_service_push_file_obj, open(after_service_push, 'r') as after_service_push_file_obj:
        before_service_push_file_content = before_service_push_file_obj.readlines()
        after_service_push_file_content = after_service_push_file_obj.readlines()

    with open(generated_service_config, 'w') as generated_service_config_obj:
        for line in before_service_push_file_content:
            if line in after_service_push_file_content:
                continue
            generated_service_config_obj.write(line)

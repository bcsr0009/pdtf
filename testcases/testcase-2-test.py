

import logging
import sys
import os
import argparse
import paramiko
import re


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


from coreutils import fileutil
from coreutils import validateutil
from coreutils import connectutil
from coreutils.logdecorator import logwrap
from coreutils.httputil import post_call, patch_call, delete_call, get_call
from payloads import service_devices_mapping

payload_str = ""
payload_str = re.search("testcase-(\d+-.*)\.py",__file__).group(1)
payload_file =payload_str

testcase_file = ""
testcase_file = __file__.split(".")[0]
testcs_file=(testcase_file.split("/"))
length = len(testcs_file)
testcase_file=testcs_file[length-1]

devices_per_service_list = []
devices_per_service_list = service_devices_mapping.devices_per_service_mapping[payload_str]

parser = argparse.ArgumentParser()
parser.add_argument("-tcp", "--testcasecreatepayload", type=str, action="store", dest="createpayload", default="payloads/"+payload_file+".json", help="provide create payload")
parser.add_argument("-setuptcp", "--setuppayload", type=str, action="store", dest="setuppayload", default="setuppayloads/"+payload_file+".json", help="provide create setuppayloads")

results = parser.parse_args()
createpayload= results.createpayload
setuppayload = results.setuppayload

#Variable Defined

device_generated_config_createflow_file_path = "generatedconfigs/deviceconfigs/"+testcase_file+"-device-generated-create-config.txt"
device_expected_create_config = "expectedconfigs/deviceconfigs/"+testcase_file+"-device-expected-create-config.txt"
ncs_generated_create_config_file = "generatedconfigs/ncsconfigs/"+testcase_file+"-ncs-generated-create-config.txt"
ncs_expected_create_config_file = "expectedconfigs/ncsconfigs/"+testcase_file+"-ncs-expected-create-config.txt"
device_generated_delete_config_file_path = "generatedconfigs/deviceconfigs/"+testcase_file+"-device-generated-delete-config.txt"
device_expected_delete_config_file_path = "expectedconfigs/deviceconfigs/"+testcase_file+"-device-expected-delete-config.txt"
ncs_generated_delete_config_file_path = "generatedconfigs/ncsconfigs/"+testcase_file+"-ncs-generated-delete-config.txt"
ncs_expected_delete_config_file_path = "expectedconfigs/ncsconfigs/"+testcase_file+"-ncs-expected-delete-config.txt"

logging.basicConfig(filename="logs/"+testcase_file+".log",
format='%(asctime)s %(message)s',
filemode='w', level=logging.DEBUG)

@logwrap
def get_device_info(device_obj):
    islsa = device_obj.get('islsa', False)
    if islsa:
        rfs_username = device_obj["rfsusername"]
        rfs_password = device_obj["rfspassword"]
        rfs_ip = device_obj["rfsipaddress"]
        rfs_port = device_obj["rfssshport"]
        cfs_username = device_obj["cfsusername"]
        cfs_password = device_obj["cfspassword"]
        cfs_ip = device_obj["cfsipaddress"]
        cfs_port = device_obj["cfssshport"]
    else:
        # IMP: Here for Non-LSA  the RFS and CFS credential are common as NCS setup
        rfs_username = device_obj["nsousername"]
        rfs_password = device_obj["nsopassword"]
        rfs_ip = device_obj["nsoipaddress"]
        rfs_port = device_obj["nsosshport"]
        cfs_username = device_obj["nsousername"]
        cfs_password = device_obj["nsopassword"]
        cfs_ip = device_obj["nsoipaddress"]
        cfs_port = device_obj["nsosshport"]

    deviceusername = device_obj["deviceusername"]
    devicepassword = device_obj["devicepassword"]
    createurl = device_obj["createurl"]
    deleteurl = device_obj["deleteurl"]
    action = device_obj["requestmethod"]
    devicename = device_obj["devicename"]
    ncs_running_config_cmd = device_obj["ncs_running_config_cmd"]
    device_address_cmd = device_obj["device_address_cmd"]
    device_port_cmd = device_obj["device_port_cmd"]
    device_running_config_cmd = device_obj["device_running_config_cmd"]
    setupflag = device_obj["issetup"]
    setupcreateurl = device_obj["setupcreateurl"]
    setupdeleteurl = device_obj["setupdeleteurl"]
    setupaction = device_obj["setuprequestmethod"]
    return deviceusername, devicepassword, createurl, deleteurl, action, rfs_username, rfs_password, rfs_ip, rfs_port, devicename, cfs_username, cfs_password, cfs_ip, cfs_port, ncs_running_config_cmd, device_address_cmd, device_port_cmd, device_running_config_cmd, setupflag, setupcreateurl, setupdeleteurl, setupaction

@logwrap
def setup(devices_per_service_list):
    #Psuedocode for Checking the Device exist on NSO and Network
    device_ip_port = {}
    setup_flag = True
    for device_obj in devices_per_service_list:
        deviceip = deviceport = None
        device_info_result = get_device_info(device_obj)
        device_ip_port[device_info_result[9]] = {}
        ncs_ssh_handler = connectutil.connect_to_ncs(device_info_result[5], device_info_result[6], device_info_result[7], device_info_result[8])

        if ncs_ssh_handler:
            temp_device_port = fileutil.execute_command(ncs_ssh_handler, device_info_result[16].format(device_info_result[9]))
            for line in temp_device_port[1].readlines():
                if 'port' in line.lower():
                    deviceport  = line[6:-2]
                    device_ip_port[device_info_result[9]]['deviceport'] = str(deviceport)
                    break
            temp_device_address = fileutil.execute_command(ncs_ssh_handler, device_info_result[15].format(device_info_result[9]))
            for line in temp_device_address[1].readlines():
                if 'address' in line.lower():
                    deviceip  = line[9:-2]
                    device_ip_port[device_info_result[9]]['deviceip'] = str(deviceip)
                    break
        else:
            logging.debug("Issue with NCS connect")
            return None
        if device_info_result[18] == True and setup_flag == True:
            setup_flag = False
            if device_info_result[21].lower() == "post":
                logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                logging.debug("Setup-Post: Setup payload the Service Configuration")
                logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                result_flag = post_call(device_info_result[10], device_info_result[11], device_info_result[19], setuppayload)
            elif device_info_result[21].lower() == "patch":
                logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                logging.debug("Setup-Patch: Setup pay loadthe Service Configuration")
                logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                result_flag = patch_call(device_info_result[10], device_info_result[11], device_info_result[19], setuppayload)
            else:
                logging.debug("Please use request method as 'POST' or 'PATCH' in Service Mapping File for initial setup")
                return None
            if result_flag == False:
                return None

        # if deviceip == None and device_ip_port != {}:
        #     return None
        # response = os.system("ping -c 1 " + deviceip)
        # if response != 0:
        #     return None
    return device_ip_port


@logwrap
def teardown(devices_per_service_list):
    setup_flag = True
    for device_obj in devices_per_service_list:
        device_info_result = get_device_info(device_obj)
        if device_info_result[18] == True and setup_flag == True:
            setup_flag = False
            logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            logging.debug("Setup-Delete: Deleting the Setup Payload Pre Configuration")
            logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            result_flag = delete_call(device_info_result[10], device_info_result[11], device_info_result[20])

@logwrap
def create(devices_per_service_list, createpayload, device_ip_port_details):

   # This method provide create flow of service and its validation 

    # #Psuedocode for Create Flow
    # Step 1: Get the running config of device and ncs before service push.

    #Iterating over devices_per_service_list
    for device_obj in devices_per_service_list:
        device_info_result = get_device_info(device_obj)

        device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
        device_port = device_ip_port_details[device_info_result[9]]['deviceport']

        create_flow_before_file_path = "tempconfigs/"+testcase_file+"-device-running-config-before-createflow-"+device_ip+"-and-"+str(device_port)+".txt"
        ncs_create_flow_before_file_path = "tempconfigs/"+testcase_file+"-ncs-running-config-before-createflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"
        createurl = device_info_result[2]
        result_flag = True
        # #1) Login to Device
        ssh_handler = connectutil.connect_to_device(device_info_result[0], device_info_result[1], device_ip, device_port)
        # #2) Get Running Config Before Service Push
        if ssh_handler:
            logging.debug("####################################################################")
            logging.debug("DEVICE-CREATE-CALL-BEFORE: Get Running Config on Device Name:{} with Ip-address:{} and port as:{} Before Create Service".format(device_info_result[9], device_ip, device_port))
            logging.debug("####################################################################")
            fileutil.get_running_config_from_device_before_service_push(ssh_handler, create_flow_before_file_path, device_info_result[17])
        else:
            result_flag = False
            return result_flag

        result_flag = True
        # 1) Login to NCS
        ncs_ssh_handler = connectutil.connect_to_ncs(device_info_result[5], device_info_result[6], device_info_result[7], device_info_result[8])
        # 2) Get NCS Running Config Before Service Push
        if ncs_ssh_handler:
            logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logging.debug("NCS-CREATE-CALL-BEFORE: Get Running Config on NCS for Device Name:{} with Ip-address:{} and port as:{} Before Create Service".format(device_info_result[9], device_ip, device_port))
            logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            fileutil.get_running_config_from_ncs_before_service_push(ncs_ssh_handler, ncs_create_flow_before_file_path, device_info_result[14].format(device_info_result[9]))
        else:
            result_flag = False
            return result_flag

    # Step 2: Push Service.
    if device_info_result[4].lower() == "post":
        logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        logging.debug("NCS-POST: Pushing the Service Configuration")
        logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        result_flag = post_call(device_info_result[10], device_info_result[11], createurl, createpayload)
    elif device_info_result[4].lower() == "patch":
        logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        logging.debug("NCS-PATCH: Pushing the Service Configuration")
        logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        result_flag = patch_call(device_info_result[10], device_info_result[11], createurl, createpayload)
    else:
        logging.debug("Please use request method as 'POST' or 'PATCH' in Service devices mapping file")
        return False
    if result_flag == False:
        return result_flag

    # Step 3: Get the running config of device and ncs after service push.

    #Iterating over devices_per_service_list
    for device_obj in devices_per_service_list:
        device_info_result = get_device_info(device_obj)
        device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
        device_port = device_ip_port_details[device_info_result[9]]['deviceport']

        create_flow_after_file_path = "tempconfigs/"+testcase_file+"-device-running-config-after-createflow-"+device_ip+"-and-"+str(device_port)+".txt"
        ncs_create_flow_after_file_path = "tempconfigs/"+testcase_file+"-ncs-running-config-after-createflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"

        # Get Running Config After Service Push
        logging.debug("#################################################################")
        logging.debug("DEVICE-CREATE-CALL-AFTER: Get Running Config on Device Name:{} with Ip-address:{} and port as:{} After Create Service".format(device_info_result[9], device_ip, device_port))
        logging.debug("#################################################################")
        fileutil.get_running_config_from_device_after_service_push(ssh_handler, create_flow_after_file_path, device_info_result[17])

        # Get the NCS running config after service push
        logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        logging.debug("NCS-CREATE-CALL-AFTER: Get Running Config on NCS for Device Name:{} with Ip-address:{} and port as:{} After Create Service".format(device_info_result[9], device_ip, device_port))
        logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        fileutil.get_running_config_from_ncs_after_service_push(ncs_ssh_handler, ncs_create_flow_after_file_path, device_info_result[14].format(device_info_result[9]))

    # Step 4: Get Service Push Config from Before & After Running Configs-->GeneratedConfig
    #Iterating over devices_per_service_list
    for device_obj in devices_per_service_list:
        device_info_result = get_device_info(device_obj)
        device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
        device_port = device_ip_port_details[device_info_result[9]]['deviceport']

        create_flow_before_file_path = "tempconfigs/"+testcase_file+"-device-running-config-before-createflow-"+device_ip+"-and-"+str(device_port)+".txt"
        create_flow_after_file_path = "tempconfigs/"+testcase_file+"-device-running-config-after-createflow-"+device_ip+"-and-"+str(device_port)+".txt"
        device_temp_generated_config_createflow_file_path = "tempconfigs/"+testcase_file+"-device-generated-config-createflow-"+device_ip+"-and-"+str(device_port)+".txt"
        ncs_create_flow_before_file_path = "tempconfigs/"+testcase_file+"-ncs-running-config-before-createflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"
        ncs_create_flow_after_file_path = "tempconfigs/"+testcase_file+"-ncs-running-config-after-createflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"
        ncs_temp_generated_config_createflow_file = "tempconfigs/"+testcase_file+"-ncs-generated-config-createflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"

        create_flow_before_config_exists = os.path.isfile(create_flow_before_file_path)
        create_flow_after_config_exists = os.path.isfile(create_flow_after_file_path)

        if create_flow_before_config_exists and create_flow_after_config_exists:
            logging.debug("#################################################################")
            logging.debug("GENERATE-CREATE-DEVICE-FILE: Generating the Create Config From Before & After Running Configs For Device Name:{} with Ip-address:{} and port as:{}".format(device_info_result[9], device_ip, device_port))
            logging.debug("#################################################################")
            fileutil.get_generated_config_from_service_create(create_flow_before_file_path, create_flow_after_file_path, device_temp_generated_config_createflow_file_path)
            validateutil.get_unified_diff_on_device_from_expected_and_generated_configs(create_flow_before_file_path, create_flow_after_file_path)
        else:
            logging.debug("temp files before and after service push configs not created")
            return False

        ncs_create_flow_before_config_exists = os.path.isfile(ncs_create_flow_before_file_path)
        ncs_create_flow_after_config_exists = os.path.isfile(ncs_create_flow_after_file_path)

        if ncs_create_flow_before_config_exists and ncs_create_flow_after_config_exists:
            logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logging.debug("GENERATE-CREATE-NCS-FILE: Generating the Create Config From Before & After Running Configs - NCS For Device Name:{} with Ip-address:{} and port as:{}".format(device_info_result[9], device_ip, device_port))
            logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            fileutil.get_generated_config_from_service_create(ncs_create_flow_before_file_path, ncs_create_flow_after_file_path, ncs_temp_generated_config_createflow_file)
            validateutil.get_unified_diff_on_ncs_from_expected_and_generated_configs(ncs_create_flow_before_file_path, ncs_create_flow_after_file_path)
        else:
            logging.debug("NCS temp files before and after service push configs not created")
            return False

    logging.debug("#################################################################")
    logging.debug("FINAL-GENERATE-CREATE-DEVICE-FILE: Aggregate All Device Create Generated Configs for Each Device into Single Generated File")
    logging.debug("#################################################################")
    # Step 5: Aggregate All Generated Configs for Each Device into Single Generated File
    with open(device_generated_config_createflow_file_path, "w+") as genconfigobj:
        for device_obj in devices_per_service_list:
            device_info_result = get_device_info(device_obj)
            device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
            device_port = device_ip_port_details[device_info_result[9]]['deviceport']

            device_temp_generated_config_createflow_file_path = "tempconfigs/"+testcase_file+"-device-generated-config-createflow-"+device_ip+"-and-"+str(device_port)+".txt"
            create_flow_generated_config_exists = os.path.isfile(device_temp_generated_config_createflow_file_path)
            if create_flow_generated_config_exists:
                with open(device_temp_generated_config_createflow_file_path, "r") as tempgenconfobj:
                    genconfigobj.write("Device : "+str(device_ip)+":"+str(device_port)+"\n")
                    genconfigobj.write("############################################\n\n")
                    for line in tempgenconfobj.readlines():
                        genconfigobj.write(line)

    logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    logging.debug("FINAL-GENERATE-CREATE-NCS-FILE: Aggregate All NCS Create Generated Configs for Each NCS into Single Generated File")
    logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    # Aggregate All NCS Generated Configs for Each NCS into Single Generated File
    with open(ncs_generated_create_config_file, "w+") as genconfigobj:
        for device_obj in devices_per_service_list:
            device_info_result = get_device_info(device_obj)
            device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
            device_port = device_ip_port_details[device_info_result[9]]['deviceport']

            ncs_temp_generated_config_createflow_file = "tempconfigs/"+testcase_file+"-ncs-generated-config-createflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"

            create_flow_generated_config_exists = os.path.isfile(ncs_temp_generated_config_createflow_file)
            if create_flow_generated_config_exists:
                with open(ncs_temp_generated_config_createflow_file, "r") as tempgenconfobj:
                    genconfigobj.write("Device : "+str(device_info_result[7])+":"+str(device_info_result[8])+"\n")
                    genconfigobj.write("############################################\n\n")
                    for line in tempgenconfobj.readlines():
                        genconfigobj.write(line)

    # Step 6: Validate Device and NCS Create Generated Config against Expected Config

    ncs_create_config_validate_result = device_create_config_validate_result = False
    # Validate Device Generated Config against Expected Config
    logging.debug("#################################################################")
    logging.debug("VALIDATE-CREATE-DEVICE: Validating Create Device Generated Config Against Expected Config For Device")
    logging.debug("#################################################################")
    try:
        device_create_config_validate_result = validateutil.validate_create_config_on_device(device_expected_create_config, device_generated_config_createflow_file_path, testcase_file)
    except Exception as ex:
        logging.debug("Exception in Device create config validation !!!%s"%ex)

    # Validate NCS Generated Config against Expected Config
    logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    logging.debug("VALIDATE-CREATE-NCS: Validating Create NCS Generated Config Against Expected Config for NCS")
    logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    try:
        ncs_create_config_validate_result = validateutil.validate_create_config_on_ncs(ncs_expected_create_config_file, ncs_generated_create_config_file, testcase_file)
    except Exception as ex:
        logging.debug("Exception in NCS create config validation !!!%s"%ex)

    if device_create_config_validate_result and ncs_create_config_validate_result:
        return True
    elif ncs_create_config_validate_result:
        logging.debug("Failed to validate the Device create configuration")
        return False
    elif device_create_config_validate_result:
        logging.debug("Failed to validate the NCS create configuration")
        return False
    else:
        logging.debug("Failed to validate both Device and NCS create configuration")
        return False

@logwrap
def delete(devices_per_service_list, device_ip_port_details):
    
    # This method provide delete flow of service and its validation
    # #Psuedocode for Delete Flow
    # Step 1: Get the running config of device and ncs before delete service.
    #Iterating over devices_per_service_list
    for device_obj in devices_per_service_list:
        device_info_result = get_device_info(device_obj)
        device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
        device_port = device_ip_port_details[device_info_result[9]]['deviceport']

        delete_flow_before_file_path = "tempconfigs/"+testcase_file+"-device-running-config-before-deleteflow-"+device_ip+"-and-"+str(device_port)+".txt"
        ncs_delete_flow_before_file_path = "tempconfigs/"+testcase_file+"-ncs-running-config-before-deleteflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"
        deleteurl = device_info_result[3]
        # #1) Login to Device
        ssh_handler = connectutil.connect_to_device(device_info_result[0], device_info_result[1], device_ip, device_port)
        # #2) Get Running Config Before Service delete
        if ssh_handler:
            logging.debug("####################################################################")
            logging.debug("DEVICE-DELETE-CALL-BEFORE: Get Running Config on Device Name:{} with Ip-address:{} and port as:{} Before Delete Service".format(device_info_result[9], device_ip, device_port))
            logging.debug("####################################################################")
            fileutil.get_running_config_from_device_before_service_push(ssh_handler, delete_flow_before_file_path, device_info_result[17])
        else:
            return False

        # 1) Login to NCS
        ncs_ssh_handler = connectutil.connect_to_ncs(device_info_result[5], device_info_result[6], device_info_result[7], device_info_result[8])
        # 2) Get NCS Running Config Before Service delete
        if ncs_ssh_handler:
            logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logging.debug("NCS-DELETE-CALL-BEFORE: Get Running Config on NCS for Device Name:{} with Ip-address:{} and port as:{} Before Delete Service".format(device_info_result[9], device_ip, device_port))
            logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            fileutil.get_running_config_from_ncs_before_service_delete(ncs_ssh_handler, ncs_delete_flow_before_file_path, device_info_result[14].format(device_info_result[9]))
        else:
            return False


    # Step 2: Delete Service.
    logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    logging.debug("NCS-DELETE: Deleting the Service Configuration")
    logging.debug("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    result_flag = delete_call(device_info_result[10], device_info_result[11], deleteurl)
    if result_flag == False:
        return result_flag

    # Step 3: Get the running config of device and ncs after delete service.
    #Iterating over devices_per_service_list
    for device_obj in devices_per_service_list:
        device_info_result = get_device_info(device_obj)
        device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
        device_port = device_ip_port_details[device_info_result[9]]['deviceport']

        delete_flow_after_file_path = "tempconfigs/"+testcase_file+"-device-running-config-after-deleteflow-"+device_ip+"-and-"+str(device_port)+".txt"
        ncs_delete_flow_after_file_path = "tempconfigs/"+testcase_file+"-ncs-running-config-after-deleteflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"

        # Get Running Config After delete Service
        logging.debug("#################################################################")
        logging.debug("DEVICE-DELETE-CALL-AFTER: Get Running Config on Device Name:{} with Ip-address:{} and port as:{} After Delete Service".format(device_info_result[9], device_ip, device_port))
        logging.debug("#################################################################")
        fileutil.get_running_config_from_device_after_service_delete(ssh_handler, delete_flow_after_file_path, device_info_result[17])

        # Get the NCS running config after service push
        logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        logging.debug("NCS-DELETE-CALL-AFTER: Get Running Config on NCS for Device Name:{} with Ip-address:{} and port as:{} After Delete Service".format(device_info_result[9], device_ip, device_port))
        logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        fileutil.get_running_config_from_ncs_after_service_delete(ncs_ssh_handler, ncs_delete_flow_after_file_path, device_info_result[14].format(device_info_result[9]))

    # Step 4: Get Delete Service Config from Before & After Running Configs-->GeneratedConfig
    #Iterating over devices_per_service_list
    for device_obj in devices_per_service_list:
        device_info_result = get_device_info(device_obj)
        device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
        device_port = device_ip_port_details[device_info_result[9]]['deviceport']

        delete_flow_before_file_path = "tempconfigs/"+testcase_file+"-device-running-config-before-deleteflow-"+device_ip+"-and-"+str(device_port)+".txt"
        delete_flow_after_file_path = "tempconfigs/"+testcase_file+"-device-running-config-after-deleteflow-"+device_ip+"-and-"+str(device_port)+".txt"
        device_temp_generated_config_deleteflow_file_path = "tempconfigs/"+testcase_file+"-device-generated-config-deleteflow-"+device_ip+"-and-"+str(device_port)+".txt"
        ncs_delete_flow_before_file_path = "tempconfigs/"+testcase_file+"-ncs-running-config-before-deleteflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"
        ncs_delete_flow_after_file_path = "tempconfigs/"+testcase_file+"-ncs-running-config-after-deleteflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"
        ncs_temp_generated_config_deleteflow_file_path = "tempconfigs/"+testcase_file+"-ncs-generated-config-deleteflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"

        delete_flow_before_config_exists = os.path.isfile(delete_flow_before_file_path)
        delete_flow_after_config_exists = os.path.isfile(delete_flow_after_file_path)

        if delete_flow_before_config_exists and delete_flow_after_config_exists:
            logging.debug("#################################################################")
            logging.debug("GENERATE-DELETE-DEVICE-FILE: Generating the Delete Config From Before & After Running Configs For Device Name:{} with Ip-address:{} and port as:{}".format(device_info_result[9], device_ip, device_port))
            logging.debug("#################################################################")
            fileutil.get_generated_config_from_service_delete(delete_flow_before_file_path, delete_flow_after_file_path, device_temp_generated_config_deleteflow_file_path)
            validateutil.get_unified_diff_on_device_from_expected_and_generated_configs(delete_flow_before_file_path, delete_flow_after_file_path)
        else:
            logging.debug("temp files before and after delete service configs not created")
            return False

        # Get Delete Service NCS Config from Before & After Running Configs-->GeneratedConfig
        ncs_delete_flow_before_config_exists = os.path.isfile(ncs_delete_flow_before_file_path)
        ncs_delete_flow_after_config_exists = os.path.isfile(ncs_delete_flow_after_file_path)

        if ncs_delete_flow_before_config_exists and ncs_delete_flow_after_config_exists:
            logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            logging.debug("GENERATE-DELETE-NCS-FILE: Generating the Delete Config From Before & After Running Configs - NCS For Device Name:{} with Ip-address:{} and port as:{}".format(device_info_result[9], device_ip, device_port))
            logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            fileutil.get_generated_config_from_service_delete(ncs_delete_flow_before_file_path, ncs_delete_flow_after_file_path, ncs_temp_generated_config_deleteflow_file_path)
            validateutil.get_unified_diff_on_ncs_from_expected_and_generated_configs(ncs_delete_flow_before_file_path, ncs_delete_flow_after_file_path)
        else:
            logging.debug("NCS temp files before and after delete service configs not created")
            return False

    logging.debug("#################################################################")
    logging.debug("FINAL-GENERATE-DELETE-DEVICE-FILE: Aggregate All Device Delete Generated Configs for Each Device into Single Generated File")
    logging.debug("#################################################################")
    # Step 5: Aggregate All Delete Generated Configs for Each Device into Single Generated File
    with open(device_generated_delete_config_file_path, "w+") as genconfigobj:
        for device_obj in devices_per_service_list:
            device_info_result = get_device_info(device_obj)
            device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
            device_port = device_ip_port_details[device_info_result[9]]['deviceport']

            device_temp_generated_config_deleteflow_file_path = "tempconfigs/"+testcase_file+"-device-generated-config-deleteflow-"+device_ip+"-and-"+str(device_port)+".txt"
            delete_flow_generated_config_exists = os.path.isfile(device_temp_generated_config_deleteflow_file_path)
            if delete_flow_generated_config_exists:
                with open(device_temp_generated_config_deleteflow_file_path, "r") as tempgenconfobj:
                    genconfigobj.write("Device : "+str(device_ip)+":"+str(device_port)+"\n")
                    genconfigobj.write("############################################\n\n")
                    for line in tempgenconfobj.readlines():
                        genconfigobj.write(line)

    logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    logging.debug("FINAL-GENERATE-DELETE-NCS-FILE: Aggregate All NCS Delete Generated Configs for Each NCS into Single Generated File")
    logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    # Aggregate All NCS Delete Generated Configs for Each Device into Single Generated File
    with open(ncs_generated_delete_config_file_path, "w+") as ncs_genconfigobj:
        for device_obj in devices_per_service_list:
            device_info_result = get_device_info(device_obj)
            device_ip = device_ip_port_details[device_info_result[9]]['deviceip']
            device_port = device_ip_port_details[device_info_result[9]]['deviceport']

            ncs_temp_generated_config_deleteflow_file_path = "tempconfigs/"+testcase_file+"-ncs-generated-config-deleteflow-"+device_info_result[9]+"-and-"+device_info_result[7]+"-and-"+str(device_info_result[8])+".txt"
            delete_flow_generated_config_exists = os.path.isfile(ncs_temp_generated_config_deleteflow_file_path)
            if delete_flow_generated_config_exists:
                with open(ncs_temp_generated_config_deleteflow_file_path, "r") as tempgenconfobj:
                    ncs_genconfigobj.write("Device : "+str(device_info_result[7])+":"+str(device_info_result[8])+"\n")
                    ncs_genconfigobj.write("############################################\n\n")
                    for line in tempgenconfobj.readlines():
                        ncs_genconfigobj.write(line)

    # Step 6: Validate Device and NCS Delete Generated Config against Expected Config
    ncs_delete_config_validate_result = device_delete_config_validate_result = False
    logging.debug("#################################################################")
    logging.debug("VALIDATE-DELETE-DEVICE: Validating Device Delete Generated Config Against Expected Config For Device")
    logging.debug("#################################################################")
    try:
        device_delete_config_validate_result = validateutil.validate_delete_config_on_device(device_expected_delete_config_file_path, device_generated_delete_config_file_path, testcase_file)
    except Exception as ex:
        logging.debug("Exception in Device delete config validation !!!%s"%ex)

    logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    logging.debug("VALIDATE-DELETE-NCS: Validating NCS Delete Generated Config Against Expected Config For NCS")
    logging.debug("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    try:
        ncs_delete_config_validate_result = validateutil.validate_delete_config_on_ncs(ncs_expected_delete_config_file_path, ncs_generated_delete_config_file_path, testcase_file)
    except Exception as ex:
        logging.debug("Exception in Device delete config validation !!!%s"%ex)

    if device_delete_config_validate_result and ncs_delete_config_validate_result:
        return True
    elif ncs_delete_config_validate_result:
        logging.debug("Failed to validate the Device delete configuration")
        return False
    elif device_delete_config_result:
        logging.debug("Failed to validate the NCS delete configuration")
        return False
    else:
        logging.debug("Failed to validate both Device and NCS delete configuration")
        return False


create_result = False
delete_result = False
try:
    device_ip_port_details = setup(devices_per_service_list)
    if device_ip_port_details == None or device_ip_port_details == {}:
        logging.debug("Issuse with Pre-Setup")
    else:
        try:
            create_result = create(devices_per_service_list, createpayload, device_ip_port_details)
        except Exception as e:
            logging.debug("CREATE-FLOW-EXCEPTION: Raised !!!%s"%e)
        try:
            delete_result = delete(devices_per_service_list, device_ip_port_details)
        except Exception as e:
            logging.debug("DELETE-FLOW-EXCEPTION: Raised !!!%s"%e)

        if create_result == True and delete_result == True:
            logging.debug("TESTCASE:PASSED for :"+testcase_file)
            print("TESTCASE:PASSED for :"+testcase_file)
        elif create_result == True and delete_result == False:
            logging.debug("TESTCASE:FAILED at Delete Flow for :"+testcase_file+" Please Check the Logs for Details")
            print("TESTCASE:FAILED at Delete Flow for :"+testcase_file+" Please Check the Logs for Details")
        elif create_result == False and delete_result == True:
            logging.debug("TESTCASE:FAILED at Create Flow for :"+testcase_file+" Please Check the Logs for Details")
            print("TESTCASE:FAILED at Create Flow for :"+testcase_file+" Please Check the Logs for Details")
        else:
            logging.debug("TESTCASE:FAILED at both Create & Delete Flows for :"+testcase_file+" Please Check the Logs for Details")
            print("TESTCASE:FAILED at both Create & Delete Flows for :"+testcase_file+" Please Check the Logs for Details")

except Exception as ex:
    logging.debug("SETUP-FLOW-EXCEPTION: Raised !!!%s"%ex)
finally:
    teardown(devices_per_service_list)


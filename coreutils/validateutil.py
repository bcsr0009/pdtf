# coding: utf-8
import requests
import json
import time
import logging
import os
import difflib
import pdb

from coreutils.logdecorator import logwrap

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
def get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file):
    # Open file for reading in text mode (default mode)
    expected_config = open(expected_config_file)
    generated_config = open(generated_config_file)


    logging.debug("-----------------------------------")
    logging.debug("Comparing files ")
    logging.debug(" > " + expected_config_file)
    logging.debug(" < " +generated_config_file)
    logging.debug("-----------------------------------")

    # Read the first line from the files
    expected_config_line = expected_config.readline()
    generated_config_line = generated_config.readline()

    # Initialize counter for line number
    line_no = 1

    # Loop if either file1 or file2 has not reached EOF
    while expected_config_line != '' or generated_config_line != '':

        # Strip the leading whitespaces
        expected_config_line = expected_config_line.rstrip()
        generated_config_line = generated_config_line.rstrip()
        
        # Compare the lines from both file
        if expected_config_line != generated_config_line:
            
            # If a line does not exist on file2 then mark the output with + sign
            if generated_config_line == '' and expected_config_line != '':
                logging.debug(">+")
                logging.debug("Line-%s" % line_no)
                logging.debug(expected_config_line)
            # otherwise output the line on file1 and mark it with > sign
            elif expected_config_line != '':
                logging.debug(">")
                logging.debug("Line-%s" % line_no)
                logging.debug(expected_config_line)
                
            # If a line does not exist on file1 then mark the output with + sign
            if expected_config_line == '' and generated_config_line != '':
                logging.debug("<+")
                logging.debug("Line-%s" % line_no)
                logging.debug(generated_config_line)
            # otherwise output the line on file2 and mark it with < sign
            elif generated_config_line != '':
                logging.debug("<")
                logging.debug("Line-%s" % line_no)
                logging.debug(generated_config_line)

            # Print a blank line
            logging.debug("")

        #Read the next line from the file
        expected_config_line = expected_config.readline()
        generated_config_line = generated_config.readline()


        #Increment line counter
        line_no += 1

    # Close the files
    expected_config.close()
    generated_config.close()

@logwrap
def get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file):
    expected_text = open(expected_config_file).readlines()
    generated_text = open(generated_config_file).readlines()
    logging.debug("-----------------------------------")
    logging.debug("Comparing files")
    logging.debug(" Expected Config File Name:" + expected_config_file)
    logging.debug(" Generated Config File Name:" +generated_config_file)
    logging.debug("-----------------------------------")
    for diff in difflib.unified_diff(expected_text, generated_text):
        logging.debug(diff)

@logwrap
def get_unified_diff_on_device_from_expected_and_generated_configs(expected_config_file, generated_config_file):
    expected_text = open(expected_config_file).readlines()
    generated_text = open(generated_config_file).readlines()
    logging.debug("--------------------------------------------")
    logging.debug("Comparing before and after device config files")
    logging.debug("--------------------------------------------")
    for diff in difflib.unified_diff(expected_text, generated_text):
        logging.debug(diff)

@logwrap
def get_unified_diff_on_ncs_from_expected_and_generated_configs(expected_config_file, generated_config_file):
    expected_text = open(expected_config_file).readlines()
    generated_text = open(generated_config_file).readlines()
    logging.debug("-------------------------------------------")
    logging.debug("Comparing before and after ncs config files")
    logging.debug("-------------------------------------------")
    for diff in difflib.unified_diff(expected_text, generated_text):
        logging.debug(diff)

@logwrap
def validate_create_config_on_device(expected_config_file, generated_config_file, testcase):
    '''
    validates create device generated configs against expected configs
    '''
    validate_create_flag = False

    expected_config_file_exists = os.path.isfile(expected_config_file)
    if expected_config_file_exists:
        logging.debug("Device create expected config file exists")
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
                logging.debug("Below Are The Details OF Delta OF Expected & Generated Create Configs on Device")
                # get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
                get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file)

            if validate_flag_create == True:
                validate_create_flag = True

            assert (validate_flag_create == True), "CREATE VALIDATION FAILED ON DEVICE: Expected & Generated Configs Not Matched!! for : "+testcase
            logging.debug("***************************************************************************************************")
            logging.debug("CREATE VALIDATION SUCCESS ON DEVCIE: Expected & Generated Configs Exactly Matched!! for : "+testcase)
            logging.debug("***************************************************************************************************")
    else:
        logging.debug("in else block-create")
        logging.debug("**********************************************************************************************")
        logging.debug("CREATE VALIDATION FAILED ON DEVICE: Expected & Generated Configs Not Matched!! for : "+testcase)
        logging.debug("**********************************************************************************************")
        logging.debug("Below Are The Details OF Delta OF Expected & Generated Create Configs on Device")
        #with open(expected_config_file) as f1, open(generated_config_file) as f2:
        # get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
        get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file)
    return validate_create_flag


@logwrap
def validate_create_config_on_ncs(expected_config_file, generated_config_file, testcase):
    '''
    validates create device generated configs against expected configs
    '''
    validate_create_flag = False

    expected_config_file_exists = os.path.isfile(expected_config_file)
    if expected_config_file_exists:
        logging.debug("NCS create expected config file exists")
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
                logging.debug("Below Are The Details OF Delta OF Expected & Generated Create Configs on NCS")
                # get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
                get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file)

            if validate_flag_create == True:
                validate_create_flag = True

            assert (validate_flag_create == True), "CREATE VALIDATION FAILED ON NCS: Expected & Generated Configs Not Matched!! for : "+testcase
            logging.debug("************************************************************************************************")
            logging.debug("CREATE VALIDATION SUCCESS ON NCS: Expected & Generated Configs Exactly Matched!! for : "+testcase)
            logging.debug("************************************************************************************************")
    else:
        logging.debug("in else block-create")
        logging.debug("*******************************************************************************************")
        logging.debug("CREATE VALIDATION FAILED ON NCS: Expected & Generated Configs Not Matched!! for : "+testcase)
        logging.debug("*******************************************************************************************")
        logging.debug("Below Are The Details OF Delta OF Expected & Generated Create Configs on NCS")
        #with open(expected_config_file) as f1, open(generated_config_file) as f2:
        # get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
        get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file)
    return validate_create_flag

@logwrap
def validate_delete_config_on_device(expected_config_file, generated_config_file, testcase):
    '''
    validates delete device generated configs against expected configs
    '''
    validate_delete_flag = False
    expected_config_file_exists = os.path.isfile(expected_config_file)
    if expected_config_file_exists:
        logging.debug("Device delete expected config file exists")
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
                logging.debug("Below Are The Details OF Delta OF Expected & Generated Delete Configs on Device")
                # get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
                get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file)


            assert (validate_flag_delete == True), "DELETE VALIDATION FAILED ON DEVICE: Expected & Generated Configs Not Matched!! for : "+testcase

            if validate_flag_delete == True:
                validate_delete_flag = True
            logging.debug("***************************************************************************************************")
            logging.debug("DELETE VALIDATION SUCCESS ON DEVICE: Expected & Generated Configs Exactly Matched!! for : "+testcase)
            logging.debug("***************************************************************************************************")
    else:
        logging.debug("in else block-delete")
        logging.debug("**********************************************************************************************")
        logging.debug("DELETE VALIDATION FAILED ON DEVICE: Expected & Generated Configs Not Matched!! for : "+testcase)
        logging.debug("**********************************************************************************************")
        logging.debug("Below Are The Details OF Delta OF Expected & Generated Delete Configs on Device")
        # get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
        get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file)
    return validate_delete_flag

@logwrap
def validate_delete_config_on_ncs(expected_config_file, generated_config_file, testcase):
    '''
    validates delete device generated configs against expected configs
    '''
    validate_delete_flag = False
    expected_config_file_exists = os.path.isfile(expected_config_file)
    if expected_config_file_exists:
        logging.debug("NCS delete expected config file exists")
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
                logging.debug("Below Are The Details OF Delta OF Expected & Generated Delete Configs on NCS")
                # get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
                get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file)


            assert (validate_flag_delete == True), "DELETE VALIDATION FAILED ON NCS: Expected & Generated Configs Not Matched!! for : "+testcase

            if validate_flag_delete == True:
                validate_delete_flag = True
            logging.debug("************************************************************************************************")
            logging.debug("DELETE VALIDATION SUCCESS ON NCS: Expected & Generated Configs Exactly Matched!! for : "+testcase)
            logging.debug("************************************************************************************************")
    else:
        logging.debug("in else block-delete")
        logging.debug("*******************************************************************************************")
        logging.debug("DELETE VALIDATION FAILED ON NCS: Expected & Generated Configs Not Matched!! for : "+testcase)
        logging.debug("*******************************************************************************************")
        logging.debug("Below Are The Details OF Delta OF Expected & Generated Delete Configs on NCS")
        #with open(expected_config_file) as f1, open(generated_config_file) as f2:
        # get_delta_from_expected_and_generated_configs(expected_config_file, generated_config_file)
        get_unified_diff_from_expected_and_generated_configs(expected_config_file, generated_config_file)
    return validate_delete_flag

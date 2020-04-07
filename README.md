
## **pdtf(Payload Driven Test Framework)**


**Prerequisite:**

Please follow the below steps to install required packages:

1. Execution permission to installation.sh file, run the below command in terminal.

chmod 777 installation.sh

2. Install required packages using the command:

sudo ./installation.sh

**Setup:**

Please follow the below steps to do setup:

1. Copy required json payloads w.r.t use-case in "pdtf/payloads/" directory 
   
   **NOTE:**
   json payloads file names starts with priority number, so that dependencies will be taken care

2. Generate test-cases and robot file for given json payloads using below command
    
	    CBADDIGU-M-C119:pdtf cbaddigu$ pwd
		/Users/cbaddigu/Downloads/pdtf
		CBADDIGU-M-C119:pdtf cbaddigu$ python coreutils/testcasegeneratorutil.py

3. Modify input file w.r.t usecase

		CBADDIGU-M-C119:payloads cbaddigu$ pwd
		/Users/cbaddigu/Downloads/pdtf/payloads
		CBADDIGU-M-C119:payloads cbaddigu$ vim service_devices_mapping.py
	
   Below are the details needs to be filled in service_devices_mapping.py

		3.1 'request_method' specify the method type like 'POST' or 'PATCH'.
		3.2 'createurl' specify http url to create service configuration.
		3.3 'deleteurl' specify http url to delete service configuration.
		3.4 'deviceip' specify device ip-address.
		3.5 'devicepassword' specify device password.
		3.6 'deviceport' specify device port.
		3.7 'deviceusername' specify device user name.

**Usage:**

Execute robot file to run test-cases using below command

		CBADDIGU-M-C119:pdtf cbaddigu$ pwd
		/Users/cbaddigu/Downloads/pdtf
		CBADDIGU-M-C119:pdtf cbaddigu$ robot drivers/
		__init__.py                     unit_test_cases_driver.robot
		CBADDIGU-M-C119:pdtf cbaddigu$ robot drivers/unit_test_cases_driver.robot

**Report:**

To Review test-cases run report, below is the location for report files


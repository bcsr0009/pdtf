*** Settings ***
Documentation          test usecases
Library                Process

*** Test Cases ***


Validate testcase-1-test test-case
    ${testcase_1_test_result}=         Run Process  python testcases/testcase-1-test.py      shell=True
    Log                <a href="logs/testcase-1-test.log">testcase-1-test.log</a>                HTML
    Should Contain     ${testcase_1_test_result.stdout}      TESTCASE:PASSED for :testcase-1-test

Validate testcase-2-test test-case
    ${testcase_2_test_result}=         Run Process  python testcases/testcase-2-test.py      shell=True
    Log                <a href="logs/testcase-2-test.log">testcase-2-test.log</a>                HTML
    Should Contain     ${testcase_2_test_result.stdout}      TESTCASE:PASSED for :testcase-2-test

Validate testcase-3-test test-case
    ${testcase_3_test_result}=         Run Process  python testcases/testcase-3-test.py      shell=True
    Log                <a href="logs/testcase-3-test.log">testcase-3-test.log</a>                HTML
    Should Contain     ${testcase_3_test_result.stdout}      TESTCASE:PASSED for :testcase-3-test

Validate testcase-4-test test-case
    ${testcase_4_test_result}=         Run Process  python testcases/testcase-4-test.py      shell=True
    Log                <a href="logs/testcase-4-test.log">testcase-4-test.log</a>                HTML
    Should Contain     ${testcase_4_test_result.stdout}      TESTCASE:PASSED for :testcase-4-test

Validate testcase-5-test test-case
    ${testcase_5_test_result}=         Run Process  python testcases/testcase-5-test.py      shell=True
    Log                <a href="logs/testcase-5-test.log">testcase-5-test.log</a>                HTML
    Should Contain     ${testcase_5_test_result.stdout}      TESTCASE:PASSED for :testcase-5-test

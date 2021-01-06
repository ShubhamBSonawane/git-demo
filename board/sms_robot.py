#!/usr/bin/env python3

# import time
# from os import path
import threading
import sms_bas
import sms_pas
import sms_wes
import sms_gpio
import uniflash_auto
import config
import os

t1 = sms_bas.thread_with_trace(target=sms_bas.func)
t1.start()


# 1 code by using multi threading.(runs in parallel)
def sms_board_get_serial_data(port, baudrate, t_min, file_name):
    global t1
    t1 = sms_bas.thread_with_trace(target=sms_bas.get_serial_data,
                                   args=(str(port), int(baudrate), int(t_min), str(file_name)))
    t1.start()
    if t1.is_alive():
        print("\nRunning")
    else:
        print("\n")
        raise AssertionError("Fail")

# def sms_board_get_serial_data(port, baudrate, t_min):
#     global test_log_name
#     file_name = test_log_name
#     print("file_name: ", file_name)
#     global t1
#     t1 = sms_bas.thread_with_trace(target=sms_bas.get_serial_data,
#                                    args=(str(port), int(baudrate), int(t_min), str(file_name)))
#     t1.start()
#     if t1.is_alive():
#         print("\nRunning")
#     else:
#         print("\n")
#         raise AssertionError("Fail")


# 2
def sms_board_check_hibernate_count(file_name):
    count = sms_bas.get_hibernate_count(file_name)
    result = config.calculate_hibernate_count()
    if count <= result:
        print("\n")
        print("Correct hibernate count as expected: " + str(count))
    else:
        print("\n")
        print("Incorrect hibernate count: " + str(count))
        raise AssertionError("Fail")


# 3 changes in if loop by shubham on 25-09-2020.
def sms_board_check_periodic_interval(file_name, interval_minutes):
    incorrect_interval = False
    get_interval_list = sms_bas.get_wakeup_intervals(file_name)
    # print("intervals", get_interval_list)
    try:
        for intervals in get_interval_list:
            # print(intervals // int(interval_minutes))
            if intervals % int(interval_minutes) != 0:
                incorrect_interval = True
    except TypeError as e:
        print("Error in sms_board_check_periodic_interval,", e)
    finally:
        if not incorrect_interval:
            print("\n")
            print("Correct periodic interval")
        else:
            print("\n")
            print("Incorrect periodic interval", interval_minutes)
            raise AssertionError("Fail")


# 4
def sms_board_check_mqtt_msgs(file_name):
    res = sms_bas.check_mqtt_msgs(file_name)
    if res[0] & res[1] & res[2]:
        print("\n")
        print("MQTT messages was sent: " + str(res))
    else:
        print("\n")
        print("MQTT messages was not sent: " + str(res))
        raise AssertionError("Fail")


def sms_board_check_mqtt_msgs_not_send(file_name):
    res = sms_bas.check_mqtt_msgs(file_name)
    if res:
        print("\n")
        print("MQTT messages was sent: " + str(res))
        raise AssertionError("Fail")
    else:
        print("\n")
        print("MQTT messages was not sent: " + str(res))


# 5
def sms_board_check_hibernate_if_data_sent(file_name):
    hib, data_sent = sms_bas.check_hibernate_if_data_sent(file_name)
    if hib:
        print("\n")
        print("Device hibernated: " + str(hib))
    else:
        print("\n")
        print("Device hibernated: {0}, Data send to cloud: {1}".format(str(hib), str(data_sent)))
        raise AssertionError("Fail")


# 6
def sms_board_check_wake_from_hibernate_send_data(file_name):
    hib, data_sent = sms_bas.check_wake_from_hibernate_send_data(file_name)
    if data_sent:
        print("\n")
        print("Device data sent: " + str(data_sent))
    else:
        print("\n")
        print("Device data sent: {0}, Device data sent : {1}".format(str(data_sent), str(hib)))
        raise AssertionError("Fail")


# 7 use small case function name
def sms_board_check_OTA_interval(file_name, interval_minutes):
    incorrect_interval = False
    get_interval_list = sms_bas.check_OTA_interval(file_name)
    for intervals in get_interval_list:
        if intervals % int(interval_minutes) != 0:
            incorrect_interval = True
    if not incorrect_interval:
        print("\n")
        print("OTA interval is correct: " + str(intervals))
    else:
        print("\n")
        print("OTA interval is not correct: " + str(intervals))
        raise AssertionError("Fail")


# 8
def sms_board_check_OTA_upgrade(file_name, fw_version):
    correct_version = False
    get_fw_list = sms_bas.get_fw_version_upgrade_OTA(file_name)
    if fw_version in get_fw_list:
        correct_version = True
    if correct_version:
        print("\n")
        print("Device running on newer version: " + str(fw_version))
    else:
        print("\n")
        print("Device running on older version: " + str(fw_version))
        raise AssertionError("Fail")


# 9
def sms_board_same_ver_bin_OTA_run_with_old_bin(file_name, fw_version):
    old_version = False
    get_fw_list = sms_bas.get_fw_version_upgrade_OTA(file_name)
    if fw_version == get_fw_list[-1]:
        old_version = True
    if old_version:
        print("\n")
        print("Device running with the old version: " + str(fw_version))
    else:
        print("\n")
        print("Device not running with the previous version: " + str(get_fw_list[-1]))
        raise AssertionError("Fail")


# 10
def sms_board_check_device_reboot_if_file_read_error(file_name):
    res = sms_bas.check_device_reboot_if_file_read_error(file_name)
    if res:
        print("\n")
        print("Device file read error has not occurred : " + str(res))
    else:
        print("\n")
        print("Device file read error occurred & Rebooted Successfully")
        # raise AssertionError("Pass")


# 11
def sms_board_check_connection_to_SSID_dev_running(file_name, ssid_name):
    get_ssid = sms_bas.get_SSID_name_dev_running(file_name)
    ssid_name = ssid_name.strip()
    if ssid_name == get_ssid:
        print("\n")
        print("Device is connected to SSID: " + str(get_ssid))
    else:
        print("\n")
        print("Device is connected to SSID: " + str(get_ssid))
        raise AssertionError("Fail")


# 12
def sms_board_check_hibernate_if_not_provisioned(file_name):
    res = sms_bas.check_hibernate_if_not_provisioned(file_name)
    if res:
        print("\n")
        print("Device hibernated: " + str(res))
    else:
        print("\n")
        print("Device not hibernated: " + str(res))
        raise AssertionError("Fail")


# 14
def sms_board_prov_wifi_not_found_hibernate_mode(file_name):
    res = sms_bas.if_prov_wifi_not_exist_hibernate_mode(file_name)
    if res:
        print("\n")
        print("Provisioned wifi found: " + str(res))
    else:
        print("\n")
        print("Provisioned wifi not found: " + str(res))
        raise AssertionError("Fail")


# 15
def sms_board_create_ota_job(device, ota_file):
    job_id = sms_pas.create_ota_job(device, ota_file)
    if job_id:
        print("\n")
        print("OTA job is created: " + str(job_id))
    else:
        print("\n")
        print("OTA job is not created: " + str(job_id))
        raise AssertionError("Fail")


# 16
def sms_board_check_ota_bad_sign(file_name):
    bad_sign_status = sms_bas.check_ota_bad_sign(file_name)
    if bad_sign_status:
        print("\n")
        print("OTA version have a bad sign: " + str(bad_sign_status))
    else:
        print("\n")
        print("OTA version does not have a bad sign: " + str(bad_sign_status))
        raise AssertionError("Fail")


# 17
def sms_board_check_ota_same_version_rejected(file_name):
    same_version_status = sms_bas.check_ota_same_version(file_name)
    if same_version_status:
        print("\n")
        print("OTA version is same: " + str(same_version_status))
    else:
        print("\n")
        print("OTA version is different: " + str(same_version_status))
        raise AssertionError("Fail")


# 18
def sms_board_check_ota_downloaded(file_name):
    ota_download_status = sms_bas.check_ota_downloaded(file_name)
    if ota_download_status:
        print("\n")
        print("OTA downloaded: " + str(ota_download_status))
    else:
        print("\n")
        print("OTA not downloaded: " + str(ota_download_status))
        raise AssertionError("Fail")


# 19
def sms_board_check_security_alert(file_name, threshold_value):
    sec_alert = False
    threshold_values = sms_bas.get_security_alert(file_name)
    # print(threshold_values)
    th = ""
    for th in threshold_values:
        if th <= int(threshold_value):
            sec_alert = True
    if sec_alert:
        print("\n")
        print("Security threshold value not crossed: " + str(th))
    else:
        print("\n")
        print("Security threshold value crossed: " + str(th))
        raise AssertionError("Fail")


# 20
def sms_board_check_ota_lesser_version(file_name):
    lesser_version_status = sms_bas.check_ota_same_version(file_name)
    if lesser_version_status:
        print("\n")
        print("OTA running on previous firmware: " + str(lesser_version_status))
    else:
        print("\n")
        print("OTA upgraded: " + str(lesser_version_status))
        raise AssertionError("Fail")


# 21
def sms_board_set_network_params(iface, loss, delay, jitter, rate):
    status = sms_wes.set_network_params(iface, loss, delay, jitter, rate)
    if status == "executed":
        print("\n")
        print("Network status set: " + str(status))
    else:
        print("\n")
        print("WES API is not working: " + str(status))
        raise AssertionError("Fail")


# code to reset the network parameters
def sms_board_reset_network_params(iface):
    status = sms_wes.reset_network_params(iface)
    if status == "executed":
        print("\n")
        print("Network has been Reset")
    else:
        print("\n Unable to reset the Network")
        raise AssertionError("Fail")


# 22
def create_test_log_dir(dir_name):
    dir_created = sms_bas.create_test_suite_dir(dir_name)
    if dir_created:
        print("\n")
        print("Pass")
    else:
        print("\n")
        raise AssertionError("Fail")


# 23
def sms_board_set_power_supply(relay, state):
    status = sms_gpio.set_relay_state(relay, state)
    if status == "executed":
        print("\n")
        print("Relay status set for : " + relay + " as " + str(status))
    else:
        print("\n")
        print("GPIO API is not working: " + str(status))
        raise AssertionError("Fail")


# 24 edited by shubham. Didn't edited the name in start and stop test case.
def start_test_case(start_test_desc="SMS_test_start"):
    global t1
    resp = sms_bas.kill_thread(t1)
    if not resp:
        print("Thread killed")
    else:
        print("Thread not killed")
    if start_test_desc:
        print("\n")
        print(start_test_desc)
    else:
        print("\n")
        raise AssertionError("Fail")


# 25
def stop_test_case(stop_test_desc="SMS_test_stop"):
    if stop_test_desc:
        print("\n")
        print(stop_test_desc)
    else:
        print("\n")
        raise AssertionError("Fail")


# 26
def sms_board_start_wait_timer(wait_min):
    status = sms_bas.wait_countdown(wait_min)
    if status:
        print("\n")
        print("Wait timer over")
    else:
        print("\n")
        raise AssertionError("Time value is not correct")


# 27
def sms_board_flash_sms_device(device_name):
    status = uniflash_auto.uni_flash_device(device_name)
    if status:
        print("\n")
        print("Sli file created and flashed")
    else:
        print("\n")
        raise AssertionError("Not flashed")


# Edited by shubham. Start of code
# Function to check whether the WES services are running and WES server is online.
def sms_board_check_wes_services_are_online(res):
    response = sms_wes.ping_wes_server()
    if res == response:
        print("\n" + "WES Server Online")
    else:
        print("\n WES services are Offline. Please check IP address of RPi in config.py file")
        raise AssertionError("Fail")


# function to confirm whether the relay server is online on Raspberry pi.
def sms_board_check_relay_server_is_online(statuscode):
    response = sms_gpio.ping_relay_server()
    if str(response) == statuscode:
        print("\n Relay setup is working")
    else:
        print("\n Please check your wiring & Rpi relay setup")
        raise AssertionError("Fail")


# function to confirm the correct port sms board is specified in excel sheet
def sms_board_check_sms_com_port(port):
    response = sms_bas.get_serial_port(port)
    if response:
        print('SMS Board is Connected')
    else:
        print("Cannot find SMS board on " + port + ".Please check the COM port in xlsx file")
        raise AssertionError("Fail")


# code added by shubham on 25-09-2020.
def sms_board_check_reset(log_file):
    response = sms_bas.check_reset(log_file)
    if response:
        print("Reset Successful: ", str(response))
    else:
        print("Reset Successful: ", str(response))
        raise AssertionError("Fail")


# def sms_board_resetting_sms_board(relay):
#     res = sms_gpio.resetting_sms_board(relay)
#     if res:
#         print("Resetting Completed")
#     else:
#         print("Unable to reset the board")
#         raise AssertionError("Fail")


# Reset board using Uniflash Application, Author - Akshay Akbari.
def sms_board_resetting_sms_board():
    execute = os.system("%windir%\\..\\ti\\uniflash_6.1.0\\simplelink\\imagecreator\\bin\\xds110reset.exe")
    if execute == 0:
        print("Resetting Completed")
    else:
        print("Unable to reset the board")
        raise AssertionError("Fail")



# changes made by shubham for kalyani on 28-09-2020.
def sms_board_check_for_start_provisioning(dev_log):
    res = sms_bas.check_for_start_provisioning(dev_log)
    if res:
        print("Provisioning Started: ", str(res))
    else:
        print("Provisioning not Started: ", str(res))
        raise AssertionError("Fail")


# Changes made by akshay @ 29-09-202
def sms_board_check_for_completed_provisioning(dev_log):
    res = sms_bas.check_for_completed_provisioning(dev_log)
    if res:
        print("Provisioning Completed Successfully: ", str(res))
    else:
        print("Provisioning not completed Please check log file: ", str(res))
        raise AssertionError("Fail")


# function to check the time period of local provisioning.
# author - shubham. changes made on 12-10-2020.
def sms_board_check_time_interval_local_provisioning(file_name, interval_minutes):
    # correct_time_interval = False
    res = sms_bas.check_time_interval_of_local_provisioning(file_name)
    if str(res) == interval_minutes:
        print("\nCorrect time Interval of local Provisioning: ", res)
    else:
        print("\nIncorrect time interval of local Provisioning: ", res)
        raise AssertionError("Fail")


def sms_board_check_mqtt_publish_topic(file_name, device_id):
    device_id = device_id.strip()
    topic = "$aws/rules/acs_sms_carlsberg_nonprod_sms_data_rule/adi.ff2def/"
    topic = topic + device_id
    response = sms_bas.check_mqtt_publish_topic(file_name)
    if response == topic:
        print("\nMqtt Publish Topic :", response)
    else:
        print("\nIncorrect Mqtt Publish Topic : ", response)
        raise AssertionError("Fail")


def sms_board_check_device_registered(file_name, device_id):
    registration_string = "MQTT demo client identifier is " + device_id.strip() + " (length 9)."
    print(registration_string)
    response = sms_bas.check_device_registered(file_name)
    if response == registration_string:
        print("\nDevice Registered Successfully :", response)
    else:
        print("\nDevice Registered Unsuccessfully :", response)
        raise AssertionError("Fail")


def sms_board_check_device_started_in_ap(file_name):
    response = sms_bas.check_device_started_in_ap(file_name)
    if response:
        print("\nDevice Started in AP mode :", response)
    else:
        print("\nDevice Started in AP mode :", response)
        raise AssertionError("Fail")


def sms_board_check_device_shadow_update(log_file, device_id):
    shadow_updated, shadow_completed = sms_bas.check_device_shadow_update(log_file, device_id)
    if shadow_updated & shadow_completed:
        print("The Device shadow updated : {0}, The Device shadow completed: {1}".format(shadow_updated,
                                                                                         shadow_completed))
    else:
        print("The Device shadow updated : {0}, The Device shadow completed: {1}".format(shadow_updated,
                                                                                         shadow_completed))
        raise AssertionError("Fail")


def sms_board_software_reset():
    response = uniflash_auto.software_reset()
    if response == 0:
        print("Board has been reset Successfully :", response)
    else:
        print("Board reset was Unsuccessfully :", response)
        raise AssertionError("Fail")


def sms_board_check_for_local_provisioning_started(file_name):
    response, time_interval = sms_bas.check_for_local_provisioning_started(file_name)
    if response:
        print("Local Provisioning Started : ", response)
    else:
        print("Local Provisioning Started : ", response)
        raise AssertionError("Fail")


def sms_board_check_wrong_wifi_credentials(file_name):
    response = sms_bas.check_wrong_wifi_credentails(file_name)
    if response:
        print("Wrong Credentials:", response)
    else:
        print("Wrong Credentials:", response)
        raise AssertionError("Fail")


def sms_board_check_watchdog_reset(file_name):
    watchdog_reset, restart_state = sms_bas.get_watchdog_timer_count(file_name)
    if restart_state and not watchdog_reset:
        print("Restart State: {} & watchdog_reset: {}". format(restart_state, watchdog_reset))
    else:
        print("Restart State : {} & watchdog_reset {}".format(restart_state, watchdog_reset))
        raise AssertionError("Fail")


# new test cases starts from here, release date - 31/12/2020.
# Author - Shubham Sonawane changes made on 14-12-2020
def sms_board_check_certificate_firmware_version_sent(file_name):
    res = sms_bas.check_certificate_firmware_version_sent(file_name)
    # print(res)
    if res[0] and res[1] and res[2]:
        print("Certificate sent: {0}, firware Version sent: {1},"
              "cloudUrl: {2}".format(res[0], res[1], res[2]))
    else:
        raise AssertionError("Failed: certificate sent: {0}, firware Version sent: {1}, "
                             "cloudUrl: {2}".format(res[0], res[1], res[2]))


def sms_board_check_cloud_confirmation(file_name, motorname):
    print("")
    res = sms_bas.check_cloud_confirmation(file_name)
    if res[0]:
        if res[1] == motorname:
            print("Cloud_confirmation: {0} and Motor Name: {1}".format(res[0], res[1]))
    else:
        print("Failed: cloud_confirmation: {0} and Motor Name: {1}".format(res[0], res[1]))


# Author - Shubham Sonawane created on 21-12-2020
def sms_board_check_networkerror_feedbackerror_retries(file_name):
    response = sms_bas.network_not_connected(file_name)
    if response:
        response1 = sms_bas.feedback_fail_error(file_name)
        if response1:
            response2 = sms_bas.get_retries_count(file_name)
        if response2:
            print("Passed, network not connected: {0}, feedback fail error: {1}, 3 retries Completed: {2}"
                  .format(response, response1, response2))
        else:
            raise AssertionError("Failed, network not connected: {0}, feedback fail error: {1}, 3 retries Completed: "
                                 "{2}".format(response, response1, response2))


def sms_board_check_invalid_signature(file_name):
    res = sms_bas.check_invalid_signature(file_name)
    if res:
        print("Invalid Signature: ", res)
    else:
        raise AssertionError("Failed, Invalid Signature: ", res)


def sms_board_check_ota_event(file_name):
    res = sms_bas.check_ota_event(file_name)
    if res:
        print("OTA event Occured: ", res)
    else:
        raise AssertionError("Failed, OTA event Occured: ", res)


#!/usr/bin/env python3


import os
import time
import serial
from datetime import datetime
import threading
import sys

test_log_dir_name = " "
sleep_timer = 1

# list of keywords (strings) which we will be processing on.
keyword_list = {"get_firmware_version": "OTA demo version",
                "get_hibernate_count": "restart after",
                "get_wakeup_intervals": "[INFO ][DEMO][1002] OTA demo version",
                "check_hibernate_if_not_provisioned": "Provisioning stopped",
                "Provisioning stopped": "restart after",
                "check_mqtt_msgs": "SMS Data Sending Completed",
                "mqtt_publish_success": "MQTT PUBLISH successfully sent",
                "mqtt_publish_ack": "1 publishes completed",
                "check_hibernate_if_data_sent": "Stage 5. SMS Data Sending Completed",
                "SMS Data Sending Completed": "restart after",
                "check_OTA_interval": "Starting OTA Agent",
                "get_fw_version_upgrade_OTA": "OTA demo version",
                "get_SSID_name_dev_prov": "Connected to SSID",
                "get_SSID_name_dev_running": "STA Connected to the AP",
                "check_device_started_in_ap": "Device started in AP role",
                "check_device_reboot_if_file_read_error": "FS - Couldn't read file. error status",
                "file_read_error": "Restart immediately",
                "check_wake_from_hibernate_send_data": "restart after",
                "restart after": "Stage 5. SMS Data Sending Completed",
                "if_prov_wifi_not_exist_hibernate_mode": "Cannot connect to AP or profile does not exist",
                "wifi_prof_not_exist": "restart after",
                "check_ota_bad_sign": "Image was rejected and bundle files rolled back",
                "check_ota_same_version": "Image was rejected and bundle files rolled back",
                "check_ota_downloaded": "File receive complete and signature is valid.",
                "get_security_alert": "Current number of alerts",
                "check_reset": "OTA demo version",
                "check_for_start_provisioning": "Provisioning Started",
                "check_for_completed_provisioning": "Provisioning completed successfully",
                "check_for_local_provisioning_started": "waits for 180 seconds",
                "check_for_local_provisioning_stopped": "Provisioning stopped",
                "check_mqtt_publish_topic": "$aws/rules/acs_sms_carlsberg_nonprod_sms_data_rule/adi.ff2def/",
                "check_device_registered": "MQTT demo client identifier is ",
                "check_device_shadow_update": "Shadow UPDATE",
                "Shadow UPDATE": "Stage 3. SMS Sensor JIT&ThingShadow Completed",
                "sms_board_wrong_wifi_credentails": "Confirmation fail: Connection failed",
                "get_watchdog_timer_count": "OTA demo version",
                "watchdog_count": "Watchdog Reset Count"}


class thread_with_trace(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False
        self.__run_backup = self.run
        self.run = self.__run

    def start(self):
        # self.__run_backup = self.run
        # self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


def kill_thread(thread):
    thread.kill()
    thread.join()
    return thread.is_alive()


def func():
    while True:
        pass


def create_test_suite_dir(dir_name):
    global test_log_dir_name
    # changes made by shubham for removal of timestamp.
    test_log_dir_name = dir_name + time_stamp()
    os.makedirs(os.path.join("logs", test_log_dir_name))
    return test_log_dir_name


# Edited by Shubham on 4/9/2020. Function to check whether the SMS board is connected
def get_serial_port(port):
    try:
        res = serial.Serial(port)
        res.flush()
        response = res.is_open
        res.close()
        return response
    except serial.serialutil.SerialException:
        return False


# End of code.
def wait_countdown(t_min):
    t_started = True
    global sleep_timer
    sleep_timer = t_min
    # int -> float changes made by me.
    t_min = int(t_min)
    if t_min >= 1:
        t_sec = t_min * 60
        time.sleep(t_sec + 3)
    else:
        t_started = False
    return t_started


# Create and collect serial data from device for n minutes and save it in a file
def get_serial_data(port, baudrate, t_min, file_name, bytesize=8, parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE, timeout=0):
    # lf_name = file_name
    lf_name = os.path.join("logs", test_log_dir_name, file_name)  # + "_" + port + sms_util.time_stamp
    # i = 0 commenting not used by shubham on 26-09.
    try:
        port = serial.Serial(port, baudrate, bytesize, parity, stopbits, timeout)
        if port.is_open:
            # int -> float changes made by me on 23-10
            t_end = time.time() + 60 * int(t_min)
            with open(lf_name, "w+", encoding="utf8") as f_write:
                while time.time() < t_end:
                    data = port.read(30000)
                    if len(data) > 1:
                        data = data.decode('utf8').strip()
                        for line in data.splitlines():
                            if len(line) > 2:
                                # print(line)
                                f_write.write("[" + datetime.now().strftime("%d-%m-%y_%H:%M:%S") + "]" + " [" + str(
                                    int(time.time())) + "] " + "\t" + str(line) + "\n")
                    time.sleep(0.2)
            port.close()
        else:
            print("Unable to open the port")
            raise AssertionError("Fail")
    except serial.SerialException:
        print("Serial port exception.")
        raise AssertionError("Fail")
    return lf_name


# Reading log file. Changes made by shubham on 25-09-2020.
def read_log_file(dev_log_file):
    contents = ()
    file_loc = os.path.join("logs", test_log_dir_name, dev_log_file)
    try:
        if os.stat(file_loc).st_size != 0:
            with open(file_loc, encoding='utf8') as dev_log_file:
                contents = dev_log_file.readlines()
        return contents
    except IOError:
        print("File not Found at ", file_loc)
        return False


# General time stamp
def time_stamp():
    t_stamp = datetime.now().strftime("_%d-%m-%y-%H_%M_%S")
    return t_stamp


# General time stamp
def time_stamp():
    t_stamp = datetime.now().strftime("_%d-%m-%y-%H_%M_%S")
    return t_stamp


# Returns firmware version(str) in first check
def get_firmware_version(dev_log_file):
    for line in read_log_file(dev_log_file):
        if keyword_list["get_firmware_version"] in line:
            break
    print(line.split(" ")[11])
    return line.split(" ")[11]


# Returns total hibernate counts(int) in a log file
def get_hibernate_count(dev_log_file):
    count_hibernate = 0
    for line in read_log_file(dev_log_file):
        if keyword_list["get_hibernate_count"] in line:
            count_hibernate += 1
    # print(count_hibernate)
    return count_hibernate


# Returns list[] of difference of time intervals after each wake up from hibernate mode
def get_wakeup_intervals(dev_log_file):
    ts_serial = []
    diff_periodic = []
    for line in read_log_file(dev_log_file):
        if keyword_list["get_wakeup_intervals"] in line:
            ts_serial.append(int(line.split(" ")[1][1:-1]))
            if len(ts_serial) > 1:
                diff = ts_serial[-1] - ts_serial[-2]
                diff_periodic.append(int(diff / 60))  # In minutes
    # print(diff_periodic)
    return diff_periodic


# Returns boolean if device not provisioned and went to hibernate mode
def check_hibernate_if_not_provisioned(dev_log_file):
    not_provision = False
    hibernate = False
    for line in read_log_file(dev_log_file):
        if keyword_list["check_hibernate_if_not_provisioned"] in line:
            not_provision = True
        if not_provision:
            if keyword_list["Provisioning stopped"] in line:
                hibernate = True
                break
    # print(hibernate)
    return hibernate


# Returns boolean if mqtt connection successful
# Author Shubham Sonawane, changes made on 30-12-2020
def check_mqtt_msgs(dev_log_file):
    """This function will check for the stage 5 completed, mqtt publishes completed and 1 publishes
    completed"""
    mqtt = False
    mqtt_publish_success = False
    mqtt_publish_ack = False
    for line in read_log_file(dev_log_file):
        if keyword_list["mqtt_publish_success"] in line:
            mqtt_publish_success = True
        if mqtt_publish_success:
            if keyword_list["mqtt_publish_ack"] in line:
                mqtt_publish_ack = True
        if mqtt_publish_ack:
            if keyword_list["check_mqtt_msgs"] in line:
                mqtt = True
                break
    return mqtt_publish_success, mqtt_publish_ack, mqtt


# changes made on 29-12-2020
# Returns boolean if device went to hibernate mode after sending data to the cloud
def check_hibernate_if_data_sent(dev_log_file):
    data_sent = False
    hibernate = False
    for line in read_log_file(dev_log_file):
        if keyword_list["check_hibernate_if_data_sent"] in line:
            data_sent = True
        if data_sent:
            if keyword_list["SMS Data Sending Completed"] in line:
                hibernate = True
                break
    # print(hibernate)
    return hibernate, data_sent


# Returns list[] of difference of time intervals for each OTA check
def check_OTA_interval(dev_log_file):
    ts_serial = []
    diff_periodic = []
    for line in read_log_file(dev_log_file):
        if keyword_list["check_OTA_interval"] in line:
            ts_serial.append(int(line.split(" ")[1][1:-1]))
            if len(ts_serial) > 1:
                diff = ts_serial[-1] - ts_serial[-2]
                diff_periodic.append(int(diff / 60))  # In minutes
    # print(diff_periodic)
    return diff_periodic


# Returns list[] of firmware versions
def get_fw_version_upgrade_OTA(dev_log_file):  # returns firmwares list
    fw_versions = []
    for line in read_log_file(dev_log_file):
        if keyword_list["get_fw_version_upgrade_OTA"] in line:
            if len(line) > 90:
                fw_versions.append(line.split(" ")[11].rstrip())
    # print(fw_versions)
    return fw_versions


# Returns SSID name during provisioning
def get_SSID_name_dev_prov(dev_log_file):
    for line in read_log_file(dev_log_file):
        if keyword_list["get_SSID_name_dev_prov"] in line:
            break
    # print("".join(line.split(":")[3]))
    return "".join(line.split(":")[3])


# Returns SSID name when the device is running
def get_SSID_name_dev_running(dev_log_file):
    for line in read_log_file(dev_log_file):
        if keyword_list["get_SSID_name_dev_running"] in line:
            break
    # print("".join(line.split(" ")[14:-3]) )
    # return "".join(line.split(" ")[14:-3])
    return line.strip().split(":")[3].split(",")[0].strip()


# Returns boolean if device started in AP mode after flashing
def check_device_started_in_ap(dev_log_file):
    started_in_ap = False
    for line in read_log_file(dev_log_file):
        if keyword_list["check_device_started_in_ap"] in line:
            started_in_ap = True
    # print(started_in_ap)
    return started_in_ap


# Returns boolean if read fill error happens and device restart after that
def check_device_reboot_if_file_read_error(dev_log_file):
    file_read = False
    not_reboot_dev = True
    for line in read_log_file(dev_log_file):
        if keyword_list["check_device_reboot_if_file_read_error"] in line:
            file_read = True
        if file_read:
            if keyword_list["file_read_error"] in line:
                not_reboot_dev = False
                break
    return not_reboot_dev


# Returns boolean if device wakes up from hibernate and sends data to the cloud
def check_wake_from_hibernate_send_data(dev_log_file):
    hibernate = False
    data_sent = False
    for line in read_log_file(dev_log_file):
        if keyword_list["check_wake_from_hibernate_send_data"] in line:
            hibernate = True
        if hibernate:
            if keyword_list["restart after"] in line:
                data_sent = True
                break
    # print(data_sent)
    return data_sent, hibernate


def if_prov_wifi_not_exist_hibernate_mode(dev_log_file):
    wifi_prof_not_exist = False
    hibernate = False
    for line in read_log_file(dev_log_file):
        if keyword_list["if_prov_wifi_not_exist_hibernate_mode"] in line:
            wifi_prof_not_exist = True
        if wifi_prof_not_exist:
            if keyword_list["wifi_prof_not_exist"] in line:
                hibernate = True
                break
    # print(hibernate)
    return hibernate


def check_ota_bad_sign(dev_log_file):
    bad_sign = False
    for line in read_log_file(dev_log_file):
        if keyword_list["check_ota_bad_sign"] in line:
            bad_sign = True

    # print(bad_sign)
    return bad_sign


def check_ota_same_version(dev_log_file):
    same_ota = False
    for line in read_log_file(dev_log_file):
        if keyword_list["check_ota_same_version"] in line:
            same_ota = True

    # print(same_ota)
    return same_ota


def check_ota_downloaded(dev_log_file):
    ota_downloaded = False
    for line in read_log_file(dev_log_file):
        if keyword_list["check_ota_downloaded"] in line:
            ota_downloaded = True
    # print(ota_downloaded)
    return ota_downloaded


def get_security_alert(dev_log_file):
    threshold_values = []
    for line in read_log_file(dev_log_file):
        if keyword_list["get_security_alert"] in line:
            threshold_values.append(int(line.split(" ")[-1].replace("\n", "")))
    return threshold_values


def check_reset(log_file):
    reset_state = False
    for line in read_log_file(log_file):
        if keyword_list["check_reset"] in line:
            reset_state = True
            break
    return reset_state


# changes made by shubham for kalyani on 28-09-2020. Checking for Provisioning Started.
def check_for_start_provisioning(log_file):
    provisioning_state = False
    for line in read_log_file(log_file):
        if keyword_list["check_for_start_provisioning"] in line:
            provisioning_state = True
            break
    return provisioning_state


def check_for_completed_provisioning(log_file):
    provisioning_completed_state = False
    for line in read_log_file(log_file):
        if keyword_list["check_for_completed_provisioning"] in line:
            provisioning_completed_state = True
    return provisioning_completed_state


# check for local provisioning and amount of time it stay in local provisioning.
# Author - Shubham, changes on 13-10-2020.
# function to check the start of local provisioning
def check_for_local_provisioning_started(log_file):
    local_provisioning_started = False
    time_local_provisioning = " "
    for line in read_log_file(log_file):
        if keyword_list["check_for_local_provisioning_started"] in line:
            local_provisioning_started = True
            time_local_provisioning = line.split(" ")[1][1:-1]
            # using human readble date
            # time_local_provisioning = line.split(" ")[0].split("_")[1][0:-1].strip()
            break
    return local_provisioning_started, time_local_provisioning


# function to check when local provisiong stopped
def check_for_local_provisioning_stopped(log_file):
    local_provisioning_stopped = False
    time_local_provisioning_stopped = " "
    for line in read_log_file(log_file):
        if keyword_list["check_for_local_provisioning_stopped"] in line:
            time_local_provisioning_stopped = line.split(" ")[1][1:-1]
            local_provisioning_stopped = True
            break
    return local_provisioning_stopped, time_local_provisioning_stopped


# function to  check the device stays in local provisioning
def check_time_interval_of_local_provisioning(log_file):
    diff_periodic, diff = 0, 0
    state_of_start, time_local_provision_start = check_for_local_provisioning_started(log_file)
    state_of_stop, time_local_provision_stop = check_for_local_provisioning_stopped(log_file)
    if state_of_start & state_of_stop:
        diff = int(time_local_provision_stop) - int(time_local_provision_start)
        diff_periodic = int(diff / 60)
    return diff_periodic


# function to check mqtt publish topic on which sms device is publishing data on the cloud.
def check_mqtt_publish_topic(log_file):
    line = " "
    for line in read_log_file(log_file):
        if keyword_list["check_mqtt_publish_topic"] in line:
            break
    return line.split(" ")[7].strip()


# function to check device is registered on cloud
def check_device_registered(log_file):
    line = " "
    for line in read_log_file(log_file):
        if keyword_list["check_device_registered"] in line:
            break
    return line[79:].strip()


# function to check whether the device shadow is updated and completed
def check_device_shadow_update(log_file, device_id):
    shadow_update = "Shadow UPDATE of {0} was ACCEPTED.".format(device_id)
    shadow_completed, shadow_updated = False, False
    for line in read_log_file(log_file):
        if keyword_list["check_device_shadow_update"] in line:
            if line.split("]")[6].strip() == shadow_update:
                shadow_updated = True
        if shadow_updated:
            if keyword_list["Shadow UPDATE"] in line:
                print(line.split("]")[6].strip())
                shadow_completed = True
                break
    return shadow_updated, shadow_completed


# Author - Shubham Sonawane, made changes on 30-10-2020.
# Function to check for wrong wifi credentials
def check_wrong_wifi_credentails(log_file):
    confirmation_fail = False
    for line in read_log_file(log_file):
        if keyword_list["sms_board_wrong_wifi_credentails"] in line:
            confirmation_fail = True
            break
        else:
            confirmation_fail = False
    return confirmation_fail


# Author by shubham Sonawane on 30-10-2020
# function to get the watchdog timer count.
def get_watchdog_timer_count(log_file):
    restart_state = False
    watchdog_reset = False
    for lines in read_log_file(log_file):
        if keyword_list["get_watchdog_timer_count"] in lines:
            restart_state = True
        if restart_state:
            if keyword_list["watchdog_count"] in lines:
                # print(lines)
                watchdog_value = lines.split(")")[1].split("[")[1].split("]")[0]
                # print(watchdog_value)
                if int(watchdog_value) != 0:
                    watchdog_reset = True
                else:
                    watchdog_reset = False
    return watchdog_reset, restart_state


# new test cases keywords starts from here, release date - 31/12/2020.
# Author - Shubham Sonawane changes made on 14-12-2020
def check_certificate_firmware_version_sent(file_name):
    """ Function to check whether the certificate sent, firmware version sent, and is
    cloud url present """
    certificate_sent = False
    firmware_version_sent = False
    cloud_url = False
    for lines in read_log_file(file_name):
        if "Firmware version sent" in lines:
            firmware_version_sent = True
            # print(lines)
        if firmware_version_sent:
            if "certificate sent" in lines:
                certificate_sent = True
                # print("\n", lines)
        if certificate_sent:
            if "Updating Configuaration file" in lines:
                cloud_url = True
                # print(lines.split("\"")[3])
                break
    return firmware_version_sent, certificate_sent, cloud_url


# Auhor - Shubham Sonawane , changes made by 17-12-2020
def check_cloud_confirmation(file_name):
    motorname = " "
    cloud_confirmartion = False
    for line in read_log_file(file_name):
        if "[External Cloud Confirmation]" in line:
            cloud_confirmartion = True
            # print(line)
            # the below print statement gives the motor name.
            # print(line.split(" ")[9].split("[")[1].split("]")[0])
            motorname = line.split(" ")[9].split("[")[1].split("]")[0]
            break
    return cloud_confirmartion, motorname


# Author - Shubham Sonawane created on 23-12-2020
def network_not_connected(file_name):
    network_not_connected_status = False
    for lines in read_log_file(file_name):
        if "Network is not connected" in lines:
            network_not_connected_status = True
            break
    return network_not_connected_status


def feedback_fail_error(file_name):
    feeback_error = False
    for lines in read_log_file(file_name):
        if "feedback to Smartphone app failed" in lines:
            feeback_error = True
            break
    return feeback_error


def get_retries_count(file_name):
    retries_count = False
    for lines in read_log_file(file_name):
        if "Device not claimed. 1 retries left" in lines:
            retries_count = True
            break
    return retries_count


# Author - Shubham Sonawane Created on 28-12-2020.
def check_invalid_signature(file_name):
    """ This function will check for invalid signature """
    invalid_signature = False
    for line in read_log_file(file_name):
        if "Image was rejected and bundle files rolled back" in line:
            invalid_signature = True
            break
    return invalid_signature


# Author - Shubham Sonawane created on 28-12-2020.
def check_ota_event(file_name):
    """This function will check for OTA event"""
    ota_event = False
    for line in read_log_file(file_name):
        if "SMS Sensor OTA Completed" in line:
            ota_event = True
            break
    return ota_event


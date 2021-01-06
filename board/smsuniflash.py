# Copyright (c) 2020 Analog Devices, Inc.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#   - Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
#   - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#   following disclaimer in the documentation and/or other materials provided with the distribution.
#   - Modified versions of the software must be conspicuously marked as such.
#   - This software is licensed solely and exclusively for use with processors/products manufactured by or for Analog
#   Devices, Inc.
#   - This software may not be combined or merged with other code in any manner that would cause the software to become
#   subject to terms and conditions which differ from those listed here.
#   - Neither the name of Analog Devices, Inc. nor the names of its contributors may be used to endorse or promote
#   products derived from this software without specific prior written permission.
#   - The use of this software may or may not infringe the patent rights of one or more patent holders.  This license
#   does not release you from the requirement that you obtain separate licenses from these patent holders to use this
#   software.
#
# THIS SOFTWARE IS PROVIDED BY ANALOG DEVICES, INC. AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, NON-INFRINGEMENT, TITLE, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL ANALOG DEVICES, INC. OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, DAMAGES ARISING OUT OF CLAIMS OF
# INTELLECTUAL PROPERTY RIGHTS INFRINGEMENT; PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# 2019-01-10-7CBSD SLA
import json
import logging
import os
import socket
import threading
from pathlib import Path
from secrets import token_bytes
from subprocess import Popen, PIPE
from time import time

import pyqrcode

from smsutil import base_dir
from smsutil import logging_format_debug, configure_logging


class SmsUniflash:
    """
    Handles Uniflash operations needed for managing an SMS (Smart Motor Sensor) device
    """

    def __init__(self, configuration: dict):
        """
        :param configuration: Dictionary of configuration parameters for Uniflash
        """
        self.__configuration = configuration
        self.__project = "SMS_ADICloud_Autogen"
        self.__temp_dir = os.path.join(base_dir, "temp")
        self.__projects_folder = self.absolute_path("uniflash\\projectDir\\projects")
        self._encryption_key = self.absolute_path(
            "uniflash\\projectDir\\projects\\Production-Digicert\\sl_ks\\ImageVendor.key.bin")

        Path(self.__temp_dir).mkdir(parents=True, exist_ok=True)
        self._out = None
        self._err = None
        self._sthread = None

    def xds110reset(self) -> float:
        """
        Perform a reset using the xds110reset utilitiy

        :return: float Time it took to reset.
        """
        logging.info("Resetting via the xds110reset utility at '%s'" % self.__configuration["Uniflash"]["xds110reset"])
        if not os.path.isfile(self.__configuration["Uniflash"]["xds110reset"]):
            raise RuntimeError("xds110reset '%s' was not found. Check that your configuration json is correct." % (
                self.__configuration["Uniflash"]["xds110reset"],))

        cmd = self.__configuration["Uniflash"]["xds110reset"]
        timeout = 5.0
        try:
            start = time()
            process = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=base_dir, )
            out, err = process.communicate(timeout=timeout)
            exit_code = process.wait(timeout=timeout)
            end = time()
            logging.debug("Execution took %d seconds" % (end - start))

            if exit_code != 0:
                raise RuntimeError("FAILED: xds110reset command '%s' failed with the error below\n\n %s" % (cmd, err))

            return end - start
        except Exception as e:
            raise RuntimeError("FAILED: xds110reset command '%s' failed with the error below\n\n %s" % (cmd, e))

    def dslite_run_cmd(self, cmd: str, timeout: float, retries: int = 1) -> float:
        """
        Get the Uniflash tool to execute the specified command
        :param retries: Number of times to retry the attempt (if attempts are likely to fail for some reason).
        :param cmd: Command line to execute
        :param timeout: timeout to wait for command to complete
        :return: Execution time in seconds
        """
        if not os.path.isfile(self.__configuration["Uniflash"]["dslite"]):
            raise RuntimeError("DSLITE.BAT '%s' was not found. Check that your configuration json is correct." % (
                self.__configuration["Uniflash"]["dslite"],))

        while retries > 0:
            try:
                start = time()
                process = Popen(cmd, stdout=PIPE, stderr=PIPE, cwd=base_dir, )
                self._out, self._err = process.communicate(timeout=timeout)
                exit_code = process.wait(timeout=timeout)
                end = time()
                logging.debug("Execution took %d seconds" % (end - start))

                if exit_code != 0:
                    retries -= 1
                    if retries == 0:
                        raise RuntimeError(
                            "FAILED: dslite command '%s' failed with the error below\n\n %s" % (cmd, self._err))
                    else:
                        logging.info(
                            "RETRYING: dslite command '%s' failed with the error below\n\n %s" % (cmd, self._err))
                else:
                    return end - start
            except Exception as e:
                raise RuntimeError("FAILED: dslite command '%s' failed with the error below\n\n %s" % (cmd, e))

    def __export_temp_json_file(self, filename: str, content: dict) -> str:
        """
        Create temporary json file
        :param filename: name of the file to be crea
        :param content: dictionary of content to export
        :return: full path of file created
        """
        # REM Create the files for this THING
        json_path = os.path.join(self.__temp_dir, filename)
        with open(json_path, 'wt') as fp:
            json.dump(content, fp, indent="   ")

        return json_path

    def absolute_path(self, possible_relative):
        if not os.path.isabs(possible_relative):
            return os.path.join(base_dir, possible_relative)
        else:
            return possible_relative

    def change_encryption_key(self):
        """
        Going to ramdomise the encryption key
        :return:
        """
        logging.info("Changing the encryption key")
        aes_image_encryption_key = token_bytes(16)
        with open(self._encryption_key, "wb") as f:
            f.write(aes_image_encryption_key)

    def create_image(self, device: str, image: str = None) -> str:
        """
        Create the SLI image file for the device, based on the contents of the configuration file

        1. Clone the base project (starting point for modifications)
        2. Use the provided 'adi_sms.cfg' and overwrite it in the project
        3. Add the "thing specific" client certificate
        4. Add the "thing specific" client private key
        5. Add the MCU Image (and signature)
        6. Update the SSID, DeviceName to match the device. Update IP address

        :param device: Device Name e.g. '00000412Z'
        :param image: None (default image for device will be used) or specify a value to override this behaviour
        :return: SLI filename of the created file
        """

        if device not in self.__configuration["Devices"]:
            raise RuntimeError("Please update configuration file with information for device '%s'" % device)

        self.__project = "SMS%s" % device
        # Production or Development mode?
        # If Production, use TI or Digicert?
        if 'Configuration' in self.__configuration["Devices"][device]:
            configuration = self.__configuration["Devices"][device]['Configuration']
        else:
            configuration = self.__configuration["Uniflash"]['Configuration']
        valid_configurations = [
            "ProductionDigiCert",
            "ProductionTI",
            "Development"
        ]
        assert configuration in valid_configurations, "configuration '%s' must be one of %s" % (configuration, valid_configurations)

        # A different base project to start from depending on the mode
        # Development projects have a mode development and contain TI signer credentials
        # Production projects have a mode Production and contain Digicert signer credentials and images are encrypted
        if configuration == "ProductionDigiCert":
            project_template = "Production-Digicert"
            encryption_key = self._encryption_key
            mcu_image_cert = "analog devices international uc.der"
            mcu_image_signer = None  # A signature generated elsewhere from the DigiCert ket MUST be provided...cannot be signed locally
        else:
            if configuration == "ProductionTI":
                project_template = "Production-Ti"
                encryption_key = self._encryption_key
                mcu_image_cert = "tisigner.crt.der"
                mcu_image_signer = self.absolute_path("uniflash\\files\\Development\\tisigner.key")
            else:
                project_template = "Development-TI"
                encryption_key = None
                mcu_image_cert = "tisigner.crt.der"
                mcu_image_signer = self.absolute_path("uniflash\\files\\Development\\tisigner.key")

        logging.info("Cloning project '%s' from template '%s'" % (self.__project, project_template))
        if encryption_key:
            # Need --with_key to copy the key over
            cmd = "%s --mode cc32xx project clone --name %s --new %s --overwrite --project_path \"%s\" --with_key" % (
                self.__configuration["Uniflash"]['dslite'], project_template, self.__project, self.__projects_folder)
        else:
            cmd = "%s --mode cc32xx project clone --name %s --new %s --overwrite --project_path \"%s\"" % (
                self.__configuration["Uniflash"]['dslite'], project_template, self.__project, self.__projects_folder)
        _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])

        # 2. Use the provided 'adi_sms.cfg' and overwrite it in the project
        adi_sms_cfg_path = self.absolute_path(self.__configuration["Devices"][device]["CfgFile"])
        logging.info("Add client cfg file '%s' into the project." % (adi_sms_cfg_path,))
        cmd = '%s --mode cc32xx project add_file --name %s --fs_path adi_sms.cfg --file "%s" --token 1523683852 ' \
              '--overwrite --flags secure,vendor,nosignaturetest --project_path \"%s\"' % (
                  self.__configuration["Uniflash"]['dslite'], self.__project, adi_sms_cfg_path, self.__projects_folder)
        _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])

        # 3. Add the "thing specific" client certificate
        client_certificate = self.absolute_path(self.__configuration["Devices"][device]["ClientCertificate"])
        logging.info("Adding client certificate '%s'" % (client_certificate,))
        cmd = '%s --mode cc32xx project add_file --name %s --fs_path /certs/clientcert.crt --file "%s" --token ' \
              '1523683852 --overwrite --flags secure,vendor,nosignaturetest --project_path \"%s\"' % (
                  self.__configuration["Uniflash"]['dslite'], self.__project, client_certificate,
                  self.__projects_folder)
        _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])

        # 4. Add the "thing specific" client private key
        client_private_key = self.absolute_path(self.__configuration["Devices"][device]["PrivateKey"])
        logging.info("Adding client private key '%s'" % (client_private_key,))
        cmd = '%s --mode cc32xx project add_file --name %s --fs_path /certs/privatekey.key --file "%s" --token ' \
              '1523683852 --overwrite --flags secure,nosignaturetest,vendor --project_path \"%s\"' % (
                  self.__configuration["Uniflash"]['dslite'], self.__project, client_private_key,
                  self.__projects_folder)
        _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])

        # 5. Add the MCU Image (and signature)
        if 'MCUImage' in self.__configuration["Devices"][device]:
            mcu_image = self.absolute_path(self.__configuration["Devices"][device]['MCUImage'])
        else:
            mcu_image = self.absolute_path(self.__configuration["Uniflash"]['MCUImage'])

        if 'MCUImageSignature' in self.__configuration["Devices"][device]:
            mcu_image_signature = self.absolute_path(self.__configuration["Devices"][device]['MCUImageSignature'])
        else:
            mcu_image_signature = self.absolute_path(self.__configuration["Uniflash"]['MCUImageSignature'])
        
        if mcu_image_signer:
            logging.info("Adding mcu image '%s' using code signing private key (external) '%s' and referring to "
                         "certificate '%s'" % (
                             mcu_image, mcu_image_signer, mcu_image_cert))
            cmd = '%s --mode cc32xx project add_file --name %s --file "%s" --token 1952007250 --mcu --flags failsafe,' \
                  'secure,vendor,publicwrite --priv "%s" --cert "%s" --overwrite --project_path \"%s\"' % (
                      self.__configuration["Uniflash"]['dslite'], self.__project, mcu_image, mcu_image_signer,
                      mcu_image_cert, self.__projects_folder)
        else:
            logging.info("Adding mcu image '%s' using provided signature '%s' and referring to "
                         "certificate '%s'" % (
                             mcu_image, mcu_image_signature, mcu_image_cert))
            cmd = '%s --mode cc32xx project add_file --name %s --file "%s" --token 1952007250 --mcu --flags failsafe,' \
                  'secure,vendor,publicwrite --sign "%s" --cert "%s" --overwrite --project_path \"%s\"' % (
                      self.__configuration["Uniflash"]['dslite'], self.__project, mcu_image, mcu_image_signature,
                      mcu_image_cert, self.__projects_folder)

        _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])

        # 6. Update the SSID, DeviceName to match the device. We might need to update the devMac if a development project
        reconfig_json = {"SimpleLink": {
            "apSsid": "SMS%s" % device,
            "deviceName": "SMS%s" % device,
            "apNetwork": self.__configuration["Devices"]["apNetwork"]
        },
        }
        if configuration == "Development":
            # The devMac can be provided or we will connect and retrieve it
            if "devMac" in self.__configuration["Devices"][device]:
                reconfig_json["SimpleLink"]["devMac"] = self.__configuration["Devices"][device]["devMac"]
                logging.info("Building development image for fixed MAC of %s" % self.__configuration["Devices"][device][
                    "devMac"])
            else:
                logging.info("Querying the device to get the MAC address as it is not provided")
                cmd = '%s --mode cc32xx device info --json' % self.__configuration["Uniflash"]['dslite']
                _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])

                # The text in self._err is JSON with the information we need.
                device_info = json.loads(self._err)
                logging.info("Building development image for attached device MAC of %s" % device_info['mac_address'])
                reconfig_json["SimpleLink"]["devMac"] = device_info['mac_address']

        reconfig_json_path = self.__export_temp_json_file('reconfig.json', reconfig_json)
        logging.info("Reconfiguring the project with '%s'" % reconfig_json)
        cmd = '%s --mode cc32xx project reconfig --name %s --file "%s" --project_path \"%s\"' % (
            self.__configuration["Uniflash"]['dslite'], self.__project, reconfig_json_path, self.__projects_folder)
        _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])

        if not image:
            image = self.__default_sli_image(device, encrypted=True if encryption_key else False)
        logging.info("Exporting the image to file '%s'" % image)
        cmd = '%s --mode cc32xx project create_image --name %s --sli_file "%s" --project_path \"%s\"' % (
            self.__configuration["Uniflash"]['dslite'], self.__project, image, self.__projects_folder)
        _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])
        logging.info("Image creation completed successfully")

        logging.info("Exporting the project to zipfile")
        cmd = '%s --mode cc32xx project export --name %s --project_path \"%s\" --path \"%s\"' % (
            self.__configuration["Uniflash"]['dslite'], self.__project, self.__projects_folder, self.__temp_dir)
        _ = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'])
        # Find the name of the exported file
        lines = self._out.decode().split("\n")
        for line in lines:
            if "Exported project file name:" in line:
                logging.info(line.strip())
                break
        logging.info("Project export completed successfully")

        text = pyqrcode.create(device)
        qr_code_file = os.path.join(base_dir, self.__temp_dir, "%s.svg" % device)
        text.svg(qr_code_file, scale=1)
        logging.info("QR Code Image  saved to '%s'" % qr_code_file)

        return image, encryption_key

    def __default_sli_image(self, device: str, relative: bool = False, encrypted=False) -> str:
        """
        Construct the default image name for a device
        :param device: Device Name e.g. '00000412Z'
        :param relative: If true, return a relative path, otherwise an absolute one
        :return: Image Name
        """
        if encrypted:
            base_filename = '%s.encrypted.sli' % device
        else:
            base_filename = '%s.sli' % device

        if relative:
            image_path = os.path.join(self.__temp_dir, base_filename)
        else:
            image_path = os.path.join(base_dir, self.__temp_dir, base_filename)

        return image_path

    def __run(self, port, hwdetails):
        """
        Connect to the specified port and log the communications for now.
        :param port:
        :return:
        """
        HOST = '127.0.0.1'  # Standard loopback interface address (localhost)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)  # timeout for listening
            s.bind((HOST, port))
            s.listen(1)
            while self._running:
                try:
                    conn, addr = s.accept()
                except socket.timeout:
                    pass
                except:
                    raise
                else:
                    with conn:
                        logging.debug('UnifLash requester client connected on "%s"', addr)
                        while True:
                            data = conn.recv(1024)
                            if not data:
                                break
                            logging.info("Received command: '%s'" % data.decode())
                            if b'POWER ON' in data:
                                if "release_reset" in hwdetails and hwdetails["release_reset"] is not None:
                                    hwdetails["release_reset"]()
                                else:
                                    if "release_reset_true" in hwdetails and hwdetails["release_reset_true"] is not None:
                                        hwdetails["release_reset_true"](True)
                                    else:
                                        logging.info("No release_reset() function was provided.")

                            if b'POWER OFF' in data:
                                if "assert_reset" in hwdetails and hwdetails["assert_reset"] is not None:
                                    hwdetails["assert_reset"]()
                                else:
                                    if "assert_reset_false" in hwdetails and hwdetails["assert_reset_false"] is not None:
                                        hwdetails["assert_reset_false"](False)
                                    else:
                                        logging.info("No assert_reset() function was provided.")

                            conn.sendall(data)

    def _stop(self):
        if self._sthread:
            if self._sthread.is_alive():
                self._running = False
                self._sthread.join()

    def get_mac_address(self, hwdetails: dict = None):
        """
        Call the device info command to get the MAC address of the connected SMS board.

        By default, we will attempt use the xds110 to do everything unless overridden by param hwdetails

        Specify "comport" in hwdetails if you want to use a UART cable.
        Specify "assert_reset" callback in hwdetails to assert the reset (only used when UART cable is used)
        Specify "release_reset" callback in hwdetails to assert the reset (only used when UART cable is used)

        :param hwdetails: Details of the interface hardware
        :return:
        """
        if hwdetails is None:
            hwdetails = {}
        logging.info("Querying the device to get the MAC address as it is not provided")
        cmd = '%s --mode cc32xx device info --json' % self.__configuration["Uniflash"]['dslite']

        if "comport" in hwdetails:
            logging.debug("Requesting to get info via COM port, and will need the KEITHLEY 2280S to implement it.")
            cmd += ' --port "%s" --script_path "%s"' % (hwdetails["comport"], base_dir[:-1])
            # Uniflash will execute two Python script files in script_path to power on and off the unit
            # - power_on_com.py
            # - power_off_com.py
            # This is using a basic Python 2.7.12 in Uniflash 5.3.0 with no chance of installing additional libraries.
            # This will communicate back via the specified socket to tell us to power off and on the power supply
            # We let these scripts know which socket to use using SMS_IPC_PSU_IP environment variable

            self._running = True
            port = 65432
            os.environ['SMS_IPC_PSU_IP'] = "%d" % port
            os.environ['SMS_IPC_PSU_DELAY'] = '1'
            # Start our thread running
            self._sthread = threading.Thread(target=self.__run, args=(port, hwdetails))
            self._sthread.start()

        try:
            execution_time = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['command_timeout'], retries=2)
            logging.info("Getting device information completed successfully in %f seconds." % execution_time)
        except RuntimeError as e:
            self._stop()
            raise

        self._stop()

        # The text in self._err is JSON with the information we need.
        device_info = json.loads(self._err)
        return device_info['mac_address']

    def program_image(self, device: str, image: str = None, encryption_key: str = None, hwdetails: dict = None) -> bool:
        """
        Programs a previously created image to the connected device using the Uniflash tool

        By default, we will attempt use the xds110 to do everything unless overridden by param hwdetails

        :param device: Device Name e.g. 'SMS00000XXXY'
        :param image: Full and absolute path of image file to program
        :param encryption_key: Encryption key (needed if image is encrypted, else None
        :param hwdetails: Details of the interface hardware
        :return:
        """
        if hwdetails is None:
            hwdetails = {}
        if not image:
            image = self.__default_sli_image(device, encrypted=True if encryption_key else False)
        logging.info(
            "Programming image file '%s' to device '%s'. (allowing %d seconds to commplete, observed to be 70)" % (
                image, device, self.__configuration["Uniflash"]['program_timeout']))

        if not os.path.isfile(image):
            raise RuntimeError(
                "Image file '%s' was not found. Check that your path is correct and if it is present." % (
                    image,))

        if encryption_key:
            logging.info("Encrypted image. Providing key otherwise FS_PROGRAMMING_ILLEGAL_FILE is expected.")
            cmd = '%s --mode cc32xx image program --file "%s" --key "%s"' % (
                self.__configuration["Uniflash"]['dslite'], image, encryption_key)
        else:
            cmd = '%s --mode cc32xx image program --file "%s"' % (
                self.__configuration["Uniflash"]['dslite'], image)

        if "comport" in hwdetails:
            logging.debug("Requesting to program via COM port, and will need the KEITHLEY 2280S to implement it.")
            cmd += ' --port "%s" --script_path "%s"' % (hwdetails["comport"], base_dir[:-1])
            # Uniflash will execute two Python script files in script_path to power on and off the unit
            # - power_on_com.py
            # - power_off_com.py
            # This is using a basic Python 2.7.12 in Uniflash 5.3.0 with no chance of installing additional libraries.
            # This will communicate back via the specified socket to tell us to power off and on the power supply
            # We let these scripts know which socket to use using SMS_IPC_PSU_IP environment variable

            self._running = True
            port = 65432
            os.environ['SMS_IPC_PSU_IP'] = "%d" % port
            os.environ['SMS_IPC_PSU_DELAY'] = '1'
            # Start our thread running
            self._sthread = threading.Thread(target=self.__run, args=(port, hwdetails))
            self._sthread.start()

        try:
            execution_time = self.dslite_run_cmd(cmd, self.__configuration["Uniflash"]['program_timeout'], retries=2)
            logging.info("Programming image file '%s' to device '%s' completed successfully in %f seconds." % (
                image, device, execution_time))
            return True
        except RuntimeError as e:
            self._stop()
            return False
            # raise

        self._stop()


if __name__ == "__main__":
    # Example usage
    configure_logging(logging_format=logging_format_debug, debug_log_file="uniflash.log")
    logging.info("Sample usage of SmsUniflash to program a device image to a SMS unit")
    logging.info("Using Uniflash and LAUNCHXL board for now.")
    unifl = SmsUniflash(configuration=json.load(open("configuration.json", "r")))
    unifl.program_image("00000856R", os.path.join(base_dir, "SMS00000XXXY.sli"))

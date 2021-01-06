from smsuniflash import SmsUniflash
import os
import json
import socket
import time
from smsutil import base_dir

default_config_file = os.path.join(base_dir, "configuration_%s.json" % socket.gethostname())

def configuration_file(cfg_file):
    template_config_file = os.path.join(base_dir, "configuration_MACHINE_NAME_TEMPLATE.json")

    if cfg_file == default_config_file and not os.path.exists(cfg_file):
        # User has not explicitly specified a configuration file and we are using the default one but it has not
        # been created yet. Let's try and create a reasonable one from the defaults
        with open(template_config_file, "r") as f_template:
            template_configuration = json.load(f_template)

            # "dslite": "C:\\ti\\uniflash_<REPLACE VERSION NUMBER>\\dslite.bat",
            # "xds110reset": "C:\\ti\\uniflash_<REPLACE VERSION NUMBER>\\simplelink\\imagecreator\\bin\\xds110reset.exe"

            ti_install_base = "C:\\ti"
            for file in os.listdir(ti_install_base):
                if file[:9] == "uniflash_":
                    uniflash_base = file
                    uniflash_dslite = os.path.join(ti_install_base, uniflash_base, "dslite.bat")
                    uniflash_xds110reset = os.path.join(ti_install_base, uniflash_base, "simplelink\\imagecreator\\bin\\xds110reset.exe")
                    if os.path.exists(uniflash_dslite) and os.path.exists(uniflash_xds110reset):
                        template_configuration["Uniflash"]["dslite"] = uniflash_dslite
                        template_configuration["Uniflash"]["xds110reset"] = uniflash_xds110reset

            devices_base = os.path.join(base_dir, "uniflash\\devices")
            for file in os.listdir(devices_base):
                device_cfg = os.path.join(devices_base, file, "adi_sms.cfg")
                device_crt = os.path.join(devices_base, file, "cert.crt")
                device_key = os.path.join(devices_base, file, "privkey.key")
                if os.path.exists(device_cfg) and os.path.exists(device_crt) and os.path.exists(device_key):
                    template_configuration["Devices"][file] = {}
                    template_configuration["Devices"][file]["ClientCertificate"] = os.path.join("uniflash\\devices", file,"cert.crt")
                    template_configuration["Devices"][file]["PrivateKey"] = os.path.join("uniflash\\devices", file, "privkey.key")
                    template_configuration["Devices"][file]["CfgFile"] = os.path.join("uniflash\\devices", file, "adi_sms.cfg")


            # Now save it out..we will use it going forward. User may have to manually change some fields now
            # but it is a good starting point.
            with open(cfg_file, 'w') as fp:
                json.dump(template_configuration, fp, indent="\t")
    else:
        if not os.path.exists(cfg_file):
            raise argparse.ArgumentTypeError("{0} does not exist".format(cfg_file))

    return open(cfg_file,"rt")


def uni_flash_device(sms_device):
    cnf_open = configuration_file(default_config_file)
    configuration = json.load(cnf_open)
    cnf_open.close()
    unifl = SmsUniflash(configuration=configuration)
    image, encryption_key = unifl.create_image(sms_device)
    status = unifl.program_image(sms_device, image=image, encryption_key=encryption_key)
    if status:
        print("Successfully flashed")
        return True
    else:
        print("Device not flashed")
        return False


# author - shubham Sonawane. Idea - Akshay akbari, changes made on 20-10-2020 made for kalyani.
# function which will soft reset the board using uniflash tool (software reset)
# need to make changes in function with regards to uniflash tool version in below command.
def software_reset():
    execute = os.system("%windir%\\..\\ti\\uniflash_6.1.0\\simplelink\\imagecreator\\bin\\xds110reset.exe")
    return execute


# software_reset()
# def soft_reser():
#     reset = SmsUniflash.xds110reset()
#     print(reset)
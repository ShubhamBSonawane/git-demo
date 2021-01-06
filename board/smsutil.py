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

import logging
import os
import sys

# Using the logging module to record activity for debugging
logging_format_info = '%(message)s'
logging_format_debug = '%(asctime)s - %(levelname)s - %(message)s'

base_dir = ""
try:
    if sys.frozen or sys.importers:
        base_dir = os.path.dirname(sys.executable)
except AttributeError:
    base_dir = os.path.dirname(os.path.realpath(__file__))

base_dir += os.path.sep


def file_path(*path_components):
    return os.path.join(base_dir, *path_components)


def configure_logging(logging_format, debug_log_file=None):
    """
    Configure logging system
    :param logging_format: Format to be be used
    :param debug_log_file: None, or name of logging file which will be used.
    :return:
    """
    logger = logging.getLogger()

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(logging_format)

    if debug_log_file is not None:
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(debug_log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(logging_format)
    console.setFormatter(formatter)

    logging.getLogger('').addHandler(console)

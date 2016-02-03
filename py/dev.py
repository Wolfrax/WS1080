#!/usr/local/bin/python

# The hid library is available here: https://github.com/gbishop/cython-hidapi
# import hid

# The USB library is available here: http://sourceforge.net/projects/pyusb/
import usb.core
import usb.util
import usb.legacy
import logging
import sys

__author__ = 'mm'

DEVICE_ENDPOINT_ADDR = 0x81
DEVICE_READ_TIMEOUT = 1200
DEVICE_CTRL_TIMEOUT = 1200

# Protocol for reading WeatherStation taken from:
# http://site.ambientweatherstore.com/easyweather/


class Device:
    """
    Implements the basic communication with the device over pyusb
    """

    def __init__(self, id_vendor=0x1941, id_product=0x8021):
        """
        Initialise the Device by opening and claiming the USB interface
        :param id_vendor: Vendor for WH1080, normally 0x1941
        :param id_product: Product for WH1080, normally 0x80291
        :return: Nothing
        """
        self.logger = logging.getLogger('WS1080.WS.device')
        self.logger.debug('init')

        self.preamble_flag = False
        self.bmRequestType = usb.util.build_request_type(
            usb.util.ENDPOINT_OUT,
            usb.util.CTRL_TYPE_CLASS,
            usb.util.CTRL_RECIPIENT_INTERFACE)

        try:
            self.dev = usb.core.find(idVendor=id_vendor, idProduct=id_product)
            if self.dev is None:
                raise IOError
            if self.dev.is_kernel_driver_active(0):
                self.dev.detach_kernel_driver(0)
            self.dev.reset()
            self.dev.set_configuration()
            usb.util.claim_interface(self.dev, 0)

        except IOError:
            self.logger.warning('open: No USB device found')
            raise IOError("device - open: Device not opened")

    def preamble(self, data):
        """

        :param data: The preamble sequence to enabler reading
        :return: the number of bytes successfully written, None if unsuccessful
        """
        self.preamble_flag = True

        try:
            result = self.dev.ctrl_transfer(
                bmRequestType=self.bmRequestType,
                bRequest=usb.legacy.REQ_SET_CONFIGURATION,  # 9, could be devinfo.PICFW_SET_VENDOR_BUFFER = 0x10
                data_or_wLength=data,
                wValue=0x200,
                timeout=DEVICE_CTRL_TIMEOUT)
        except usb.core.USBError as err:
            self.logger.warning('preamble: USBError - %s', err)
            return None
        except:
            self.logger.warning('preamble: Unknown error - %s', sys.exc_info()[0])
            return None

        if result != len(data):
            self.logger.warning('preamble: Write failed result: %d, len: %d', result, len(data))
            return None
        return result

    def read(self, buf):
        """
        Read from the device into using buf
        :param buf: Number of bytes to read
        :return: the result as a list
        """
        assert self.preamble_flag
        self.preamble_flag = False

        try:
            result = self.dev.read(DEVICE_ENDPOINT_ADDR, buf, timeout=DEVICE_READ_TIMEOUT)
        except usb.core.USBError as err:
            self.logger.warning('read: USBError - %s', err)
            return None
        except:
            self.logger.warning('read: Unknown error - %s', sys.exc_info()[0])
            return None

        if not result or len(result) < buf:
            self.logger.warning('read: device read failed result: %d', result)
            return None

        return list(result)

if __name__ == '__main__':
    print "USB devices"
    print usb.core.show_devices()

    print "Opening weather station"
    h = Device()
    h.preamble([0xa1, 0x0, 0x0, 0x20, 0xa1, 0x0, 0x0, 0x20])
    print ' '.join('%02x' % b for b in h.read(0x20))

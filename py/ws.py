#!/usr/local/bin/python

import logging
from datetime import datetime
import util
import dev
import json
import threading
import sys

__author__ = 'mm'

E2PROM_START_ADDRESS = 0x00
E2PROM_START_VARIABLE = 0x100
E2PROM_END_ADDRESS = 0x10000
E2PROM_WRITE = 0xa0
E2PROM_READ = 0xa1
E2PROM_NONE = 0x00
E2PROM_END = 0x20
E2PROM_OFFSET = 0x100
E2PROM_CHUNK = 0x20
E2PROM_CHUNK_HALF = 0x10
E2PROM_CHUNK_START = 0x00


class E2PROM:
    def __init__(self):
        self.device = dev.Device()
        self.lock = threading.Lock()

    def read(self, address, offset):
        self.lock.acquire()

        cmd = [E2PROM_READ, address / E2PROM_OFFSET, address % E2PROM_OFFSET, E2PROM_END,
               E2PROM_READ, E2PROM_NONE, E2PROM_NONE, E2PROM_END]

        bfr = []
        # data from device are read in E2PROM_CHUNKS by 8 bytes (or less)
        offset = E2PROM_CHUNK if offset < E2PROM_CHUNK else offset

        chunks = offset / E2PROM_CHUNK

        try:
            for ind in range(chunks):
                if not self.device.preamble(cmd):
                    bfr = None
                    break
                res = self.device.read(E2PROM_CHUNK)
                if res is None:
                    bfr = None
                    break
                bfr += res
                address += E2PROM_CHUNK
                cmd[1] = address / E2PROM_OFFSET  # update high address to next position
                cmd[2] = address % E2PROM_OFFSET  # update low address to next position
        finally:
            self.lock.release()
            return bfr


class WS:
    def __init__(self):
        self.logger = logging.getLogger('WS1080.WS')
        self.logger.debug('init')

        self.E2PROM = E2PROM()
        self.dataDef = self.E2PROM.read(E2PROM_START_ADDRESS, E2PROM_OFFSET)
        if self.dataDef is None:
            self.logger.warning("WS init: dataDef is None, terminating...")
            sys.exit(1)
        self.fixedPar = util.parse_data_def(self.dataDef)
        if self.fixedPar is None:
            self.logger.warning("WS init: fixedPar is None, Length: %d terminating...", len(self.dataDef))
            sys.exit(1)

    def _get(self, address):
        if address + E2PROM_CHUNK > E2PROM_END_ADDRESS:
            self.logger.warning("_get: wrong address: %d, returning None", address)
            return None, None

        tmp = self.E2PROM.read(address, E2PROM_CHUNK)
        if tmp is None:
            return None

        # return 2 records, 16 bytes each, Weather station history
        return tmp[E2PROM_CHUNK_START:E2PROM_CHUNK_HALF], tmp[E2PROM_CHUNK_HALF:E2PROM_CHUNK]

    def get_read_period(self):
        return self.fixedPar['state']['read_Period']

    def read(self):
        data_def = self.E2PROM.read(E2PROM_START_ADDRESS, E2PROM_OFFSET)
        if data_def is None:
            self.logger.warning("read: data_def is None, returning None")
            return None

        fixed_data = util.parse_data_def(data_def)

        if fixed_data is None:
            if len(data_def) > 1:
                self.logger.warning("read: wrong fixed data, length: %d, [0]: %x [1]: %x, returning None",
                                    len(data_def), data_def[0], data_def[1])
            elif len(data_def) > 0:
                self.logger.warning("read: wrong fixed data, length: %d, [0]: %x, returning None",
                                    len(data_def), data_def[0])
            else:
                self.logger.warning("read: wrong fixed data, returning None")

            return None

        if ((fixed_data['state']['current_pos'] > E2PROM_END_ADDRESS) or
                (fixed_data['state']['current_pos'] < E2PROM_START_VARIABLE) or
                (fixed_data['state']['current_pos'] % E2PROM_CHUNK_HALF != 0)):
            self.logger.warning("read: wrong cursor value %d, returning None", fixed_data['state']['current_pos'])
            self.logger.warning("read: previous cursor value %d", self.fixedPar['state']['current_pos'])
            return None

        if self.fixedPar['state']['current_pos'] != fixed_data['state']['current_pos']:
            old_pos = self.fixedPar['state']['current_pos']
            self.dataDef = data_def
            self.fixedPar = fixed_data

            if ((fixed_data['state']['current_pos'] - old_pos > E2PROM_CHUNK_HALF) or
                (fixed_data['state']['current_pos'] == E2PROM_START_VARIABLE and
                 old_pos != E2PROM_END_ADDRESS - E2PROM_CHUNK_HALF)):
                self.logger.warning('New pos (%d) distance not correct, previous pos (%d)',
                                    fixed_data['state']['current_pos'],
                                    self.fixedPar['state']['current_pos'])
                return None

        cursor = self.fixedPar['state']['current_pos']

        if cursor < (E2PROM_END_ADDRESS - E2PROM_CHUNK_HALF):
            buf1, buf2 = self._get(cursor)
            if buf1 is None or buf2 is None:
                self.logger.warning("read: _get (1) returned None, cursor: %d, returning None", cursor)
                return None
            rec = util.parse_ws_record(buf1)
        else:
            cursor -= E2PROM_CHUNK_HALF
            self.logger.info('get_current_record: buffer end (%d)', cursor)
            buf1, buf2 = self._get(cursor)
            if buf1 is None or buf2 is None:
                self.logger.warning("read: _get (2) returned None, cursor: %d, returning None", cursor)
                return None
            rec = util.parse_ws_record(buf2)

        ts = datetime.now()
        rec['time_str'] = ts.isoformat()
        rec['time'] = util.msecs(ts)
        rec['cursor'] = cursor

        return rec

if __name__ == '__main__':
    weather_stn = WS()
    print json.dumps(weather_stn.read(), indent=4, separators=(',', ': '))

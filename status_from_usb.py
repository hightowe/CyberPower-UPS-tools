#!/usr/bin/python3

# Pulled from here on 03/17/2026 and ported to Ubuntu 24.04 by hightowe:
# https://github.com/bjonnh/cyberpower-usb-watcher/blob/master/usb.py

#  Copyright 2019 Jonathan Bisson
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import hid    # python3-hid
import json

class CyberPower:
    device = None
    def __init__(self, device):
        self.device = device

    def dict_status(self):
        return {
            "load_pct": self.load(),
            "vin": self.vin(),
            "vout": self.vout(),
            "test": self.test(),
            "capacity": self.capacity(),
            "batterytype": self.batterytype(),
            "manufacturer": self.manufacturer(),
            "product": self.product(),
            "firmware": self.firmware(),
            "Watts": self.watts(),
            "VA": self.va(),
            "last_test": self.last_test_result(),
            "last_event_raw": self.last_event(),
            **self.battery_runtime(),
            **self.get_ups_status(),
            }

    def last_test_result(self):
        # Report 0x14 is 'Test'. 
        # Usually: 1=Done, 2=Passed, 3=Failed, 4=In Progress, 5=Aborted
        data = self.device.get_feature_report(0x14, 2)
        results = {1: "Done", 2: "Passed", 3: "Failed", 4: "In Progress", 5: "Aborted", 6: "Manual"}
        return results.get(data[1], "Unknown")

    def last_event(self):
        # This pulls the buffered event data. 
        # We strip null bytes to get the clean string.
        raw_event = self.device.get_feature_report(0x1c, 64)
        event_str = "".join(chr(b) for b in raw_event[1:] if 31 < b < 127).strip()
        return event_str if event_str else "No recent events"

    def iname(self):
        return self.device.get_feature_report(0x01,8)[1]

    def load(self):
        return self.device.get_feature_report(0x13,2)[1]
    def vout(self):
        return self.device.get_feature_report(0x12,3)[1]
    def vin(self):
        return self.device.get_feature_report(0x0f,3)[1]
    def test(self):
        return self.device.get_feature_report(0x14,2)[1]
    def battery_runtime(self):
        report = self.device.get_feature_report(0x08,6)
        return {"runtime":int((report[3]*256+report[2])/60),
                "battery": report[1]}

    def capacity(self):
        report = self.device.get_feature_report(0x18,6)
        return (report[2]*256+report[1])

    def product(self):
        return self.device.get_indexed_string(self.iname())

    def firmware(self):
        return self.device.get_indexed_string(2)

    def manufacturer(self):
        return self.device.get_indexed_string(3)

    def batterytype(self):
        return self.device.get_indexed_string(4)

    def watts(self):
        # Report ID 0x19: Active Power (Watts)
        data = self.device.get_feature_report(0x19, 3)
        return data[1] + (data[2] << 8)

    def va(self):
        # Report ID 0x1d: Apparent Power (VA)
        data = self.device.get_feature_report(0x1d, 3)
        return data[1] + (data[2] << 8)

    def get_ups_status(self):
      # Get Report 0x0b (Status bits)
      data = self.device.get_feature_report(0x0b, 2)
      bits = data[1]
      return {
        "on_ac":         bool(bits & 0x01), # Bit 0
        "charging":      bool(bits & 0x02), # Bit 1
        "discharging":   bool(bits & 0x04), # Bit 2
        "battery_low":   bool(bits & 0x08), # Bit 3
        "fully_charged": bool(bits & 0x10), # Bit 4
        "timer_valid":   bool(bits & 0x20)  # Bit 5 (Your "overtimelimit")
      }

    def quick_status(self):
        read = self.device.read(1024)
        return {"battery": read[1], "runtime": int((read[3]*256+read[2])/60)}

def main():
    VENDOR_ID = 0x0764
    PRODUCT_ID = 0x0501
    device_list = hid.enumerate(VENDOR_ID, PRODUCT_ID)
    for device_item in device_list:
      device = hid.device()
      try:
        device.open_path(device_item['path'])

        ups = CyberPower(device)
        # This crashes the hid library because some of these devices have no serial...
        #print("Serial Number: {}".format(device.))
        #print(ups.dict_status())
        status_data = ups.dict_status()
        # indent=4 makes it "pretty", sort_keys keeps it consistent
        pretty_json = json.dumps(status_data, indent=4, sort_keys=True)
        print(pretty_json)
      except Exception as e:
        print(f"Error: {e}")
      finally:
        # If you just need the remaining time and battery charge
        # print(ups.quick_status())
        device.close()


if __name__ == "__main__":
    main()

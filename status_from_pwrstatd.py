#!/usr/bin/python3

######################################################################
# A program to pull the current status of a CyberPower UPS from the
# pwrstatd program (CyberPower PowerPanel) and dump it as JSON, to
# allow for things like this:
#
# $ ./status_from_pwrstatd.py | \
#     jq '{ac_present: .ac_present,
#         utility_volt: (.utility_volt | tonumber / 1000) }'
# {
#   "ac_present": "yes",
#   "utility_volt": 117
# }
#
# $ ./status_from_pwrstatd.py | jq '(.battery_remainingtime | tonumber / 60)'
# 76
#
# Note that pwrstatd keeps its state data in /var/pwrstatd.dev.
######################################################################

import socket    # core
import json      # core

def get_pwrstatd_data():
    try:
        # Connect a Unix socket to pwrstatd's IPC socket
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect("/var/pwrstatd.ipc")
        # Send the STATUS command and receive the response
        client.sendall(b"STATUS\n\n")
        response = client.recv(4096).decode('utf-8')
        # Close the socket
        client.close()

        # Parse the newline-separated response into a dictionary
        data = {}
        for line in response.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                data[key] = value
        # Return the data
        return data
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
  status_data=get_pwrstatd_data()
  pretty_json = json.dumps(status_data, indent=4, sort_keys=False)
  print(pretty_json)



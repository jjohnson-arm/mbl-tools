#!/usr/bin/env python3

# Copyright (c) 2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Parse LAVA results."""

import lavaResultExtract as lRE
from os import environ
import sys
import xmlrpc.client


def main():
    """Perform the main execution."""

    try:
        server = lRE.connect_to_server(
            environ["LAVA_SERVER"], environ["LAVA_USER"], environ["LAVA_TOKEN"]
        )
    except KeyError as key:
        print("ERROR: unset environment variable - {}".format(key))
        exit(2)

    # Find results from jobs submitted by mbl and containing the provided build tag

    allDevices = server.scheduler.all_device_types()

    try:
        current_queues = server.scheduler.pending_jobs_by_device_type()
    except xmlrpc.client.ProtocolError as e:
        current_queues = None

    print("<head>")
    print("<style>")
    print("table, th, td {")
    print("border: 1px solid black;")
    print("border-collapse: collapse;")
    print("}")
    print("</style>")
    print("</head>")
    print("<body>")
    print("<table>")
    print('<col width="250">')
    print('<col width="40">')
    print('<col width="40">')
    print('<col width="40">')
    print('<col width="40">')
    print('<col width="40">')
    print(
        "<tr> \
        <th>Device Type</th> \
        <th>Total</th> \
        <th>Busy</th> \
        <th>Idle</th> \
        <th>Offline</th> \
        <th>Queue</th> \
        </tr>\n"
    )

    for device in allDevices:
        numIdle = device["idle"]
        numBusy = device["busy"]
        numOffline = device["offline"]
        total = numIdle + numBusy + numOffline

        if numOffline == 0:
            numOffline = ""

        if current_queues != None:
            numQueue = current_queues[device["name"]]
        else:
            numQueue = 0

        if numQueue == 0:
            numQueue = ""

        if numIdle == 0:
            numIdle = ""

        if numBusy == 0:
            numBusy = ""

        name = '{}<br>'.format(device["name"])

        print(
            "<tr><td>{:>23}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><tr>".format(
                name, total, numBusy, numIdle, numOffline, numQueue
            )
        )

    print(
        "<tr> \
        <th></th> \
        <th></th> \
        <th>Busy</th> \
        <th></th> \
        <th>Offline</th> \
        <th>Queue</th> \
        </tr>\n"
    )
    print("</table>")

    print("</body>")


if __name__ == "__main__":
    sys.exit(main())

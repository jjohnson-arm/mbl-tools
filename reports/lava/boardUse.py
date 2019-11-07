#!/usr/bin/env python3

# Copyright (c) 2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Parse LAVA results."""

import lavaResultExtract as lRE
from os import environ
import sys
import xmlrpc.client

HTML_HEADER = """
<head>
<style>
body { background-color: black; }
table, th, td {
    border:1px solid #669999;
    border-collapse: collapse;
    font-size: 1.3vw; /* Default size (jobs/tests) */
    font-family: Arial, Helvetica, sans-serif;
    font-weight: bold;
    padding:5px;
    border-bottom:3px solid #669999;
    background-color:#f2f2f2;
}
table { min-width: 100%; }
th { color:#353531; }
.backamber  { background-color:#cc7a00; color:#fff; }
.backred    { background-color:#8b0000; color:#fff; }
.backgreen  { background-color:#006400; color:#fff; }
.backgrey   { background-color:#808080; color:#fff; }
.textbuild  { font-size: 2vw; } /* Build job header size */
.textboard  { font-size: 0.9vw; } /* Board results size */
.texttime   { float: right; font-size: 0.8vw; color:#fff }
.textkey    { background-color:#000; color:#fff; font-size: 0.9vw; }
.textred    { color: #e60000; text-align: right; }
.textamber  { color: #e68a00; text-align: right; }
.textgreen  { color: #009900; text-align: right; }
.textblack  { color: #353531; text-align: right; }
.row { display: flex; }
.column { flex: 50%; }
a:link { text-decoration: none; color:#fff; }
a:visited { text-decoration: none; color:#fff; }
a:hover { text-decoration: underline; }
a:active { text-decoration: underline; }
</style>
</head>
<body>
"""


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

    print(HTML_HEADER)

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

        name = "{}<br>".format(device["name"])

        print(
            "<tr><td>{:>23}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><tr>".format(
                name, total, numBusy, numIdle, numOffline, numQueue
            )
        )

    print("</table>")

    print("</body>")


if __name__ == "__main__":
    sys.exit(main())

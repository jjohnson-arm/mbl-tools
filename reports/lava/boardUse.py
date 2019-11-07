#!/usr/bin/env python3

# Copyright (c) 2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Parse LAVA results."""

import argparse
import lavaResultExtract as lRE
from os import environ
import pickle
import sys

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

HTML_FOOTER = """
</body>
"""

HELP_TEXT = """Lava farm status report generator.
Requires the following environment variables to be set:
  LAVA_SERVER - hostname of the server
  LAVA_USER   - username of login to server
  LAVA_TOKEN  - token used by username to login to server
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

    parser = argparse.ArgumentParser(
        description=HELP_TEXT, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--pickle",
        type=str,
        default="lava-farm-status.pkl",
        nargs=None,
        help="Name of pickle file that contains previous/current status",
    )
    args = parser.parse_args()

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

    try:
        lastStats = pickle.load(open(args.pickle,"rb"))
    except FileNotFoundError:
        lastStats = []

    stats = []

    for device in allDevices:
        numIdle = device["idle"]
        numBusy = device["busy"]
        numOffline = device["offline"]
        total = numIdle + numBusy + numOffline

        if current_queues != None:
            numQueue = current_queues[device["name"]]
        else:
            numQueue = 0

        stats.append([{"name" : device["name"]},{"total":total},{"busy":numBusy},{"idle":numIdle},{"offline":numOffline},{"queue":numQueue}])


        if numOffline == 0:
            numOffline = ""

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

    print(HTML_FOOTER)

    print(lastStats)
    print(stats)
    pickle.dump(stats, open(args.pickle, "wb"))

def compare_runs(runs, value, board=None):
    """Compare a value between runs and return indication of better/worse.

    :return: HTML symbol to indicate status.

    """
    if "Previous" in runs:
        if board:
            last = runs["Last"]["Boards"][board][value]
            prev = runs["Previous"]["Boards"][board][value]
        else:
            last = runs["Last"]["Totals"][value]
            prev = runs["Previous"]["Totals"][value]
        if last > prev:
            return "&uArr; "
        elif last < prev:
            return "&dArr; "
        else:
            return "&equals; "
    else:
        return ""


if __name__ == "__main__":
    sys.exit(main())

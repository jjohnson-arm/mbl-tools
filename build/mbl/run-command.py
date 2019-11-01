#!/usr/bin/env python3

# Copyright (c) 2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Script to run a Bash command inside the MBL build environment"""

import argparse
import sys

import file_util
from bitbake_util import Bitbake

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--builddir",
        metavar="DIR",
        type=file_util.str_to_resolved_path,
        help="directory in which to build",
        required=True,
    )
    parser.add_argument(
        "--machine", metavar="STRING", help="Machine to build.", required=True
    )
    parser.add_argument(
        "--distro",
        metavar="STRING",
        help="Name of the distro to build.",
        default="mbl-development",
        required=False,
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--command",
        metavar="STRING",
        help="Bash command to run in build environment.",
        required=True,
    )

    args, _ = parser.parse_known_args()
    file_util.ensure_is_directory(args.builddir)
    return args

def main():
    """Script entry point."""
    args = _parse_args()

    # Set up the BitBake environemnt
    bitbake = Bitbake(
        builddir=args.builddir, machine=args.machine, distro=args.distro
    )
    bitbake.setup_environment(verbose=args.verbose)
    bitbake.run_command(args.command, verbose=args.verbose)
    status = bitbake.run_command("echo $?", stdout=args.verbose, verbose=args.verbose).strip()
    if not status.isdigit():
        print("Failed to determine exit status of command", file=sys.stderr)
        return 1
    return int(status)


if __name__ == "__main__":
    sys.exit(main())

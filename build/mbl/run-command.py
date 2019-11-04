#!/usr/bin/env python3

# Copyright (c) 2019, Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Script to run a Bash command inside the MBL build environment"""

import argparse
import os

import file_util


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

    os.chdir(str(args.builddir))
    os.environ["MACHINE"] = args.machine
    os.environ["DISTRO"] = args.distro
    os.execlp(
        "bash",
        "bash",
        "-c",
        "source setup-environment; {}".format(args.command),
    )


if __name__ == "__main__":
    main()

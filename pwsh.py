# Copyright (C) 2025 originalFactor
#
# This file is part of autouploader.
#
# autouploader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# autouploader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with autouploader.  If not, see <https://www.gnu.org/licenses/>.

"""
Powershell calling functions
"""

import asyncio
import os
import random
import string
from collections.abc import Iterable
from typing import Any
from globals import SCRIPT_DIR
from shutil import which

if not which("pwsh"):
    raise Exception("Powershell 7 not found. You should install it first.")


def flatten(obj: Iterable) -> list[Any]:
    result = []
    for item in obj:
        if isinstance(item, Iterable):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


async def pwsh_run(*commands) -> str:
    proc = await asyncio.create_subprocess_exec(
        "pwsh",
        "-Command",
        " ".join(map(str, flatten(commands))),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise Exception(stderr.decode("gbk"))
    if len(stderr):
        print("Powershell STDERR: ", stderr.decode("gbk"))
    return stdout.decode("gbk")


async def pwsh_md5(file: str) -> str:
    md5 = (
        (await pwsh_run(f'Get-FileHash -Path "{file}" -Algorithm MD5'))
        .split()[-2]
        .lower()
    )
    print(f"MD5 of {file}: {md5}")
    return md5


async def pwsh_splitfile(file: str, size: int) -> tuple[str, list]:
    directory, filename = os.path.split(file)
    for _ in range(10):
        tmp_dir = os.path.join(
            directory, "".join(random.choices(string.hexdigits, k=8))
        )
        if not os.path.isdir(tmp_dir):
            break
    else:
        raise Exception("Cannot find a unused folder name")

    await pwsh_run(
        f'{os.path.join(SCRIPT_DIR, "splitfile.ps1")} -File "{file}" -ChunkSize {size} -Output "{tmp_dir}"'
    )

    return tmp_dir, [os.path.join(tmp_dir, i) for i in os.listdir(tmp_dir)]


async def pwsh_rmdir(dir: str):
    await pwsh_run(f"Remove-Item -Path {dir} -Recurse -Force")

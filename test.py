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

from asyncio import create_subprocess_exec, subprocess, run


async def pwsh_md5(file: str) -> str:
    proc = await create_subprocess_exec(
        "pwsh",
        "-Command",
        f'Get-FileHash -Path "{file}" -Algorithm MD5',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise Exception(stderr.decode("gbk"))
    print(stdout.decode("gbk").split()[-2])


if __name__ == "__main__":
    run(pwsh_md5("Pipfile.lock"))

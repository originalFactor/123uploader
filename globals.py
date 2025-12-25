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

from os.path import dirname, abspath
import sys

SCRIPT_DIR = dirname(abspath(__file__))
if getattr(sys, "frozen", False):  # 检查是否为打包后的环境
    CURR_DIR = dirname(abspath(sys.executable))  # 返回 .exe 文件所在目录
else:
    CURR_DIR = SCRIPT_DIR

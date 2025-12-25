<!--
 Copyright (C) 2025 originalFactor

 This file is part of autouploader.

 autouploader is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 autouploader is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with autouploader.  If not, see <https://www.gnu.org/licenses/>.
-->

# 123Uploader

Add a `config.json` file in the same directory as the executable.

```json
{
  "123ClientId": "xxx",
  "123ClientSecret": "xxx"
}
```

Apply it here: https://www.123pan.com/developer
You should receive these two values in your email.

Then run

```bash
python pan.py <local_file_path> <remote_file_path>
```

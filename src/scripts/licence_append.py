"""
Copyright (C) 2023 William Redding - All Rights Reserved

Script to append the licence to the end of every python source file if not already there

See end of file for licence details
"""

import os

LICENCE_PREAMBLE = """
\"\"\"
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
\"\"\""""

if __name__ == "__main__":
    root = os.getcwd()
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.endswith(".py"):
                with open(os.path.join(path, name), "r+", encoding="utf-8") as f:
                    if LICENCE_PREAMBLE not in f.read():
                        f.write(LICENCE_PREAMBLE)
                        print(f"Licence added to {name}")

"""
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

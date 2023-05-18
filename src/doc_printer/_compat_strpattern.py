import re
import sys
from typing_extensions import TypeAlias


if sys.version_info < (3, 9):
    StrPattern: TypeAlias = re.Pattern
else:
    StrPattern: TypeAlias = re.Pattern[str]

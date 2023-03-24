import os
import sys

test1 = sys.path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)

test = sys.path

import data_storage

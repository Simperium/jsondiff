import sys
import inspect
import unittest

def noop( something ):
    pass

__builtins__['reload'] = noop

from diffmatchpatch.diff_match_patch_test import *

if __name__ == '__main__':
    unittest.main()

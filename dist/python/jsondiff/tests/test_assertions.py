import unittest
import simplejson
import os.path

from jsondiff import diff
from jsondiff import equals


class AssertionsTests(unittest.TestCase):
    """
    process the list of common assertions all clients should implement
    """
    def test_assertions(self):
        assertions = simplejson.load(open(os.path.join(
            os.path.dirname(__file__), '../../../../src/test/assertions.json')))

        for method, args, expected, description in assertions:
            method = {
                'diff': diff,
            }[method]
            got = method(*args)
            if not equals(got, expected):
                print
                print "Exception coming..."
                print
                print "\texpected", simplejson.dumps(expected)
                print "\tgot", simplejson.dumps(got)

            self.assertTrue(equals(got, expected))


if __name__ == '__main__':
    unittest.main()

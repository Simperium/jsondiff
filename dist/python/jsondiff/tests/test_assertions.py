import unittest
import simplejson
import os.path

from jsondiff import diff
from jsondiff import applydiff
from jsondiff import equals


class AssertionsTests(unittest.TestCase):
    """
    process the list of common assertions all clients should implement
    """
    def test_assertions(self):
        assertions = simplejson.load(open(os.path.join(
            os.path.dirname(__file__), '../../../../src/test/assertions.json')))

        def run_assertion(method, description, args, expected):
            description = method + ': ' + description
            method = {
                'diff': diff,
                'applydiff': applydiff,
            }[method]
            got = method(*args)
            if not equals(got, expected):
                print
                print "Exception coming..."
                print
                print "\tdescription", description
                print "\texpected", simplejson.dumps(expected)
                print "\tgot", simplejson.dumps(got)
            self.assertTrue(equals(got, expected))

        for method, description, args, expected, in assertions:
            run_assertion(method, description, args, expected)
            if method == 'diff':
                # generate applydiff tests from diff tests
                original, target = args
                run_assertion(
                    'applydiff', description, [original, expected['v']], target)


if __name__ == '__main__':
    unittest.main()

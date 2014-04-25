import unittest
import simplejson
import os.path

from jsondiff import diff
from jsondiff import apply_diff
from jsondiff import equals
from jsondiff import transform_object_diff


class AssertionsTests(unittest.TestCase):
    """
    process the list of common assertions all clients should implement
    """
    def test_assertions(self):
        assertions = simplejson.load(open(os.path.join(
            os.path.dirname(__file__), '../../../../src/test/assertions.json')))

        def run_assertion(method, description, args, expected):
            description = method + ': ' + description
            print
            print "Running", description, method
            methods = {
                'diff': diff,
                'apply_diff': apply_diff,
                'transform': transform_object_diff
            }
            if method in methods:
                method = methods[method]
            else:
                return True

            if method is transform_object_diff:
                if len(args) == 3:
                    original, obja, objb = args
                    policy = None
                else:
                    original, obja, objb, policy = args
                diffa = diff(original, obja, policy)['v']
                diffb = diff(original, objb, policy)['v']
                tdiff = transform_object_diff(diffa, diffb, original, policy)
                intermediate = apply_diff(original, diffb)
                method = apply_diff
                args = [intermediate, tdiff]

            got = method(*args)
            if not equals(got, expected):
                print
                print "Exception coming..."
                print
                print "\tdescription", description
                print "\tgot", simplejson.dumps(got)
                print "\texp", simplejson.dumps(expected)
            return equals(got, expected)
#            self.assertTrue(equals(got, expected))

        for method, description, args, expected, in assertions:
            ok = run_assertion(method, description, args, expected)
            if method == 'diff':
                # generate apply_diff tests from diff tests
                if len(args) == 2:
                    original, target = args
                    policy = None
                else:
                    original, target, policy = args
                if ok:
                    run_assertion(
                        'apply_diff', description+", doing apply", [original, expected['v']], target)

    def test_transform(self):
        """(andy) just trying to work out transforms. i don't think i've
        quite got it yet, fred just committing this to have something to chat
        through with you.
        """
        # odiff = {"a": {"o": "r", "v": 7}}
        odiff = {"e": {"o": "+", "v": "y"}}
        o = {"a":"b"}
        diff = {"e": {"o": "+", "v": "d"}}
        print "FROAR", transform_object_diff(diff, odiff, o)


if __name__ == '__main__':
    unittest.main()

import unittest

from jsondiff import *

class DifferTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_prefix(self):
        a = ['a', 'b', 'c']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(common_prefix(a,b), 3)
        b[1] = 'x'
        self.assertEqual(common_prefix(a,b), 1)
        self.assertEqual(common_prefix(a,[]), 0)
        self.assertEqual(common_prefix([],b), 0)

    def test_suffix(self):
        a = ['a', 'b', 'c', 'd']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(common_suffix(a,b), 4)
        b[1] = 'x'
        self.assertEqual(common_suffix(a,b), 2)
        self.assertEqual(common_suffix(a,[]), 0)
        self.assertEqual(common_suffix([],a), 0)

    def test_object_equals(self):
        a = {'a':'b', 'c':'d', 'q':5, 'x':'test'}
        b = {'a':'b', 'c':'d', 'q':5, 'x':'test'}
        self.assertTrue(object_equals(a, b))
        b['a'] = 'c'
        self.assertFalse(object_equals(a, b))
        b['a'] = 'b'
        b['new'] = 'test'
        self.assertFalse(object_equals(a, b))
        a['new'] = 'test'
        self.assertTrue(object_equals(a, b))

    def test_list_equals(self):
        a = ['1', '2', '3', '4']
        b = ['1', '2', '3', '4']
        self.assertTrue(list_equals(a, b))
        b[0] = '0'
        self.assertFalse(list_equals(a, b))
        b[0] = 1
        self.assertFalse(list_equals(a, b))

    def test_list_diff(self):
        a = ['a', 'b', 'c', 'd', 'e']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(apply_list_diff(a, list_diff(a, b)), b)

        a = ['a', 'b', 'x', 'c', 'd']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(apply_list_diff(a, list_diff(a, b)), b)

        a = ['1', '2', '3', '4', 'd']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(apply_list_diff(a, list_diff(a, b)), b)

        a = ['a', 'b', 'c', 'd', 'e']
        b = ['a', 'b', 'q', 'c', 't', 'd', 'e']
        self.assertEqual(apply_list_diff(a, list_diff(a, b)), b)

        a = ['a', 'b', 'c', 'd', 'e', 's']
        b = ['a', 'b', 'q', 'c', 't', 'd', 'e', 's']
        self.assertEqual(apply_list_diff(a, list_diff(a, b)), b)

        a = ['a', 'b', 'q', 'c', 't', 'd', 'e', 's']
        b = ['a', 'b', 'c', 'd', 'e', 's']
        self.assertEqual(apply_list_diff(a, list_diff(a, b)), b)

        a = ['a', 'b', 'x', 'q', 'd', 'e']
        b = ['a', 'b', 'c']
        self.assertEqual(apply_list_diff(a, list_diff(a, b)), b)

    def test_object_diffs(self):
        a = {'test':['a', 'b', 'c'], 'blah':{'hi':'test'}, 'num':50}
        b = {'test':['a', 'b'], 'blah':{'hi':'there'}, 'num':51}
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        a = {'test':['a', 'b', 'c'], 'blah':{'hi':'test'}, 'num':50}
        b = {'blah':{'hi':'there'}, 'num':-10, 'new':{'list':['a', 'b', 'c']}}
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        a = {'test':['a', 'b', 'c'], 'blah':{'hi':'test'}, 'num':-100, 'new':{'list':['a', 'x'], 'delete':'this'}}
        b = {'blah':{'hi':'there'}, 'num':-10, 'new':{'list':['a', 'b', 'c']}}
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))


if __name__ == '__main__':
    unittest.main()

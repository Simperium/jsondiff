import unittest

from jsondiff import *

class DifferTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_prefix(self):
        a = ['a', 'b', 'c']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(commonprefix(a,b), 3)
        b[1] = 'x'
        self.assertEqual(commonprefix(a,b), 1)
        self.assertEqual(commonprefix(a,[]), 0)
        self.assertEqual(commonprefix([],b), 0)

    def test_suffix(self):
        a = ['a', 'b', 'c', 'd']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(commonsuffix(a,b), 4)
        b[1] = 'x'
        self.assertEqual(commonsuffix(a,b), 2)
        self.assertEqual(commonsuffix(a,[]), 0)
        self.assertEqual(commonsuffix([],a), 0)

    def test_objequals(self):
        a = {'a':'b', 'c':'d', 'q':5, 'x':'test'}
        b = {'a':'b', 'c':'d', 'q':5, 'x':'test'}
        self.assertTrue(objequals(a, b))
        b['a'] = 'c'
        self.assertFalse(objequals(a, b))
        b['a'] = 'b'
        b['new'] = 'test'
        self.assertFalse(objequals(a, b))
        a['new'] = 'test'
        self.assertTrue(objequals(a, b))

    def test_listequals(self):
        a = ['1', '2', '3', '4']
        b = ['1', '2', '3', '4']
        self.assertTrue(listequals(a, b))
        b[0] = '0'
        self.assertFalse(listequals(a, b))
        b[0] = 1
        self.assertFalse(listequals(a, b))

    def test_listdiffs2(self):
        a = ['a', 'b', 'c', 'd', 'e']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(applylistdiff2(a, listdiff2(a, b)), b)

        a = ['a', 'b', 'x', 'c', 'd']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(applylistdiff2(a, listdiff2(a, b)), b)

        a = ['1', '2', '3', '4', 'd']
        b = ['a', 'b', 'c', 'd']
        self.assertEqual(applylistdiff2(a, listdiff2(a, b)), b)

        a = ['a', 'b', 'c', 'd', 'e']
        b = ['a', 'b', 'q', 'c', 't', 'd', 'e']
        self.assertEqual(applylistdiff2(a, listdiff2(a, b)), b)

        a = ['a', 'b', 'c', 'd', 'e', 's']
        b = ['a', 'b', 'q', 'c', 't', 'd', 'e', 's']
        self.assertEqual(applylistdiff2(a, listdiff2(a, b)), b)

        a = ['a', 'b', 'q', 'c', 't', 'd', 'e', 's']
        b = ['a', 'b', 'c', 'd', 'e', 's']
        self.assertEqual(applylistdiff2(a, listdiff2(a, b)), b)

        a = ['a', 'b', 'x', 'q', 'd', 'e']
        b = ['a', 'b', 'c']
        self.assertEqual(applylistdiff2(a, listdiff2(a, b)), b)

    def test_objdiffs2(self):
        a = {'test':['a', 'b', 'c'], 'blah':{'hi':'test'}, 'num':50}
        b = {'test':['a', 'b'], 'blah':{'hi':'there'}, 'num':51}
        self.assertTrue(objequals(b, applyobjdiff2(a, objdiff2(a, b))))

        a = {'test':['a', 'b', 'c'], 'blah':{'hi':'test'}, 'num':50}
        b = {'blah':{'hi':'there'}, 'num':-10, 'new':{'list':['a', 'b', 'c']}}
        self.assertTrue(objequals(b, applyobjdiff2(a, objdiff2(a, b))))

        a = {'test':['a', 'b', 'c'], 'blah':{'hi':'test'}, 'num':-100, 'new':{'list':['a', 'x'], 'delete':'this'}}
        b = {'blah':{'hi':'there'}, 'num':-10, 'new':{'list':['a', 'b', 'c']}}
        self.assertTrue(objequals(b, applyobjdiff2(a, objdiff2(a, b))))

if __name__ == '__main__':
    unittest.main()

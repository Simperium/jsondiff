import unittest

from jsondiff import *

class DifferTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_emoji(self):
        # insert character after emoji
        # surrogate pair
        a = {"s" : u"\ud83d\udc7f"}
        b = {"s" : u"\ud83d\udc7f#"}
        expect = {"s" : {"o":"d", "v":"=2\t+#"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # real unicode code point
        a = {"s" : u"\U0001F47F"}
        b = {"s" : u"\U0001F47F#"}
        expect = {"s" : {"o":"d", "v":"=2\t+#"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # insert character before emoji
        # surrogate pair
        a = {"s" : u"\ud83d\udc7f"}
        b = {"s" : u"#\ud83d\udc7f"}
        expect = {"s" : {"o":"d", "v":"+#\t=2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # real unicode code point
        a = {"s" : u"\U0001F47F"}
        b = {"s" : u"#\U0001F47F"}
        expect = {"s" : {"o":"d", "v":"+#\t=2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # remove character after emoji
        # surrogate pair
        a = {"s" : u"\ud83d\udc7f#"}
        b = {"s" : u"\ud83d\udc7f"}
        expect = {"s" : {"o":"d", "v":"=2\t-1"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # real unicode code point
        a = {"s" : u"\U0001F47F#"}
        b = {"s" : u"\U0001F47F"}
        expect = {"s" : {"o":"d", "v":"=2\t-1"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # remove character before emoji
        # surrogate pair
        a = {"s" : u"#\ud83d\udc7f"}
        b = {"s" : u"\ud83d\udc7f"}
        expect = {"s" : {"o":"d", "v":"-1\t=2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # real unicode code point
        a = {"s" : u"#\U0001F47F"}
        b = {"s" : u"\U0001F47F"}
        expect = {"s" : {"o":"d", "v":"-1\t=2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # insert character before many emoji
        # surrogate pair
        a = {"s" : u"\ud83d\udc7fs"*5}
        b = {"s" : "#" + u"\ud83d\udc7fs"*5}
        expect = {"s" : {"o":"d", "v":"+#\t=15"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # real unicode code point
        a = {"s" : u"\U0001F47Fs"*5}
        b = {"s" : "#" + u"\U0001F47Fs"*5}
        expect = {"s" : {"o":"d", "v":"+#\t=15"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # insert character inbetween emoji
        # surrogate pair
        a = {"s" : u"\ud83d\udc7f"*2}
        b = {"s" : u"\ud83d\udc7f#\ud83d\udc7f"}
        expect = {"s" : {"o":"d", "v":"=2\t+#\t=2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # real unicode code point
        a = {"s" : u"\U0001F47F"*2}
        b = {"s" : u"\U0001F47F#\U0001F47F"}
        expect = {"s" : {"o":"d", "v":"=2\t+#\t=2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))


        # insert emoji after character
        # surrogate pair
        a = {"s" : u"#"}
        b = {"s" : u"#\ud83d\udc7f"}
        expect = {"s" : {"o":"d", "v":"=1\t+%F0%9F%91%BF"}}
        diff = object_diff(a, b)
        self.assertEqual(diff, expect)
        b['s'] = b['s'].encode( 'UTF-16' ).decode( 'UTF-16' )
        self.assertTrue(object_equals(b, apply_object_diff(a, diff)))

        # real unicode code point
        a = {"s" : u"#"}
        b = {"s" : u"#\U0001F47F"}
        expect = {"s" : {"o":"d", "v":"=1\t+%F0%9F%91%BF"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # insert emoji before character
        # surrogate pair
        a = {"s" : u"#"}
        b = {"s" : u"\ud83d\udc7f#"}
        expect = {"s" : {"o":"d", "v":"+%F0%9F%91%BF\t=1"}}
        diff = object_diff(a, b)
        self.assertEqual(diff, expect)
        b['s'] = b['s'].encode( 'UTF-16' ).decode( 'UTF-16' )
        self.assertTrue(object_equals(b, apply_object_diff(a, diff)))

        # real unicode code point
        a = {"s" : u"#"}
        b = {"s" : u"\U0001F47F#"}
        expect = {"s" : {"o":"d", "v":"+%F0%9F%91%BF\t=1"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # remove emoji after character
        # surrogate pair
        a = {"s" : u"#\ud83d\udc7f"}
        b = {"s" : u"#"}
        expect = {"s" : {"o":"d", "v":"=1\t-2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # real unicode code point
        a = {"s" : u"#\U0001F47F"}
        b = {"s" : u"#"}
        expect = {"s" : {"o":"d", "v":"=1\t-2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # remove emoji before character
        # surrogate pair
        a = {"s" : u"\ud83d\udc7f#"}
        b = {"s" : u"#"}
        expect = {"s" : {"o":"d", "v":"-2\t=1"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # real unicode code point
        a = {"s" : u"\U0001F47F#"}
        b = {"s" : u"#"}
        expect = {"s" : {"o":"d", "v":"-2\t=1"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))


        # insert emoji between emoji
        # surrogate pair
        a = {"s" : u"\ud83d\udc7f\ud83d\udc7f"}
        b = {"s" : u"\ud83d\udc7f\ud83d\ude07\ud83d\udc7f"}
        expect = {"s" : {"o":"d", "v":"=2\t+%F0%9F%98%87\t=2"}}
        diff = object_diff(a, b)
        self.assertEqual(diff, expect)
        applied = apply_object_diff(a, diff)
        b['s'] = b['s'].encode( 'UTF-16' ).decode( 'UTF-16' )
        applied['s'] = applied['s'].encode( 'UTF-16' ).decode( 'UTF-16' )
        self.assertTrue(object_equals(b, applied))

        # real unicode code point
        a = {"s" : u"\U0001F47F\U0001F47F"}
        b = {"s" : u"\U0001F47F\U0001F607\U0001F47F"}
        expect = {"s" : {"o":"d", "v":"=2\t+%F0%9F%98%87\t=2"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # swap emoji with same leading surrogate
        # surrogate pair
        a = {"s" : u"@\ud83d\ude00#"}
        b = {"s" : u"@\ud83d\ude01#"}
        expect = {"s" : {"o":"d", "v":"=1\t-2\t+%F0%9F%98%81\t=1"}}
        diff = object_diff(a, b)
        self.assertEqual(diff, expect)
        applied = apply_object_diff(a, diff)
        b['s'] = b['s'].encode( 'UTF-16' ).decode( 'UTF-16' )
        applied['s'] = applied['s'].encode( 'UTF-16' ).decode( 'UTF-16' )
        self.assertTrue(object_equals(b, applied))

        # real unicode code point
        a = {"s" : u"@\U0001F600#"}
        b = {"s" : u"@\U0001F601#"}
        expect = {"s" : {"o":"d", "v":"=1\t-2\t+%F0%9F%98%81\t=1"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

        # swap emoji with same trailing surrogate
        # surrogate pair
        a = {"s" : u"@\ud83c\ude34#"}
        b = {"s" : u"@\ud83d\ude34#"}
        expect = {"s" : {"o":"d", "v":"=1\t-2\t+%F0%9F%98%B4\t=1"}}
        diff = object_diff(a, b)
        self.assertEqual(diff, expect)
        applied = apply_object_diff(a, diff)
        b['s'] = b['s'].encode( 'UTF-16' ).decode( 'UTF-16' )
        applied['s'] = applied['s'].encode( 'UTF-16' ).decode( 'UTF-16' )
        self.assertTrue(object_equals(b, applied))

        # real unicode code point
        a = {"s" : u"@\U0001F234#"}
        b = {"s" : u"@\U0001F634#"}
        expect = {"s" : {"o":"d", "v":"=1\t-2\t+%F0%9F%98%B4\t=1"}}
        self.assertEqual(object_diff(a, b), expect)
        self.assertTrue(object_equals(b, apply_object_diff(a, object_diff(a, b))))

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

    def test_bad_transform(self):
        o = {'log' : 'Original Captains Log'}
        a = {'log' : 'Local Captains Log'}
        b = {'log' : 'Remote Captains Log'}

        a_diff = diff(o, a)['v']
        b_diff = diff(o, b)['v']

        a_prime_diff = transform_object_diff(a_diff, b_diff, o)

        ob = apply_object_diff(o, b_diff)

        self.assertTrue(object_equals(ob, b))

        oba = apply_object_diff(ob, a_prime_diff)

        self.assertFalse(object_equals(oba, ob))
        self.assertTrue(object_equals(oba, a))

if __name__ == '__main__':
    unittest.main()

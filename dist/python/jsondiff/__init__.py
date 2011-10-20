"""
jsondiff.py

Created by Fred Cheng on 2011-02-21.
Copyright (c) 2011 Simperium, Inc. All rights reserved.
"""

import sys
import os
import copy
import json

from diffmatchpatch import diff_match_patch

DMP = diff_match_patch()

def sametype(a, b):
    if (type(a) == str and type(b) == unicode) or (type(a) == unicode and type(b) == str):
        return True
    return type(a) == type(b)

def equals(a, b):
    if not sametype(a, b):
        return False
    if type(a) == list:
        return listequals(a, b)
    elif type(a) == dict:
        return objequals(a, b)
    else:
        return a == b

def commonprefix(a, b):
    maxl = min(len(a), len(b))
    for i in range(maxl):
        if not equals(a[i], b[i]):
            return i
    return maxl

def commonsuffix(a, b):
    maxl = min(len(a), len(b))
    maxa = len(a)
    maxb = len(b)
    for i in range(maxl):
        if not equals(a[maxa-i-1], b[maxb-i-1]):
            return i
    return maxl

# a = list, c = list of ops to apply to a
def applylistdiff2(a, c):
    deleted = []
    ac = copy.deepcopy(a)
    print "ac", ac
    for i,o in sorted(c.iteritems()):
        # shift i
        i = int(i)
        si = i - len(filter(lambda x: x <= i, deleted))
        sp = len(filter(lambda x: x <= i, deleted))
#       i = o['i']
        if o['o'] == '+':
            ac.insert(si, o['v'])
#           added.append(i)
            print "ac insert at %d = %s, ac is %s, si is %d" % (si, o['v'], ac, si)
        elif o['o'] == '-':
            print "ac before delete at %d, si is %d, ac %s, sp %d" % (i, si, ac, sp)
            ac.pop(si)
            deleted.append(i)
            print "ac delete at %d, ac now %s, si is %d, sp %d" % (i, ac, si, sp)
        elif o['o'] == 'r':
            ac[si] = o['v']
        elif o['o'] == 'I':
            ac[si] += o['v']
        elif o['o'] == 'L':
            ac[si] = applylistdiff2(ac[si], o['v'])
        elif o['o'] == 'O':
            ac[si] = applyobjdiff2(ac[si], o['v'])
        elif o['o'] == 'd':
            diffs = DMP.diff_fromDelta(ac[si], o['v'])
            patches = DMP.patch_make(ac[si], diffs)
            result = DMP.patch_apply(patches, ac[si])
            ac[si] = result[0]
    return ac

def listdiff2(a, b):
    c = {}
    d = {}
#   print "a", a
#   print "b", b
    cp = commonprefix(a, b)
    cs = commonsuffix(a, b)
    ca = a[cp:-cs+len(a)]
    cb = b[cp:-cs+len(b)]
#   print "cp", cp
#   print "cs", cs
#   print "ca", ca
#   print "cb", cb

    sr = 0
    smax = 0
    for i in range(len(a)/2):
        nsame = 0
        blen = min(len(a)-i, len(b))
        for j in range(blen):
            if equals(a[i+j], b[j]): nsame = nsame + 1
        if nsame > smax:
            smax = nsame
            sr = i
    print "sr", sr, "smax", smax
    if sr > 0 and smax >= len(a)/2:
        blen = max(len(a), len(b)+sr)
        for i in range(blen):
            k = str(i)
            if i < sr:
                c[k] = {'o':'-'}
            elif i < len(b) + sr and i < len(a):
                if not equals(a[i], b[i-sr]):
                    c[k] = diff(a[i], b[i-sr])
            elif i < len(b) + sr:
                c[k] = {'o':'+', 'v':b[i-sr]}
            elif i < len(a):
                c[k] = {'o':'-'}
        d = c
        c = {}

    for i in range(max(len(ca), len(cb))):
        k = str(i+cp)
#       print "i is", i
        if i < len(ca) and i < len(cb):
            if not equals(ca[i], cb[i]):
                c[k] = diff(ca[i], cb[i])
        elif i < len(ca):
            c[k] = {'o':'-'}
        elif i < len(cb):
            c[k] = {'o':'+', 'v':cb[i]}
    print "d", d
    print "c", c
    print "d len", len(d), "c len", len(c)
    if len(d) < len(c) and len(d) > 0 and len(c) > 0:
        return d
    return c

def listequals(a, b):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if not equals(a[i], b[i]):
            return False
    return True

def objequals(a, b):
    for k, v in a.iteritems():
        if k not in b:
            return False
        if not equals(v, b[k]):
            return False
    for k, v in b.iteritems():
        if k not in a:
            return False
    return True

def objdiff2(a, b):
    c = {}
    for k,v in a.iteritems():
        if k in b:
            if not equals(v, b[k]):
                c[k] = diff(v, b[k])
        else:
            c[k] = {'o':'-'}
    for k,v in b.iteritems():
        if k not in a:
            c[k] = {'o':'+', 'v':v}
    return c

def applyobjdiff2(a, c):
    ac = copy.deepcopy(a)
    for k,o in c.iteritems():
        if o['o'] == '-':
            del ac[k]
        elif o['o'] == '+':
            ac[k] = o['v']
        elif o['o'] == 'r':
            ac[k] = o['v']
        elif o['o'] == 'I':
            ac[k] += o['v']
        elif o['o'] == 'L':
            ac[k] = applylistdiff2(a[k], o['v'])
        elif o['o'] == 'O':
            ac[k] = applyobjdiff2(a[k], o['v'])
        elif o['o'] == 'd':
            diffs = DMP.diff_fromDelta(a[k], o['v'])
            patches = DMP.patch_make(a[k], diffs)
            result = DMP.patch_apply(patches, a[k])
            ac[k] = result[0]
    return ac

def transform_list(a, b, s):
    ac = {}
    b_inserts = []
    b_deletes = []
    for i, op in b.iteritems():
        if op['o'] == '+': b_inserts.append(int(i))
        if op['o'] == '-': b_deletes.append(int(i))
    for i, op in a.iteritems():
        shift_r = len(filter(lambda x: x <= int(i), b_inserts))
        shift_l = len(filter(lambda x: x <= int(i), b_deletes))
        i_t = int(i) + shift_r - shift_l

        ac[str(i_t)] = op
        if str(i_t) in b:
            if op['o'] == '+' and b[i_t]['o'] == '+':
                pass
            elif op['o'] == '-' and b[i_t]['o'] == '-':
                del ac[str(i_t)]
            else:
                ac[str(i_t)] = transform_object({str(i_t):op}, {str(i_t):b[str(i_t)]}, s)[str(i_t)]
    return ac

# diff a on S0 and diff b on S0
# return a' where T(T(S0, b), a') == T(T(S0, a), b') # not really since DMP deltas will not satisfy this property
def transform_object(a, b, s):
    ac = copy.deepcopy(a)
    for k, op in a.iteritems():
        if k in b:
            sk = None
            if type(s) == list:
                if len(s) > int(k):
                    sk = s[int(k)]
            else:
                if k in s:
                    sk = s[k]
            if op['o'] == '+' and b[k]['o'] == '+':
                if equals(b[k]['v'], op['v']):
                    del ac[k]
                else:
                    ac[k] = diff(b[k]['v'], op['v'])
            elif op['o'] == '-' and b[k]['o'] == '-':
                del ac[k]
            elif b[k]['o'] == '-' and op['o'] in ['O', 'L', 'I', 'd']:
                ac[k] = {'o':'+'}
                if op['o'] == 'O':
                    ac[k]['v'] = applyobjdiff2(sk, op['v'])
                elif op['o'] == 'L':
                    ac[k]['v'] = applylistdiff2(sk, op['v'])
                elif op['o'] == 'I':
                    ac[k]['v'] = sk + op['v']
                elif op['o'] == 'd':
                    diffs = DMP.diff_fromDelta(sk, op['v'])
                    patches = DMP.patch_make(sk, diffs)
                    result = DMP.patch_apply(patches, sk)
                    ac[k]['v'] = result[0]
            elif op['o'] == 'O' and b[k]['o'] == 'O':
                ac[k] = {'o':'O', 'v':transform_object(op['v'], b[k]['v'], sk)}
            elif op['o'] == 'L' and b[k]['o'] == 'L':
                ac[k] = {'o':'L', 'v':transform_list(op['v'], b[k]['v'], sk)}
            elif op['o'] == 'd' and b[k]['o'] == 'd':
                del ac[k]
                a_patches = DMP.patch_make(sk, DMP.diff_fromDelta(sk, op['v']))
                b_patches = DMP.patch_make(sk, DMP.diff_fromDelta(sk, b[k]['v']))
                b_text = DMP.patch_apply(b_patches, sk)[0]
                ab_text = DMP.patch_apply(a_patches, b_text)[0]
                diffs = DMP.diff_main(b_text, ab_text)
                if len(diffs) > 2:
                    DMP.diff_cleanupEfficiency(diffs)
                if len(diffs) > 0:
                    delta = DMP.diff_toDelta(diffs)
                    ac[k] = {'o':'d', 'v':delta}
        else:
            # nothing to transform
            pass
    return ac

# a = operation to transform
# changes = list of operations
# s = common object ancestor
def transform(a, changes, s):
    for change in changes:
        a = transform_object(a, change, s)
        s = applydiff(s, change)
    return a

def diff(a, b):
    if equals(a,b):
        return None
    if not sametype(a,b):
        return {'o':'r', 'v': b}
    if type(a) in [int, float, long]:
        return {'o':'r', 'v': b}
    elif type(a) == bool:
        return {'o':'r', 'v': b}
    elif type(a) == list:
        return {'o':'r', 'v': b}
    elif type(a) == dict:
        return {'o':'O', 'v':objdiff2(a,b)}
    elif type(a) in [str, unicode]:
        diffs = DMP.diff_main(a, b)
        if len(diffs) > 2:
            DMP.diff_cleanupEfficiency(diffs)
        if len(diffs) > 0:
            delta = DMP.diff_toDelta(diffs)
            return {'o':'d', 'v':delta}
    return None

# transform should work on CHANGES
# CHANGE = {'o':TYPE, 'v':VALUE}
# diffs should work on OPERATIONS?
# DIFF = {'}
def applydiff(a, ops):
    if type(a) == dict:
        return applyobjdiff2(a, ops)
    elif type(a) == list:
        return applylistdiff2(a, ops)

class differ:
    def __init__(self):
        pass

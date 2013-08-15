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

def same_type(a, b):
    if isinstance(a, basestring) and isinstance(b, basestring):
        return True
    if (type(a) == bool and type(b) == int) or (type(a) == int and type(b) == bool):
        return True
    return type(a) == type(b)

def equals(a, b):
    if not same_type(a, b):
        return False
    if type(a) == bool and type(b) == int:
        return int(a) == b
    if type(a) == int and type(b) == bool:
        return a == int(b)
    if type(a) == list:
        return list_equals(a, b)
    elif type(a) == dict:
        return object_equals(a, b)
    else:
        return a == b

def serialize_to_text(a):
    return ''.join([json.dumps(s)+'\n' for s in a])

def text_to_list(s):
    return [json.loads(e) for e in s.split('\n') if len(e)]

def list_diff_dmp(a, b, policy=None):
    atext = serialize_to_text(a)
    btext = serialize_to_text(b)

    diffs = DMP.diff_lineMode(atext, btext, 0.1)
    DMP.diff_cleanupEfficiency(diffs)
    delta = DMP.diff_toDelta(diffs)
    return delta

def apply_list_diff_dmp(s, delta):
    ptext = serialize_to_text(s)

    diffs = DMP.diff_fromDelta(ptext, delta)
    patches = DMP.patch_make(ptext, diffs)
    result = DMP.patch_apply(patches, ptext)

    return text_to_list(result[0])

def transform_list_diff_dmp(ad, bd, s, policy=None):
    stext = serialize_to_text(s)

    a_patches = DMP.patch_make(stext, DMP.diff_fromDelta(stext, ad))
    b_patches = DMP.patch_make(stext, DMP.diff_fromDelta(stext, bd))

    b_text = DMP.patch_apply(b_patches, stext)[0]
    ab_text = DMP.patch_apply(a_patches, b_text)[0]
    if ab_text != b_text:
      diffs = DMP.diff_lineMode(b_text, ab_text, 0.1)
      if len(diffs) > 2:
        DMP.diff_cleanupEfficiency(diffs)
      if len(diffs) > 0:
        return DMP.diff_toDelta(diffs)
    return ""

def common_prefix(a, b):
    maxl = min(len(a), len(b))
    for i in range(maxl):
        if not equals(a[i], b[i]):
            return i
    return maxl

def common_suffix(a, b):
    maxl = min(len(a), len(b))
    maxa = len(a)
    maxb = len(b)
    for i in range(maxl):
        if not equals(a[maxa-i-1], b[maxb-i-1]):
            return i
    return maxl

# a = list, c = list of ops to apply to a
def apply_list_diff(a, c):
    deleted = []
    ac = copy.deepcopy(a)
    for i,o in sorted(c.iteritems()):
        # shift i
        i = int(i)
        si = i - len(filter(lambda x: x <= i, deleted))
        sp = len(filter(lambda x: x <= i, deleted))
        if o['o'] == '+':
            ac.insert(si, o['v'])
        elif o['o'] == '-':
            ac.pop(si)
            deleted.append(i)
        elif o['o'] == 'r':
            ac[si] = o['v']
        elif o['o'] == 'I':
            ac[si] += o['v']
        elif o['o'] == 'L':
            ac[si] = apply_list_diff(ac[si], o['v'])
        elif o['o'] == 'dL':
            ac[si] = apply_list_diff_dmp(ac[si], o['v'])
        elif o['o'] == 'O':
            ac[si] = apply_object_diff(ac[si], o['v'])
        elif o['o'] == 'd':
            diffs = DMP.diff_fromDelta(ac[si], o['v'])
            patches = DMP.patch_make(ac[si], diffs)
            result = DMP.patch_apply(patches, ac[si])
            ac[si] = result[0]
    return ac

def list_diff(a, b, policy=None):
    if policy and 'item' in policy:
        policy = policy['item']
    else:
        policy = None

    c = {}
    d = {}
    cp = common_prefix(a, b)
    cs = common_suffix(a, b)
    ca = a[cp:-cs+len(a)]
    cb = b[cp:-cs+len(b)]

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
    if sr > 0 and smax >= len(a)/2:
        blen = max(len(a), len(b)+sr)
        for i in range(blen):
            k = str(i)
            if i < sr:
                c[k] = {'o':'-'}
            elif i < len(b) + sr and i < len(a):
                if not equals(a[i], b[i-sr]):
                    c[k] = diff(a[i], b[i-sr], policy)
            elif i < len(b) + sr:
                c[k] = {'o':'+', 'v':b[i-sr]}
            elif i < len(a):
                c[k] = {'o':'-'}
        d = c
        c = {}

    for i in range(max(len(ca), len(cb))):
        k = str(i+cp)
        if i < len(ca) and i < len(cb):
            if not equals(ca[i], cb[i]):
                c[k] = diff(ca[i], cb[i], policy)
        elif i < len(ca):
            c[k] = {'o':'-'}
        elif i < len(cb):
            c[k] = {'o':'+', 'v':cb[i]}
    if len(d) < len(c) and len(d) > 0 and len(c) > 0:
        return d
    return c

def list_equals(a, b):
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if not equals(a[i], b[i]):
            return False
    return True

def object_equals(a, b):
    for k, v in a.iteritems():
        if k not in b:
            return False
        if not equals(v, b[k]):
            return False
    for k, v in b.iteritems():
        if k not in a:
            return False
    return True

def object_diff(a, b, policy=None):
    c = {}

    if policy and 'attributes' in policy:
        policy = policy['attributes']

    for k,v in a.iteritems():
        if policy and k in policy:
            sub_policy = policy[k]
        else:
            sub_policy = None

        if k in b:
            if not equals(v, b[k]):
                c[k] = diff(v, b[k], sub_policy)
        else:
            c[k] = {'o':'-'}
    for k,v in b.iteritems():
        if k not in a:
            c[k] = {'o':'+', 'v':v}

    return c

def apply_object_diff(a, c):
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
            ac[k] = apply_list_diff(a[k], o['v'])
        elif o['o'] == 'dL':
            ac[k] = apply_list_diff_dmp(a[k], o['v'])
        elif o['o'] == 'O':
            ac[k] = apply_object_diff(a[k], o['v'])
        elif o['o'] == 'd':
            diffs = DMP.diff_fromDelta(a[k], o['v'])
            patches = DMP.patch_make(a[k], diffs)
            result = DMP.patch_apply(patches, a[k])
            ac[k] = result[0]
    return ac

def transform_list_diff(ad, bd, s, policy=None):
    ac = {}
    b_inserts = []
    b_deletes = []
    if policy and 'item' in policy:
        sub_policy = policy['item']
    else:
        sub_policy = None

    for index, op in bd.iteritems():
        index = int(index)
        if op['o'] == '+': b_inserts.append(index)
        if op['o'] == '-': b_deletes.append(index)
    last_index = 0
    last_shift = 0

    for index, op in ad.iteritems():
        index = int(index)
        shift_r = len(filter(lambda x: x < index, b_inserts))
        shift_l = len(filter(lambda x: x < index, b_deletes))

        if last_index+1 == index:
            index = index + last_shift
        else:
            index = index + shift_r - shift_l
        last_index = index
        last_shift = shift_r - shift_l

        sindex = str(index)
        ac[sindex] = op
        if sindex in bd:
            if op['o'] == '+' and bd[sindex]['o'] == '+':
                pass
            elif op['o'] == '-':
                if bd[sindex]['o'] == '-':
                    del ac[sindex]
            elif bd[sindex]['o'] == '-':
                if op['o'] == 'r':
                    ac[sindex] = {'o': '+', 'v': op['v']}
                elif op['o'] not in ['+']:
                    ac[sindex] = {'o':'+', 'v': apply_object_diff(s[index], op['v'])}
            else:
                ac[sindex] = transform_object_diff({sindex:op}, {sindex:bd[sindex]}, s, sub_policy)[sindex]
    return ac

# diff a on S0 and diff b on S0
# return a' where T(T(S0, b), a') == T(T(S0, a), b') # not really since DMP deltas will not satisfy this property
def transform_object_diff(a, b, s, policy=None):
    ac = copy.deepcopy(a)

    if policy and 'attributes' in policy:
        policy = policy['attributes']

    for k, op in a.iteritems():
        if k in b:
            if policy and k in policy:
                sub_policy = policy[k]
            else:
                sub_policy = None

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
                    ac[k] = diff(b[k]['v'], op['v'], sub_policy)
            elif op['o'] == '-' and b[k]['o'] == '-':
                del ac[k]
            elif b[k]['o'] == '-' and op['o'] in ['O', 'L', 'I', 'd']:
                ac[k] = {'o':'+'}
                if op['o'] == 'O':
                    ac[k]['v'] = apply_object_diff(sk, op['v'])
                elif op['o'] == 'L':
                    ac[k]['v'] = apply_list_diff(sk, op['v'])
                elif op['o'] == 'I':
                    ac[k]['v'] = sk + op['v']
                elif op['o'] == 'd':
                    diffs = DMP.diff_fromDelta(sk, op['v'])
                    patches = DMP.patch_make(sk, diffs)
                    result = DMP.patch_apply(patches, sk)
                    ac[k]['v'] = result[0]
            elif op['o'] == 'O' and b[k]['o'] == 'O':
                ac[k] = {'o':'O', 'v':transform_object_diff(op['v'], b[k]['v'], sk, sub_policy)}
            elif op['o'] == 'L' and b[k]['o'] == 'L':
                ac[k] = {'o':'L', 'v':transform_list_diff(op['v'], b[k]['v'], sk, sub_policy)}
            elif op['o'] == 'dL' and b[k]['o'] == 'dL':
                ac[k] = {'o':'dL', 'v':transform_list_diff_dmp(op['v'], b[k]['v'], sk, sub_policy)}
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
# diffs = list of operations
# s = common object ancestor
def transform(a, diffs, s, policy=None):
    for diff in diffs:
        a = transform_object_diff(a, diff, s, policy)
        s = apply_diff(s, diff)
    return a

def diff(a, b, policy=None):
    if equals(a,b):
        return {}

    if policy and 'attributes' in policy:
        policy = policy['attributes']

    if policy and 'otype' in policy:
        otype = policy['otype']
        if otype == 'replace':
            return {'o': 'r', 'v': b}
        elif otype == 'list_dmp':
            return {'o': 'dL', 'v': list_diff_dmp(a, b, policy)}
        elif otype == 'list':
            return {'o': 'L', 'v': list_diff(a, b, policy)}
        elif otype == 'integer':
            return {'o': 'I', 'v': b-a}
        elif otype == 'string':
            diffs = DMP.diff_main(a, b)
            if len(diffs) > 2:
                DMP.diff_cleanupEfficiency(diffs)
            if len(diffs) > 0:
                delta = DMP.diff_toDelta(diffs)
                return {'o':'d', 'v':delta}

    if not same_type(a,b):
        return {'o':'r', 'v': b}

    if type(a) in [int, float, long]:
        return {'o':'r', 'v': b}
    elif type(a) == bool:
        return {'o':'r', 'v': b}
    elif type(a) == list:
        return {'o':'r', 'v': b}
    elif type(a) == dict:
        return {'o':'O', 'v': object_diff(a, b, policy)}
    elif isinstance(a, basestring):
        diffs = DMP.diff_main(a, b)
        if len(diffs) > 2:
            DMP.diff_cleanupEfficiency(diffs)
        if len(diffs) > 0:
            delta = DMP.diff_toDelta(diffs)
            return {'o':'d', 'v':delta}
    return {}

# transform should work on CHANGES
# CHANGE = {'o':TYPE, 'v':VALUE}
# diffs should work on OPERATIONS?
# DIFF = {'}
def apply_diff(a, ops):
    if type(a) == dict:
        return apply_object_diff(a, ops)
    elif type(a) == list:
        return apply_list_diff(a, ops)

class differ:
    def __init__(self):
        pass

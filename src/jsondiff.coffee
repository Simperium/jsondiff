# Used to generate a diff between two JSON objects, and also transform a diff with respect to another diff
#
# Generally when we diff two objects A and B, the diff can be thought of as, what are the operations needed to perform on A, to create an object identical to B
# So B can be thought of as the target object, A is the origin object
#
#### Example 1:
#
#     A = { 'num' : 5 }
#     B = { 'num' : 6 }
#
# The `diff(A,B)` should specify an operation to add 1 to the value of the object key 'num'
#
# We specify the diffs as a map of keys to operations.  An operation consists of 'o': specifies the kind/type of operation and 'v': a value or parameter for the operation
# The 'v' is a parameter for the specified operation, in cases where the operation doesn't need a parameter, it might be omitted.
# Currently this only happens when o = '-', which means, we are deleting a key, no parameter is necessary.
#
# For the two example objects above, the diff would be:
#
#     {
#      'num' : {'o':'I', 'v':1}
#     }
#
# For the key 'num', it defines an operation, the 'o' = 'I' specifies to treat the value of the subsequent 'v' as the parameter in an integer diff
# For integer diffs,
#   When generating the diff, to obtain the 'v' used in the operation, we just substract the value of the key of the origin object from the value of the key from the target object
#   In other words, to get the 'v', we just do B.num - A.num, or 6-5
#
#   If we then applied this diff to A, because the 'o' is 'I' for integer, we know to just add the value of 'v' to A.num to get 6
#
#
#### Example 2:
#
#
#     A = { 'numbers' : [1, 3, 2, 3, 4],
#           'name' : 'Ted'
#          }
#     B = { 'numbers' : [1, 2, 3, 4],
#           'name' : 'Red'
#          }
#
# The `diff(A,B)` should be two main operations, one to somehow rearrange the array in numbers, to match the second array.  There are a number of different ways we could do this.
# And the second should be to change the first letter of T to R in name - we don't care exactly how since DiffMatchPatch will take care of it. The value of the operation then is just the output of DMP.
#
# Diff for array
#
# When generating the diff, we see that the value of numbers is an array so we will call `list_diff()` to generate the diff for that portion.
#
#     a = [1, 3, 2, 3, 4]
#     b = [1, 2, 3, 4]
#
# The most naive approach we could do is to compare directly each index of the array, and when it is different, add an operation to change the value for that index.
#
# For the above, we could do a series of operations like,
#
#     Change a[1] to 2,
#     Change a[2] to 3,
#     Change a[3] to 4,
#     Delete a[4]
#
# But the most efficient thing we could do is just to delete a[1]
# We can optimize the operations generated by doing some work beforehand, like removing the common prefix/suffixes.
# If we remove the common prefix/suffix, the resulting arrays are:
#
#     [3]
#     []
#
# Now if we do the diff, we know we only need to delete 3 (a[1])
#
# There are many more optimizations on [Neil Fraser's page](http://neil.fraser.name/writing/diff/), but currently that is the only one we do.
#
# The delete a[1] will look like: '1' : {'o':'-'}
# We use similar notation for arrays as objects. Where the keys are indexes.
# That says at array index 1, we have a delete operation ('o' = '-'), since it is delete there is no parameter and no 'v'
# That is the output of the `list_diff()` then, {'1': {'o' : '-'}}
# When we apply that diff to array a, we know to go to index 1, do that operation (delete)
#
# Back to the example, the diff for the 'numbers' key will first be 'o':'L' , with 'v', the value being the output of the `list_diff()` function.
# That portion of the diff for 'numbers' will look like:
#
#     {'numbers' : {'o':'L',
#                   'v': [output of list diff]
#                  }
#     }
#
# or
#
#     {'numbers' : {'o':'L',
#                   'v': {'1': {'o' : '-'}}
#                  }
#     }
#
# Now we move on to the next key, 'name'.  We check the value and see that it is a string. For strings we automatically use diffmatchpatch.
# When generating the diff, we set 'o' to 'd', so we know later to use DMP, and the value 'v' is the output of DMP diff (in DMP terms generating a delta)
#
# This looks like:
#
#     {'o':'d', 'v':'-1\t+R\t=2'}
#
# So the diff for the 'name' key is:
#
#     {'name': {'o':'d', 'v':'-1\t+R\t=2'}}
#
# Now the diff for the whole object is all the diffs for all the keys.
#
#     {'numbers' : {'o': 'L', 'v': {'1': {'o': '-'}}},
#      'name'    : {'o': 'd', 'v': '-1\t+R\t=2'}}
#
# We can use that as a parameter to `apply_obj_diff(A, diff)`, which would apply the above diff to object A (defined at top of example),
# The output of that `apply_obj_diff(A, diff)` then should be an object identical to B.

#### Main documentation
class jsondiff
  @dmp = new diff_match_patch()

  #### Helper functions

  # Return the number of entries in an object
  entries: (obj) =>
    n = 0
    for own key, value of obj
      n++
    n

  # Get the type properly, javascripts `typeof` is broken, see [http://javascript.crockford.com/remedial.html]().
  typeOf: (value) =>
    s = typeof value
    if s is 'object'
      if value
        if typeof value.length is 'number' and
          typeof value.splice is 'function' and
          not value.propertyIsEnumerable 'length'
            s = 'array'
      else
        s = 'null'
    return s

  # Return a deep copy of the object
  deepCopy: (obj) =>
    if Object::toString.call(obj) is '[object Array]'
      out = []
      for i in [0...obj.length]
        out[i] = arguments.callee obj[i]
      return out
    if typeof obj is 'object'
      out = {}
      for i of obj
        out[i] = arguments.callee obj[i]
      return out
    return obj

  # Deep equals comparison
  equals: (a, b) =>
    typea = @typeOf a
    if typea != @typeOf b
      return false
    if typea is 'array'
      return @list_equals a, b
    else if typea is 'object'
      return @object_equals a, b
    else
      return a is b

  # Given two arrays, returns true if all elements of array are equal
  list_equals: (a, b) =>
    alength = a.length
    if alength != b.length
      return false
    for i in [0...alength]
      if not @equals a[i], b[i]
        return false
    return true

  # Given two objects, returns true if both objects have same set of keys and values
  object_equals: (a, b) =>
    for own key of a
      if not (key of b)
        return false
      if not @equals a[key], b[key]
        return false
    for own key of b
      if not (key of a)
        return false
    return true

  # Returns the length of common elements at beginning of two arrays
  _common_prefix: (a, b) =>
    minlen = Math.min a.length, b.length
    for i in [0...minlen]
      if not @equals a[i], b[i]
        return i
    return minlen

  # Returns the length of common elements at end of two arrays
  _common_suffix: (a, b) =>
    lena = a.length
    lenb = b.length
    minlen = Math.min a.length, b.length
    if minlen is 0
      return 0
    for i in [0...minlen]
      if not @equals a[lena-i-1], b[lenb-i-1]
        return i
    return minlen

# Compare two arrays and generate a diff object to be applied to an array.
# For arrays we treat them like objects, in an object we have explicit mapping of keys : values.
# The same format is used for arrays, where we replace the key with the index.
#
# For example, if we have the objects:
#
#     A = { 'num1' : 4, 'num2' : 7 }
#     B = { 'num1' : 8, 'num2' : 2 }
#
# The `diff(A,B)` would be
#
#     { 'num1' : {'o':'I', 'v':4},
#       'num2' : {'o':'I', 'v':-5} }
#
# Similarly, if we have an array instead with the same values:
#
#     A = [4, 7]
#     B = [8, 2]
#
# The diff would be:
#
#     { '0' : {'o':'I', 'v':4},
#       '1' : {'o':'I', 'v':-5} }
  list_diff: (a, b) =>
    diffs = {}
    lena = a.length
    lenb = b.length

    prefix_len = @_common_prefix a, b
    suffix_len = @_common_suffix a, b

    a = a[prefix_len...lena-suffix_len]
    b = b[prefix_len...lenb-suffix_len]

    lena = a.length
    lenb = b.length

    maxlen = Math.max lena, lenb

    # Iterate over both arrays
    for i in [0..maxlen]
      if i < lena and i < lenb
        # If values aren't equal we set the value to be the output of the diff
        if not @equals a[i], b[i]
          diffs[i+prefix_len] = @diff a[i], b[i]
      else if i < lena
        # array b doesn't have this element so remove it
        diffs[i+prefix_len] = {'o':'-'}
      else if i < lenb
        # array a doesn't have this element so add it
        diffs[i+prefix_len] = {'o':'+', 'v':b[i]}

    return diffs

# Compare two objects and generate a diff object to be applied to an object (dictionary).
  object_diff: (a, b) =>
    diffs = {}
    if not a? or not b? then return {}
    for own key of a
      if key of b
        # Both objects have the same key, if the values aren't equal, set the value to tbe the output of the diff
        if not @equals a[key], b[key]
          diffs[key] = @diff a[key], b[key]
      else
        # Object a has this key but object b doesn't, remove from a
        diffs[key] = {'o':'-'}
    for own key of b
      if not (key of a)
        # Object b has this key but object a doesn't, add to a
        diffs[key] = {'o':'+', 'v':b[key]}

    return diffs

# This is intended to be used by internal functions to automatically generate
# the correct operations for a value based on the type.
# diff(a,b) returns an operation object, such that when the operation is performed on a, the result is b.
# An operation object is
#
#     {'o':(operation type), 'v':(operation parameter value)}
  diff: (a, b) =>
    if @equals a, b
      return {}
    typea = @typeOf a
    if typea != @typeOf b
      return {'o':'r', 'v':b }

    switch typea
      when 'boolean'  then return {'o': 'r', 'v': b}
#      when 'number'   then return {'o': 'I', 'v': b-a}
      when 'number'   then return {'o': 'r', 'v': b}
      when 'array'    then return {'o': 'L', 'v': @list_diff a, b}
      when 'object'   then return {'o': 'O', 'v': @object_diff a, b}
      when 'string'
        # Use diffmatchpatch here for comparing strings
        diffs = jsondiff.dmp.diff_main a, b
        if diffs.length > 2
          jsondiff.dmp.diff_cleanupEfficiency diffs
        if diffs.length > 0
          return {'o': 'd', 'v': jsondiff.dmp.diff_toDelta diffs}

    return {}


# Applies a diff object (which consists of a map of keys to operations) to an array (`s`) and
# returns a new list with the operations in `diffs` applied to it
  apply_list_diff: (s, diffs) =>
    patched = @deepCopy s
    indexes = []
    deleted = []

    # Sort the keys (which are array indexes) so we can process them in order
    for own key of diffs
      indexes.push key
      indexes.sort()

    for index in indexes
      op = diffs[index]

      # Resulting index may be shifted depending if there were delete
      # operations before the current index.
      shift = (x for x in deleted when x <= index).length
      s_index = index - shift

      switch op.o
        # Insert new value at index
        when '+'
          patched[s_index..s_index] = op.v
        # Delete value at index
        when '-'
          patched[s_index..s_index] = []
          deleted[deleted.length] = s_index
        # Replace value at index
        when 'r'
          patched[s_index] = op.v
        # Integer, add the difference to current value
        when 'I'
          patched[s_index] += op.v
        # List, apply the diff operations to the current array
        when 'L'
          patched[s_index] = @apply_list_diff patched[s_index], op.v
        # Object, apply the diff operations to the current object
        when 'O'
          patched[s_index] = @apply_object_diff patched[s_index], op.v
        # String, apply the patch using diffmatchpatch
        when 'd'
          dmp_diffs = jsondiff.dmp.diff_fromDelta patched[s_index], op.v
          dmp_patches = jsondiff.dmp.patch_make patched[s_index], dmp_diffs
          dmp_result = jsondiff.dmp.patch_apply dmp_patches, patched[s_index]
          patched[s_index] = dmp_result[0]

    return patched


# Applies a diff object (which consists of a map of keys to operations) to an object (`s`) and
# returns a new object with the operations in `diffs` applied to it
  apply_object_diff: (s, diffs) =>
    patched = @deepCopy s
    for own key, op of diffs
      switch op.o
        # Add new key/value
        when '+'
          patched[key] = op.v
        # Delete a key
        when '-'
          delete patched[key]
        # Replace the value for key
        when 'r'
          patched[key] = op.v
        # Integer, add the difference to current value
        when 'I'
          patched[key] += op.v
        # List, apply the diff operations to the current array
        when 'L'
          patched[key] = @apply_list_diff patched[key], op.v
        # Object, apply the diff operations to the current object
        when 'O'
          patched[key] = @apply_object_diff patched[key], op.v
        # String, apply the patch using diffmatchpatch
        when 'd'
          dmp_diffs = jsondiff.dmp.diff_fromDelta patched[key], op.v
          dmp_patches = jsondiff.dmp.patch_make patched[key], dmp_diffs
          dmp_result = jsondiff.dmp.patch_apply dmp_patches, patched[key]
          patched[key] = dmp_result[0]

    return patched

# Applies a diff object (which consists of a map of keys to operations) to an object (`s`) and
# returns a new object with the operations in `diffs` applied to it
  apply_object_diff_with_offsets: (s, diffs, field, offsets) =>
    patched = @deepCopy s
    for own key, op of diffs
      switch op.o
        # Add new key/value
        when '+'
          patched[key] = op.v
        # Delete a key
        when '-'
          delete patched[key]
        # Replace the value for key
        when 'r'
          patched[key] = op.v
        # Integer, add the difference to current value
        when 'I'
          patched[key] += op.v
        # List, apply the diff operations to the current array
        when 'L'
          patched[key] = @apply_list_diff patched[key], op.v
        # Object, apply the diff operations to the current object
        when 'O'
          patched[key] = @apply_object_diff patched[key], op.v
        # String, apply the patch using diffmatchpatch
        when 'd'
          dmp_diffs = jsondiff.dmp.diff_fromDelta patched[key], op.v
          dmp_patches = jsondiff.dmp.patch_make patched[key], dmp_diffs
          if key is field
            patched[key] = @patch_apply_with_offsets dmp_patches, patched[key],
                offsets
          else
            dmp_result = jsondiff.dmp.patch_apply dmp_patches, patched[key]
            patched[key] = dmp_result[0]

    return patched

  transform_list_diff: (ad, bd, s) =>
    ad_new = {}
    b_inserts = []
    b_deletes = []
    for own index, op of bd
      if op.o is '+' then b_inserts.push index
      if op.o is '-' then b_deletes.push index
    for own index, op of ad
      shift_r = [x for x in b_inserts when x <= index].length
      shift_l = [x for x in b_deletes when x <= index].length

      index = index + shift_r - shift_l
      sindex = String(index)

      ad_new[sindex] = op
      if index of bd
        if op.o is '+' and bd.index.op is '+'
          continue
        else if op.o is '-' and bd.index.op is '-'
          delete ad_new[sindex]
        else
          diff = @transform_object_diff({sindex:op}, {sindex:bd.index.op}, s)
          ad_new[sindex] = diff[sindex]
    return ad_new

  transform_object_diff: (ad, bd, s) =>
    ad_new = @deepCopy ad
    for own key, aop of ad
      if not (key of bd) then continue

      sk = s[key]
      bop = bd[key]

      if aop.o is '+' and bop.o is '+'
        if @equals aop.v, bop.v
          delete ad_new[key]
        else
          ad_new[key] = @diff bop.v, aop.v
      else if aop.o is '-' and bop.o is '-'
        delete ad_new[key]
      else if bop.o is '-' and aop.o in ['O', 'L', 'I', 'd']
        ad_new[key] = {'o':'+'}
        if aop.o is 'O'
          ad_new[key].v = @apply_object_diff sk, aop.v
        else if aop.o is 'L'
          ad_new[key].v = @apply_list_diff sk, aop.v
        else if aop.o is 'I'
          ad_new[key].v = sk + aop.v
        else if aop.o is 'd'
          dmp_diffs = jsondiff.dmp.diff_fromDelta sk, aop.v
          dmp_patches = jsondiff.dmp.patch_make sk, dmp_diffs
          dmp_result = jsondiff.dmp.patch_apply dmp_patches, sk
          ad_new[key].v = dmp_result[0]
      else if aop.o is 'O' and bop.o is 'O'
        ad_new[key] = {'o':'O', 'v': @transform_object_diff aop.v, bop.v, sk}
      else if aop.o is 'L' and bop.o is 'L'
        ad_new[key] = {'o':'O', 'v': @transform_list_diff aop.v, bop.v, sk}
      else if aop.o is 'd' and bop.o is 'd'
        delete ad_new[key]
        a_patches = jsondiff.dmp.patch_make sk, jsondiff.dmp.diff_fromDelta sk, aop.v
        b_patches = jsondiff.dmp.patch_make sk, jsondiff.dmp.diff_fromDelta sk, bop.v
        b_text = (jsondiff.dmp.patch_apply b_patches, sk)[0]
        ab_text = (jsondiff.dmp.patch_apply a_patches, b_text)[0]
        if ab_text != b_text
          dmp_diffs = jsondiff.dmp.diff_main b_text, ab_text
          if dmp_diffs.length > 2
            jsondiff.dmp.diff_cleanupEfficiency dmp_diffs
          if dmp_diffs.length > 0
            ad_new[key] = {'o':'d', 'v':jsondiff.dmp.diff_toDelta dmp_diffs}

      return ad_new

  patch_apply_with_offsets: (patches, text, offsets) =>


window['jsondiff'] = jsondiff

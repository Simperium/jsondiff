import urllib

from diffmatchpatch import diff_match_patch

def length_ucs2( string ):
    return len( string.encode( 'UTF-16LE' ) ) / 2

def diff_toDelta_ucs2(self, diffs):
    """Crush the diff into an encoded string which describes the operations
    required to transform text1 into text2.
    E.g. =3\t-2\t+ing  -> Keep 3 chars, delete 2 chars, insert 'ing'.
    Operations are tab-separated.  Inserted text is escaped using %xx notation.

    Args:
      diffs: Array of diff tuples.

    Returns:
      Delta text.
    """
    text = []
    for (op, data) in diffs:
        if op == self.DIFF_INSERT:
            # High ascii will raise UnicodeDecodeError.  Use Unicode instead.
            data = data.encode("utf-8")
            text.append("+" + urllib.quote(data, "!~*'();/?:@&=+$,# "))
        elif op == self.DIFF_DELETE:
            text.append("-%d" % length_ucs2(data))
        elif op == self.DIFF_EQUAL:
            text.append("=%d" % length_ucs2(data))
    return "\t".join(text)

def diff_fromDelta_ucs2(self, text1, delta):
    """Given the original text1, and an encoded string which describes the
    operations required to transform text1 into text2, compute the full diff.

    Args:
    text1: Source string for the diff.
    delta: Delta text.

    Returns:
    Array of diff tuples.

    Raises:
    ValueError: If invalid input.
    """
    if type(delta) == unicode:
        # Deltas should be composed of a subset of ascii chars, Unicode not
        # required.  If this encode raises UnicodeEncodeError, delta is invalid.
        delta = delta.encode("ascii")
    diffs = []
    pointer = 0  # Cursor in text1
    pointer_ucs2 = 0
    tokens = delta.split("\t")
    for token in tokens:
        if token == "":
            # Blank tokens are ok (from a trailing \t).
            continue
        # Each token begins with a one character parameter which specifies the
        # operation of this token (delete, insert, equality).
        param = token[1:]
        if token[0] == "+":
            param = urllib.unquote(param).decode("utf-8")
            diffs.append((self.DIFF_INSERT, param))
        elif token[0] == "-" or token[0] == "=":
            try:
                n_ucs2 = int(param)
            except ValueError:
               raise ValueError("Invalid number in diff_fromDelta: " + param)
            if n_ucs2 < 0:
               raise ValueError("Negative number in diff_fromDelta: " + param)
            n = n_ucs2
            if pointer + n > len(text1):
                n = len(text1) - pointer
            while length_ucs2( text1[pointer : pointer + n] ) > n_ucs2:
            # may also need to make sure no surrogate pair is split
                n -= 1
            text = text1[pointer : pointer + n]
            pointer += n
            pointer_ucs2 += n_ucs2
            if token[0] == "=":
                diffs.append((self.DIFF_EQUAL, text))
            else:
                diffs.append((self.DIFF_DELETE, text))
        else:
            # Anything else is an error.
            raise ValueError("Invalid diff operation in diff_fromDelta: " +
                token[0])
    if pointer_ucs2 != length_ucs2(text1):
        raise ValueError(
            "Delta length (%d) does not equal source text length (%d)." %
            (pointer_ucs2, length_ucs2(text1)))
    return diffs

def is_leading_surrogate( char ):
    return 0xD800 <= ord( char ) <= 0xDBFF

def is_trailing_surrogate( char ):
    return 0xDC00 <= ord( char ) <= 0xDFFF

dmp_diff_commonPrefix = diff_match_patch.diff_commonPrefix
def diff_commonPrefix( self, text1, text2 ):
    pos = dmp_diff_commonPrefix( self, text1, text2 )
    if not pos:
        return pos

    if is_leading_surrogate( text1[pos - 1] ):
        pos -= 1

    return pos

dmp_diff_commonSuffix = diff_match_patch.diff_commonSuffix
def diff_commonSuffix( self, text1, text2 ):
    pos = dmp_diff_commonSuffix( self, text1, text2 )
    if not pos:
        return pos

    if is_trailing_surrogate( text1[-1 * pos] ):
        pos -= 1

    return pos

dmp_diff_halfMatch = diff_match_patch.diff_halfMatch
def diff_halfMatch( self, text1, text2 ):
    hm = dmp_diff_halfMatch( self, text1, text2 )
    if not hm:
        return hm

    common = hm[4]

    is_changed = False

    if is_trailing_surrogate( common[0] ):
        hm = list( hm )
        is_changed = True

        hm[0] += common[0]
        hm[2] += common[0]
        common = common[1:]

    if is_leading_surrogate( common[-1] ):
        if not is_changed:
            hm = list( hm )
        is_changed = True

        hm[1] = common[-1] + hm[1]
        hm[3] = common[-1] + hm[3]
        common = common[:-1]

    if not len( common ):
        return None

    if is_changed:
        hm[4] = common
        hm = tuple( hm )

    return hm

class String_Offset_Override:
    def __init__( self, string ):
        self.string = string

    def __len__( self ):
        return len( self.string )

    def __getitem__( self, start ):
        ret = self.string[start]
        if not ret:
            return ret

        if -1 == start:
            stop = None
        else:
            stop = start + 1

        if is_leading_surrogate( ret[-1] ):
            if stop is not None:
                stop += 1
        elif is_trailing_surrogate( ret[0] ):
            if start > 0:
                start -= 1

        return self.string[start:stop]

class Diff_No_Split( Exception ):
    pass

dmp_diff_bisect = diff_match_patch.diff_bisect
def diff_bisect( self, text1, text2, deadline ):
    text1o = String_Offset_Override( text1 )
    text2o = String_Offset_Override( text2 )
    try:
        ret = dmp_diff_bisect( self, text1o, text2o, deadline )
    except Diff_No_Split:
        return [ ( self.DIFF_DELETE, text1 ), ( self.DIFF_INSERT, text2 ) ]

    if ret and 2 == len( ret ) and ret[0][0] == self.DIFF_DELETE and ret[1][0] == self.DIFF_INSERT and ret[0][1] == text1o and ret[1][1] == text2o:
        return [ ( self.DIFF_DELETE, text1 ), ( self.DIFF_INSERT, text2 ) ]

    return ret

dmp_diff_bisectSplit = diff_match_patch.diff_bisectSplit
def diff_bisectSplit( self, text1, text2, x, y, deadline ):
    # diff_match_patch.diff_bisect didn't see a way to split the texts up further
    # Bail now to prevent recursion
    if not x and not y:
        raise Diff_No_Split
    return dmp_diff_bisectSplit( self, text1.string, text2.string, x, y, deadline )

def diff_commonOverlap(self, text1, text2):
    """Determine if the suffix of one string is the prefix of another.

    Args:
      text1 First string.
      text2 Second string.

    Returns:
      The number of characters common to the end of the first
      string and the start of the second string.
    """
    # Cache the text lengths to prevent multiple calls.
    text1_length = len(text1)
    text2_length = len(text2)
    # Eliminate the null case.
    if text1_length == 0 or text2_length == 0:
        return 0
    # Truncate the longer string.
    if text1_length > text2_length:
        text1 = text1[-text2_length:]
        if is_trailing_surrogate( text1[0] ):
            text2_length -= 1
            text1 = text1[1:]
            text2 = text2[:-1]
    elif text1_length < text2_length:
        text2 = text2[:text1_length]
        if is_leading_surrogate( text2[-1] ):
            text1_length -= 1
            text1 = text1[1:]
            text2 = text2[:-1]
    text_length = min(text1_length, text2_length)
    # Quick check for the worst case.
    if text1 == text2:
        return text_length

    # Start by looking for a single character match
    # and increase length until no match is found.
    # Performance analysis: http://neil.fraser.name/news/2010/11/04/
    best = 0
    length = 1
    while True:
        pattern = text1[-length:]
        if is_trailing_surrogate( pattern[0] ):
            length += 1
            pattern = text1[-length:]

        found = text2.find(pattern)
        if found == -1:
            return best
        length += found
        if found == 0 or text1[-length:] == text2[:length]:
            best = length
            length += 1

def monkey():
    if 1 == len( u'\U0001f4a9' ):
        diff_match_patch.diff_toDelta = diff_toDelta_ucs2
        diff_match_patch.diff_fromDelta = diff_fromDelta_ucs2
    diff_match_patch.diff_commonPrefix = diff_commonPrefix
    diff_match_patch.diff_commonSuffix = diff_commonSuffix
    diff_match_patch.diff_halfMatch = diff_halfMatch
    diff_match_patch.diff_bisect = diff_bisect
    diff_match_patch.diff_bisectSplit = diff_bisectSplit
    diff_match_patch.diff_commonOverlap = diff_commonOverlap

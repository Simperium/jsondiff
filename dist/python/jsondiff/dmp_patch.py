import re
import urllib

sp_utf16be = re.compile( '[\xd8-\xdb][\x00-\xff][\xdc-\xdf][\x00-\xff]' )

def length_ucs2( string ):
    return len( string ) + len( sp_utf16be.findall( string.encode( 'UTF-16BE' ) ) )

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
            n = 0
            while length_ucs2( text1[pointer : pointer + n] ) < n_ucs2:
            # may also need to make sure no surrogate pair is split
                n += 1
            text = text1[pointer : pointer + n]
            pointer += n
            if token[0] == "=":
                diffs.append((self.DIFF_EQUAL, text))
            else:
                diffs.append((self.DIFF_DELETE, text))
        else:
            # Anything else is an error.
            raise ValueError("Invalid diff operation in diff_fromDelta: " +
                token[0])
    if pointer != len(text1):
        raise ValueError(
            "Delta length (%d) does not equal source text length (%d)." %
            (pointer, length_ucs2(text1)))
    return diffs


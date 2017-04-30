import re
import gzip
import json
import random

from wordfilter import Wordfilter

def ucfirst(s):
    """Return a copy of string s with its first letter converted to upper case.

    >>> ucfirst("this is a test")
    'This is a test'

    >>> ucfirst("come on, Eileen")
    'Come on, Eileen'

    """
    return s[0].upper()+s[1:]

def lcfirst(s):
    """Return a copy of string s with its first letter converted to lower case.

    >>> lcfirst("Mother said there'd be days like these")
    "mother said there'd be days like these"

    >>> lcfirst("Come on, Eileen")
    'come on, Eileen'

    """
    return s[0].lower()+s[1:]

def tokens(s):
    """Return a list of strings containing individual words from string s.

    This function splits on whitespace transitions, and captures apostrophes
    (for contractions).

    >>> tokens("I'm fine, how are you?")
    ["I'm", 'fine', 'how', 'are', 'you']

    """
    words = re.findall(r"\b[\w']+\b", s)
    return words

def isprobablytitle(s):
    """Return True if string s looks like it could be a title; False otherwise.

    This is a heuristic function based on my Gutenberg Poetry corpus. Takes
    every word from string s with five or more characters
    and returns True if the resulting joined string is in title case.

    >>> isprobablytitle("The Day The Earth Stood Still")
    True

    >>> isprobablytitle("The Day the Earth Stood Still")
    True

    >>> isprobablytitle("the day the earth stood still")
    False

    """
    s = ' '.join([t.capitalize() if len(t) <= 4 else t for t in s.split()])
    return s.istitle()

def loadlines(filename='poetry.json-stream.gz', startidx=0, count=None,
        modulo=1):
    """Yields successive dictionaries from my Gutenberg Poetry corpus gzip.

    Lines are returned as dictionaries with keys for the Gutenberg ID of the
    text containing the line of poetry and the line itself. Optional startidx 
    and count parameters allow you to load only a subset of lines (starting at
    one index and collecting until the count is reached); a modulo parameter,
    if specified, will only yield the line if its index is divisible by the
    modulo. (This is a simple proxy for getting a "sampling" of lines.)

    >>> for line in loadlines(startidx=100, count=5):
    ...     print(line['line'])
    By the alders in the Summer,
    By the white fog in the Autumn,
    By the black line in the Winter;
    And beside them dwelt the singer,
    In the green and silent valley.

    >>> for line in loadlines(modulo=250000):
    ...     print(line['gutenberg_id'])
    617
    6130
    9567
    10161
    12137
    13561
    16209
    18466
    20174
    22692
    25599
    28621
    30720
    36508

    """
    wordfilter = Wordfilter()
    already_seen = set()
    for i, line in enumerate(gzip.open(filename, mode='rt')):
        if i < startidx:
            continue
        if count is not None and i > startidx + count:
            break
        if i % modulo != 0:
            continue
        # load the data and decode
        line = json.loads(line)
        
        if wordfilter.blacklisted(line['line']):
            continue
    
        # disqualifying characteristics (looks like a title, has brackets)
        if isprobablytitle(line['line']): continue
        if '[' in line['line'] or ']' in line['line']: continue
        if re.search(r"^\d", line['line']): continue

        # parse into words
        words = tuple([x.lower() for x in tokens(line['line'])])
        
        # no short lines, as they're not very interesting
        if len(words) <= 2:
            continue
        
        # skip if we've already seen something like this
        if words in already_seen:
            continue
        already_seen.add(words)

        yield line

def randomcounts(num):
    group_count = random.randrange(3, int(num / 4))
    counts = group_count * [4]
    while sum(counts) < num:
        counts[random.randrange(len(counts))] += 1
    return counts

def stanzify(t):
    # two stanza strategies:
    # 1. regular (if length of poem is divisible by 4, 5, 6, 7, 8, 9, 10, 12, 14)
    # 2. irregular (otherwise). this means: random groupings of similar length
    divisors = [x for x in (4, 5, 6, 7, 8, 9, 10, 12, 14) if len(t) % x == 0]
    if len(divisors) > 0:
        divisor = random.choice(divisors)
        groups = [t[i:i+divisor] for i in range(0, len(t), divisor)]
        output = []
        for i, group in enumerate(groups):
            output.extend(group)
            if i < len(groups) - 1:
                output.append("")
        return output
    else:
        counts = randomcounts(len(t))
        output = []
        for i, c in enumerate(counts):
            output.extend(t[:c])
            del t[:c]
            if i < len(counts) - 1:
                output.append("")
        return output

if __name__ == "__main__":
    import doctest
    doctest.testmod()

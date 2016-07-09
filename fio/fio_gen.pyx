""" Cythonizing this gave an ~20% overall speedup. The call to min()
    was the main culprit, which includes the str.split() and int()
    (6.4 seconds out of a 35.5 second run).
"""

# TODO: seem to be losing data points at the end of the file - make sure the
# lines dictionary here is being fully flushed by the generator...
def fio_generator(fps):
    """ Create a generator for reading multiple fio files in end-time order """
    lines = {fp: fp.next() for fp in fps}

    while True:
        # Get fp with minimum value in the first column (fio log end-time value)
        fp = min(lines, key=lambda k: int(lines.get(k).split(',')[0]))
        yield (lines[fp].rstrip() + ", " + str(fps.index(fp)) + '\n')
        lines[fp] = fp.next() # read a new line into our dictionary


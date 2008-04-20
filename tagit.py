#!/usr/bin/env python

import getopt
import sys
from taglib import Tag
import os.path

"""these are extensions taglib supports"""
valid_extensions = set(['mp3', 'ogg', 'm4a', 'aac', 'flc', 'mp4'])

def excerpt(s, length): 
    if len(s) > length:
        s = s[:length - 3] + '...'
    return s

def fmt(s): 
    return excerpt(s, 20).ljust(20)

def fmt_track(s):
    try:
        s = str(int(s))
    except ValueError:
        s = '-'
    return s.ljust(4)

def fmt_year(s): 
    if s == None:
        s = ''
    return s.ljust(4)
    
def show_dir(path, lvl=0): 
    path = os.path.abspath(path)
    filenames = []
    for filename in os.listdir(path):
        ext = filename[-3:].lower()
        if ext not in valid_extensions:
            continue
        filenames.append(filename)
    if filenames:
        print path
    for filename in filenames:
        f = os.path.join(path, filename)
        t = Tag(f)
        if not t.artist or not t.title or not t.album:
            print >> sys.stderr, f, "is missing an artist, album or title"
        else:
            print "  ", fmt(t.title), fmt(t.album), fmt(t.artist), t.year, fmt_track(t.track), filename


def usage():
    """show usage information"""
    print "usage: tagdir [options] <directory with mp3s>"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output = None
    verbose = False
    if len(args) != 1:
        usage()
        sys.exit(1)

    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit(1)

    show_dir(args[0])
    
if __name__ == '__main__':
    main() 


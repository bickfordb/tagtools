#!/usr/bin/env python
from ctypes import *
import os.path
import sys
libtag_c = CDLL('/opt/local/lib/libtag_c.dylib')
libtag_c.taglib_tag_title.restype = c_char_p
libtag_c.taglib_tag_album.restype = c_char_p
libtag_c.taglib_tag_genre.restype = c_char_p
libtag_c.taglib_tag_artist.restype = c_char_p

class Tag(object): 
    fields = ['title', 'artist', 'album', 'track', 'genre', 'year']

    def __init__(self, path): 
        if not os.path.exists(path):
            raise ValueError("file does not exist")
        fileid = libtag_c.taglib_file_new(path)
        tagid = libtag_c.taglib_file_tag(fileid)
        self.title = libtag_c.taglib_tag_title(tagid)
        self.artist =libtag_c.taglib_tag_artist(tagid)
        self.album = libtag_c.taglib_tag_album(tagid)
        self.track = libtag_c.taglib_tag_track(tagid)
        self.genre = libtag_c.taglib_tag_genre(tagid)
        self.year = libtag_c.taglib_tag_year(tagid)
        libtag_c.taglib_file_free(fileid) 

    def __str__(self): 
        fields_s = ', '.join([(i + ':' + repr(getattr(self, i))) for i in self.fields])
        return '<Tag ' + fields_s + '>'

if __name__ == '__main__':
    t = Tag(sys.argv[1])
    for field in t.fields:
        print field, getattr(t, field)


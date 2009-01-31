#!/usr/bin/env python
from ctypes import *
from os import walk
import os.path
from os.path import join, isfile, exists
import sys
from itertools import chain, izip
from optparse import OptionParser

libtag_c = CDLL('/opt/local/lib/libtag_c.dylib')
libtag_c.taglib_tag_title.restype = c_char_p
libtag_c.taglib_tag_album.restype = c_char_p
libtag_c.taglib_tag_genre.restype = c_char_p
libtag_c.taglib_tag_artist.restype = c_char_p

# this shouldn't be necessary 
#UTF8=3
#libtag_c.taglib_id3v2_set_default_text_encoding(UTF8)

class Tag(object): 
    """represents a tag record
    """
    def __init__(self, title=u'', artist=u'', album=u'', track=0, genre=u'', year=0):
        self.title = title
        self.artist = artist
        self.album = album
        self.track = track
        self.genre = genre
        self.year = year

    @classmethod
    def read(self, path):
        if not exists(path):
            raise ValueError("file does not exist")
        fileid = libtag_c.taglib_file_new(path.encode('utf-8'))
        if not fileid:
            raise ValueError("cant open file: " + path)

        tagid = libtag_c.taglib_file_tag(fileid)
        if not tagid:
            raise ValueError("invalid tagid")
        title = libtag_c.taglib_tag_title(tagid).decode('utf-8')
        artist = libtag_c.taglib_tag_artist(tagid).decode('utf-8')
        album = libtag_c.taglib_tag_album(tagid).decode('utf-8')
        track = libtag_c.taglib_tag_track(tagid)
        genre = libtag_c.taglib_tag_genre(tagid).decode('utf-8')
        year = libtag_c.taglib_tag_year(tagid)
        libtag_c.taglib_file_free(fileid) 
        libtag_c.taglib_tag_free_strings()
        return Tag(title=title, artist=artist, album=album, genre=genre, year=year, track=track)

    def save(self, filename):
        """Save the current tag values to a file"""
        orig = self.read(filename)
        fileid = libtag_c.taglib_file_new(path.encode('utf-8'))
        if not fileid:
            raise ValueError("cant open file: " + path)
        tagid = libtag_c.taglib_file_tag(fileid)
        
        if self.artist != orig.artist:
            taglib_tag_set_artist(tagid, self.artist.encode('utf-8'))
        
        if self.album != orig.album:
            taglib_tag_set_album(tagid, self.album.encode('utf-8'))
        
        if self.title != orig.title:
            taglib_tag_set_title(tagid, self.title.encode('utf-8'))

        if self.genre != orig.genre:
            taglib_tag_set_genre(tagid, self.genre.encode('utf-8'))

        libtag_c.taglib_file_save(fileid)
        libtag_c.taglib_file_free(fileid) 

    def __repr__(self): 
        return u'Tag(title=%(title)r, album=album=%(album)r, artist=%(artist)r, genre=%(genre)r, year=%(year)r, track=%(track)r)' % vars(self)

class TagScript(object):
    """Skeleton class for a script that processes ID3 tags from a set of input files"""

    def traverse(self, path):
        path = unicode(path)
        if isfile(path):
            yield path
        else:
            for root_dir, sub_dirs, files in walk(path):
                sub_dirs = list(sub_dirs)
                if sub_dirs and self.options.ignore_roots:
                    continue
                for filename in files:
                    yield join(root_dir, filename)


    def __init__(self):
        self.option_parser = OptionParser()
        self.option_parser.add_option('--dry-run', action='store_true', dest='dry_run', default=False)
        self.option_parser.add_option('--dont-ignore-roots', action='store_false', dest='ignore_roots', default=True, help='don\'t ignore directories that contain other directories.  directories with subdirectories are probably not album directories.  they are ignored by default.')

    def main(self):
        self.options, self.args = self.option_parser.parse_args()
        traversals = map(self.traverse, self.args)
        self.visit_filenames(chain(*traversals))

    def visit_filenames(self, filenames):
        def to_tags():
            for filename in filenames:
                try:
                    yield filename, Tag.read(filename)
                except ValueError:
                    continue
        self.visit_filenames_tags(to_tags())

    def visit_filenames_tags(self, filenames_tags):
        for filename, tag in filenames_tags:
            self.visit_filename_tag(filename, tag)

    def visit_filename_tag(self, filename, tag):
        print filename, tag

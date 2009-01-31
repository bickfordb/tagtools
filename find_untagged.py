#!/usr/bin/python

from os import walk
import sys
from taglib import TagScript

class FindUntagged(TagScript):
    def __init__(self):
        super(FindUntagged, self).__init__()
        self.option_parser.add_option('--fields', default='artist,album,title', dest='fields', help='comma separated list of fields to check')
    
    def visit_filename_tag(self, filename, tag):
        for field in self.options.fields.split(','):
            field = field.strip()
            if not hasattr(tag, field):
                continue
            if not getattr(tag, field):
                print filename 
                break

if __name__ == '__main__':
    FindUntagged().main()

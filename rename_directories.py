from taglib import TagScript
from os.path import dirname, split, sep, join
import os
from collections import defaultdict 
import string
import re
import unicodedata

def parse_directory(directory): 
    if sep in directory:
        directory = split(directory)[1]
    artist = extract_artist(directory)
    album = extract_album(directory)
    year = extract_year(directory)
    notes = extract_notes(directory)
    return {'artist': artist, 'album': album, 'year': year, 'notes':notes}

def extract_artist(directory):
    if '-' in directory:
        return directory[:directory.index('-')].strip()

def extract_album(directory):
    if '-' in directory:
        after_dash = directory[directory.index('-') + 1:]
        if '(' in after_dash:
            after_dash = after_dash[:after_dash.index('(')]
        return after_dash.strip()

def extract_year(directory):
    m = re.search(r'(\d{4})', directory)
    if m:
        year = m.groups()[0]
        if 1000 <= int(year) <= 3000:
            return year

def extract_notes(directory):
    m = re.match(r'^.*\((.+?)\).*$', directory)
    if m:
        notes = m.groups()[0]
        # remove the year if there is one:
        notes = re.sub(r'\b\d{4}\b', '', notes)
        return notes.strip(', ')

class RenameDirectories(TagScript):
    def visit_filenames_tags(self, filenames_tags):
        filenames_tags = list(filenames_tags)
        dir_to_tags = defaultdict(list)
        for filename, tag in filenames_tags:
            dir_to_tags[dirname(filename)].append((filename, tag))
        for directory, filenames_tags in dir_to_tags.iteritems():
            if filenames_tags:
                self.process_directory(directory, filenames_tags)

    def process_directory(self, directory, filenames_tags):
        artists = set()
        albums = set()
        years = set()
        for filename, tag in filenames_tags:
            if tag.artist:
                artists.add(tag.artist)
            if tag.album:
                albums.add(tag.album)
            year = unicode(tag.year) if 1000 < tag.year < 3000 else None
            if year is not None:
                years.add(year)

        artists = filter(bool, artists)
        albums = filter(bool, albums)
        years = filter(bool, years)

        dirinfo = parse_directory(directory)

        if dirinfo['artist'] and not artists:
            artists.append(dirinfo['artist'])

        if dirinfo['album'] and not albums:
            albums.append(dirinfo['album'])

        if dirinfo['year'] and not years:
            years.append(dirinfo['year'])

        notes = dirinfo['notes']

        if len(artists) > 2:
            print directory, "has too many artists set, skipping"
            return
        elif not artists:
            print directory, "has no artist set, skipping"
            return
        elif len(albums) > 1:
            print directory, "has too many albums set, skipping"
            return
        elif not albums:
            print directory, "has no album set, skipping"
            return
        elif len(years) > 1:
            print directory, "has too many years set, skipping"
            return
        
        artist = ', '.join(sorted(artists))
        album = albums[0] if albums else None
        year = years[0] if years else None
        title = artist + ' - ' + album
        if year or notes:
            extra = filter(bool, [year, notes])
            title += u' (' + u', '.join(extra) + u')'
        dir_root, dir_base = split(directory)
        
        if norm_NFKD(dir_base) == norm_NFKD(title):
            return
        title = filter(not_('/\\'.__contains__), title)
        self.rename(directory, join(dir_root, title))

    def rename(self, directory, new_directory):
        print "rename %(directory)r => %(new_directory)r" % locals()
        if not self.options.dry_run:
            os.rename(directory, new_directory)

norm_NFKD = lambda s: unicodedata.normalize('NFKD', s)

def not_(f):
    def not__(*args, **kwargs):
        return not f(*args, **kwargs)
    return not__

if __name__ == '__main__':
    RenameDirectories().main()


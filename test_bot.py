#!/usr/bin/env python

import sys
import os
import urllib2
import urllib
import subprocess
import re
import time
from glob import glob

def get_online_score(mapfile, route):
    req = urllib2.Request(url='http://undecidable.org.uk/~edwin/cgi-bin/weblifter.cgi',
                          data=urllib.urlencode({'mapfile': mapfile, 'route': route}))
    rep = urllib2.urlopen(req).read()
    board = re.search(r'<pre>(.*)</pre>', rep, re.M | re.S).groups()[0]
    score = int(re.search(r'Score: (-?[0-9]*)', rep).groups()[0])
    return (board, score)

def download_high_scores():
    req = urllib2.Request(url='http://undecidable.org.uk/~edwin/cgi-bin/weblifter.cgi?standings=1')
    rep = urllib2.urlopen(req).read()
    scores = re.findall(r'<h4>(.+?)</h4><p>([^<]+)', rep)
    nscores = {}
    for (name, values) in scores:
        nscores[name] = values
    return nscores

def test_bot(mapfile):
    path = os.path.join('..', 'task', mapfile + '.map')
    sp = subprocess.Popen(['./Main', path, 'dummy', 'dummy'],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    start = time.time()
    out, err = sp.communicate()
    end = time.time()
    lasted = end - start
    route = re.search(r'Used route: (.+)', out).group(1)
    onl_board, onl_score = get_online_score(mapfile, route)
    return lasted, onl_board, onl_score, route, out

def test_bot_on_all(*maps):
    os.chdir('src')
    subprocess.call(['ghc', 'Main.hs'])
    high_scores = download_high_scores()
    if not maps:
        maps = glob('../task/*.map')
    maps = [os.path.basename(m[:-4] if m.endswith('.map') else m) for m in maps]
    for mapfile in maps:
        print 'Testing %r...' % mapfile
        lasted, onl_board, onl_score, route, out = test_bot(mapfile)
        try:
            diff = int(high_scores[mapfile].split(' ', 1)[0]) - onl_score
            his = 'High scores: %s\nDistance from highest high score: %d' % (high_scores[mapfile], diff)
        except KeyError:
            his = 'No high scores.'
        print out
#        print 'Online board: \n%s' % onl_board

        print 'Took %f seconds (with simulator on)' % lasted
        print 'Online score: %s' % onl_score
        print his
        

if __name__ == '__main__':
    test_bot_on_all(*sys.argv[1:])


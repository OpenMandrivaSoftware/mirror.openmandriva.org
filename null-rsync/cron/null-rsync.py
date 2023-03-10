#!/usr/bin/python

"""
Create a local file tree as copy from a remote server via rsync.
All files will contain zeroes and do not use any disk space.

Copyright 2009,2010,2011,2012,2015 Peter Poeml

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

__version__ = '0.9'

import sys
import os
import subprocess
import time
import stat
import signal
import textwrap
from optparse import OptionParser



class SignalInterrupt(Exception):
    """Exception raised on SIGTERM and SIGHUP."""

def catchterm(*args):
    raise SignalInterrupt

for name in 'SIGBREAK', 'SIGHUP', 'SIGTERM':
    num = getattr(signal, name, None)
    if num: signal.signal(num, catchterm)


def perms_to_mode(p):

    m = 0

    if p[0] == 'r': m |= stat.S_IRUSR
    if p[1] == 'w': m |= stat.S_IWUSR
    if p[2] == 'x': m |= stat.S_IXUSR

    if p[3] == 'r': m |= stat.S_IRGRP
    if p[4] == 'w': m |= stat.S_IWGRP
    if p[5] == 'x': m |= stat.S_IXGRP
    elif p[5] == 'S': m |= stat.S_ISGID
    elif p[5] == 's': m |= stat.S_ISGID | stat.S_IXGRP

    if p[6] == 'r': m |= stat.S_IROTH
    # we never receive the following bit, because we run rsync with --chmod=o-w
    # so that it always considers the bit off in the source permissions
    if p[7] == 'w': m |= stat.S_IWOTH
    if p[8] == 'x': m |= stat.S_IXOTH

    # for security reasons, we probably don't want these:
    # stat.S_ISUID
    # stat.S_ISVTX

    return m


def main():

    usage = textwrap.dedent("""\
    usage: %prog [options] RSYNC_SOURCE_URL LOCAL_PATH

    Create a local file tree as "copy" from a remote server via rsync.
    All files will contain zeroes.

    All files will be created as sparse files, so they don't take actual space
    in the filesystem (besides metadata of the filesystem itself).

    This massively saves time and diskspace when you need some tree for testing
    that looks like a real one.

    To get the file metadata over rsync, rsync's own itemized output is used,
    because it tells us all we need to know:
        del. rw-r--r-- *deleting   ultimate-edition-1.9-x64.iso 0 1970/01/01-01:00:00
        recv rwxr-xr-x cd+++++++++ firefox/releases/3.0.15/ 4096 2009/10/26-19:23:12
        recv rw-r--r-- >f+++++++++ firefox/releases/3.0.15/MD5SUMS 54256 2009/10/26-19:21:21

    We copy all permissions and timestamps where possible. An exception are
    timestamps on symlinks, that can't be set by Python (its os.utime()
    implementation always follows to the target). (It *would* work if Python
    would export utimensat() with AT_SYMLINK_NOFOLLOW.) But it doesn't really
    matter.""")

    version = '%prog ' + __version__

    parser = OptionParser(usage=usage, version=version)
    #parser.disable_interspersed_args()

    parser.add_option('--exclude',
                      action='append', dest='excludes', metavar='PATTERN', default=[],
                      help='exclude files matching PATTERN (passed through to rsync')

    parser.add_option('-q', '--quiet',
                      action='store_true', dest='quiet', default=False,
                      help='Don\'t show output, except errors')

    parser.add_option('-v', '--verbose', action='count', dest='verbosity',
                      help='Print debug messages to stderr. '
                           'Option can be repeated to increase verbosity.')



    (options, args) = parser.parse_args()

    if len(args) < 2:
        print >>sys.stderr, 'Not enough arguments.'
        sys.exit(2)
    elif len(args) > 2:
        print >>sys.stderr, 'Too many arguments.'
        sys.exit(2)

    rsync_src = args[0]
    rsync_dst = args[1]
    rsync_dst = rsync_dst.rstrip('/')

    cmd = [ 'rsync',
            '--no-motd', 
            # not -a because we don't want --devices --specials --owner --group
            '-rlpt', 
            # upstream may have world-writable files/directories, but that doesn't mean
            # that we want that locally
            '--chmod=o-w',
            '--out-format=%o %B %i %M %l %n%L',
            '--delete',
            '--ignore-errors',
            '-n',
            rsync_src,
            rsync_dst ]

    for i in options.excludes:
        cmd.append('--exclude')
        cmd.append(i)

    if not os.path.exists(rsync_dst):
        os.mkdir(rsync_dst)
    # remember directories to set mtime afterwards
    mtime_dir_list = []

    o = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                    close_fds=True).stdout

    for line in o.readlines():

        if not options.quiet:
            # print what we are doing
            # but omit symlinks with incorrect mtime
            if not line.startswith('recv rwxrwxrwx .L..t......'):
                print line.rstrip()

        if line.startswith('IO'):
            sys.exit('rsync returned an error:\n%s' % line)

        words = line.strip().split(None, 5)
        # ['recv', 'rwxrwxrwx', 'cL+++++++++', '2009/05/31-03:31:46', '25', 'repo/1.0/11.1/suse/x86_64/yaz.rpm -> yaz-3.0.34-1.8.x86_64.rpm']

        action = words[0]
        perms  = words[1]
        attrs  = words[2]
        mtime_rsync = words[3]
        size   = int(words[4])
        name   = words[5]
        
        if attrs[1] == 'L':
            # symlink
            name, name_to = name.split(' -> ')

        path = os.path.join(rsync_dst, name)

        # this special case also deals with broken links that point outside the tree
        if attrs[1] == 'd' and os.path.islink(path.rstrip('/')):
            print 'removing link %r, to be replaced by directory' % path.rstrip('/')
            os.unlink(path.rstrip('/'))

        # for safety
        canonical_path = os.path.realpath(path)
        if not canonical_path.startswith(rsync_dst):
            sys.exit("Error: After canonicalization, %r is outside the rsync destination path (%r):\n       %r" \
                       % (name, rsync_dst, canonical_path))
        path = canonical_path.rstrip('/')

        if action == 'del.':
            if name.endswith('/'):
                if options.verbosity > 1:
                    print >>sys.stderr, 'unlinking directory', name
                os.rmdir(os.path.join(rsync_dst, name))
            else:
                if options.verbosity > 1:
                    print >>sys.stderr, 'unlinking file', name
                os.unlink(os.path.join(rsync_dst, name))

        elif action == 'recv':

            if attrs[1] == 'd':
                if name == './':
                    # top-level dir
                    # recv rwxr-xr-x .d..t...... 2009/11/06-00:46:02 4096 ./
                    if options.verbosity > 1:
                        print >>sys.stderr, 'ignoring top-level dir'
                    mtime_dir_list.append((path, mtime_rsync))

                if attrs[0] == 'c':
                    # recv rwxr-xr-x cd+++++++++ 2005/09/06-22:00:35 4096 firefox/
                    if options.verbosity > 1:
                        print >>sys.stderr, 'creating directory %r' % path
                    os.mkdir(path)
                    mtime_dir_list.append((path, mtime_rsync))

                elif attrs[0] == '.':
                    pass

                else:
                    sys.exit('don\'t know how to handle this line: %r' % words)


            elif attrs == 'cL+++++++++':
                if options.verbosity > 1:
                    print >>sys.stderr, 'creating symlink from %s to %s' % (name, name_to)
                os.symlink(name_to, path)


            if attrs.startswith('>f') and attrs[3] in ['s', '+']:
                # transfer a file
                fd = open(path, 'w')
                # writing info wastes massive space already; the mozilla file tree took 
                # 254 MB instead of 19 MB (real size: 25 G)
                #info = 'This is only a pseudo file, containing nothing than zeros. ' + \
                #      'Same length as the original file.'
                #if size > len(info):
                #    fd.write(info)
                if size == 0:
                    fd.truncate()
                else:
                    fd.seek(size - 1)
                    fd.write('\0')
                fd.close()

            if attrs[5] in ['p', '+']:
                if attrs[1] == 'L':
                    # not relevant for symlinks
                    pass
                else:
                    if options.verbosity > 1:
                        print >>sys.stderr, '%s: setting permissions' % path
                    os.chmod(path, perms_to_mode(perms))

            if attrs[4] in ['t', '+'] or attrs[3] in ['s', '+']:
                if attrs[1] == 'L':
                    # not doable jor symlinks
                    # it *would* work if Python would export utimensat() with
                    # AT_SYMLINK_NOFOLLOW
                    pass
                else:
                    t = time.strptime(mtime_rsync, '%Y/%m/%d-%H:%M:%S')
                    mtime = int(time.mktime(t))
                    if options.verbosity > 1:
                        print >>sys.stderr, '%s: setting mtime (%s)' % (path, mtime_rsync)
                    os.utime(path, (mtime, mtime))


        else:
            sys.exit('unknown action %r (line was: %r)' % (action, line))
        
    while len(mtime_dir_list) > 0:
        path, mtime_rsync = mtime_dir_list.pop()
        if options.verbosity > 0:
            print >>sys.stderr, 'delayed setting of mtime on %r' % path

        t = time.strptime(mtime_rsync, '%Y/%m/%d-%H:%M:%S')
        mtime = int(time.mktime(t))
        os.utime(path, (mtime, mtime))


            
    if options.verbosity > 0:
        print >>sys.stderr, 'rsync command for validation:'
        print >>sys.stderr, 'rsync --no-motd -rlpt --chmod=o-w %s %s -i -n' % (rsync_src, rsync_dst)




if __name__ == '__main__':

    try:
        main()

    except SignalInterrupt:
        print >>sys.stderr, 'killed!'

    except KeyboardInterrupt:
        print >>sys.stderr, 'interrupted!'



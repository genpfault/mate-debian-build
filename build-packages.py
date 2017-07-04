#!/usr/bin/env python

import codecs
import datetime
import optparse
import os
import subprocess
import sys
import tempfile
import glob

# script location
script_dir = os.path.dirname(os.path.realpath(__file__))

# create output directories
os.chdir(script_dir)
os.system('mkdir -p deb')
os.system('mkdir -p logs')

def build_package( package, options ):
    # grab SHA1 of package
    os.chdir(script_dir)
    os.chdir(package)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:7]

    # create & populate temp. directory
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    os.system('cp -R {0}/{1} .'.format(script_dir, package))
    os.chdir(package)
    os.system('cp -R {0}/debian-packages/{1}/debian/ .'.format(script_dir, package))

    # stock foramt files are (quilt)
    # convert to (native)
    # (quilt) assumes you're building from a tarball, not a repo working dir
    # and has some patch processing magicks
    os.system('echo \'3.0 (native)\' > debian/source/format')

    # patch up debian/changelog to satisfy (native) format requirements
    date = datetime.date.today().strftime('%Y%m%d')
    suffix = '+git.' + date + '.' + head
    orig_changelog_file = codecs.open('debian/changelog', encoding='utf-8', mode='r')
    orig_changelog = orig_changelog_file.read().splitlines()
    orig_changelog_file.close()
    new_changelog = orig_changelog
    new_changelog[0] = new_changelog[0].replace(')', suffix + ')')
    for i in range(10):
        new_changelog[0] = new_changelog[0].replace('-' + str(i), '')
    new_changelog_file = codecs.open('debian/changelog', encoding='utf-8', mode='w')
    new_changelog_file.write('\n'.join(new_changelog))
    new_changelog_file.close()

    # discover and install build dependencies
    if options.install_deps:
        os.system('sudo mk-build-deps --tool="apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y" --install --remove')

    # build package
    if options.source:
        os.system('dpkg-buildpackage -S -Zxz -uc -us')
        os.system('cp -v ../*.dsc {0}/deb/'.format(script_dir))
        os.system('cp -v ../*.xz {0}/deb/'.format(script_dir))
        os.system('cp -v ../*.changes {0}/deb/'.format(script_dir))
    else:
        if options.i386:
            os.system('dpkg-buildpackage -B -ai386 -Zxz -uc -tc 2>&1 | tee build.log')
        else:
            os.system('dpkg-buildpackage -b -Zxz -uc -tc 2>&1 | tee build.log')
        os.system('cp -v build.log {0}/logs/{1}.log'.format(script_dir, package))
        os.system('cp -v ../*.deb {0}/deb/'.format(script_dir))
        if options.install:
            # install built package(s)
            os.chdir('..')
            for deb in glob.glob('*.deb'):
                os.system('sudo dpkg --install {0}'.format(deb))
            os.system('sudo apt-get -y -f install')

    # cleanup
    os.chdir(script_dir)
    os.system('rm -rf {0}'.format(temp_dir))
    print "---------------------------------------------------------------"
    return

# options
parser = optparse.OptionParser()
parser.add_option('-s', '--source', dest='source', action='store_true', help='Build source package')
parser.add_option('-i', '--i386', dest='i386', action='store_true', help='Build i386 binary package')
parser.add_option("-d", "--install-deps", dest="install_deps", action="store_true", help="Install development dependencies")
parser.add_option("-n", "--install", dest="install", action="store_true", help="Install built package")
(options, packages) = parser.parse_args()

if len(packages) == 0:
    # no packages given, build 'em all
    packages = [
        'mate-common',
        'mate-desktop',
        'libmatekbd',
        'libmateweather',
        'mate-icon-theme',
        'caja',
        'mate-polkit',
        'marco',
        'libmatemixer',
        'mate-settings-daemon',
        'mate-session-manager',
        'mate-menus',
        'mate-terminal',
        'mate-panel',
        'mate-backgrounds',
        'mate-themes',
        'mate-notification-daemon',
        'mate-control-center',
        'mate-screensaver',
        'mate-media',
        'mate-power-manager',
        'mate-system-monitor',
        'mate-applets',
        'mate-sensors-applet',
        'mate-icon-theme-faenza',
        'mate-indicator-applet',
        'mate-calc',
        'mate-utils',
        'mate-user-share',
        'mate-user-guide',
        'python-caja',
        'caja-extensions',
        'caja-dropbox',
        'pluma',
        'eom',
        'engrampa',
        'atril',
        'mozo',
        ]
    options.install_deps = True
    options.install = True

# build given package(s)
for i in range(0, len(packages)):
    package = packages[i]
    if package == '':
        sys.exit(1)
    if package[-1] == '/':
        package = package[:-1]
    if not os.path.exists('{0}/{1}'.format(script_dir,package)):
        print 'E: package \'{0}\' not found'.format(package)
        sys.exit(1)

    build_package(package, options)

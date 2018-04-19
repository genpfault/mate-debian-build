`build-packages.py` is a Python script to automate building Debian packages for the MATE desktop environment in the proper order.

The MATE project submodules are pinned to the latest stable release for convenience.

I recommend spinning up a clean Debian Strech VM to build the packages in, `mk-build-deps` pulls in a bunch of packages you may or may not want cluttering up your day-to-day system.  2-4 cores, 2-4 GiB of memory, and ~10 GiB worth of disk should be enough.  Uncheck everything but `standard system utilities` in `tasksel`.

Build procedure:

    sudo apt-get install git-core devscripts dpkg-dev
    git clone --recurse-submodules https://github.com/genpfault/mate-debian-build.git
    cd mate-debian-build
    ./build-packages.py

Packages are copied to `mate-debian-build/deb`.

Building everything takes around 35 minutes on a Xeon D-1521 in a 4-core, 4 GiB KVM VM.

You'll also want to install some of the `xorg` metapackages as well as the display manager (LightDM, GDM, KDM, etc.) of your choice.  For example:

    sudo apt-get install lightdm desktop-base xorg xserver-xorg-input-all xserver-xorg-video-all

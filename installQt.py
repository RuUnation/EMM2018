#!/usr/bin/python3

import argparse
import subprocess
import os, sys, stat
import fileinput
import shutil

DEFAULT_DOWNLOAD_PATH = "/home/pi/Downloads"
DEFAULT_BUILD_PATH = "/home/pi/build"
DEFAULT_PLATFORM = "linux-rasp-pi3-g++"


def init_args_parser():
    parser= argparse.ArgumentParser()
    parser.add_argument("-d","--downloadpath", help="downloadpath for the qt5.10.1 source. Default is home/pi/Downloads.", type=str, default=DEFAULT_DOWNLOAD_PATH)
    parser.add_argument("-b","--buildpath", help="shadow build directory. Default is home/pi/build", type=str, default=DEFAULT_BUILD_PATH)
    parser.add_argument("-j","--jobs", help="number of jobs for make (j4 in the doc)", type=int, choices=range(1,5), default=1)
    parser.add_argument("-p", "--platform", help="which platform, default is linux-rasp-pi3-g++. \n Other Platforms are:  linux-rasp-pi-g++, linux-rasp-pi2-g++ and linux-rasp-pi3-vc4-g++", type=str, default=DEFAULT_PLATFORM)
    parser.add_argument("-a", "--all", help="install all optional development packages (Bluetooth, Audio and gstreamer, ...)", action='store_true')
    parser.add_argument("--bluetooth", help="install optional development packages for bluetooth", action='store_true')
    parser.add_argument("--audio", help="install optional development packages for audio", action='store_true')
    parser.add_argument("--database", help="install optional development packages for databases", action='store_true')
    parser.add_argument("--print", help="install optional development packages for printing", action='store_true')
    parser.add_argument("--wayland", help="install optional development packages for wayland support", action='store_true')
    parser.add_argument("--accessibility", help="install optional development packages for accessibility", action='store_true')
    parser.add_argument("--distupgrade", help="edits sources.list and performes dist-upgrade", action='store_true')
    parser.add_argument("--rpiupdate", help="updates the pi's firmware", action='store_true')
    args = parser.parse_args()
    return parser, args


def start_install_dependencies(args):
    
     #install build dependencies
    print("install build dependencies ...")
    subprocess.call(["apt-get", "update"])
    subprocess.call(["apt-get", "install", "-y", "libx11-dev", "libxext-dev", "libxfixes-dev", "libxrender-dev", "libxcb1-dev", "libx11-xcb-dev", "libxcb-glx0-dev", "build-essential", "libfontconfig1-dev", "libdbus-1-dev", "libfreetype6-dev", "libicu-dev", "libinput-dev", "libxkbcommon-dev", "libsqlite3-dev", "libssl-dev", "libpng-dev", "libjpeg-dev", "libglib2.0-dev", "libraspberrypi-dev"])

    #install optional development packages
    if(args.all):
        print("Installing all optional development packages")
        install_bluetooth()
        install_audio()
        install_database()
        install_print()
        install_wayland()
        install_accessibility()
    

    if(args.bluetooth):
        print("installing blutooth support")
        install_bluetooth

    if(args.audio):
        print("installing audio support")
        install_audio()
    
    if(args.database):
        print("installing database support")
        install_database()
    
    if(args.print):
        print("installing printing support")
        install_print()
    
    if(args.wayland):
        print("installing wayland support")
        install_wayland()

    if(args.accessibility):
        print("installing accessibility support")
        install_accessibility()
    
    #setup pi for cross compilation
    print("install dependencies for cross compilation")
    subprocess.call(["apt-get", "-y", "install", "build-dep", "qt4-x11"])

    subprocess.call(["apt-get", "-y", "install", "build-dep", "libqt5gui5"])

    subprocess.call(["apt-get", "-y", "install", "libudev-dev", "libinput-dev", "libts-dev", "libxcb-xinerama0-dev", "libxcb-xinerama0"])


    


def start_install_of_qt(args):

    #download Qt5.10.1 source
    os.chdir(args.downloadpath)
    if not os.path.isfile("qt-everywhere-src-5.10.1.tar.xz") and not os.path.isdir("qt-everywhere-src-5.10.1"):
        print("downloading source ...")
        subprocess.call(["wget", "http://download.qt.io/official_releases/qt/5.10/5.10.1/single/qt-everywhere-src-5.10.1.tar.xz"])
    else:
        print("Source is already there ...")
    #un-tar the source    
    if not os.path.isdir("qt-everywhere-src-5.10.1"):
        print("un-tar will take at least 8mins ...")
        subprocess.call(["tar", "-xf", "qt-everywhere-src-5.10.1.tar.xz"])
    else:
        print("this time no un-tar ...")

    #Create shadow build directory. We will be using /home/pi/build by default.
    if not os.path.exists(args.buildpath):
        print("creating build folder ...")
        os.makedirs(args.buildpath)
        #os.chmod(args.buildpath, 0o777)
        print("set user and group to pi")
        shutil.chown(args.buildpath, user="pi", group="pi")
    os.chdir(args.buildpath)

    #configure the build
    print("building qt now ...")
    print("make will start "+ str(args.jobs) + "jobs")
    os.environ['PKG_CONFIG_LIBDIR'] = "/usr/lib/arm-linux-gnueabihf/pkgconfig"
    os.environ['PKG_CONFIG_SYSROOT_DIR'] = "/"
    
    subprocess.call([args.downloadpath+"/qt-everywhere-src-5.10.1/configure", "-v", "-opengl", "es2", "-eglfs", "-no-gtk", "-qt-xcb", "-device", args.platform, "-device-option", "CROSS_COMPILE=/usr/bin/", "-opensource", "-confirm-license", "-release", "-reduce-exports", "-nomake", "examples", "-no-compile-examples", "-skip", "qtwayland", "-skip", "qtwebengine", "-no-feature-geoservices_mapboxgl", "-qt-pcre", "-ssl", "-evdev", "-prefix", "/opt/Qt5.10.1"])
    print("make process will now be started ...")
    if(args.platform == DEFAULT_PLATFORM) or (args.platform == "linux-rasp-pi3-vc4-g++") or (args.platform == "linux-rasp-pi2-g++"):
        subprocess.call(["make", "--jobs="+str(args.jobs)])
    else:
        subprocess.call(["make", "--jobs=1"])

    subprocess.call(["make", "install"])
    
    os.chdir(args.downloadpath+"/qt-everywhere-src-5.10.1/qtscript")
    subprocess.call(["make"])
    
    print("move qtscript stuff to opt/Qt5.10.1 Folder")
    os.chdir(args.downloadpath+"/qt-everywhere-src-5.10.1/qtscript/lib")
    subprocess.call(["cp", "-av", ".", "/opt/Qt5.10.1/lib"])
    os.chdir(args.downloadpath+"/qt-everywhere-src-5.10.1/qtscript/include")
    subprocess.call(["cp", "-av", ".", "/opt/Qt5.10.1/include"])

    #add to PATH
    print("add qmake to PATH")
    with open('/home/pi/.bashrc', 'a') as file:
        file.write("export PATH=/opt/Qt5.10.1/bin:$PATH \n")
    
    #install qtcreator
    print("installing qtcreator ...")
    subprocess.call(["apt-get", "-y", "install", "qtcreator"])

    #setup pi for cross compilation
    path = "/usr/local/qt5pi"
    print("setup pi for cross compilation")
    os.makedirs(path)
    #os.chmod(path, 0o777)
    shutil.chown(path, user="pi", group="pi")
    for root, dirs, files in os.walk(path):
        for momo in dirs:
            shutil.chown(os.path.join(root,momo), user="pi", group="pi")
        for momo in files:
            shutil.chown(os.path.join(root,momo), user="pi", group="pi")
    os.chmod(path,0o777)


    
    
    with open('/home/pi/.bashrc', 'a') as file:
        file.write("export LD_LIBRARY_PATH=/usr/local/qt5pi/lib:$LD_LIBRARY_PATH \n")
        
    #end
    print("rebooting now ...")
    print("reboot is needed to bashrc is reloaded (Env Variables are exported)")
    os.system('reboot')

    
def distupgrade():
    print("editing sources.list ...")
    for line in fileinput.FileInput("/etc/apt/sources.list", inplace=1):
        line = line.replace("#deb-src", "deb-src")
        print(line)
          
    subprocess.call(["apt-get", "-y", "update"])
    subprocess.call(["apt-get", "-y", "dist-upgrade"])
    print("rebooting now ...")
    os.system('reboot')


def rpiupdate():
    subprocess.call(["rpi-update"])
    print("rebooting now ...")
    os.system('reboot')

    

        

def install_bluetooth():
    subprocess.call(["apt-get", "-y","install", "bluez", "libbluetooth-dev"])
    

def install_audio():
    subprocess.call(["apt-get", "-y","install", "libasound2-dev", "pulseaudio", "libpulse-dev", "libgstreamer1.0-dev", "libgstreamer-plugins-base1.0-dev", "gstreamer1.0-plugins-base", "gstreamer1.0-plugins-good", "gstreamer1.0-plugins-ugly", "gstreamer1.0-plugins-bad", "gstreamer1.0-pulseaudio", "gstreamer1.0-tools", "gstreamer1.0-alsa", "gstreamer-tools"])

def install_database():
    subprocess.call(["apt-get", "-y","install", "libpq-dev", "libmariadbclient-dev"])

def install_print():
    subprocess.call(["apt-get", "-y","install", "libcups2-dev"])
  
def install_wayland():
    subprocess.call(["apt-get", "-y","install", "l4ibwayland-dev"])

def install_accessibility():
    subprocess.call(["apt-get", "-y","install", " libatspi-dev"])


def main():
    if not os.geteuid()==0:
        sys.exit('This script must be run as root!')
    else:   
        parser, args = init_args_parser()
        if args.distupgrade == True or args.rpiupdate == True:
            if (args.distupgrade == True) and (len(sys.argv) == 1):
                distupgrade()
            elif (args.rpiupdate == True) and (len(sys.argv) == 1):
                rpiupdate()
            else:
                print("option --distupdate and --rpiupdate can only be used separately and can't be mixed with other options")
        else:
            start_install_dependencies(args)
            start_install_of_qt(args)

if __name__ == '__main__':
    main()



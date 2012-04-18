__author__ = 'fccoelho'

from fabric.api import *
from fabric.contrib.console import confirm
env.hosts = ["localhost"]


def aptinstall(package):
    """
    Check if package is installed. If not installs it
    """
    if run("dpkg -s %s | grep 'Status:' ; true" % package).find('installed') == -1:
        sudo("apt-get install " + package)

def setup_mongodb():
    """Setup mongodb if it is not installed"""
    if  run("dpkg -s mongodb | grep 'Version:' ; true") >= "1:2.0.3-1ubuntu1":
        aptinstall("mongodb")
    else:
        #TODO: Create users, perhaps use cuisine for this
        sudo("mkdir -p /opt/mongodb")
        with cd("/opt/mongodb"):
            sudo("wget http://fastdl.mongodb.org/linux/mongodb-linux-x86_64-2.0.3.tgz")
            sudo("tar xzf mongodb-linux-x86_64-2.0.3.tgz")
            sudo("rm mongodb-linux-x86_64-2.0.3.tgz ")
            sudo(" ln -s mongodb-linux-x86_64-2.0.3/bin/* /usr/local/bin/")

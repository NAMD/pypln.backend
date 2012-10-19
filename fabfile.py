import os
from fabric.api import cd, run, sudo, settings

USER = "pypln"
HOME = "/srv/pypln/"
LOG_DIR = os.path.join(HOME, "logs/")
PROJECT_ROOT = os.path.join(HOME, "project/")
PROJECT_WEB_ROOT = os.path.join(PROJECT_ROOT, "pypln/web/")
REPO_URL = "https://github.com/NAMD/pypln.git"

def _reload_supervisord():
    # XXX: Why does supervisor's init script exit with 1 on "restart"?
    sudo("service supervisor stop")
    sudo("service supervisor start")

def _checkout_branch():
    with cd(PROJECT_ROOT):
        #TODO: use master branch
        run("git checkout feature/deploy")

def initial_setup():
    setup_dependecies = " ".join(["git-core", "supervisor"])
    sudo("apt-get update")
    sudo("apt-get upgrade -y")
    sudo("apt-get install -y {}".format(setup_dependecies))

    with settings(warn_only=True):
        user_does_not_exist = run("id {}".format(USER)).failed

    if user_does_not_exist:
        sudo("useradd --shell=/bin/bash --home {} --create-home {}".format(
            HOME, USER))
        sudo("mkdir {}".format(LOG_DIR))
        sudo("chown -R {0}:{0} {1}".format(USER, LOG_DIR))
        sudo("passwd {}".format(USER))

    with settings(warn_only=True, user=USER):
        run("git clone {} {}".format(REPO_URL, PROJECT_ROOT))
        _checkout_branch()

    for daemon in ["manager", "pipeliner", "broker"]:
        config_file_path = os.path.join(PROJECT_ROOT,
                "server_config/pypln-{}.conf".format(daemon))
        sudo("ln -sf {} /etc/supervisor/conf.d/".format(config_file_path))

    _reload_supervisord()

def update_nltk_data():
    # FIXME: When we download to the home directory of the user,
    # nltk.downloader knows how to handle already installed packages
    # but this does not work with the --dir flag. That's why, for now,
    # we're downloading to the default location and then copying it to
    # the desired place
    sudo("python -m nltk.downloader all")
    sudo("cp -r /root/nltk_data /usr/share/nltk_data")

def deploy():
    #TODO: Use a virtualenv
    with settings(warn_only=True):
        sudo("supervisorctl stop pypln-manager")
        sudo("supervisorctl stop pypln-broker")
        sudo("supervisorctl stop pypln-pipeliner")

    system_packages = " ".join(["python-setuptools", "python-pip", "python-numpy",
        "build-essential", "python-dev", "mongodb", "pdftohtml"])
    sudo("apt-get install -y {}".format(system_packages))

    with cd(PROJECT_ROOT), settings(user=USER):
        run("git pull")
        _checkout_branch()

    with cd(PROJECT_ROOT):
        sudo("python setup.py install")

    update_nltk_data()

    with cd(PROJECT_WEB_ROOT):
        sudo("pip install -r requirements/project.txt")

        with settings(user=USER):
            run("python {} syncdb --noinput".format(os.path.join(PROJECT_WEB_ROOT,
                    "manage.py")))

    # Aparently we need to restart supervisord after the deploy, or it won't
    # be able to find the processes. This is weird. It should be enough to
    # reload the configs.
    _reload_supervisord()

    #TODO: run("python ./manage.py runserver") with supervisor

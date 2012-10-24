import os
from fabric.api import cd, run, sudo, settings, prefix

USER = "pypln"
HOME = "/srv/pypln/"
LOG_DIR = os.path.join(HOME, "logs/")
PROJECT_ROOT = os.path.join(HOME, "project/")
PROJECT_WEB_ROOT = os.path.join(PROJECT_ROOT, "pypln/web/")
REPO_URL = "https://github.com/NAMD/pypln.git"
ACTIVATE_SCRIPT = os.path.join(PROJECT_ROOT, "bin/activate")

def _reload_supervisord():
    # XXX: Why does supervisor's init script exit with 1 on "restart"?
    sudo("service supervisor stop")
    sudo("service supervisor start")

def _checkout_branch():
    with cd(PROJECT_ROOT):
        #TODO: use master branch
        run("git checkout feature/deploy")

def initial_setup():
    setup_dependecies = " ".join(["git-core", "supervisor", "nginx",
        "python-virtualenv"])
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
        run("virtualenv --system-site-packages {}".format(PROJECT_ROOT))

    for daemon in ["manager", "pipeliner", "broker", "web"]:
        config_file_path = os.path.join(PROJECT_ROOT,
                "server_config/pypln-{}.conf".format(daemon))
        sudo("ln -sf {} /etc/supervisor/conf.d/".format(config_file_path))

    _reload_supervisord()

    nginx_vhost_path = os.path.join(PROJECT_ROOT, "server_config/nginx.conf")
    sudo("ln -sf {} /etc/nginx/sites-enabled/pypln".format(nginx_vhost_path))

def deploy():
    #TODO: Use a virtualenv
    with settings(warn_only=True):
        sudo("supervisorctl stop pypln-manager")
        sudo("supervisorctl stop pypln-broker")
        sudo("supervisorctl stop pypln-pipeliner")
        sudo("supervisorctl stop pypln-web")

    system_packages = " ".join(["python-setuptools", "python-pip", "python-numpy",
        "build-essential", "python-dev", "mongodb", "pdftohtml"])
    sudo("apt-get install -y {}".format(system_packages))

    with prefix("source {}".format(ACTIVATE_SCRIPT)), settings(user=USER), cd(PROJECT_ROOT):
        run("git pull")
        _checkout_branch()
        run("python setup.py install")
        run("python -m nltk.downloader all")

        with cd(PROJECT_WEB_ROOT):
            run("pip install -r requirements/project.txt")

        manage("syncdb --noinput")
        manage("collectstatic --noinput")


    # Aparently we need to restart supervisord after the deploy, or it won't
    # be able to find the processes. This is weird. It should be enough to
    # reload the configs.
    _reload_supervisord()

    sudo("service nginx restart")

def manage(command):
    # FIXME: we need to be in the web root because of path issues that should
    # be fixed
    with prefix("source {}".format(ACTIVATE_SCRIPT)), cd(PROJECT_WEB_ROOT), settings(user=USER):
        manage_script = os.path.join(PROJECT_WEB_ROOT, "manage.py")
        run("python {} {}".format(manage_script, command))

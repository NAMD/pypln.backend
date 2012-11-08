import os
import random
import string
from fabric.api import cd, run, sudo, settings, prefix
from fabric.contrib.files import comment, append

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

def create_db(db_user, db_name, db_host="localhost", db_port=5432):
    # we choose a random password with letters, numbers and some punctuation.
    db_password = ''.join(random.choice(string.ascii_letters + string.digits +\
            '#.,/?@+=') for i in range(32))

    pgpass_path = os.path.join(HOME, ".pgpass")
    pgpass_content = "{}:{}:{}:{}:{}".format(db_user, db_port, db_name,
            db_user, db_password)

    with settings(warn_only=True):
        user_creation = sudo('psql template1 -c "CREATE USER {} WITH CREATEDB ENCRYPTED PASSWORD \'{}\'"'.format(db_user, db_password), user='postgres')

    if not user_creation.failed:
        sudo("echo '{}' > {}".format(pgpass_content, pgpass_path))
        sudo('chown {0}:{0} {1}'.format(USER, pgpass_path))
        sudo('chmod 600 {}'.format(pgpass_path))
        sudo('createdb "{}" -O "{}"'.format(db_name, db_user), user='postgres')

def install_system_packages():
    packages = " ".join(["python-setuptools", "python-pip",
        "python-numpy", "build-essential", "python-dev", "mongodb",
        "pdftohtml", "git-core", "supervisor", "nginx", "python-virtualenv",
        "postgresql"])
    sudo("apt-get update")
    sudo("apt-get install -y {}".format(packages))

def initial_setup():
    install_system_packages()
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

    # Commenting out the path to the socket that supervisorctl uses should make
    # it fallback to it's default of connecting on localhost:9001.  This should
    # allow non-root users to control the running processes.
    supervisor_conf = "/etc/supervisor/supervisord.conf"
    comment(supervisor_conf,
                "^serverurl=unix:///var/run//supervisor.sock .*",
                use_sudo=True, char=";")
    append(supervisor_conf, ["[inet_http_server]", "port=127.0.0.1:9001"],
                use_sudo=True)

    _reload_supervisord()

    nginx_vhost_path = os.path.join(PROJECT_ROOT, "server_config/nginx.conf")
    sudo("ln -sf {} /etc/nginx/sites-enabled/pypln".format(nginx_vhost_path))

    create_db('pypln', 'pypln')

def deploy():
    with prefix("source {}".format(ACTIVATE_SCRIPT)), settings(user=USER), cd(PROJECT_ROOT):
        run("git pull")
        _checkout_branch()
        run("python setup.py install")
        run("python -m nltk.downloader all")

        with cd(PROJECT_WEB_ROOT):
            run("pip install -r requirements/project.txt")

        manage("syncdb --noinput")
        manage("collectstatic --noinput")

        run("supervisorctl reload")

def manage(command):
    # FIXME: we need to be in the web root because of path issues that should
    # be fixed
    with prefix("source {}".format(ACTIVATE_SCRIPT)), cd(PROJECT_WEB_ROOT), settings(user=USER):
        manage_script = os.path.join(PROJECT_WEB_ROOT, "manage.py")
        run("python {} {}".format(manage_script, command))

#
# Copyright 2012 NAMD-EMAP-FGV
#
# This file is part of PyPLN. You can get more information at: http://pypln.org/.
#
# PyPLN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPLN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPLN.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import os
import random
import string
from fabric.api import cd, run, sudo, settings, prefix, abort
from fabric.contrib.files import comment, append
from fabric.contrib.console import confirm

USER = "pypln"
HOME = "/srv/pypln/"
LOG_DIR = os.path.join(HOME, "logs/")
BACKUP_DIR = os.path.join(HOME, "backups/")
PROJECT_ROOT = os.path.join(HOME, "project/")
PYPLN_BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
PYPLN_WEB_ROOT = os.path.join(PROJECT_ROOT, "web/")
DJANGO_PROJECT_ROOT = os.path.join(PYPLN_WEB_ROOT, "pypln/web/")
BACKEND_REPO_URL = "https://github.com/NAMD/pypln.backend.git"
WEB_REPO_URL = "https://github.com/NAMD/pypln.web.git"
ACTIVATE_SCRIPT = os.path.join(PROJECT_ROOT, "bin/activate")

def _reload_supervisord():
    # XXX: Why does supervisor's init script exit with 1 on "restart"?
    sudo("service supervisor stop")
    sudo("service supervisor start")

def _update_repository(rev):
    run("git remote update")
    run("git checkout {}".format(rev))
    run("git reset --hard {}".format(rev))

def _update_code(rev="master"):
    with cd(PYPLN_BACKEND_ROOT):
        _update_repository(rev)
    with cd(PYPLN_WEB_ROOT):
        _update_repository(rev)

def create_db(db_user, db_name, db_host="localhost", db_port=5432):
    # we choose a random password with letters, numbers and some punctuation.
    db_password = ''.join(random.choice(string.ascii_letters + string.digits +\
            '#.,/?@+=') for i in range(32))

    pgpass_path = os.path.join(HOME, ".pgpass")
    pgpass_content = "{}:{}:{}:{}:{}".format(db_host, db_port, db_name,
            db_user, db_password)

    with settings(warn_only=True):
        user_creation = sudo('psql template1 -c "CREATE USER {} WITH CREATEDB ENCRYPTED PASSWORD \'{}\'"'.format(db_user, db_password), user='postgres')

    if not user_creation.failed:
        sudo("echo '{}' > {}".format(pgpass_content, pgpass_path))
        sudo('chown {0}:{0} {1}'.format(USER, pgpass_path))
        sudo('chmod 600 {}'.format(pgpass_path))
        sudo('createdb "{}" -O "{}"'.format(db_name, db_user), user='postgres')

def _create_secret_key_file():
    valid_chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = ''.join([random.choice(valid_chars) for i in range(50)])
    secret_key_file_path = os.path.join(HOME, ".secret_key")
    sudo("echo '{}' > {}".format(secret_key, secret_key_file_path))
    sudo('chown {0}:{0} {1}'.format(USER, secret_key_file_path))

def db_backup():
    now = datetime.datetime.now()
    filename = now.strftime("pypln_%Y-%M-%d_%H-%m-%S.backup")
    backup_file_path = os.path.join(BACKUP_DIR, filename)
    with settings(user=USER):
        run("pg_dump -Fc -o -f {}".format(backup_file_path))

def db_restore(filename, db_name="pypln"):
    message = "Are you sure you want to replace the current database with {}"
    if not confirm(message.format(filename), default=False):
        abort("Aborting database restore...")

    backup_file_path = os.path.join(BACKUP_DIR, filename)
    sudo("pg_restore -d template1 -C {}".format(backup_file_path), user="postgres")

def install_system_packages():
    packages = " ".join(["python-setuptools", "python-pip",
        "python-numpy", "build-essential", "python-dev", "mongodb",
        "pdftohtml", "git-core", "supervisor", "nginx", "python-virtualenv",
        "postgresql", "python-psycopg2"])
    sudo("apt-get update")
    sudo("apt-get install -y {}".format(packages))

def initial_setup(rev="master"):
    install_system_packages()
    # Updating virtualenv is specially important since the default changed
    # to not giving access to system python packages and the option to disable
    # this didn't exist in old versions.
    sudo("pip install --upgrade virtualenv")

    with settings(warn_only=True):
        user_does_not_exist = run("id {}".format(USER)).failed

    if user_does_not_exist:
        sudo("useradd --shell=/bin/bash --home {} --create-home {}".format(
            HOME, USER))
        sudo("mkdir {}".format(LOG_DIR))
        sudo("chown -R {0}:{0} {1}".format(USER, LOG_DIR))
        sudo("mkdir {}".format(BACKUP_DIR))
        sudo("chown -R {0}:{0} {1}".format(USER, BACKUP_DIR))
        sudo("passwd {}".format(USER))
        _create_secret_key_file()

    with settings(warn_only=True, user=USER):
        run("git clone {} {}".format(WEB_REPO_URL, PYPLN_WEB_ROOT))
        run("git clone {} {}".format(BACKEND_REPO_URL, PYPLN_BACKEND_ROOT))
        _update_code(rev)
        run("virtualenv --system-site-packages {}".format(PROJECT_ROOT))

    for daemon in ["router", "pipeliner", "broker", "web"]:
        config_file_path = os.path.join(PYPLN_BACKEND_ROOT,
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

    nginx_vhost_path = os.path.join(PYPLN_BACKEND_ROOT, "server_config/nginx.conf")
    sudo("ln -sf {} /etc/nginx/sites-enabled/pypln".format(nginx_vhost_path))
    sudo("service nginx restart")

    create_db('pypln', 'pypln')

def deploy(rev="master"):
    with prefix("source {}".format(ACTIVATE_SCRIPT)), settings(user=USER), cd(PROJECT_ROOT):
        _update_code(rev)
        with cd(PYPLN_BACKEND_ROOT):
            run("python setup.py install")

        with cd(PYPLN_WEB_ROOT):
            run("python setup.py install")

        #TODO: We need to put all pypln.web requirements in one place.
        with cd(DJANGO_PROJECT_ROOT):
            run("pip install -r requirements/project.txt")

        run("python -m nltk.downloader all")

        manage("syncdb --noinput")
        manage("collectstatic --noinput")

        run("supervisorctl reload")

def manage(command, environment="production"):
    # FIXME: we need to be in the web root because of path issues that should
    # be fixed
    with prefix("source {}".format(ACTIVATE_SCRIPT)), cd(DJANGO_PROJECT_ROOT), settings(user=USER):
        manage_script = os.path.join(DJANGO_PROJECT_ROOT, "manage.py")
        run("python {} {} --settings=settings.{}".format(manage_script,
            command, environment))

import os
import time

from contextlib import contextmanager as _contextmanager

import yaml

from fabric.api import run, cd, env, lcd, sudo, put, local
from fabric.context_managers import settings, prefix
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.decorators import roles

env.activate = 'source /opt/paysys/python/bin/activate'
app_user = 'paysys'

@_contextmanager
def virtualenv():
    with prefix(env.activate):
        yield

# Loads an environment from a yaml config and stores in env.config
def loadenv(environment=None):
    """Loads an environment config file for role definitions"""
    if environment:
        with open('./%s.yml' % environment, 'r') as f:
            yaml_config = yaml.load(f)
            for key, value in yaml_config.iteritems():
                setattr(env, key, value)

@roles('application')
def setup(wipe=False):
    """Sets up payment system"""
    dependencies = (
        "wget",
        "build-essential",
        "git",
        "openssl-devel",
        "zlib-devel",
        "bzip2-devel",
        "python-virtualenv",
        "rabbitmq-server",
        "mysql-server",
        "npm"
    )

    wipe = bool(wipe)
    if wipe or not exists('/opt/paysys'):
        sudo('rm -rf /opt/paysys')

    sudo('useradd -d /opt/paysys %s || true' % app_user)
    sudo('yum install -q -y %s' % ' '.join(dependencies))
    sudo('npm install -g bower')

    if not exists('/opt/python2.7'):
        with cd('/tmp'):
            run('wget https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz')
            run('wget https://bootstrap.pypa.io/get-pip.py')
            run('tar -xf Python-2.7.8.tgz')
        with cd('/tmp/Python-2.7.8'):
            run('./configure --prefix=/opt/python2.7')
            run('make -j4')
            sudo('make install')

    with settings(sudo_user=app_user):
        if not exists('/opt/paysys/python'):
            sudo('virtualenv -p /opt/python2.7/bin/python /opt/paysys/python')
        sudo('mkdir -p /opt/paysys/{logs,beat,uploads,rules} || true')
        with virtualenv():
            sudo('pip install gunicorn supervisor')

    sudo('mkdir -p /etc/supervisor.d')
    put('./files/supervisord-init', '/etc/init.d/supervisord', use_sudo=True, mode=0755)
    put('./files/supervisord.conf', '/etc/supervisord.conf', use_sudo=True)
    sudo('service supervisord start')
    sudo('chkconfig supervisord on')
    sudo('service rabbitmq-server start')
    sudo('chkconfig rabbitmq-server on')
    sudo('service mysqld start')
    sudo('chkconfig mysqld on')
    sudo('mysqladmin create pay')
    sudo('mysql -e \'GRANT ALL ON pay.* TO `payApp`@localhost IDENTIFIED BY "apple1010"\'')

    sudo('mysqladmin create paysys')

    if env.get('sql_seedfile', False):
        if os.path.exists(sql_seedfile):
            put(sql_seedfile, '/tmp/seedDB.sql')
            sudo('mysql paysys < seedDB.sql')

@roles('application')
def deploy(version='master'):
    """Deploys payment code to application server"""
    if not exists('/opt/paysys'):
        setup()

    sudo('mkdir /opt/paysys/.ssh; chmod 0700 /opt/paysys/.ssh')
    put('./files/id_deploy', '/opt/paysys/.ssh/id_rsa', mode=0400, use_sudo=True)
    sudo('chown -R %s. /opt/paysys/.ssh' % app_user)

    with settings(sudo_user=app_user), cd('/opt/paysys'):
        sudo('ssh-keyscan github.com >> ~/.ssh/known_hosts')
        sudo('git clone git@github.com:dgaedcke/paymentSystem.git /opt/paysys/current')
        with cd('/opt/paysys/current'):
            sudo('git checkout %s' % version)
            with virtualenv():
                sudo('pip install -r requirements/common.txt')
        with cd('/opt/paysys/current/source'):
            with virtualenv():
                sudo('pip install --editable .')
        if not exists('/opt/paysys/rules/__init__.py'):
            sudo('/bin/cp -r /opt/paysys/current/rules-initial/* /opt/paysys/rules/')
        sudo('ln -sf /opt/paysys/rules /opt/paysys/current/source/rules')

    put('./files/supervisor-payment.conf', '/etc/supervisor.d/payment.conf', use_sudo=True)
    sudo('rm -rf /opt/paysys/current/source/web/static/.cache')

    with settings(sudo_user=app_user), cd('/opt/paysys/current/source/web/static'):
        sudo('bower install --config.interactive=false -s')

    put('./files/local_settings.py', '/opt/paysys/current/source/configuration/local_settings.py', use_sudo=True)

    sudo('rm -rf /opt/paysys/current/source/rules')
    sudo('service supervisord restart')
    sudo('/opt/paysys/python/bin/supervisorctl restart payment')
    sudo('/opt/paysys/python/bin/supervisorctl restart celery')
    sudo('/opt/paysys/python/bin/supervisorctl restart celerybeat')
    sudo('/opt/paysys/python/bin/supervisorctl status payment')
    sudo('/opt/paysys/python/bin/supervisorctl status celery')
    sudo('/opt/paysys/python/bin/supervisorctl status celerybeat')
    cleanupBuilds()

@roles('application')
def cleanupBuilds():
    sudo('/bin/rm -rf `/bin/ls -t /opt/paysys/builds/ | /usr/bin/tail -n +5`')
    sudo('/bin/rm -f /tmp/payment-*.tar.gz')
    local('/bin/rm -f /tmp/payment-*.tar.gz')

def syncReports(clean=True):
    execute(getReports)
    execute(sendReports)
    execute(archiveReports)
    if clean:
        execute(cleanReports)

@roles('reports')
def getReports():
    rsync_project('/incoming/exftp/payments/examiner/' + env.config['environment'] + '/', 'examiner', upload=False)
    rsync_project('/incoming/exftp/payments/axs/' + env.config['environment'] + '/', 'axs', upload=False)
    rsync_project('/incoming/exftp/payments/rowdy/' + env.config['environment'] + '/', 'rowdy', upload=False)
    if env.config['environment'] == 'staging':
        rsync_project('/incoming/exftp/payments/examiner/prod/', 'examiner', upload=False)
        rsync_project('/incoming/exftp/payments/axs/prod/', 'axs', upload=False)
        rsync_project('/incoming/exftp/payments/rowdy/prod/', 'rowdy', upload=False)

@roles('application')
def sendReports():
    rsync_project('/opt/paysys/ftp/examiner/', 'examiner/', upload=True)
    rsync_project('/opt/paysys/ftp/axs/', 'axs/', upload=True)
    rsync_project('/opt/paysys/ftp/rowdy/', 'rowdy/', upload=True)
    sudo('/bin/find /opt/paysys/ftp -user "jenkins" -exec /bin/chgrp paysys {} \;')
    sudo('/bin/find /opt/paysys/ftp -user "jenkins" -exec /bin/chmod g+rw {} \;')

@roles('reports')
def archiveReports():
    backup_time =  time.strftime('%Y%m%d%H%M%S')
    sudo('/bin/mkdir -p /backups', shell=False)
    sudo('/bin/tar -czvf /backups/payments-' + env.config['environment'] + '-' + backup_time + '.tar.gz  /incoming/exftp/payments/*/' + env.config['environment'] + '', shell=False)

@roles('reports')
def cleanReports():
    sudo('/bin/rm -rf /incoming/exftp/payments/examiner/' + env.config['environment'] + '/*', shell=False)
    sudo('/bin/rm -rf /incoming/exftp/payments/axs/' + env.config['environment'] + '/*', shell=False)
    sudo('/bin/rm -rf /incoming/exftp/payments/rowdy/' + env.config['environment'] + '/*', shell=False)
    local('/bin/rm -rf examiner axs rowdy')

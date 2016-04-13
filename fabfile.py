from fabric.api import *
from fabric.context_managers import settings
from fabric.contrib.project import rsync_project
from fabric.decorators import roles
from fabric.api import run, cd, env, roles, lcd
from contextlib import contextmanager as _contextmanager
from fabric.contrib.files import exists
from pprint import pprint
from time import sleep
import time
import yaml
import fabric

config_dir = '/var/www/cap/examiner/current/payments/config/'

env.directory = '/opt/paysys/current'
env.activate = 'source /opt/paysys/python/bin/activate'
app_user = 'paysys'

@_contextmanager
def virtualenv():
    with prefix(env.activate):
        yield

# Loads an environment from a yaml config and stores in env.config
def loadenv(environment = ''):
    """Loads an environment config file for role definitions"""
    with open(config_dir + environment + '.yaml', 'r') as f:
        env.config = yaml.load(f)
        env.roledefs = env.config['roledefs']

@roles('application')
def setup(wipe=False):
    """Sets up payment system"""
    wipe = bool(wipe)
    if wipe or not exists('/opt/paysys'):
        sudo('rm -rf /opt/paysys')
    sudo('mkdir -p /opt/paysys')
    sudo('chown ' + env.user + ':' + env.user + ' /opt/paysys')
    if not exists('/opt/python2.7'):
        with cd('/tmp'):
            run('wget https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz')
            run('tar -zxf Python-2.7.8.tgz')
        with cd('/tmp/Python-2.7.8'):
            run('./configure --prefix=/opt/python2.7')
            run('make')
            sudo('make install')
    if not exists('/opt/paysys/python'):
        run('virtualenv -p /opt/python2.7/bin/python /opt/paysys/python')
    sudo('chown ' + env.user + ':' + env.user + ' /opt/paysys')
    run('mkdir -p /opt/paysys/logs')
    sudo('chown ' + app_user + ':' + app_user + ' /opt/paysys/logs')
    run('mkdir -p /opt/paysys/beat')
    sudo('chown ' + app_user + ':' + app_user + ' /opt/paysys/beat')
    run('mkdir -p /opt/paysys/uploads')
    sudo('chown ' + app_user + ':' + app_user + ' /opt/paysys/uploads')
    if not exists('/opt/paysys/rules'):
        run('mkdir -p /opt/paysys/rules')
        sudo('chown -R ' + app_user + ':' + app_user + ' /opt/paysys/rules')
    with virtualenv():
        run('pip install gunicorn supervisor')
    sudo('mkdir -p /etc/supervisor.d')
    put(config_dir + '/files/supervisord-init', '/etc/init.d/supervisord', use_sudo=True, mode=0755)
    put(config_dir + '/files/supervisord.conf', '/etc/supervisord.conf', use_sudo=True)
    sudo('/sbin/service supervisord start')
    sudo('chkconfig supervisord on')

@roles('application')
def deploy(version='master'):
    """Deploys payment code to application server"""
    if not exists('/opt/paysys'):
        setup()
    local('rm -rf paymentSystem')
    local('/usr/bin/git clone git@github.com:dgaedcke/paymentSystem.git')
    env.release = time.strftime('%Y%m%d%H%M%S')
    with lcd('paymentSystem'):
        local('git checkout ' + version)
        local('git archive --format=tar ' + version + ' | gzip > /tmp/payment-' + env.release + '.tar.gz')
    put('/tmp/payment-' + env.release + '.tar.gz', '/tmp/')
    run('mkdir -p /opt/paysys/builds/' + env.release)
    with cd('/opt/paysys/builds/' + env.release):
        run('tar -zxf /tmp/payment-' + env.release + '.tar.gz')
    run('rm /opt/paysys/current')
    run('ln -sf /opt/paysys/builds/' + env.release + ' /opt/paysys/current')
    put(config_dir + '/files/' + env.config['environment'] + '/local_settings.py', '/opt/paysys/current/source/configuration/local_settings.py')
    with cd('/opt/paysys/current'):
        with virtualenv():
            run('pip install -r requirements/common.txt')
    with cd('/opt/paysys/current/source'):
        with virtualenv():
            run('pip install --editable .')
    put(config_dir + '/files/' + env.config['environment'] + '/supervisor-payment.conf', '/etc/supervisor.d/payment.conf', use_sudo=True)
    with cd('/opt/paysys/current/source/web/static'):
        run('rm -rf ~/.cache')
        run('bower install --config.interactive=false -s')
    if not exists('/opt/paysys/rules/__init__.py'):
        sudo('/bin/cp -r /opt/paysys/current/rules-initial/* /opt/paysys/rules/')
        sudo('chown -R ' + app_user + ':' + app_user + ' /opt/paysys/rules')
    run('rm -rf /opt/paysys/current/source/rules')
    run('ln -sf /opt/paysys/rules /opt/paysys/current/source/rules')
    sudo('/opt/paysys/python/bin/supervisorctl reread')
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

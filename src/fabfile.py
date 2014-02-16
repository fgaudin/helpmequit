from fabric.operations import local, run, sudo
from fabric.state import env
from fabric.context_managers import cd, prefix
import os

env.hosts = ['alf@alfbox.net']

base_dir = '/var/www/sites/iquit'
code_dir = 'src/helpmequit'

def tag(message='Deployment'):
    previous_tag = local('git tag | sort -n | tail -1', capture=True) or '0'
    new_tag = 'v%d' % (int(previous_tag.lstrip('v')) + 1)
    local('git tag -a %s -m "%s"' % (new_tag, message))
    local('git push')
    local('git push --tags')
    return new_tag

def pull(tag):
    with cd(os.path.join(base_dir, code_dir)):
        run('git checkout master')
        run('git pull')
        run('git checkout %s' % (tag))

def requirements():
    with prefix('source %s/bin/activate' % (base_dir)):
        run('pip install -r %s' % os.path.join(base_dir, code_dir, 'src', 'requirements.txt'))

def migrate():
    with cd(os.path.join(base_dir, code_dir, 'src', 'iquitsupportit')):
        with prefix('source %s/bin/activate' % (base_dir)):
            run('python manage.py migrate --settings=iquitsupportit.settings_prod')

def reload():
    sudo('/etc/init.d/apache2 reload')

def deploy():
    deploy_tag = tag()
    pull(deploy_tag)
    requirements()
    migrate()
    reload()


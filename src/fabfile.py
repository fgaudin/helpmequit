from fabric.operations import local, run
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
    local('git push origin %s' % new_tag)
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
    pass

def reload():
    pass

def deploy():
    tag = tag()
    pull(tag)
    requirements()
    migrate()
    reload()


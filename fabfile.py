from fabric.operations import local, run, sudo
from fabric.state import env
from fabric.context_managers import cd, prefix
import os
from fabric.decorators import hosts

git_host = ['1276965@git.dc0.gpaas.net']
console_host = ['1276965@console.dc0.gpaas.net']

base_dir = '/var/www/sites/iquit'
code_dir = 'src/helpmequit'

def tag(message='Deployment'):
    previous_tag = local('git tag | cut -d"v" -f2 | sort -n | tail -1', capture=True) or '0'
    new_tag = 'v%d' % (int(previous_tag) + 1)
    local('git tag -a %s -m "%s"' % (new_tag, message))
    local('git push')
    local('git push --tags')
    return new_tag

def push_to_gandi():
    local('git push gandi master')
    local('git push gandi--tags')

@hosts(git_host)
def deploy_tag(tag):
    run('deploy default.git')

def migrate():
    with cd(os.path.join(base_dir, code_dir, 'src', 'iquitsupportit')):
        with prefix('source %s/bin/activate' % (base_dir)):
            run('python manage.py migrate --settings=iquitsupportit.settings_prod')


def deploy():
    deploy_tag = tag()
    push_to_gandi()
    deploy_tag(deploy_tag)
    # migrate()


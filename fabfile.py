from fabric.operations import local
from fabric.context_managers import lcd


def tag(message='Deployment'):
    previous_tag = local('git tag | cut -d"v" -f2 | sort -n | tail -1', capture=True) or '0'
    new_tag = 'v%d' % (int(previous_tag) + 1)
    local('git tag -a %s -m "%s"' % (new_tag, message))
    local('git push')
    local('git push --tags')
    return new_tag

def collect_static():
    with lcd('src'):
        local('python manage.py collectstatic --noinput --settings=iquitsupportit.settings_prod')

def deploy_tag(deploy_tag):
    local('gondor deploy primary master')

def deploy():
    t = tag()
    collect_static()
    deploy_tag(t)


from fabric.api import task, run, env, put
from fabric.contrib.files import exists
from fabric.colors import *

env.hosts = ['192.168.66.6']
env.user = 'root'

# custom env
env.app_root = '/var/www/sampleapp'
env.web_public = env.app_root + '/web'
env.img_path = env.app_root + '/web/images'
env.js_path = env.web_public + '/javascript'
env.git_repository = 'https://github.com/kemmeter/sampleApp.git'


@task
def setup():
    """Basic Server Setup"""
    print(yellow('\nBasic server setup\n\n'))
    run('apt-get -y install apache2 php5 git curl ruby-compass')
    run('echo "ServerName localhost" >> /etc/apache2/apache2.conf')
    # clone my dotfiles
    run('rm -rf ~/.dotfiles')
    run('cd ~ && git clone https://github.com/kemmeter/dotfiles .dotfiles')
    # get the git prompt bash extention
    run('cd ~ && curl https://raw.github.com/git/git/master/contrib/completion/git-prompt.sh -o ~/.git-prompt.sh')
    # symlink
    run('rm -f ~/.bashrc && ln -s ~/.dotfiles/bashrc ~/.bashrc')
    run('rm -f ~/.vimrc && ln -s ~/.dotfiles/vimrc ~/.vimrc')

    print(green('\nServer setup complete :)\n\n'))


@task
def deploy():
    """Start the deployment"""

    if exists(env.app_root):
        print(yellow('\npulling from %s...\n\n' % env.git_repository))
        run('cd %s && git pull' % env.app_root)

    else:
        print(yellow('\ncloning %s...\n\n' % env.git_repository))
        run('git clone %s %s' % (env.git_repository, env.app_root))

    upload_media()
    get_latest_jquery()
    compile_compass()
    set_ownership(env.app_root)
    set_vhosts()

    print(green('\nDeployment complete :)\n\n'))


def upload_media():
    """Upload the media files"""
    print(yellow('\nuploading mediafiles...\n\n'))
    run('mkdir -p /var/www/sampleapp/web/images/')
    put('/Users/robert/Sites/github/kemmeter/sampleApp/web/images/*', '/var/www/sampleapp/web/images/')


def get_latest_jquery():
    """download the latest jQuery Version"""
    print(yellow('\ndownloading latest jquery file...\n\n'))
    run('mkdir -p /var/www/sampleapp/web/javascript')
    run('cd %s && curl http://code.jquery.com/jquery-latest.min.js > jquery.min.js' %
        '/var/www/sampleapp/web/javascript')


def compile_compass():
    """Compass compile"""
    print(yellow('\ncompiling sass files with compass...\n\n'))
    run('cd /var/www/sampleapp && compass clean && compass compile')


def set_ownership(path):
    """
    Sets the given path recursively to www-data user and group
    """
    print(yellow('\nsetting ownership for %s to www-data:www-data...\n\n' % path))
    run('chown -R www-data:www-data %s' % path)


def set_vhosts():
    """
    makes vhost config files available for apache
    enables vhost
    restarts apache
    """
    print(yellow('\nsetting up vhosts...\n\n'))
    vhost_file = '/etc/apache2/sites-available/sampleapp'

    run('cp %s/vhosts/sampleapp %s' % (env.app_root, vhost_file))
    run('a2ensite sampleapp')
    run('apache2ctl restart')
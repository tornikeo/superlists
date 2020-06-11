from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, sudo
import random

REPO_URL = 'https://github.com/tornikeo/superlists.git'
DEBUG = False

# NOTE: To run type: fab deploy:host=USER@SERVER --sudo-password=PASSWORD

def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)
    _configure_nginx_and_gunicorn(source_folder)

def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('database', 'static', 'virtualenv', 'source'):
        run(f'mkdir -p {site_folder}/{subfolder}')

def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run(f'cd {source_folder} && git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')
    current_commit = local('git log -n 1 --format=%H', capture=True)
    run(f'cd {source_folder} && git reset --hard {current_commit}')

def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/superlists/settings.py'
    sed(settings_path, 'DEBUG = True', f'DEBUG = {DEBUG}')
    sed(settings_path, 
        "ALLOWED_HOSTS =.+$",
        f'ALLOWED_HOSTS = ["{site_name}"]',
    )
    secret_key_file = source_folder + '/superlists/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, f'SECRET_KEY = "{key}"')
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
        run(f'python3.6 -m venv {virtualenv_folder}')
    # TODO: pip or pip3?
    run(f'{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt')

def _update_static_files(source_folder):
    # TODO: python or python3? 
    run(
        f'cd {source_folder} &&'
        ' ../virtualenv/bin/python manage.py collectstatic --noinput'
    )

def _update_database(source_folder):
    run(f'cd {source_folder} &&'
        ' ../virtualenv/bin/python manage.py migrate --noinput'
    )


def _configure_nginx_and_gunicorn(source_folder):
    sudo(f'sed s/SITENAME/{env.host}/g '
        f' {source_folder}/deploy_tools/nginx.template.conf '
        f' | tee /etc/nginx/sites-available/{env.host} '
    )
    sudo(f' ln -sfn /etc/nginx/sites-available/{env.host} '
        f' /etc/nginx/sites-enabled/{env.host} ',
    )
    sudo(f'sed s/SITENAME/{env.host}/g '
        f' {source_folder}/deploy_tools/gunicorn-systemd.template.service '
        f' |  tee /etc/systemd/system/gunicorn.{env.host}.service '
    )
    sudo(' systemctl daemon-reload && '
        ' systemctl reload nginx && '
        f' systemctl enable gunicorn.{env.host} &&'
        f' systemctl start gunicorn.{env.host}',
    )
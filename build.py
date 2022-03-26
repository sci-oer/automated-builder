#!/usr/bin/env python3

"""Automated sci-oer builder.

This command will take the base sci-oer image and create a custom image pre filled
with all the specified content.

Usage:
  ./build.py [options] [ --example=<examples>... ]
  ./build.py (-h | --help)

Options:
 -j --jupyter-repo=<jupyter>        The git repository to fetch the builtin jupyter notebooks from.
 -l --lectures-repo=<lecture>       The git repository to fetch the builtin lessons content.
 -e --example=<examples>...         A git repository to fetch a worked example from. One repository per exmple, one branch per version.

General git options:
  --ssh-key=<private_key>           The SSH private key to use. WARNING: this will be passed in plain text, use a read-only key if possible.
  --key-file=<key_file>             The path to the ssh private key that should be used.

WikiJS options:
  -w --wiki-repo=<wiki>             The git repository to fetch the wiki content from.
  --wiki-title=<title>              The title to use for the wiki website.
  --wiki-user=<wiki_user>           The git username to use when cloning the the wikijs content.
  --wiki-password=<wiki_pass>       The git password to use when cloning the wikiks content.
  --wiki-branch=<wiki_branch>       The name of the branch that the wiki content should be loaded from. [default: main]
  --wiki-no-verify                  Do not verify the ssl certificate when cloning the wikijs wiki.

Docker options:
  -t --tag=<tag>                    The docker tag to use for the generated image. [default: sci-oer/custom:latest]
  -b --base=<base>                  The base image to use [default: marshallasch/oo-resources:main]
  --no-pull                         Don't pull the base image first

Other interface options:
  -h --help                         Show this help message.
  -V --version                      Show the current version.
  -v --verbose                      Show verbose log messages.
  -d --debug                        Show debug log messages.
""" # noqa E501

import docker
import random
import string
import tempfile
import os
import sys
import shutil
import platform
import requests
import json
from git import Repo  # noqa: I900
import time
from docopt import docopt
import subprocess
import colorlog
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import datetime


from version import __version__  # noqa: I900


SSH_KEY_ENV = 'SSH_KEY'
SSH_KEY_FILE_ENV = 'SSH_KEY_FILE'


# this is the api token that has been built into the base oo-resources container
API_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjEsImdycCI6MSwiaWF0IjoxNjQyOTcyMTk5LCJleHAiOjE3Mzc2NDQ5OTksImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.xkvgFfpYw2OgB0Z306YzVjOmuYzrKgt_fZLXetA0ThoAgHNH1imou2YCh-JBXSBCILbuYvfWMSwOhf5jAMKT7O1QJNMhs5W0Ls7Cj5tdlOgg-ufMZaLH8X2UQzkD-1o3Dhpv_7hs9G8xt7qlqCz_-DwroOGUGPaGW6wrtUfylUyYh86V9eJveRJqzZXiGFY3n6Z3DuzIVZtz-DoCHMaDceSG024BFOD-oexMCnAxTpk5OalEhwucaYHS2sNCLpmwiEGHSswpiaMq9-JQasVJtQ_fZ9yU_ZZLBlc0AJs1mOENDTI6OBZ3IS709byqxEwSPnWaF_Tk7fcGnCYk-3gixA" # noqa E501

_LOGGER = logging.getLogger(__name__)


def _make_opts(args):

    opts = {}
    for arg, val in args.items():
        opt = arg.replace('--', '').replace('-', '_')
        opts[opt] = val
    return opts


def _get_git_version():
    """Check that `git` is accessible and return its version."""
    try:
        return subprocess.check_output(['git', '--version']).strip().decode()
    except FileNotFoundError:
        return None


def _gen_version():
    extra = ''
    if _get_git_version() and os.path.isdir('.git'):
        rev_parse = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode()
        describe = subprocess.check_output(['git', 'describe', '--always', '--dirty']).strip().decode()  # noqa: E501

        extra = rev_parse[:12]
        extra += '-dirty' if describe.endswith('-dirty') else ''

        extra = f' ({extra})'

    return f'autobuild v{__version__}{extra}'


def fetch_latest(client, repository, **kwargs):
    _LOGGER.info(f'pulling latest version of the "{repository}" docker image, this may take a while...')
    client.images.pull(repository)
    _LOGGER.info('Done pulling the latest docker image')


def start_container(client, volume, image, **kwargs):
    name = f'auto-build-tmp-{generate_random_string()}'

    _LOGGER.info(f'starting `{image}` container as `{name}`...')
    onHost = not check_if_container(client)
    container = client.containers.run(image,
                                      publish_all_ports=onHost,
                                      name=name,
                                      tty=True,
                                      detach=True,
                                      volumes=[f'{volume.name}:/course']
                                      )

    return container


def stop_container(container, **kwargs):
    _LOGGER.info('stopping docker container...')
    container.stop()


def delete_container(container, **kwargs):
    _LOGGER.info('Deleteing setup container...')
    container.remove()


def generate_random_string(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def create_volume(client, name):
    return client.volumes.create(f'{name}-{generate_random_string()}')


def delete_volume(volume, **kwargs):
    _LOGGER.info('Deleteing setup volume...')
    volume.remove()


def clone_repo(repo, name, dir, **kwargs):
    folder = os.path.join(dir, name)

    if repo is None:
        os.mkdir(folder)
        _LOGGER.info(f'no repository specified for "{name}", skipping...')
        return

    Repo.clone_from(repo, folder)

    # make sure that the git directory is removed before it gets loaded into the image
    shutil.rmtree(os.path.join(folder, '.git'))


def setup_tmp_build(**kwargs):
    dir = tempfile.TemporaryDirectory()
    shutil.copy2(os.path.join('custom', 'Dockerfile'), os.path.join(dir.name, 'Dockerfile'))
    return dir


def cleanup_build(dir):
    _LOGGER.info('removing temporary setup folder...')
    dir.cleanup()


def build_image(client, dir, tag="sci-oer:custom", base=None, **kwargs):

    args = {
        'BASE_IMAGE': base,
        'BUILD_DATE': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    _LOGGER.info(f'Building custom image with name `{tag}`...')
    client.images.build(path=dir, tag=tag, buildargs=args)
    _LOGGER.info('Done building custom image.')


def extract_db(container, dir, **kwargs):
    _LOGGER.info('extracting wikijs database...')
    f = open(os.path.join(dir, 'database.sqlite.tar'), 'wb')
    bits, stat = container.get_archive('/course/wiki/database.sqlite')

    for chunk in bits:
        f.write(chunk)
    f.close()


def create_network(client, **kwargs):
    return client.networks.create(generate_random_string(), attachable=True)


def get_current_container(client, **kwargs):
    return client.containers.get(platform.node())


class Authentication:
    ssh_key = ""
    username = ""
    password = ""

    def __init__(self, username, password, ssh_key):
        self.username = username
        self.password = password
        self.ssh_key = ssh_key

    def authType(self):
        if self.ssh_key != "":
            return 'ssh'

        return 'basic'


class Repository:
    uri = ""
    branch = "main"
    verify_ssl = True

    auth = Authentication("", "", "")

    def __init__(self, uri, branch, verify):
        self.uri = uri
        self.branch = branch
        self.verify_ssl = verify


def set_wiki_contents(host, repo, **kwargs):
    configure_wiki_repo(host, True, repo, **kwargs)
    import_wiki_repo(host, **kwargs)
    remove_git_repo(host, **kwargs)


def remove_git_repo(host, **kwargs):
    configure_wiki_repo(host, False, Repository("", "", ""),  **kwargs)


def sync_wiki_repo(host, **kwargs):
    query = """mutation Storage {
        storage {
            executeAction (handler: "sync", targetKey: "git" ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query, **kwargs)


def import_wiki_repo(host, **kwargs):
    query = """mutation Storage {
        storage {
            executeAction (handler: "importAll", targetKey: "git" ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    _LOGGER.warning('Importing all the wiki content from the git repository, this may take a while...')  # noqa: E501
    api_call(host, query, **kwargs)
    _LOGGER.warning('Done importing wiki content')


def set_wiki_title(host, title, **kwargs):

    if title is None:
        _LOGGER.info('Custom title has not been configured skipping...')
        return

    query = """mutation Site ($title: String){
        site {
            updateConfig (title: $title ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query, variables={"title": title}, **kwargs)


def load_ssh_key(keyValue, keyFile):

    env_key = os.getenv(SSH_KEY_ENV)
    env_key_file = os.getenv(SSH_KEY_FILE_ENV)

    keyFileContents = load_ssh_key_from_file(keyFile)
    envKeyFileContents = load_ssh_key_from_file(env_key_file)

    if keyValue is not None:
        _LOGGER.debug('Using ssh key specified with cli key flag')
        return keyValue
    elif keyFileContents != "":
        _LOGGER.debug('Using ssh key specified with cli keyfile flag')
        return keyFileContents
    elif env_key is not None:
        _LOGGER.debug(f'Using ssh key specified with {SSH_KEY_ENV} env variable')
        return env_key
    elif envKeyFileContents != "":
        _LOGGER.debug(f'Using ssh key specified with {SSH_KEY_FILE_ENV} env variable')
        return envKeyFileContents
    else:
        _LOGGER.debug('no ssh key has been specified')
        return ""


def load_ssh_key_from_file(keyFile):

    if keyFile is None or not os.path.isfile(keyFile):
        _LOGGER.info(f'the specified ssh key file `{keyFile}` does not exist')
        return ""

    with open(keyFile, 'r') as f:
        return f.read()


def configure_wiki_repo(host, enabled, repo, **kwargs):
    query = """mutation ($targets: [StorageTargetInput]!) {
        storage {
            updateTargets(targets: $targets) {
                responseResult {
                    succeeded
                    errorCode
                    message
                }
            }
        }
    }"""

    variables = {"targets": [{
            "isEnabled": enabled,
            "key": "git",
            "config": [
                {
                    "key": "authType",
                    "value": f'{{"v": "{repo.auth.authType()}"}}'
                }, {
                    "key": "repoUrl",
                    "value": f'{{"v": "{repo.uri}"}}'
                }, {
                    "key": "branch",
                    "value": f'{{"v": "{repo.branch}"}}'
                }, {
                    "key": "sshPrivateKeyMode",
                    "value": '{"v": "contents"}'
                }, {
                    "key": "sshPrivateKeyPath",
                    "value": '{"v": ""}'
                }, {
                    "key": "sshPrivateKeyContent",
                    "value": f'{{"v": "{repo.auth.ssh_key}"}}'
                }, {
                    "key": "verifySSL",
                    "value": f'{{"v": "{repo.verify_ssl}"}}'
                }, {
                    "key": "basicUsername",
                    "value": f'{{"v": "{repo.auth.username}"}}'
                }, {
                    "key": "basicPassword",
                    "value": f'{{"v": "{repo.auth.password}"}}'
                }, {
                    "key": "defaultEmail",
                    "value": '{ "v": "sci-oer@example.com"}'
                }, {
                    "key": "defaultName",
                    "value": '{ "v": "Open Educational Resource Container"}'
                }, {
                    "key": "localRepoPath",
                    "value": '{ "v": "./data/repo"}'
                }, {
                    "key": "gitBinaryPath",
                    "value": '{ "v": ""}'
                }
            ],
            "mode": "pull",
            "syncInterval": "PT5M"
        }
        ]
    }

    api_call(host, query, variables=variables,  **kwargs)


def dissable_api(host, **kwargs):
    query = """mutation Authentication {
        authentication {
            setApiState (enabled: false ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query, **kwargs)


def api_call(host, query, variables="{}", port=3000):

    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    body = {
        "query": query,
        "variables": variables
    }

    r = requests.post(f'http://{host}:{port}/graphql', json=body, headers=headers)

    if r.status_code == 200:
        _LOGGER.info("Made change successfully")
    else:
        _LOGGER.error(json.dumps(r.json(), indent=2))
        raise Exception(f"Query failed to run with a {r.status_code}.")


def check_if_container(client):

    try:
        get_current_container(client)
        return True
    except docker.errors.NotFound:
        return False


def get_wiki_port(isContainer, container):

    if isContainer:
        return '3000'

    wikiPort = int(container.ports.get('3000/tcp')[0]['HostPort'])
    _LOGGER.info(f'Wiki running on port {wikiPort}')

    return wikiPort


def wait_for_wiki_to_be_ready(host, port=3000, **kwargs):
    http = requests.Session()
    retry_strategy = Retry(total=5, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http.mount('http://', adapter)
    r = http.get(f'http://{host}:{port}')

    if r.status_code == 200:
         _LOGGER.info('wiki is ready')


def main(opts, **kwargs):

    client = docker.from_env()

    if not opts['no_pull']:
        fetch_latest(client, opts['base'])

    network = create_network(client)

    this = None
    containerized = check_if_container(client)

    if containerized:
        _LOGGER.debug("Currently running in a docker container")
        this = get_current_container(client)
        network.connect(this)

    volume = create_volume(client, "course")
    container = start_container(client, volume, opts['base'])
    network.connect(container)

    container.reload()

    port = get_wiki_port(containerized, container)
    host = '127.0.0.1' if not containerized else container.name

    wait_for_wiki_to_be_ready(host, port)

    dir = setup_tmp_build()
    
    clone_repo(opts['jupyter_repo'], 'jupyter', dir.name)
    clone_repo(opts['lectures_repo'], 'lectures', dir.name)

    examples = os.path.join(dir.name, 'practiceProblems')
    os.makedirs(examples, exist_ok=True)
    for example in opts['example']:
        clone_repo(example, example.split('/')[-1][:-4], examples)
    else:
        _LOGGER.info("no example repos were specified, skipping...")

    if opts['wiki_repo'] is not None:
        sshKey = load_ssh_key(opts['ssh_key'], opts['key_file'])
        wikiRepo = Repository(opts['wiki_repo'], opts['wiki_branch'], not opts['wiki_no_verify'])
        wikiRepo.auth = Authentication(opts['wiki_user'], opts['wiki_password'], sshKey)

        set_wiki_contents(host, wikiRepo, port=port)
    else:
        _LOGGER.info('wiki content repository has not been set. skipping...')

    set_wiki_title(host, opts['wiki_title'], port=port)
    dissable_api(host, port=port)

    stop_container(container)
    network.disconnect(container)

    extract_db(container, dir.name)

    delete_container(container)
    delete_volume(volume)

    build_image(client, dir.name, tag=opts['tag'], base=opts['base'])
    cleanup_build(dir)

    if containerized:
        network.disconnect(this)
    network.remove()

    _LOGGER.info('Done.')


if __name__ == "__main__":

    args = docopt(__doc__)

    if args['--debug']:
        args['--verbose'] = True
        log_fmt = '%(log_color)s[%(levelname)s] (%(module)s) (%(funcName)s): %(message)s'
        log_level = logging.DEBUG
    elif args['--verbose']:
        log_fmt = '%(log_color)s%(levelname)s: %(message)s'
        log_level = logging.INFO
    else:
        log_fmt = '%(log_color)s%(levelname)s: %(message)s'
        log_level = logging.WARNING
        sys.tracebacklimit = 0

    if sys.platform == 'win32':
        log_colors = {
            'DEBUG': 'bold_blue',
            'INFO': 'bold_purple',
            'WARNING': 'yellow,bold',
            'ERROR': 'red,bold',
            'CRITICAL': 'red,bold,bg_white',
        }
    else:
        log_colors = {
            'DEBUG': 'blue',
            'INFO': 'purple',
            'WARNING': 'yellow,bold',
            'ERROR': 'red,bold',
            'CRITICAL': 'red,bold,bg_white',
        }

    log_fmtter = colorlog.TTYColoredFormatter(fmt=log_fmt, stream=sys.stderr,
                                              log_colors=log_colors)

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_fmtter)
    logging.basicConfig(level=log_level, handlers=[log_handler])

    _LOGGER.debug('version: %s', _gen_version())
    _LOGGER.debug('platform: %s', platform.platform())

    if args['--version']:
        print(_gen_version())
        sys.exit(0)

    opts = _make_opts(args)
    _LOGGER.info(opts)

    main(opts)

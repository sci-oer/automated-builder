#!/usr/bin/env python3

"""Automated sci-oer builder

Usage:
  ./build.py [options] [ --example=<examples>... ]
  ./build.py (-h | --help)

Options:
  -t --tag=<tag>                    The docker tag to use for the generated image. [default: sci-oer/custom:latest]
  -b --base=<base>                  The base image to use [default: marshallasch/oo-resources:main]
  -w --wiki-repo=<wiki>             The git repository to fetch the wiki content from.
  -j --jupyter-repo=<jupyter>       The git repository to fetch the builtin jupyter notebooks from.
  -e --example=<examples>...        A git repository to fetch a worked example from. One repository per exmple, one branch per version.
  --ssh-key=<private_key>           The SSH private key to use. WARNING: this will be passed in plain text, use a read-only key if possible.
  --key-file=<key_file>             The path to the ssh private key that should be used.

Other interface options:
  -h --help         Show this help message.
  -V --version      Show the current version.
  -v --verbose      Show verbose log messages.
  -d --debug        Show debug log messages.
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
from git import Repo
import time
from docopt import docopt
import subprocess
import colorlog
import logging

from version import __version__


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
    client.images.pull(repository)


def start_container(client, volume, image, **kwargs):
    name = f'auto-build-tmp-{generate_random_string()}'

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
    container.stop()


def delete_container(container, **kwargs):
    container.remove()


def generate_random_string(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def create_volume(client, name):
    return client.volumes.create(f'{name}-{generate_random_string()}')


def delete_volume(volume, **kwargs):
    volume.remove()


def setup_tmp_build(notebook_repo, **kwargs):

    dir = tempfile.TemporaryDirectory()

    shutil.copy2(os.path.join('custom', 'Dockerfile'), os.path.join(dir.name, 'Dockerfile'))
    Repo.clone_from(notebook_repo, os.path.join(dir.name, 'builtin'))

    return dir


def cleanup_build(dir):
    dir.cleanup()


def build_image(client, dir, tag="sci-oer:custom", **kwargs):
    client.images.build(path=dir.name, tag=tag)


def extract_db(container, dir, **kwargs):
    f = open(os.path.join(dir.name, 'database.sqlite.tar'), 'wb')
    bits, stat = container.get_archive('/course/wiki/database.sqlite')
    print(stat)

    for chunk in bits:
        f.write(chunk)
    f.close()


def create_network(client, **kwargs):
    return client.networks.create(generate_random_string(), attachable=True)


def get_current_container(client, **kwargs):
    return client.containers.get(platform.node())


def create_page(host, page, **kwargs):
    q = """mutation Page {{
        pages {{
            create (
                content: "{}",
                description: "{}",
                path: "{}",
                tags: [{}],
                title: "{}",
                editor: "code",
                isPublished: true,
                isPrivate: false,
                locale: "en"
            ) {{
                responseResult {{ succeeded, errorCode, slug, message }}
            }}
        }}
    }}
    """

    query = q.format(page.content, page.description, page.path, page.tags, page.title)

    api_call(host, query, **kwargs)


def dissable_api(host, **kwargs):
    query = """mutation Authentication {
        authentication {
            setApiState (enabled: false ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query, **kwargs)


def api_call(host, query, port=3000):

    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    r = requests.post(f'http://{host}:{port}/graphql', json={"query": query}, headers=headers)

    print(r.json)
    print(r.text)
    print(r.content)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        raise Exception(f"Query failed to run with a {r.status_code}.")


class Page:
    content = ""
    description = ""
    path = ""
    tags = ""
    title = ""

    def __init__(self, title, path, description, tags, content):
        self.title = title
        self.path = path
        self.description = description
        self.tags = '"' + '", "'.join(tags) + '"'
        self.content = content


def load_wiki_files(dir):

    pages = []

    # recursivly look at all file in dir
    # filename is path
    # parse the preamble out of each file

    page = Page("Cool Sample Page",
                "/test",
                "This is a super cool sample page",
                ["test", "sample"],
                "my cool markdown content"
                )
    pages.append(page)

    return pages


def upload_wiki(pages, hostname, **kwargs):

    for page in pages:
        create_page(hostname, page, **kwargs)


def check_if_container(client):

    try:
        get_current_container(client)
        return True
    except docker.errors.NotFound:
        return False


def get_wiki_port(isContainer, container):

    if isContainer:
        return '3000'

    _LOGGER.info(container)
    ports = container.ports
    _LOGGER.info(ports)

    return int(container.ports.get('3000/tcp')[0]['HostPort'])


def main(opts, **kwargs):

    client = docker.from_env()

    fetch_latest(client, opts['base'])

    network = create_network(client)

    this = None
    containerized = check_if_container(client)

    if containerized:
        this = get_current_container(client)
        network.connect(this)

    volume = create_volume(client, "course")
    container = start_container(client, volume, opts['base'])
    network.connect(container)

    print("waiting a 5 seconds to make sure the container is up")
    time.sleep(5)
    container.reload()

    dir = setup_tmp_build(opts['jupyter_repo'])

    # TODO:clone the wiki here and make the api calls to import all the wiki data

    port = get_wiki_port(containerized, container)
    host = '127.0.0.1' if not containerized else container.name

    pages = load_wiki_files("tmp")
    upload_wiki(pages, host, port=port)
    dissable_api(host, port=port)

    stop_container(container)
    network.disconnect(container)

    extract_db(container, dir)

    delete_container(container)
    delete_volume(volume)

    build_image(client, dir, tag=opts['tag'])
    cleanup_build(dir)

    if containerized:
        network.disconnect(this)
    network.remove()


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
    print(opts)

    main(opts)

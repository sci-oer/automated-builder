#!/usr/bin/env python3

"""Automated sci-oer builder.

This command will take the base sci-oer image and create a custom image pre filled
with all the specified content.

Usage:
  scioer-builder [options] [ --example=<examples>... ]
  scioer-builder (-h | --help)

Options:
 -j --jupyter-repo=<jupyter>        The git repository to fetch the builtin jupyter notebooks from. The default branch will be used.
 -l --lectures-repo=<lecture>       The git repository to fetch the builtin lessons content. The default branch will be used.
 --lectures-directory=<lecture>     A path to the directory containing the builtin lessons content. Cannot be used with `--lectures-repo`.
 -e --example=<examples>...         A list of repositories to fetch worked examples from. The default branch will be used.

General git options:
  --key-file=<key_file>             The path to the ssh private key that should be used.
  --no-verify-host                  Sets the `StrictHostKeyChecking=no` option when cloning git repos, may be needed to non-interactivly accept git clones using ssh.
  --keep-git                        Will not remove the `.git` folder in repositories if this is set. This can be used to create an instructor version of the container.

WikiJS options:
  -w --wiki-git-repo=<wiki>         The git repository to fetch the wiki content from.
  --wiki-git-user=<wiki_user>       The git username to use when cloning the the wikijs content.
  --wiki-git-password=<wiki_pass>   The git password to use when cloning the wikiks content.
  --wiki-title=<title>              The title to use for the wiki website.
  --wiki-git-branch=<wiki_branch>   The name of the branch that the wiki content should be loaded from. [default: main]
  --wiki-git-no-verify              Do not verify the ssl certificate when cloning the wikijs wiki.

Docker options:
  -t --tag=<tag>                    The docker tag to use for the generated image. This should exclude the registry portion. [default: sci-oer/custom:latest]
  -b --base=<base>                  The base image to use [default: marshallasch/java-resource:latest]
  --no-pull                         Don't pull the base image first
  --push                            Push the image to the DockerHub registry.
  --multi-arch                      Build the docker image for amd64 and arm64. [default: False]

Other interface options:
  -h --help                         Show this help message.
  -V --version                      Show the current version.
  -v --verbose                      Show verbose log messages.
  -d --debug                        Show debug log messages.
  -i --interactive                  Interactivly prompt for all of the options.
"""  # noqa E501

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
import copy
import subprocess

from docopt import docopt
import colorlog
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import datetime
import importlib.resources as pkg_resources

try:
    from git import Repo  # noqa: I900
except:
    sys.exit("Can not run, `git` must be installed on the system.")

from .__version__ import __version__  # noqa: I900
from .prompt import prompt, yesno, prompt_list

SSH_KEY_FILE_ENV = "SSH_KEY_FILE"

# this is the api token that has been built into the base-resource container
API_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjEsImdycCI6MSwiaWF0IjoxNjQyOTcyMTk5LCJleHAiOjE3Mzc2NDQ5OTksImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.xkvgFfpYw2OgB0Z306YzVjOmuYzrKgt_fZLXetA0ThoAgHNH1imou2YCh-JBXSBCILbuYvfWMSwOhf5jAMKT7O1QJNMhs5W0Ls7Cj5tdlOgg-ufMZaLH8X2UQzkD-1o3Dhpv_7hs9G8xt7qlqCz_-DwroOGUGPaGW6wrtUfylUyYh86V9eJveRJqzZXiGFY3n6Z3DuzIVZtz-DoCHMaDceSG024BFOD-oexMCnAxTpk5OalEhwucaYHS2sNCLpmwiEGHSswpiaMq9-JQasVJtQ_fZ9yU_ZZLBlc0AJs1mOENDTI6OBZ3IS709byqxEwSPnWaF_Tk7fcGnCYk-3gixA"  # noqa E501

_LOGGER = logging.getLogger(__name__)


def _make_opts(args):

    opts = {}
    for arg, val in args.items():
        opt = arg.replace("--", "").replace("-", "_")
        opts[opt] = val
    return opts


def ask_interactive(opts):
    input = copy.deepcopy(opts)

    # general image setup  information
    print("## Information about the container to be built.")
    input["tag"] = prompt(
        "Enter the name of the image to be built, including the tag: ",
        default=input["tag"],
    )
    input["base"] = prompt(
        "Enter the base image that should be used for this course:",
        default=input["base"],
    )
    input["no_pull"] = not yesno(
        "Should a the latest base image be fetched?",
        default="no" if input["no_pull"] else "yes",
    )

    input["push"] = yesno(
        "Do you want to push the generated image to dockerhub?",
        default="yes" if input["push"] else "no",
    )

    print("")
    print("## General options for cloning git repositories.")
    input["no_verify_host"] = yesno(
        "Should the SSH host keys be verified?",
        default="no" if input["no_verify_host"] else "yes",
    )
    input["keep_git"] = yesno(
        "Should the git histories be kept after they are cloned?",
        default="yes" if input["keep_git"] else "no",
    )
    input["key_file"] = prompt(
        "Enter the path to the SSH private key used to clone the git repos if one is being used:",
        default=input["key_file"],
    )

    print("")
    print("## Information about the wiki to be created.")
    input["wiki_title"] = prompt(
        "Enter the title for the Wiki:", default=input["wiki_title"]
    )
    input["wiki_git_repo"] = prompt(
        "Enter the git repository URL for the wiki:", default=input["wiki_git_repo"]
    )
    input["wiki_git_branch"] = prompt(
        "Enter the branch name for the wiki repository:",
        default=input["wiki_git_branch"],
    )

    isSSH = yesno("Do you want to clone the wiki repository using ssh?", default="yes")
    if not isSSH:
        input["wiki_git_user"] = prompt(
            "Enter the git username for cloning the wiki contents:",
            default=input["wiki_git_user"],
        )
        input["wiki_git_password"] = prompt(
            "Enter the git password for cloning the wiki contents",
            default=input["wiki_git_password"],
        )

    input["wiki_git_no_verify"] = yesno(
        "Should the SSL certificates be verified when cloning the wiki?",
        default="no" if input["wiki_git_no_verify"] else "yes",
    )

    print("")
    print("## Where the rest of the content is being loaded from.")
    input["jupyter_repo"] = prompt(
        "Enter the git repository that holds the Jupyter Notebook files (leave blank if not being used)",
        default=input["jupyter_repo"],
    )
    input["lectures_repo"] = prompt(
        "Enter the git repository that holds the Jupyter Lecture video files (leave blank if not being used)",
        default=input["lectures_repo"],
    )
    input["lectures_directory"] = prompt(
        "Enter the directory that contains the Jupyter Lecture video files (leave blank if not being used)",
        default=input["lectures_directory"],
    )

    input["example"] = prompt_list(
        "Enter a git repository that contains an example project"
    )

    return input


def fetch_latest(client, repository, **kwargs):
    _LOGGER.info(
        f'pulling latest version of the "{repository}" docker image, this may take a while...'
    )
    client.images.pull(repository)
    _LOGGER.info("Done pulling the latest docker image")


def start_container(client, volume, image, keyFile, **kwargs):
    name = f"auto-build-tmp-{generate_random_string()}"

    volumes = [f"{volume.name}:/course"]
    if keyFile[0] != "" and keyFile[1] != "":
        volumes.append(f"{keyFile[0]}:{keyFile[1]}:ro")

    _LOGGER.info(f"starting `{image}` container as `{name}`...")
    onHost = not check_if_container(client)
    container = client.containers.run(
        image,
        publish_all_ports=onHost,
        name=name,
        tty=True,
        detach=True,
        volumes=volumes,
    )

    return container


def change_key_permissions(container, keyFile, **kwargs):
    _LOGGER.info(
        "Copying the SSH key within the container to set the correct ownership"
    )
    container.exec_run(f'sudo cp "{keyFile}" "{keyFile}.CONTAINER"')
    container.exec_run(f'sudo chown 1000:1000 "{keyFile}.CONTAINER"')


def stop_container(container, **kwargs):
    _LOGGER.info("stopping docker container...")
    container.stop()


def delete_container(container, **kwargs):
    _LOGGER.info("Deleteing setup container...")
    container.remove()


def generate_random_string(length=10):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


def create_volume(client, name):
    return client.volumes.create(f"{name}-{generate_random_string()}")


def push_image(
    client: docker.client, registry: string, image: docker.models.images.Image
):

    toPush = image.tags[0]
    if registry is not None:
        toPush = f"{registry}/{toPush}"
        image.tag(toPush)

    try:
        # this can also return a generator to be used for a progress bar
        client.images.push(toPush)
    except:
        _LOGGER.error(
            "Failed to push the image to the registry, are you sure you have properly authenticated with the remote registry"
        )


def delete_volume(volume, **kwargs):
    _LOGGER.info("Deleteing setup volume...")
    volume.remove()


def clone_repo(repo, name, dir, keep_git=False, **kwargs):
    folder = os.path.join(dir, name)

    if repo.uri is None:
        os.mkdir(folder)
        _LOGGER.info(f'no repository specified for "{name}", skipping...')
        return
    else:
        _LOGGER.info(f'cloning repository; "{name}"...')

    git_ssh_cmd = ""
    if repo.isSSH():
        git_ssh_cmd = f'ssh {"-o StrictHostKeyChecking=no " if not repo.verify_host else " "}-i {repo.auth.ssh_file}'
    Repo.clone_from(repo.uri, folder, env=dict(GIT_SSH_COMMAND=git_ssh_cmd))

    if not keep_git:
        # make sure that the git directory is removed before it gets loaded into the image
        shutil.rmtree(os.path.join(folder, ".git"))


def setup_tmp_build(**kwargs):
    dir = tempfile.TemporaryDirectory()

    with pkg_resources.path("builder.data", "Dockerfile") as template:
        shutil.copy2(template, os.path.join(dir.name, "Dockerfile"))
    return dir


def cleanup_build(dir):
    _LOGGER.info("removing temporary setup folder...")
    dir.cleanup()


def build_multi_arch(
    client, dir, tag="sci-oer:custom", base=None, push=False, **kwargs
):

    args = {
        "BASE_IMAGE": base,
        "BUILD_DATE": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    _LOGGER.info(f"Building custom image with name `{tag}`...")

    # platforms = 'linux/amd64,linux/arm64,linux/amd64/v2,linux/arm/v7,linux/arm/v6,linux/386'
    platforms = "linux/amd64,linux/arm64"

    buildArgs = ""
    for k, v in args.items():
        buildArgs = f"{buildArgs}--build-arg {k}={v} "

    push = "" if not push else "--push"

    cmd = f"docker buildx build --progress=plain --platform {platforms} --tag {tag} {push} {buildArgs} {dir}"
    _LOGGER.debug(f"build command: `{cmd}`")
    subprocess.run(cmd, shell=True, check=True)
    _LOGGER.info("Done building custom image.")


def build_single_arch(client, dir, tag="sci-oer:custom", base=None, **kwargs):

    args = {
        "BASE_IMAGE": base,
        "BUILD_DATE": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    _LOGGER.info(f"Building custom image with name `{tag}`...")

    image, logs = client.images.build(path=dir, tag=tag, buildargs=args)
    _LOGGER.info("Done building custom image.")

    return image


def extract_db(container, dir, **kwargs):
    _LOGGER.info("extracting wikijs database...")
    f = open(os.path.join(dir, "database.sqlite.tar"), "wb")
    bits, stat = container.get_archive("/course/wiki/database.sqlite")

    for chunk in bits:
        f.write(chunk)
    f.close()


def create_network(client, **kwargs):
    return client.networks.create(generate_random_string(), attachable=True)


def get_current_container(client, **kwargs):
    return client.containers.get(platform.node())


class Authentication:
    username = ""
    password = ""
    ssh_file = ""

    def __init__(self, username, password, ssh_file=""):
        self.username = username or ""
        self.password = password or ""
        self.ssh_file = ssh_file


class Repository:
    uri = ""
    branch = "main"
    verify_ssl = True
    verify_host = True

    auth = Authentication("", "")

    def __init__(self, uri, branch, verify_ssl, verify_host=True):
        self.uri = uri
        self.branch = branch
        self.verify_ssl = verify_ssl
        self.verify_host = verify_host

    def isSSH(self):
        return not self.uri.startswith("https")


def set_wiki_contents(host, repo, keep_git=False, **kwargs):
    configure_wiki_repo(host, True, repo, **kwargs)
    sync_wiki_repo(host, **kwargs)
    import_wiki_repo(host, **kwargs)

    if not keep_git:
        _LOGGER.info("removing git repo from config")
        remove_git_repo(host, **kwargs)


def remove_git_repo(host, **kwargs):
    configure_wiki_repo(host, False, Repository("", "", ""), **kwargs)


def sync_wiki_repo(host, **kwargs):
    query = """mutation Storage {
        storage {
            executeAction (handler: "sync", targetKey: "git" ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    _LOGGER.warning(
        "Syncing all the wiki content from the git repository, this may take a while..."
    )  # noqa: E501
    api_call(host, query, **kwargs)
    _LOGGER.warning("Done syncing wiki content")


def import_wiki_repo(host, **kwargs):
    query = """mutation Storage {
        storage {
            executeAction (handler: "importAll", targetKey: "git" ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    _LOGGER.warning(
        "Importing all the wiki content from the git repository, this may take a while..."
    )  # noqa: E501
    api_call(host, query, **kwargs)
    _LOGGER.warning("Done importing wiki content")


def set_wiki_title(host, title, **kwargs):

    if title is None:
        _LOGGER.info("Custom title has not been configured skipping...")
        return

    query = """mutation Site ($title: String){
        site {
            updateConfig (title: $title ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query, variables={"title": title}, **kwargs)


def load_ssh_key(keyFile):

    env_key_file = os.getenv(SSH_KEY_FILE_ENV)

    keyFileContents = load_ssh_key_from_file(keyFile)
    envKeyFileContents = load_ssh_key_from_file(env_key_file)

    if keyFileContents != "":
        _LOGGER.debug("Using ssh key specified with cli keyfile flag")
        return keyFile
    elif envKeyFileContents != "":
        _LOGGER.debug(f"Using ssh key specified with {SSH_KEY_FILE_ENV} env variable")
        return env_key_file
    else:
        _LOGGER.debug("no ssh key has been specified")
        return ""


def load_ssh_key_from_file(keyFile):

    if keyFile is None or not os.path.isfile(keyFile):
        _LOGGER.info(f"the specified ssh key file `{keyFile}` does not exist")
        return ""

    with open(keyFile, "r") as f:
        _LOGGER.info(f"found ssh key file: `{keyFile}`")
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

    variables = {
        "targets": [
            {
                "isEnabled": True,
                "key": "git",
                "mode": "pull",
                "syncInterval": "PT5M",
                "config": [
                    {
                        "key": "authType",
                        "value": f'{{"v": "{"ssh" if repo.isSSH() else "basic"}"}}',
                    },
                    {"key": "repoUrl", "value": f'{{"v": "{repo.uri}"}}'},
                    {"key": "branch", "value": f'{{"v": "{repo.branch}"}}'},
                    {
                        "key": "sshPrivateKeyMode",
                        "value": '{"v": "path"}',
                    },
                    {
                        "key": "sshPrivateKeyPath",
                        "value": f'{{"v": "{repo.auth.ssh_file}.CONTAINER"}}',
                    },
                    {
                        "key": "sshPrivateKeyContent",
                        "value": '{"v": ""}',
                    },
                    {
                        "key": "verifySSL",
                        "value": f'{{"v": {"true" if repo.verify_ssl else "false"}}}',
                    },
                    {
                        "key": "basicUsername",
                        "value": f'{{"v": "{repo.auth.username if repo.auth.username is not None else "" }"}}',
                    },
                    {
                        "key": "basicPassword",
                        "value": f'{{"v": "{repo.auth.password if repo.auth.password is not None else "" }"}}',
                    },
                    {"key": "defaultEmail", "value": '{ "v": "sci-oer@example.com"}'},
                    {
                        "key": "defaultName",
                        "value": '{ "v": "Open Educational Resource Container"}',
                    },
                    {"key": "localRepoPath", "value": '{ "v": "./data/repo"}'},
                    {"key": "gitBinaryPath", "value": '{ "v": ""}'},
                ],
            }
        ]
    }

    api_call(host, query, variables=variables, **kwargs)


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

    body = {"query": query, "variables": variables}

    r = requests.post(f"http://{host}:{port}/graphql", json=body, headers=headers)

    payload = r.json()
    payload = payload["data"][list(payload["data"].keys())[0]]
    succeeded = payload[list(payload.keys())[0]]["responseResult"]["succeeded"]
    message = payload[list(payload.keys())[0]]["responseResult"]["message"]

    if r.status_code == 200 and succeeded:
        _LOGGER.info(message or "API call was successful")
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
        return "3000"

    wikiPort = int(container.ports.get("3000/tcp")[0]["HostPort"])
    _LOGGER.info(f"Wiki running on port {wikiPort}")

    return wikiPort


def wait_for_wiki_to_be_ready(host, port=3000, **kwargs):
    http = requests.Session()
    retry_strategy = Retry(total=5, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http.mount("http://", adapter)
    r = http.get(f"http://{host}:{port}")

    if r.status_code == 200:
        _LOGGER.info("wiki is ready")


def get_real_key_path(container, keyName):

    mounts = [m for m in container.attrs["Mounts"] if m["Destination"] == keyName]

    if len(mounts) != 0:
        return mounts[0]["Source"]
    return ""


def run(opts, **kwargs):

    # Checking incompatible arguments

    if opts["lectures_repo"] is not None and opts["lectures_directory"] is not None:
        _LOGGER.error(
            "Cannot specify both `--lectures-repo` and `--lectures-directory`, only one can be used at a time."
        )
        sys.exit("Incompatible arguments")

    sshKeyFile = load_ssh_key(os.path.expanduser(opts["key_file"]))
    if sshKeyFile != "":
        sshKeyFile = os.path.realpath(sshKeyFile)

    # starting main builder logic
    try:
        client = docker.from_env()
    except:
        _LOGGER.error(
            "failed to connect to docker, check that Docker is running on the host."
        )
        sys.exit("Docker is not running")

    if not opts["no_pull"]:
        fetch_latest(client, opts["base"])

    network = create_network(client)

    this = None
    containerized = check_if_container(client)

    realKey = sshKeyFile
    if containerized:
        _LOGGER.debug("Currently running in a docker container")
        this = get_current_container(client)
        network.connect(this)

        realKey = get_real_key_path(this, opts["key_file"])

    volume = create_volume(client, "course")
    container = start_container(
        client,
        volume,
        opts["base"],
        [realKey, sshKeyFile],
    )

    if containerized:
        network.connect(container)

    container.reload()

    port = get_wiki_port(containerized, container)
    host = "127.0.0.1" if not containerized else container.name

    try:
        wait_for_wiki_to_be_ready(host, port)
    except:
        _LOGGER.error("Requests timed out, container failed to start.")

        stop_container(container)
        if containerized:
            network.disconnect(container)

        delete_container(container)
        delete_volume(volume)
        return

    dir = setup_tmp_build()

    gitAuthentication = Authentication(
        opts["wiki_git_user"],
        opts["wiki_git_password"],
        sshKeyFile,
    )

    jupyterRepo = Repository(
        opts["jupyter_repo"], None, True, not opts["no_verify_host"]
    )
    jupyterRepo.auth = gitAuthentication

    lecturesRepo = Repository(
        opts["lectures_repo"], None, True, not opts["no_verify_host"]
    )
    lecturesRepo.auth = gitAuthentication

    clone_repo(jupyterRepo, "jupyter", dir.name, keep_git=opts["keep_git"])

    if opts["lectures_directory"]:
        shutil.copytree(opts["lectures_directory"], os.path.join(dir.name, "lectures"))
    else:
        clone_repo(lecturesRepo, "lectures", dir.name, keep_git=opts["keep_git"])

    examples = os.path.join(dir.name, "practiceProblems")
    os.makedirs(examples, exist_ok=True)

    for example in opts["example"]:
        exampleRepo = Repository(example, None, True, not opts["no_verify_host"])
        exampleRepo.auth = gitAuthentication
        clone_repo(
            exampleRepo,
            example.split("/")[-1][:-4] if len(opts["example"]) > 1 else ".",
            examples,
            keep_git=opts["keep_git"],
        )
        break
    else:
        _LOGGER.info("no example repos were specified, skipping...")

    if opts["wiki_git_repo"] is not None:
        wikiRepo = Repository(
            opts["wiki_git_repo"],
            opts["wiki_git_branch"],
            not opts["wiki_git_no_verify"],
        )
        wikiRepo.auth = gitAuthentication

        if sshKeyFile:
            change_key_permissions(container, sshKeyFile)
        set_wiki_contents(host, wikiRepo, port=port, keep_git=opts["keep_git"])
    else:
        _LOGGER.info("wiki content repository has not been set. skipping...")

    set_wiki_title(host, opts["wiki_title"], port=port)
    dissable_api(host, port=port)

    stop_container(container)
    if containerized:
        network.disconnect(container)

    extract_db(container, dir.name)

    delete_container(container)
    delete_volume(volume)

    if opts["multi_arch"]:
        _LOGGER.info("Starting multi platform build")
        build_multi_arch(
            client, dir.name, tag=opts["tag"], base=opts["base"], push=opts["push"]
        )
    else:
        _LOGGER.info("Starting single platform build")
        build_single_arch(client, dir.name, tag=opts["tag"], base=opts["base"])

    cleanup_build(dir)

    if containerized:
        network.disconnect(this)
    network.remove()

    _LOGGER.info("Done.")


def main():
    args = docopt(__doc__)

    if args["--debug"]:
        args["--verbose"] = True
        log_fmt = (
            "%(log_color)s[%(levelname)s] (%(module)s) (%(funcName)s): %(message)s"
        )
        log_level = logging.DEBUG
    elif args["--verbose"]:
        log_fmt = "%(log_color)s%(levelname)s: %(message)s"
        log_level = logging.INFO
    else:
        log_fmt = "%(log_color)s%(levelname)s: %(message)s"
        log_level = logging.WARNING
        sys.tracebacklimit = 0

    if sys.platform == "win32":
        log_colors = {
            "DEBUG": "bold_blue",
            "INFO": "bold_purple",
            "WARNING": "yellow,bold",
            "ERROR": "red,bold",
            "CRITICAL": "red,bold,bg_white",
        }
    else:
        log_colors = {
            "DEBUG": "blue",
            "INFO": "purple",
            "WARNING": "yellow,bold",
            "ERROR": "red,bold",
            "CRITICAL": "red,bold,bg_white",
        }

    log_fmtter = colorlog.TTYColoredFormatter(
        fmt=log_fmt, stream=sys.stderr, log_colors=log_colors
    )

    log_handler = logging.StreamHandler()
    log_handler.setFormatter(log_fmtter)
    logging.basicConfig(level=log_level, handlers=[log_handler])

    _LOGGER.debug("version: %s", __version__)
    _LOGGER.debug("platform: %s", platform.platform())

    if args["--version"]:
        print(f"scioer-builder: {__version__}")
        sys.exit(0)

    try:
        docker.from_env()
    except:
        _LOGGER.error(
            "failed to connect to docker, check that Docker is running on the host."
        )
        sys.exit("Docker is not running")

    opts = _make_opts(args)
    _LOGGER.info(opts)

    if opts["interactive"]:
        opts = ask_interactive(opts)
        _LOGGER.info(opts)
    run(opts)


if __name__ == "__main__":
    sys.exit(main())

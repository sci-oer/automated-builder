#!/usr/bin/env python3

"""Automated sci-oer builder.

This command will take the base sci-oer image and create a custom image pre filled
with all the specified content.

Usage:
  scioer-builder [options] [ --example=<examples>... ] [ --example-dir=<examples>... ]
  scioer-builder (-h | --help)

Options:
 -j --jupyter-repo=<jupyter>        The git repository to fetch the builtin jupyter notebooks from. The default branch will be used.
 --jupyter-directory=<jupyter>      A path to the directory containing the builtin jupyter notebooks from.
 -l --lectures-repo=<lecture>       The git repository to fetch the builtin lessons content. The default branch will be used.
 --lectures-directory=<lecture>     A path to the directory containing the builtin lessons content. Cannot be used with `--lectures-repo`.
 -e --example=<examples>...         A list of repositories to fetch worked examples from. The default branch will be used.
 --example-dir=<examples>...        A list of directories to include worked examples from.
 --static-url=<url>                 A url to a public server that holds the static lectures content, so it does not need to be included to reduce the image size.
 --motd-file=<file>                 A file that contains the content of the Message Of The Day, to be printed when the container starts and when a user gets a shell in the container.

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
  --wiki-navigation=<type>          The type of wiki navigation to confgigure, either 'TREE' or 'NONE'. [default: TREE]
  --wiki-comments                   If commenting should be enabled in the wiki. [default: False]

Docker options:
  -t --tag=<tag>                    The docker tag to use for the generated image. This should exclude the registry portion. [default: sci-oer/custom:latest]
  -b --base=<base>                  The base image to use [default: scioer/java-resource:latest]
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

import copy
import datetime
import importlib.resources as pkg_resources
import json
import logging
import os
import platform
import random
import shutil
import signal
import string
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from time import sleep
from typing import List, Optional, Tuple

import colorlog
import docker
import requests
from docker.models.containers import Container
from docker.models.images import Image
from docker.models.networks import Network
from docker.models.volumes import Volume
from docopt import docopt
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from builder.prompt import prompt, prompt_list, yesno, prompt_options

try:
    from git import GitCommandError, Repo  # noqa: I900
except:
    sys.exit("Can not run, `git` must be installed on the system.")

try:
    from builder.__version__ import __version__  # noqa: I900
except:
    __version__ = "LOCAL DEV"

SSH_KEY_FILE_ENV: str = "SSH_KEY_FILE"
SSH_OPTIONS: str = "SSH_OPTIONS"

# this is the api token that has been built into the base-resource container
API_TOKEN: str = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjEsImdycCI6MSwiaWF0IjoxNjQyOTcyMTk5LCJleHAiOjE3Mzc2NDQ5OTksImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.xkvgFfpYw2OgB0Z306YzVjOmuYzrKgt_fZLXetA0ThoAgHNH1imou2YCh-JBXSBCILbuYvfWMSwOhf5jAMKT7O1QJNMhs5W0Ls7Cj5tdlOgg-ufMZaLH8X2UQzkD-1o3Dhpv_7hs9G8xt7qlqCz_-DwroOGUGPaGW6wrtUfylUyYh86V9eJveRJqzZXiGFY3n6Z3DuzIVZtz-DoCHMaDceSG024BFOD-oexMCnAxTpk5OalEhwucaYHS2sNCLpmwiEGHSswpiaMq9-JQasVJtQ_fZ9yU_ZZLBlc0AJs1mOENDTI6OBZ3IS709byqxEwSPnWaF_Tk7fcGnCYk-3gixA"  # noqa E501

_LOGGER = logging.getLogger(__name__)


class Authentication:
    username: str = ""
    password: str = ""
    ssh_file: str = ""

    def __init__(
        self, username: Optional[str], password: Optional[str], ssh_file: str = ""
    ):
        self.username = username or ""
        self.password = password or ""
        self.ssh_file = ssh_file


class Repository:
    uri: str = ""
    branch: Optional[str]
    verify_ssl: bool = True
    verify_host: bool = True

    auth = Authentication("", "")

    def __init__(
        self,
        uri: str,
        branch: Optional[str],
        verify_ssl: bool,
        verify_host: bool = True,
    ):
        self.uri = uri
        self.branch = branch
        self.verify_ssl = verify_ssl
        self.verify_host = verify_host

    def isSSH(self) -> bool:
        return not self.uri.startswith("https")


@dataclass
class CleanupWraper:
    container: Optional[Container]
    volume: Optional[Volume]
    network: Optional[Network]
    build_dir: Optional[tempfile.TemporaryDirectory]


cleanup_resources = CleanupWraper(None, None, None, None)


def _make_opts(args: dict) -> dict:
    """Convert all the cli options from flag form to underscore form.

    converts `--my-arg` to `my_arg`

    Args:
        args (dict): the raw dictionary from argparse

    Returns:
        dict: a cleaned set of the arguments
    """

    opts: dict = {}
    for arg, val in args.items():
        opt: str = arg.replace("--", "").replace("-", "_")
        opts[opt] = val
    return opts


def ask_interactive(opts: dict) -> dict:
    input = copy.deepcopy(opts)

    # general image setup  information
    print("## Information about the container to be built.")
    input["tag"]: str = prompt(
        "Enter the name of the image to be built, including the tag: ",
        default=input["tag"],
    )
    input["base"]: str = prompt(
        "Enter the base image that should be used for this course:",
        default=input["base"],
    )
    input["no_pull"]: bool = not yesno(
        "Should a the latest base image be fetched?",
        default="no" if input["no_pull"] else "yes",
    )
    input["push"]: bool = yesno(
        "Do you want to push the generated image to dockerhub?",
        default="yes" if input["push"] else "no",
    )
    input["multi_arch"]: bool = yesno(
        "Do you want to build the image for multiple CPU architectures?",
        default="yes" if input["multi_arch"] else "no",
    )

    print("")
    print("## General options for cloning git repositories.")
    input["no_verify_host"]: bool = yesno(
        "Should the SSH host keys be verified?",
        default="no" if input["no_verify_host"] else "yes",
    )
    input["keep_git"]: bool = yesno(
        "Should the git histories be kept after they are cloned?",
        default="yes" if input["keep_git"] else "no",
    )
    input["key_file"]: str = prompt(
        "Enter the path to the SSH private key used to clone the git repos if one is being used:",
        default=input["key_file"],
    )

    print("")
    print("## Information about the wiki to be created.")
    input["wiki_title"]: str = prompt(
        "Enter the title for the Wiki:", default=input["wiki_title"]
    )
    input["wiki_git_repo"]: str = prompt(
        "Enter the git repository URL for the wiki:", default=input["wiki_git_repo"]
    )
    input["wiki_git_branch"]: str = prompt(
        "Enter the branch name for the wiki repository:",
        default=input["wiki_git_branch"],
    )
    input["wiki_comments"]: str = yesno(
        "Should commenting be enabled for the wiki?",
        default="no" if input["wiki_comments"] else "yes",
    )
    input["wiki_navigation"]: str = prompt_options(
        "The type of navigation that should be used in the wiki",
        options=["TREE", "NONE"],
        default=input["wiki_navigation"],
    )

    isSSH = yesno("Do you want to clone the wiki repository using ssh?", default="yes")
    if not isSSH:
        input["wiki_git_user"]: str = prompt(
            "Enter the git username for cloning the wiki contents:",
            default=input["wiki_git_user"],
        )
        input["wiki_git_password"]: str = prompt(
            "Enter the git password for cloning the wiki contents",
            default=input["wiki_git_password"],
        )

    input["wiki_git_no_verify"]: str = yesno(
        "Should the SSL certificates be verified when cloning the wiki?",
        default="no" if input["wiki_git_no_verify"] else "yes",
    )

    print("")
    print("## Where the rest of the content is being loaded from.")
    input["jupyter_repo"]: str = prompt(
        "Enter the git repository that holds the Jupyter Notebook files (leave blank if not being used)",
        default=input["jupyter_repo"],
    )
    input["jupyter_directory"]: str = prompt(
        "Enter the directory that contains the Jupyter Notebook files (leave blank if not being used)",
        default=input["jupyter_directory"],
    )
    input["lectures_repo"]: str = prompt(
        "Enter the git repository that holds the Jupyter Lecture video files (leave blank if not being used)",
        default=input["lectures_repo"],
    )
    input["lectures_directory"]: str = prompt(
        "Enter the directory that contains the Jupyter Lecture video files (leave blank if not being used)",
        default=input["lectures_directory"],
    )
    input["example"]: List[str] = prompt_list(
        "Enter a git repository that contains an example project"
    )
    input["example_dir"]: List[str] = prompt_list(
        "Enter a directory that contains an example project"
    )

    print("")
    print("## Other options (the defaults are probably fine).")
    input["motd_file"]: str = prompt(
        "The path to the file that contains the message to be printed when the container starts",
        default=input["motd_file"],
    )
    input["static_url"]: str = prompt(
        "The optional external url to service the static lectures content if it is not included in the image",
        default=input["static_url"],
    )
    input["static_url"]: str = prompt(
        "The optional external url to service the static lectures content if it is not included in the image",
        default=input["static_url"],
    )

    return input


def fetch_latest(client: docker.client.APIClient, repository: str, **kwargs) -> None:
    _LOGGER.info(
        f'pulling latest version of the "{repository}" docker image, this may take a while...'
    )
    client.images.pull(repository)
    _LOGGER.info("Done pulling the latest docker image")


def start_container(
    client: docker.client.APIClient,
    volume: Volume,
    image: str,
    keyFile: List[str],
    **kwargs,
) -> Container:
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


def change_key_permissions(container: Container, keyFile: str, **kwargs):
    _LOGGER.info(
        "Copying the SSH key within the container to set the correct ownership"
    )
    container.exec_run(f'sudo cp "{keyFile}" "{keyFile}.CONTAINER"')
    container.exec_run(f'sudo chown 1000:1000 "{keyFile}.CONTAINER"')
    container.exec_run(f'sudo chmod 600 "{keyFile}.CONTAINER"')


def stop_container(container, **kwargs):
    _LOGGER.info("stopping docker container...")
    container.stop()


def delete_container(container: Optional[Container], force: bool = False, **kwargs):
    if not container:
        return

    _LOGGER.info("Deleteing setup container...")
    container.remove(force=force)


def generate_random_string(length: int = 10) -> str:
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


def create_volume(client: docker.client.APIClient, name: str) -> Volume:
    return client.volumes.create(f"{name}-{generate_random_string()}")


def push_image(client: docker.client.APIClient, image: Image) -> None:
    toPush = image.tags[0]

    try:
        _LOGGER.info(f"Pushing `{toPush}` image to registry....")
        # this can also return a generator to be used for a progress bar
        client.images.push(toPush)
        _LOGGER.info(f"Done pushing `{toPush}`")
    except:
        _LOGGER.error(
            "Failed to push the image to the registry, are you sure you have properly authenticated with the remote registry"
        )


def delete_volume(volume: Optional[Volume], **kwargs) -> None:
    if not volume:
        return

    _LOGGER.info("Deleteing setup volume...")
    volume.remove()


def clone_repo(repo: Repository, name: str, dir: str, keep_git: bool = False, **kwargs):
    folder = os.path.join(dir, name)

    if repo.uri is None:
        os.mkdir(folder)
        _LOGGER.info(f'no repository specified for "{name}", skipping...')
        return
    else:
        _LOGGER.info(f'cloning repository; "{name}"...')

    git_ssh_cmd = ""
    if repo.isSSH():
        sshOptions = os.environ.get(SSH_OPTIONS, "")
        keyFile = f"-i {repo.auth.ssh_file}" if repo.auth.ssh_file else ""
        git_ssh_cmd = f'ssh {sshOptions} {"-o StrictHostKeyChecking=no " if not repo.verify_host else " "}{keyFile}'

    try:
        Repo.clone_from(repo.uri, folder, env=dict(GIT_SSH_COMMAND=git_ssh_cmd))
    except GitCommandError as e:
        _LOGGER.error("Failed to clone the git repository")
        _LOGGER.error(e)
        return

    if not keep_git:
        # make sure that the git directory is removed before it gets loaded into the image
        shutil.rmtree(os.path.join(folder, ".git"))


def setup_tmp_build(**kwargs) -> tempfile.TemporaryDirectory:
    dir = tempfile.TemporaryDirectory()

    with pkg_resources.path("builder.data", "Dockerfile") as template:
        shutil.copy2(template, os.path.join(dir.name, "Dockerfile"))
    return dir


def cleanup_build(dir: Optional[tempfile.TemporaryDirectory]) -> None:
    if not dir:
        return

    _LOGGER.info("removing temporary setup folder...")
    dir.cleanup()


def build_multi_arch(
    client: docker.client.APIClient,
    dir: str,
    tag: str = "sci-oer:custom",
    base: Optional[str] = None,
    push: bool = False,
    static_url: Optional[str] = None,
    **kwargs,
) -> None:
    args = {
        "BASE_IMAGE": base,
        "BUILD_DATE": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "REMOTE_STATIC_SERVER_URL": static_url or "",
    }

    _LOGGER.info(f"Building custom image with name `{tag}`...")

    # platforms = 'linux/amd64,linux/arm64,linux/amd64/v2,linux/arm/v7,linux/arm/v6,linux/386'
    platforms = "linux/amd64,linux/arm64"

    buildArgs = ""
    for k, v in args.items():
        buildArgs = f"{buildArgs}--build-arg {k}={v} "

    push = "" if not push else "--push"

    # get the old builder
    (old_builder, builder_name) = setup_buildx()

    res = subprocess.run(
        "docker buildx create --use", shell=True, check=True, capture_output=True
    )
    builder_name = res.stdout.decode("utf-8").strip()
    cmd = f"docker buildx build --progress=plain --platform {platforms} --tag {tag} {push} {buildArgs} {dir}"
    _LOGGER.debug(f"build command: `{cmd}`")
    subprocess.run(cmd, shell=True, check=True)
    _LOGGER.info("Done building custom image.")

    cleanup_buildx(old_builder, builder_name)


def check_buildx() -> bool:
    res = subprocess.run("docker buildx version >/dev/null 2>/dev/null", shell=True)
    return res.returncode == 0


def setup_buildx() -> Tuple[str, str]:
    res = subprocess.run(
        "docker buildx inspect", shell=True, check=True, capture_output=True
    )
    old_builder = res.stdout.decode("utf-8").split("\n")[0].split(":")[1].strip()

    builder_name = res.stdout.decode("utf-8").strip()
    res = subprocess.run(
        "docker buildx create --use", shell=True, check=True, capture_output=True
    )
    builder_name = res.stdout.decode("utf-8").strip()

    return (old_builder, builder_name)


def cleanup_buildx(old_builder: str, builder_name: str) -> None:
    _LOGGER.info("Clean up buildx context")
    subprocess.run(
        f"docker buildx stop {builder_name}",
        shell=True,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        f"docker buildx rm {builder_name}", shell=True, check=True, capture_output=True
    )
    subprocess.run(
        f"docker buildx use {old_builder}", shell=True, check=True, capture_output=True
    )


def build_single_arch(
    client: docker.client.APIClient,
    dir: str,
    tag: str = "sci-oer:custom",
    base: Optional[str] = None,
    static_url: Optional[str] = None,
    **kwargs,
) -> Image:
    args = {
        "BASE_IMAGE": base,
        "BUILD_DATE": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "REMOTE_STATIC_SERVER_URL": static_url or "",
    }

    _LOGGER.info(f"Building custom image with name `{tag}`...")

    image, logs = client.images.build(path=dir, tag=tag, buildargs=args)
    _LOGGER.info("Done building custom image.")

    return image


def extract_db(container: Container, dir: str, **kwargs) -> None:
    _LOGGER.info("extracting wikijs database...")
    f = open(os.path.join(dir, "database.sqlite.tar"), "wb")
    bits, stat = container.get_archive("/course/wiki/database.sqlite")

    for chunk in bits:
        f.write(chunk)
    f.close()


def create_network(client: docker.client.APIClient, **kwargs) -> Network:
    return client.networks.create(generate_random_string(), attachable=True)


def get_current_container(
    client: docker.client.APIClient, **kwargs
) -> Optional[Container]:
    return client.containers.get(platform.node())


def set_wiki_contents(host: str, repo: Repository, keep_git: bool = False, **kwargs):
    configure_wiki_repo(host, True, repo, **kwargs)
    sync_wiki_repo(host, **kwargs)
    import_wiki_repo(host, **kwargs)

    if not keep_git:
        _LOGGER.info("removing git repo from config")
        remove_git_repo(host, **kwargs)


def remove_git_repo(host: str, **kwargs) -> None:
    configure_wiki_repo(host, False, Repository("", "", False), **kwargs)


def sync_wiki_repo(host: str, **kwargs) -> None:
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
    try:
        api_call(host, query, **kwargs)
        _LOGGER.warning("Done syncing wiki content")
    except:
        error_message = get_wiki_storage_status(host, **kwargs)
        _LOGGER.error(f"Failed to sync the wiki: {error_message}")
        raise Exception("Failed to sync the wiki")


def import_wiki_repo(host: str, **kwargs):
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
    try:
        api_call(host, query, **kwargs)
        _LOGGER.warning("Done importing wiki content")
    except:
        error_message = get_wiki_storage_status(host, **kwargs)
        _LOGGER.error(f"Failed to import the wiki: {error_message}")
        raise Exception("Failed to import the wiki")


def get_wiki_storage_status(host: str, **kwargs) -> str:
    query = """{
        storage {
            status {
            key
            status
            message
            }
        }
    }"""

    _LOGGER.info("Getting the status of the wiki storage...")  # noqa: E501
    message = api_call(host, query, **kwargs)
    _LOGGER.info("Done fetching the wiki status")
    return message


def set_wiki_comments(host: str, enabled: bool, **kwargs):
    query = """mutation Site ($comments: Boolean!){
        site {
            updateConfig (featurePageComments: $comments ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query, variables={"comments": enabled}, **kwargs)


def set_wiki_title(host: str, title: Optional[str], **kwargs):
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


def set_wiki_navigation_mode(host: str, mode: str, **kwargs):
    if mode not in ["NONE", "TREE"]:
        _LOGGER.warning(f"Invalid navigation mode '{mode}'")
        return

    query = """mutation Navigation ($mode: NavigationMode!){
        navigation {
            updateConfig (mode: $mode ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query, variables={"mode": mode}, **kwargs)


def load_ssh_key(keyFile: str) -> str:
    env_key_file = os.getenv(SSH_KEY_FILE_ENV)

    keyFileContents = load_ssh_key_from_file(keyFile)
    envKeyFileContents = load_ssh_key_from_file(env_key_file)

    if keyFileContents != "":
        _LOGGER.debug("Using ssh key specified with cli keyfile flag")
        return keyFile
    elif env_key_file and envKeyFileContents != "":
        _LOGGER.debug(f"Using ssh key specified with {SSH_KEY_FILE_ENV} env variable")
        return env_key_file
    else:
        _LOGGER.debug("no ssh key has been specified")
        return ""


def load_ssh_key_from_file(keyFile: str) -> str:
    if keyFile is None or not os.path.isfile(keyFile):
        _LOGGER.info(f"the specified ssh key file `{keyFile}` does not exist")
        return ""

    with open(keyFile, "r") as f:
        _LOGGER.info(f"found ssh key file: `{keyFile}`")
        return f.read()


def configure_wiki_repo(host: str, enabled: bool, repo: Repository, **kwargs) -> None:
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

    keyFile = f"{repo.auth.ssh_file}.CONTAINER" if repo.auth.ssh_file else ""
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
                        "value": f'{{"v": "{keyFile}"}}',
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


def dissable_api(host: str, **kwargs) -> None:
    query: str = """mutation Authentication {
        authentication {
            setApiState (enabled: false ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query, **kwargs)


def api_call(host: str, query: str, variables: dict = {}, port: int = 3000) -> str:
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    body = {"query": query, "variables": variables}

    r = requests.post(f"http://{host}:{port}/graphql", json=body, headers=headers)

    payload = r.json()

    if "responseResult" in query:
        payload = payload["data"][list(payload["data"].keys())[0]]
        succeeded = payload[list(payload.keys())[0]]["responseResult"]["succeeded"]
        message = payload[list(payload.keys())[0]]["responseResult"]["message"]
    else:
        payload = payload["data"][list(payload["data"].keys())[0]]
        succeeded = True
        message = payload[list(payload.keys())[0]][0]["message"]

    if r.status_code == 200 and succeeded:
        _LOGGER.debug(message or "API call was successful")
        return message
    else:
        _LOGGER.error(json.dumps(r.json(), indent=2))
        raise Exception(f"Query failed to run with a {r.status_code}.")


def check_if_container(client: docker.client.APIClient) -> bool:
    try:
        get_current_container(client)
        return True
    except docker.errors.NotFound:
        return False


def get_wiki_port(isContainer: bool, container: Container) -> int:
    if isContainer:
        return 3000

    wikiPort = int(container.ports.get("3000/tcp")[0]["HostPort"])
    _LOGGER.info(f"Wiki running on port {wikiPort}")

    return wikiPort


def wait_for_wiki_to_be_ready_no_healthcheck(
    host: str, port: int = 3000, **kwargs
) -> bool:
    try:
        http = requests.Session()
        retry_strategy = Retry(total=5, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        http.mount("http://", adapter)
        r = http.get(f"http://{host}:{port}")

        if r.status_code == 200:
            _LOGGER.info("wiki is ready")
            return True
    except:
        _LOGGER.error("Requests timed out, container failed to start.")
    return False


def wait_for_wiki_to_be_ready_healthcheck(container: Container, **kwargs) -> bool:
    status: str = ""
    while True:
        container.reload()
        status = container.attrs["State"]["Health"]["Status"]

        if status != "starting":
            _LOGGER.info("Container has started")
            break
        sleep(5)
        _LOGGER.info("Container is not yet ready, sleeping for 5s...")

    return status == "healthy"


def wait_for_wiki_to_be_ready(
    container: Container, host: str, port: int = 3000, **kwargs
) -> bool:
    """If the container has a healthcheck then it will block until it has settled on healthy or unhealthy
    otherwise this will wait until the wiki returns a 200 status code or hits the retry limit.
    """

    if "Health" in container.attrs["State"]:
        return wait_for_wiki_to_be_ready_healthcheck(container)
    else:
        return wait_for_wiki_to_be_ready_no_healthcheck(host, port=port, **kwargs)


def get_real_file_path(container: Container, fileName: str) -> str:
    mounts = [m for m in container.attrs["Mounts"] if m["Destination"] == fileName]

    if len(mounts) != 0:
        return mounts[0]["Source"]
    return ""


def run(opts: dict, **kwargs):
    if opts["lectures_repo"] is not None:
        _LOGGER.warning(
            "deprecated option `--lectures-repo`, use `--lectures-directory` instead of a git repository. This will be removed in a future version."
        )
    # Checking incompatible arguments

    opts["wiki_navigation"] = opts["wiki_navigation"].strip().upper()
    if opts["wiki_navigation"] not in ["TREE", "NONE"]:
        _LOGGER.error(
            f"'{opts['wiki_navigation']}' is not a valid navigation option must be one of ['TREE', 'NONE']."
        )
        sys.exit("Incompatible arguments")

    if opts["lectures_repo"] is not None and opts["lectures_directory"] is not None:
        _LOGGER.error(
            "Cannot specify both `--lectures-repo` and `--lectures-directory`, only one can be used at a time."
        )
        sys.exit("Incompatible arguments")

    if opts["jupyter_repo"] is not None and opts["jupyter_directory"] is not None:
        _LOGGER.error(
            "Cannot specify both `--jupyter-repo` and `--jupyter-directory`, only one can be used at a time."
        )
        sys.exit("Incompatible arguments")

    motdFile = None
    if opts["motd_file"]:
        motdFile = os.path.realpath(os.path.expanduser(opts["motd_file"]))

    sshKeyFile = load_ssh_key(os.path.expanduser(opts["key_file"] or ""))
    if sshKeyFile != "":
        sshKeyFile = os.path.realpath(sshKeyFile)

    if opts["multi_arch"] and not check_buildx():
        _LOGGER.error(
            "docker buildx not present on system, cannot build for multi-arch."
        )
        sys.exit("Docker buildx not present")

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

    this = None
    containerized = check_if_container(client)

    realKey = sshKeyFile
    network: Optional[Network] = None
    if containerized:
        _LOGGER.debug("Currently running in a docker container")
        network = create_network(client)
        cleanup_resources.network = network

        this = get_current_container(client)
        network.connect(this)

        realKey = get_real_file_path(this, opts["key_file"])

    volume = create_volume(client, "course")
    container = start_container(
        client,
        volume,
        opts["base"],
        [realKey, sshKeyFile],
    )

    cleanup_resources.volume = volume
    cleanup_resources.container = container

    if network:
        network.connect(container)

    container.reload()

    port = get_wiki_port(containerized, container)
    host = "127.0.0.1" if not containerized else container.name

    started = wait_for_wiki_to_be_ready(container, host, port)

    if not started:
        _LOGGER.error("Container failed to start.")

        stop_container(container)
        if network:
            network.disconnect(container)

        delete_container(container)
        delete_volume(volume)
        return

    dir = setup_tmp_build()
    cleanup_resources.build_dir = dir

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

    if opts["jupyter_directory"]:
        shutil.copytree(opts["jupyter_directory"], os.path.join(dir.name, "jupyter"))
    else:
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

    for example in opts["example_dir"]:
        target = examples
        if len(opts["example_dir"]) > 1:
            target = os.path.join(examples.name, os.path.basename(example))
        shutil.copytree(example, target, dirs_exist_ok=True)
    else:
        _LOGGER.info("no example directories were specified, skipping...")

    if motdFile:
        _LOGGER.info("Copying custom motd.txt file...")
        shutil.copy2(motdFile, os.path.join(dir.name, "motd.txt"))
    else:
        _LOGGER.info("Copying default motd.txt file...")
        with pkg_resources.path("builder.data", "motd.txt") as template:
            shutil.copy2(template, os.path.join(dir.name, "motd.txt"))

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
    set_wiki_navigation_mode(host, opts["wiki_navigation"], port=port)
    set_wiki_comments(host, opts["wiki_comments"], port=port)
    dissable_api(host, port=port)

    stop_container(container)
    if network:
        network.disconnect(container)

    extract_db(container, dir.name)

    delete_container(container)
    delete_volume(volume)

    if opts["multi_arch"]:
        _LOGGER.info("Starting multi platform build")
        build_multi_arch(
            client,
            dir.name,
            tag=opts["tag"],
            base=opts["base"],
            push=opts["push"],
            static_url=opts["static_url"],
        )
    else:
        _LOGGER.info("Starting single platform build")
        image = build_single_arch(
            client,
            dir.name,
            tag=opts["tag"],
            base=opts["base"],
            static_url=opts["static_url"],
        )

        if opts["push"]:
            push_image(client, image)

    cleanup_build(dir)

    if network:
        network.disconnect(this)
        network.remove()

    _LOGGER.info("Done.")


def signal_handler(sig, frame):
    print("Gracefully cleaning up all resources shutdown....")

    delete_container(cleanup_resources.container, force=True)
    delete_volume(cleanup_resources.volume)
    if cleanup_resources.network:
        cleanup_resources.network.remove()

    cleanup_build(cleanup_resources.build_dir)

    sys.exit(1)


def main():
    signal.signal(signal.SIGINT, signal_handler)
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

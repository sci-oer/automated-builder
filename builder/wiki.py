import logging
import json
import requests

from typing import List, Optional
from .helper import Repository

_LOGGER = logging.getLogger(__name__)

# this is the api token that has been built into the base-resource container
API_TOKEN: str = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjEsImdycCI6MSwiaWF0IjoxNjQyOTcyMTk5LCJleHAiOjE3Mzc2NDQ5OTksImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.xkvgFfpYw2OgB0Z306YzVjOmuYzrKgt_fZLXetA0ThoAgHNH1imou2YCh-JBXSBCILbuYvfWMSwOhf5jAMKT7O1QJNMhs5W0Ls7Cj5tdlOgg-ufMZaLH8X2UQzkD-1o3Dhpv_7hs9G8xt7qlqCz_-DwroOGUGPaGW6wrtUfylUyYh86V9eJveRJqzZXiGFY3n6Z3DuzIVZtz-DoCHMaDceSG024BFOD-oexMCnAxTpk5OalEhwucaYHS2sNCLpmwiEGHSswpiaMq9-JQasVJtQ_fZ9yU_ZZLBlc0AJs1mOENDTI6OBZ3IS709byqxEwSPnWaF_Tk7fcGnCYk-3gixA"  # noqa E501

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

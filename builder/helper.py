import random
import string
import tempfile
from dataclasses import dataclass
from typing import List, Optional, Tuple
from docker.models.containers import Container
from docker.models.images import Image
from docker.models.networks import Network
from docker.models.volumes import Volume


def generate_random_string(length: int = 10) -> str:
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))


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

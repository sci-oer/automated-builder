import logging
import docker
import platform
import requests
from docker.models.containers import Container
from docker.models.images import Image
from docker.models.networks import Network
from docker.models.volumes import Volume

from typing import List, Optional, Tuple
from .helper import generate_random_string

_LOGGER = logging.getLogger(__name__)


def get_current_container(
    client: docker.client.APIClient, **kwargs
) -> Optional[Container]:
    return client.containers.get(platform.node())


def check_if_container(client: docker.client.APIClient) -> bool:
    try:
        get_current_container(client)
        return True
    except docker.errors.NotFound:
        return False


def fetch_latest(client: docker.client.APIClient, repository: str, **kwargs) -> None:
    _LOGGER.info(
        f'pulling latest version of the "{repository}" docker image, this may take a while...'
    )
    client.images.pull(repository)
    _LOGGER.info("Done pulling the latest docker image")


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


def stop_container(container, **kwargs):
    _LOGGER.info("stopping docker container...")
    container.stop()


def delete_container(container: Optional[Container], force: bool = False, **kwargs):
    if not container:
        return

    _LOGGER.info("Deleteing setup container...")
    container.remove(force=force)


def create_volume(client: docker.client.APIClient, name: str) -> Volume:
    return client.volumes.create(f"{name}-{generate_random_string()}")


def delete_volume(volume: Optional[Volume], **kwargs) -> None:
    if not volume:
        return

    _LOGGER.info("Deleteing setup volume...")
    volume.remove()


def create_network(client: docker.client.APIClient, **kwargs) -> Network:
    return client.networks.create(generate_random_string(), attachable=True)

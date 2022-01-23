#!/usr/bin/env python3


import docker
import random
import string
import tempfile
import os
import shutil
import platform
import requests
import json
from git import Repo
import time

API_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjEsImdycCI6MSwiaWF0IjoxNjQyOTcyMTk5LCJleHAiOjE3Mzc2NDQ5OTksImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.xkvgFfpYw2OgB0Z306YzVjOmuYzrKgt_fZLXetA0ThoAgHNH1imou2YCh-JBXSBCILbuYvfWMSwOhf5jAMKT7O1QJNMhs5W0Ls7Cj5tdlOgg-ufMZaLH8X2UQzkD-1o3Dhpv_7hs9G8xt7qlqCz_-DwroOGUGPaGW6wrtUfylUyYh86V9eJveRJqzZXiGFY3n6Z3DuzIVZtz-DoCHMaDceSG024BFOD-oexMCnAxTpk5OalEhwucaYHS2sNCLpmwiEGHSswpiaMq9-JQasVJtQ_fZ9yU_ZZLBlc0AJs1mOENDTI6OBZ3IS709byqxEwSPnWaF_Tk7fcGnCYk-3gixA"


def fetch_latest(client, repository="marshallasch/oo-resources:main", **kwargs):
    client.images.pull(repository)

def start_container(client, volume, image="marshallasch/oo-resources:main", **kwargs):


    name = f'auto-build-tmp-{generate_random_string()}'

    container = client.containers.run(image, name=name, tty=True, detach=True, volumes=[f'{volume.name}:/course'])

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

def build_image(client, dir, **kwargs):
    client.images.build(path=dir.name, tag="sci-oer:custom")

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

def create_page(host, page):
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

    api_call(host, query)

def dissable_api(host):
    query = """mutation Authentication {
        authentication {
            setApiState (enabled: false ) {
                responseResult { succeeded, errorCode, slug, message }
            }
        }
    }"""

    api_call(host, query)

def api_call(host, query):

    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    r = requests.post(f'http://{host}:3000/graphql', json={"query": query}, headers=headers)

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


    pages.append(Page("Cool Sample Page", "/test", "This is a super cool sample page", ["test", "sample"], "my cool markdown content"))

    return pages

def upload_wiki(pages, hostname):

    for page in pages:
        create_page(hostname, page)

def main(notebook_repo, **kwargs):

    client = docker.from_env()

    fetch_latest(client)

    network = create_network(client)
    this = get_current_container(client)

    network.connect(this)

    volume = create_volume(client, "course")
    container = start_container(client, volume)
    network.connect(container)


    print("waiting a 5 seconds to make sure the container is up")
    time.sleep(5)

    dir = setup_tmp_build(notebook_repo)

    ##
    ## clone the wiki here and make the api calls to import all the wiki data
    ##

    pages = load_wiki_files("tmp")
    upload_wiki(pages, container.name)
    dissable_api(container.name)


    stop_container(container)
    network.disconnect(container)

    extract_db(container, dir)


    delete_container(container)
    delete_volume(volume)

    build_image(client, dir)
    cleanup_build(dir)

    network.disconnect(this)
    network.remove()



if __name__ == "__main__":

    main('https://github.com/sci-oer/automated-builder.git')

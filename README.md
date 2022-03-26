# Automated SCI-OER Image Builder

[![Deployment](https://github.com/sci-oer/automated-builder/actions/workflows/deployment.yml/badge.svg)](https://github.com/sci-oer/automated-builder/actions/workflows/deployment.yml)
![GitHub](https://img.shields.io/github/license/sci-oer/automated-builder?style=plastic)


This is an automated build tool to generate customized versions of the [oo-resources](https://github.com/sci-oer/oo-resources) image. 

Typically, a customized docker image can be created by extending a `Dockerfile` with the new modifications and setup script and your good to go. 
However, some of the tools that are prepackaged in this container can not be customized and configured without the services running (wiki-js). 
This service aims to solve this problem by running a version of the base image, customizing it, extracting the configuration files, then repackaging them into a new Docker image. 

## Requirements

In order to run this project you must have the following installed and running on your machine:

- docker
- git
- python3

The build script will start a docker container in the background, so it can be customized then build a new docker image. 
The user that is running the build script must have permissions to run docker commands. 

Git must be installed in-order to load and configure the seeded content. 

## Creating a Custom Image

This script will create a sci-oer image that is customized with the following:
- a set of pre-made lecture content
- one or more example project repositories. 
- wiki content to be loaded from a git repository 
- a set of Jupyter lab notebooks
- a customized wiki title 

There are a number of configuration options that can be specified when building the customized container.
Run `./build.py --help` to see a complete list of configuration options and how they can be used. 

All the options are optional, if one is left out then no content will be configured. 

There are currently two methods that can be used to create a customized image.

1. Using a prebuilt docker command
2. running the `./build.py` script directly 

### Using Docker

For convenience a prebuilt [Docker image](https://hub.docker.com/r/marshallasch/automated-builder) has been published that includes all the dependencies needed to generate a custom image. 

For the `automated-builder` container to be able to create the custom docker image it must have the docker socket passed into the container. 

```bash
$ docker run -v /var/run/docker.sock:/var/run/docker.sock \
    marshallasch/automated-builder:latest <options here>
```

### Running the `./build.py` Script Directly

Alternatively the build command can be run directly. 
This still has the same system requirements. 

1. Install this repository. `git clone https://github.com/sci-oer/automated-builder.git`
2. Install the dependencies. `pip3 install -r requirements.txt`
3. Build the custom image. `./build.py <options>`

## Getting Help

If you need help getting the builder script to work or have questions or find any issues you can open a [GitHub Issue](https://github.com/sci-oer/automated-builder/issues). 


## Getting Involved

If you notice something that doesn't quite work or if you want to add new features or support the implementation any contributions are welcome. 

Currently, we are focusing on completing this script so that all of the aspects of the sci-oer container can be customized using the cli, or possibly a configuration file. The next steps will be to develop a web interface so that the customized version can be created without needing to install all the tools. 


## License 

This project has been published under the [AGPL-3.0 License](https://github.com/sci-oer/automated-builder/blob/main/LICENSE). 
This essentially means that you can use this for whatever you want as long as any modifications you make are published under the same license. 



## Components of Dockerfile

Create your first Dockerfile:

### Dockerfile Commands:
```
FROM
ENV
WORKDIR
RUN
ENTRYPOINT
CMD
COPY
ADD
EXPOSE
```
### FROM
```
FROM <image> [AS <name>]
```
FROM is used to define the base image to start the build process. Every Dockerfile must start with the FROM instruction. The idea behind this is that you need a starting point to build your image.
```
FROM ubuntu
```
It means our project require ubuntu as a parent image.
### ENV
```
ENV <key> <value>
```
This command used to set the environment variables that is required to run the project.

ENV sets the environment variables, which can be used in the Dockerfile and any scripts that it calls. These are persistent with the container too and they can be referenced at any time.
```
ENV HTTP_PORT="9000"
```
We provided HTTP_PORT as an environment variable.
### WORKDIR
```
WORKDIR /path/to/workdir
```
WORKDIR tells Docker that the rest of the commands will be run in the context of the /app folder inside the image.
```
WORKDIR /app
```
It will create the app directory in the container.
### RUN

RUN has 2 forms:
```
    RUN <command> (shell form, the command is run in a shell, which by default is /bin/sh -c on Linux or cmd /S /C on Windows)
    RUN ["executable", "param1", "param2"] (exec form)
```
The RUN instruction will execute any commands in a new layer on top of the current image and commit the results. The resulting committed image will be used for the next step in the Dockerfile.

The RUN command runs within the container at build time.
```
RUN /bin/bash -c 'source $HOME/.bashrc; echo $HOME'
```
### ENTRYPOINT

ENTRYPOINT has two forms:
```
    ENTRYPOINT ["executable", "param1", "param2"] (exec form, preferred)
    ENTRYPOINT command param1 param2 (shell form)
```
An ENTRYPOINT allows you to configure a container that will run as an executable.

ENTRYPOINT sets the command and parameters that will be executed first when a container is run. Any command-line arguments passed to docker run <image> will be appended to the ENTRYPOINT command, and will override all elements specified using CMD. For example, docker run <image> bash we will add the command argument bash to the end of the ENTRYPOINT command.

You can override ENTRYPOINT instructions using the docker run --entrypoint
``` 
ENTRYPOINT [ "sh", "-c", "echo $HOME" ]
```
If the ENTRYPOINT isn’t specified, Docker will use /bin/sh -c as the default executor.

### CMD

The CMD instruction has three forms:
```
    CMD ["executable","param1","param2"] (exec form, this is the preferred form)
    CMD ["param1","param2"] (as default parameters to ENTRYPOINT)
    CMD command param1 param2 (shell form)
```
The main purpose of a CMD is to provide defaults when executing a container. These will be executed after the entry point.

In Dockerfiles, you can define CMD defaults that include an executable.

***Example:***
```
CMD ["executable","param1","param2"]
```
If they omit the executable, you must specify an ENTRYPOINT instruction as well.
```
CMD ["param1","param2"] (as default parameters to ENTRYPOINT)
```
NOTE: There can only be one CMD instruction in a Dockerfile. If you want to list more than one CMD, then only the last CMD will take effect.
```
CMD ["bin/ping", "localhost"]
```
    
### COPY

COPY has two forms:
```
    COPY <src>... <dest>
    COPY ["<src>",... "<dest>"] (this form is required for paths containing whitespace)
```
The COPY command is used to copy one or many local files or folders from source and adds them to the filesystem of the containers at the destination path.

It builds up the image in layers, starting with the parent image, defined using FROM.The Docker instruction WORKDIR defines a working directory for the COPY instructions that follow it.

The <dest> is an absolute path, or a path relative to WORKDIR, into which the source will be copied inside the destination container.

COPY test relativeDir/   # adds "test" to `WORKDIR`/relativeDir/
COPY test /absoluteDir/  # adds "test" to /absoluteDir/

### ADD

ADD has two forms:
```
    ADD <src>... <dest>
    ADD ["<src>",... "<dest>"]
```
The ADD command is used to add one or many local files or folders from the source and adds them to the filesystem of the containers at the destination path.

It is Similar to COPY command but it has some additional features:

    If the source is a local tar archive in a recognized compression format, then it is automatically unpacked as a directory into the Docker image.
    If the source is a URL, then it will download and copy the file into the destination within the Docker image. However, Docker discourages using ADD for this purpose.
```
ADD rootfs.tar.xz /
ADD http://example.com/big.tar.xz /usr/src/things/
```
### EXPOSE
```
EXPOSE <port> [<port>/<protocol>...]
```
The EXPOSE command informs the Docker that the container listens on the specified network ports at runtime. You can specify whether the port listens on TCP or UDP, and the default is TCP if the protocol is not specified.

But EXPOSE will not allow communication via the defined ports to containers outside of the same network or to the host machine. To allow this to happen you need to publish the ports.

The EXPOSE command does not actually publish the port. To actually publish the port when running the container, use the -p flagon docker run to publish and map one or more ports, or the -P flag to publish all exposed ports and map them to high-order ports.

These are the flags -p and -P, and they differ in terms of whether you want to publish one or all ports:

    To actually publish the port when running the container, use the -p flag on docker run to publish and map one or more ports
    he -P flag to publish all exposed ports 

//Publish host port to container port
```
docker run -p 80:80/tcp -p 80:80/udp app
```
//To publish all the ports you define in your Dockerfile with EXPOSE and bind them to the host machine, you can use the -P flag.
```
docker run -P app
```

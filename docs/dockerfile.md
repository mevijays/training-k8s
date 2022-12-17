## Components of Dockerfile

Create your first Dockerfile:

    Dockerfile Commands:

FROM
ENV
WORKDIR
RUN
ENTRYPOINT
CMD

    Understand how CMD and ENTRYPOINT interact

COPY
ADD
EXPOSE

FROM

FROM <image> [AS <name>]

FROM is used to define the base image to start the build process. Every Dockerfile must start with the FROM instruction. The idea behind this is that you need a starting point to build your image.

FROM ubuntu

It means our project require ubuntu as a parent image.
ENV

ENV <key> <value>

This command used to set the environment variables that is required to run the project.

ENV sets the environment variables, which can be used in the Dockerfile and any scripts that it calls. These are persistent with the container too and they can be referenced at any time.

ENV HTTP_PORT="9000"

We provided HTTP_PORT as an environment variable.
WORKDIR

WORKDIR /path/to/workdir

WORKDIR tells Docker that the rest of the commands will be run in the context of the /app folder inside the image.

WORKDIR /app

It will create the app directory in the container.
RUN

RUN has 2 forms:

    RUN <command> (shell form, the command is run in a shell, which by default is /bin/sh -c on Linux or cmd /S /C on Windows)
    RUN ["executable", "param1", "param2"] (exec form)

The RUN instruction will execute any commands in a new layer on top of the current image and commit the results. The resulting committed image will be used for the next step in the Dockerfile.

The RUN command runs within the container at build time.

RUN /bin/bash -c 'source $HOME/.bashrc; echo $HOME'

ENTRYPOINT

ENTRYPOINT has two forms:

    ENTRYPOINT ["executable", "param1", "param2"] (exec form, preferred)
    ENTRYPOINT command param1 param2 (shell form)

An ENTRYPOINT allows you to configure a container that will run as an executable.

ENTRYPOINT sets the command and parameters that will be executed first when a container is run. Any command-line arguments passed to docker run <image> will be appended to the ENTRYPOINT command, and will override all elements specified using CMD. For example, docker run <image> bash we will add the command argument bash to the end of the ENTRYPOINT command.

You can override ENTRYPOINT instructions using the docker run --entrypoint

ENTRYPOINT [ "sh", "-c", "echo $HOME" ]

If the ENTRYPOINT isn’t specified, Docker will use /bin/sh -c as the default executor.
CMD

The CMD instruction has three forms:

    CMD ["executable","param1","param2"] (exec form, this is the preferred form)
    CMD ["param1","param2"] (as default parameters to ENTRYPOINT)
    CMD command param1 param2 (shell form)

The main purpose of a CMD is to provide defaults when executing a container. These will be executed after the entry point.

In Dockerfiles, you can define CMD defaults that include an executable.

Example:

CMD ["executable","param1","param2"]

If they omit the executable, you must specify an ENTRYPOINT instruction as well.

CMD ["param1","param2"] (as default parameters to ENTRYPOINT)

NOTE: There can only be one CMD instruction in a Dockerfile. If you want to list more than one CMD, then only the last CMD will take effect.

CMD ["bin/ping", "localhost"]

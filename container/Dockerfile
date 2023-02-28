
FROM ubuntu:20.04

ARG GIT_CONSOLE_COMMIT
ARG GIT_BRANCH
ARG GIT_COMMIT
ARG RELEASE_VERSION

LABEL skyline.build_console_commit=${GIT_CONSOLE_COMMIT}
LABEL skyline.build_branch=${GIT_BRANCH}
LABEL skyline.build_commit=${GIT_COMMIT}
LABEL skyline.release_version=${RELEASE_VERSION}

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update -y && apt-get install -y --no-install-recommends apt-utils \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    gcc make nginx traceroute lsof iputils-ping vim git wget curl locales-all ssl-cert \
    python3 python3-pip python3-dev python3-venv python-dev-is-python3

COPY ./skyline_console /opt/skyline_apiserver/skyline_console

RUN pip install -U /opt/skyline_apiserver/skyline_console/skyline_console.tar.gz

COPY ./requirements.txt /opt/skyline_apiserver/requirements.txt

RUN pip install -r /opt/skyline_apiserver/requirements.txt -chttps://releases.openstack.org/constraints/upper/master

COPY ./ /opt/skyline_apiserver/

RUN git init /opt/skyline_apiserver \
    && pip install /opt/skyline_apiserver -chttps://releases.openstack.org/constraints/upper/master \
    && apt-get clean \
    && rm -rf ~/.cache/pip \
    && mkdir -p /etc/skyline /var/log/skyline /var/lib/skyline

COPY ./etc/gunicorn.py /etc/skyline/gunicorn.py
COPY ./etc/skyline.yaml.sample /etc/skyline/skyline.yaml
COPY ./container/start_service.sh /usr/local/bin/start_service.sh

EXPOSE 443

CMD ["start_service.sh"]

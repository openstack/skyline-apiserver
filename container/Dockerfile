FROM --platform=linux/amd64 ubuntu:jammy

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

EXPOSE 443

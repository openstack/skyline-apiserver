# Setp1. Build static
FROM node:erbium AS builder

COPY ./libs/skyline-console /skyline-console/

RUN cd /skyline-console \
    && yarn install \
    && rm -rf /skyline-console/skyline_console/static \
    && yarn run build


# Setp2. Build image
FROM ubuntu:20.04

ARG GIT_BRANCH
ARG GIT_COMMIT
ARG RELEASE_VERSION

LABEL skyline.build_branch=${GIT_BRANCH}\
      skyline.build_commit=${GIT_COMMIT} \
      skyline.release_version=${RELEASE_VERSION}

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

COPY ./ /skyline/
COPY --from=builder /skyline-console/skyline_console/static /skyline/libs/skyline-console/skyline_console/static
COPY ./container/start_service.sh /usr/local/bin/start_service.sh
COPY ./etc/skyline.yaml.sample /etc/skyline/skyline.yaml
COPY ./etc/gunicorn.py /etc/skyline/gunicorn.py

RUN export LANG=C.UTF-8 \
    && apt-get update -y && apt-get install -y --no-install-recommends apt-utils \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    gcc make nginx traceroute lsof iputils-ping vim git wget curl locales-all ssl-cert \
    python3 python3-pip python3-dev python3-venv \
    && rm -rf /usr/bin/python /usr/bin/pip \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && ln -s /usr/bin/pip3 /usr/bin/pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && mkdir -p /etc/skyline /var/log/skyline/ /var/lib/skyline \
    && cd /skyline \
    && poetry install \
    && apt-get clean \
    && rm -rf ~/.cache/pip

EXPOSE 443

CMD ["start_service.sh"]

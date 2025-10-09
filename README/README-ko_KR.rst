===================
스카이라인 API 서버
===================

`English <../README.rst>`__ \| `简体中文 <./README-zh_CN.rst>`__ \| 한국어

스카이라인(지평선)은 UI와 UE에 의해 최적화된 오픈스택 대시보드로
오픈스택 Train릴리즈 이상 버전을 지원합니다.
최신 기술 스택과 생태계를 갖추고 있으며, 개발자들이 보다 쉽게 유지와 운영할 수
있고 높은 동시성 성능을 가지고 있습니다.

스카이라인의 마스코트는 구색록(아홉빛깔사슴)입니다. 구색록은 불교정신을 기반으로 한
둔황 벽화의 “구색록본생”에서 유래했으며, 인과와 은혜를 알고 보답하는 것은
99cloud의 커뮤니티를 포용하고 피드백하는 개념과 일치합니다.
스카이라인은 구색록처럼 가볍고 우아하며 강력하게 유지되길 바라며,
오픈스택 커뮤니티와 사용자를 위한 보다 우수한 품질의 대시보드를 제공합니다.

|image0|

**목차**

-  `스카이라인 API 서버 <#스카이라인 API 서버>`__

   -  `리소스 <#리소스>`__
   -  `빠른 시작 <#빠른-시작>`__

      -  `전제조건 <#전제조건>`__
      -  `구성 <#구성>`__
      -  `Sqlite를 사용한 배포 <#sqlite를-사용한-배포>`__
      -  `MariaDB를 사용한 배포 <#MariaDB를-사용한-배포>`__
      -  `테스트 액세스 <#테스트-액세스>`__

   -  `Skyline-apiserver 개발 <#Skyline-apiserver-개발>`__

      -  `종속성 도구 <#종속성-도구>`__
      -  `설치 & 작동 <#설치--작동>`__

   -  `Devstack 통합 <#Devstack-통합>`__
   -  `Kolla Ansible 배포 <#Kolla-Ansible-배포>`__

리소스
---------

-  `개발자 문서 <https://docs.openstack.org/skyline-apiserver/latest/>`__
-  `릴리즈 노트 <https://docs.openstack.org/releasenotes/skyline-apiserver/>`__
-  `위키 <https://wiki.openstack.org/wiki/Skyline>`__
-  `버그 트래커 <https://launchpad.net/skyline-apiserver>`__

빠른 시작
-----------

전제조건
~~~~~~~~~~

-  오픈스택의 최소한의 코어 컴포넌트가 작동중이면서,
   키스톤 엔드포인트로 오픈스택 컴포넌트의 엑세스 가능한 상태
-  컨테이너 엔진(`도커 <https://docs.docker.com/engine/install/>`__ 또는
   `포드맨 <https://podman.io/getting-started/installation>`__)이 설치되어 있는 리눅스 서버


구성
~~~~~~

1. 설치할 리눅스 서버에서 ``/etc/skyline/skyline.yaml`` 파일을 수정합니다.

   `샘플 파일 <../etc/skyline.yaml.sample>`__ 을 참고 할수 있고,
   실제 환경에 따라 다음 파라미터를 수정합니다.
   -  database_url
   -  keystone_url
   -  default_region
   -  interface_type
   -  system_project_domain
   -  system_project
   -  system_user_domain
   -  system_user_name
   -  system_user_password

Sqlite를 사용한 배포
~~~~~~~~~~~~~~~~~~~~~~

dockerhub에서 dockerimage를 가져오는 데 실패하면 알리미러 저장소에서 dockerimage를 꺼낼 수 있으며,
알리미러의 미러링은 매 시간 동기화되며, 미러 주소는 다음과 같습니다.

- registry.cn-shanghai.aliyuncs.com/99cloud-sh/skyline:zed
- registry.cn-shanghai.aliyuncs.com/99cloud-sh/skyline:latest

1. skyline_bootstrap 를 컨테이너로 실행해서 부트스트랩

   .. code:: bash

      rm -rf /tmp/skyline && mkdir /tmp/skyline && mkdir /var/log/skyline

      docker run -d --name skyline_bootstrap -e KOLLA_BOOTSTRAP="" -v /var/log/skyline:/var/log/skyline -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

      # 부트스트랩이 `exit 0` 출력하는지 확인하세요
      docker logs skyline_bootstrap

2. 부트스트랩이 완료된 이후 스카이라인 서비스 작동

   .. code:: bash

      docker rm -f skyline_bootstrap

   다른포트로 변경이 필요할 경우, 변수 ``-e LISTEN_ADDRESS=<ip:port>`` 를 추가하고 다음 명령어를 실행하세요.

   ``LISTEN_ADDRESS`` 의 기본값은 ``0.0.0.0:9999`` 입니다.

   서비스의 정책 규칙을 변경이 필요한 경우, 변수 ``-v /etc/skyline/policy:/etc/skyline/policy`` 를 추가하고 명령어를 실행하고,

   서비스 정책 yaml 파일을 다음과 같이 ``<service_name>_policy.yaml`` 이름을 변경하시고 ``/etc/skyline/policy`` 폴더에 추가하세요.

   .. code:: bash

      docker run -d --name skyline --restart=always -v /var/log/skyline:/var/log/skyline -v /etc/skyline/skyline.yaml:/etc/skyline/skyline.yaml -v /tmp/skyline:/tmp --net=host 99cloud/skyline:latest

MariaDB로 사용한 배포
~~~~~~~~~~~~~~~~~~~~~~

https://docs.openstack.org/skyline-apiserver/latest/install/docker-install-ubuntu.html

API 문서
~~~~~~~~~

API 문서에 접속 할 수 있습니다: ``https://<ip_address>:9999/api/openstack/skyline/docs``

테스트 액세스
~~~~~~~~~~~~~

대시보드를 엑세스할 수 있습니다: ``https://<ip_address>:9999``

Skyline-apiserver 개발
-------------------------

**Support Linux & Mac OS (Recommend Linux OS) (Because uvloop & cython)**

종속성 도구
~~~~~~~~~~~~~~~

새로운 기능의 컨텍스트 변수를 사용하는 python37과 uvloop (0.15.0+ python37버전이 필요)
대부분 시스템이 python37버전을 지원하지 않는다는 점을 고려해서,
적어도 python38을 지원하도록 선택했습니다.

-  make >= 3.82
-  python >= 3.8
-  node >= 10.22.0 (선택적 apiserver개발시)
-  yarn >= 1.22.4 (선택적 apiserver개발시)

설치 & 작동
~~~~~~~~~~~~~

1. 종속성 패키지 설치

   .. code:: bash

      tox -e venv

2. skyline.yaml 설정파일 확인

   .. code:: bash

      cp etc/skyline.yaml.sample etc/skyline.yaml
      export OS_CONFIG_DIR=$(pwd)/etc

   다음 변수를 실제 환경과 동일하게 변경하세요:

   .. code:: yaml

      - database_url
      - keystone_url
      - default_region
      - interface_type
      - system_project_domain
      - system_project
      - system_user_domain
      - system_user_name
      - system_user_password

   ``database_url`` 에 ``sqlite:////tmp/skyline.db`` 가 존재한다면
    다음 순번으로 넘어가시고, ``database_url`` 에
    ``mysql://root:root@localhost:3306/skyline`` 와 같이 mysql로
    작성되어있다면, ``1`` 번과 ``2`` 번을 ``Deployment with MariaDB`` 를
    먼저 참고하시고 진행하세요.

3. 스카이라인 데이터베이스 초기화

   .. code:: bash

      source .tox/venv/bin/activate
      make db_sync
      deactivate

4. skyline-apiserver 작동

   .. code:: console

      $ source .tox/venv/bin/activate
      $ uvicorn --reload --reload-dir skyline_apiserver --port 28000 --log-level debug skyline_apiserver.main:app

      INFO:     Uvicorn running on http://127.0.0.1:28000 (Press CTRL+C to quit)
      INFO:     Started reloader process [154033] using statreload
      INFO:     Started server process [154037]
      INFO:     Waiting for application startup.
      INFO:     Application startup complete.

   이후 온라인 API 문서를 엑세스할 수 있습니다:
   ``http://127.0.0.1:28000/docs``

   또는, vscode에서 ``.vscode/lauch.json`` 와 함께 디버그를 작동시킬 수 있습니다.


5. 이미지 빌드

   .. code:: bash

      # Ubuntu 22.04 / 24.04 install docker-buildx
      # apt install docker-buildx
      # docker buildx create --name mybuilder --driver docker-container --use --bootstrap

      # 로컬 빌드 (현재 플랫폼)
      make build PLATFORMS=linux/amd64

      # 멀티 플랫폼 빌드 및 푸시
      make build PLATFORMS=linux/amd64,linux/arm64 IMAGE=yourrepo/skyline IMAGE_TAG=latest PUSH=true

Devstack 통합
--------------------

`빠른 데브스택 통합 빌드환경. <../devstack/README.rst>`__

Kolla Ansible 배포
------------------------

`Kolla Ansible을 통한 빌드환경. <../kolla/README.md>`__

|image1|

.. |image0| image:: ../doc/source/images/logo/OpenStack_Project_Skyline_horizontal.png
.. |image1| image:: ../doc/source/images/logo/nine-color-deer-64.png

FAQ
---

1. 정책

   Q: Why common user could login, but could list the nova servers?
      `Bug #2049807 <https://bugs.launchpad.net/skyline-apiserver/+bug/2049807>`_

   ::

      Symptom:
      -----------------------------------
      1. Login Horizon with common user A, list servers OK.
      2. Login Skyline with same common user A, could list the nova servers, F12 show no http requests sent from network, however webpage show 401, do not allow to list servers

      Root Cause Analysis:
      -----------------------------------
      1. Horizon don't know whether a user could do an action at a resource or not. It simply pass request to recording service, & service (Nova) do the check by its policy file. So it works.
      2. Skyline check the action by itself, with /policy API. If you do not configure it, the default value follows community, like: https://docs.openstack.org/nova/2023.2/configuration/sample-policy.html

      How to fix:
      -----------------------------------
      1. By default, list servers need "project_reader_api": "role:reader and project_id:%(project_id)s"
      2. You should config your customized role, for example: member, _member_, projectAdmin, etc, create implied reader role. "openstack implied role create --implied-role member projectAdmin", or "openstack implied role create --implied-role reader _member_"

      # openstack implied role list
      +----------------------------------+-----------------+----------------------------------+-------------------+
      | Prior Role ID | Prior Role Name | Implied Role ID | Implied Role Name |
      +----------------------------------+-----------------+----------------------------------+-------------------+
      | fe21c5a0d17149c2a7b02bf39154d110 | admin | 4376fc38ba6a44e794671af0a9c60ef5 | member |
      | 4376fc38ba6a44e794671af0a9c60ef5 | member | e081e01b7a4345bc85f8d3210b95362d | reader |
      | bee8fa36149e434ebb69b61d12113031 | projectAdmin | 4376fc38ba6a44e794671af0a9c60ef5 | member |
      | 77cec9fc7e764bd4bf60581869c048de | _member_ | e081e01b7a4345bc85f8d3210b95362d | reader |
      +----------------------------------+-----------------+----------------------------------+-------------------+

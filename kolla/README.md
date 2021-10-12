# Kolla Ansible Deployment

## Environments

> **Requirements:**\
> 2 network interfaces\
> 8GB main memory\
> 100GB disk space\
> ubuntu20.04 / centos8

- kolla : `https://github.com/openstack/kolla`
- kolla-ansible : `https://github.com/openstack/kolla-ansible`
- kolla skyline patch : `https://opendev.org/skyline/skyline-apiserver/src/branch/master/kolla/kolla-xxxxxxx.diff`
- kolla-ansible skyline patch : `https://opendev.org/skyline/skyline-apiserver/src/branch/master/kolla/kolla-ansible-xxxxxxx.diff`

## kolla build docker image

- If kolla is not installed in the deployment environment

  ```shell
  cd /opt
  git clone https://github.com/openstack/kolla-ansible
  curl https://opendev.org/skyline/skyline-apiserver/src/branch/master/kolla/kolla-ansible-xxxxxxx.diff -o kolla-ansible.diff
  cd /opt/kolla-ansible
  git apply --check /opt/kolla-ansible.diff
  git apply /opt/kolla-ansible.diff
  sudo pip3 install /opt/kolla-ansible
  ```

- If kolla has been installed in the deployment environment

  Get the kolla installation directory:

  ```shell
  KOLLA_PACKAGE_PATH=$(python3 -c "import kolla;from pathlib import Path;print(Path(kolla.__file__).parents[1])")
  KOLLA_DATA_FILES_PATH=$(python3 -c "import kolla;from pathlib import Path;print(Path(kolla.__file__).parents[4].joinpath('share/kolla'))")
  ```

  Install kolla patch

  ```shell
  curl https://opendev.org/skyline/skyline-apiserver/src/branch/master/kolla/kolla-xxxxxxx.diff -o /opt/kolla.diff
  cd ${KOLLA_PACKAGE_PATH}
  git apply --check --include='kolla/*' /opt/kolla.diff
  git apply --include='kolla/*' /opt/kolla.diff
  cd ${KOLLA_DATA_FILES_PATH}
  git apply --check --include='docker/*' /opt/kolla.diff
  git apply --include='docker/*' /opt/kolla.diff
  ```

### Build skyline image

> **Note : Only provide ubuntu-source-skyline of skyline image**

- `-b`: The distro type of the base image
- `-t`: The method of the OpenStack install
- `-n`: The Docker namespace name
- `--tag`: Docker tag
- `--registry`: The docker registry host
- `--push`: Push images after building

```shell
kolla-build -b ubuntu -t source -n kolla --tag master --registry 127.0.0.1:4000 --push skyline
```

## Kolla Ansible Install

### kolla-ansible install

- If kolla-ansible is not installed in the deployment environment

  ```shell
  cd /opt
  git clone https://github.com/openstack/kolla-ansible
  curl https://opendev.org/skyline/skyline-apiserver/src/branch/master/kolla/kolla-ansible-xxxxxxx.diff -o kolla-ansible.diff
  cd /opt/kolla-ansible
  git apply --check /opt/kolla-ansible.diff
  git apply /opt/kolla-ansible.diff
  sudo pip3 install /opt/kolla-ansible
  ```

- If kolla-ansible has been installed in the deployment environment

  Get the kolla-ansible installation directory:

  ```shell
  KOLLA_ANSIBLE_DATA_FILES_PATH=$(python3 -c "import kolla_ansible;from pathlib import Path;print(Path(kolla_ansible.__file__).parents[4].joinpath('share/kolla-ansible'))")
  ```

  Install kolla-ansible patch

  ```shell
  curl https://opendev.org/skyline/skyline-apiserver/src/branch/master/kolla/kolla-ansible-xxxxxxx.diff -o /opt/kolla-ansible.diff
  cd ${KOLLA_ANSIBLE_DATA_FILES_PATH}
  git apply --check --include='ansible/*' /opt/kolla-ansible.diff
  git apply --include='ansible/*' /opt/kolla-ansible.diff
  ```

### Configuration

- If the configuration file does not exist(globals.yml/passwords.yml/all-in-one/multinode), copy the
  configuration files and generate passwords

  ```shell
  cp -r kolla-ansible/etc/kolla/* /etc/kolla
  cp kolla-ansible/ansible/inventory/* /etc/kolla
  kolla-genpwd
  ```

- If the configuration file exists(globals.yml/passwords.yml/all-in-one/multinode), modify it
  manually
  - Edit `/etc/kolla/all-in-one` and `/etc/kolla/multinode`, add the following options

    ```bash
    [skyline:children]
    control
    ```

  - Edit `/etc/kolla/passwords.yml` and add the following options, then generate passwords manually
    or by running `kolla-genpwd`

    ```shell
    skyline_database_password:
    skyline_keystone_password:
    ```

Edit `/etc/ansible/ansible.cfg` file

```bash
[defaults]
host_key_checking=False
pipelining=True
forks=100
```

Edit `/etc/kolla/globals.yml` file, for example:

```bash
network_interface: "eth0"
neutron_external_interface: "eth1"
kolla_internal_vip_address: "192.168.10.250"
enable_skyline: "yes"
docker_registry: "127.0.0.1:4000"
docker_namespace: "kolla"
kolla_base_distro: "ubuntu"
kolla_install_type: "source"
```

### Skyline Deployment

> **Note : Openstack basic modules have been installed**

```shell
kolla-ansible -i ./all-in-one bootstrap-servers -t skyline
kolla-ansible -i ./all-in-one prechecks -t skyline
kolla-ansible -i ./all-in-one deploy -t skyline
```

## FAQ

### Local Repository Error "connect: Connection refused" occurred during skyline image build and skyline deployment

Edit `/etc/docker/daemon.json` file and Delete the following options

```shell
bridge: "none"
```

Restart docker service

```shell
sudo service docker restart
```

Run local registry

```shell
docker run -d --name registry --restart=always -p 4000:5000 -v registry:/var/lib/registry registry:2
```

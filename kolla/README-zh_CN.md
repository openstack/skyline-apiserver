# Kolla Ansible 部署

## 环境准备

> **部署环境配置建议:**\
> 2个网络接口\
> 8GB内存\
> 100GB磁盘\
> ubuntu20.04 / centos8

- kolla : `https://github.com/openstack/kolla`
- kolla-ansible : `https://github.com/openstack/kolla-ansible`

## kolla build docker image

- 若部署环境未安装 kolla

  ```shell
  cd /opt
  git clone https://github.com/openstack/kolla
  cd /opt/kolla
  sudo pip3 install /opt/kolla
  ```

### skyline 镜像构建

> **注 : skyline 镜像目前仅支持 ubuntu-source-skyline 版本**

- `-b`:基础镜像类型
- `-t`:安装方式
- `-n`:命名空间
- `--tag`:标签
- `--registry`:docker仓库
- `--push`:镜像构建之后自动推送

```shell
kolla-build -b ubuntu -t source -n kolla --tag master --registry 127.0.0.1:4000 --push skyline
```

## kolla-ansible install

### kolla-ansible 安装

- 若部署环境未安装 kolla-ansible

  ```shell
  cd /opt
  git clone https://github.com/openstack/kolla-ansible
  cd /opt/kolla-ansible
  sudo pip3 install /opt/kolla-ansible
  ```

### 配置文件

- 若没有配置文件(globals.yml/passwords.yml/all-in-one/multinode)，复制配置文件并生成密码

  ```shell
  sudo mkdir -p /etc/kolla
  sudo chown $USER:$USER /etc/kolla
  cp -r kolla-ansible/etc/kolla/* /etc/kolla
  cp kolla-ansible/ansible/inventory/* .
  kolla-genpwd
  ```

- 若已有配置文件，则需要手动更改
  - 编辑 `all-in-one` 和 `multinode` 并增加以下配置项

    ```bash
    [skyline:children]
    control
    ```

  - 编辑 `/etc/kolla/passwords.yml` 并增加以下配置项，自定义密码或使用 `kolla-genpwd` 命令生成以下配置密码

    ```shell
    skyline_database_password:
    skyline_keystone_password:
    ```

创建并编辑 `/etc/ansible/ansible.cfg` 文件

```bash
[defaults]
host_key_checking=False
pipelining=True
forks=100
```

编辑 `/etc/kolla/globals.yml` 文件，根据构建的skyline镜像更改配置项

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

### skyline 部署

> **注 : 环境需已安装 Openstack 基础模块**

kolla-ansible 进行 skyline 部署，选择 `all-in-one` 或 `multinode` 配置文件

```shell
kolla-ansible -i ./all-in-one bootstrap-servers -t skyline
kolla-ansible -i ./all-in-one prechecks -t skyline
kolla-ansible -i ./all-in-one deploy -t skyline
```

## FAQ

### 在 skyline 镜像构建 和 skyline 部署过程中出现本地仓库 "connect: connection refused" 错误

编辑 `/etc/docker/daemon.json` 文件，删除以下配置项

```shell
bridge: "none"
```

重启 docker 服务

```shell
sudo service docker restart
```

启动本地镜像 registry

```shell
docker run -d --name registry --restart=always -p 4000:5000 -v registry:/var/lib/registry registry:2
```

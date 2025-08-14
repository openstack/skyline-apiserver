# Copyright 2021 99cloud
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import Any, Dict, List, Optional

from cinderclient.exceptions import NotFound
from dateutil import parser
from fastapi import status
from fastapi.param_functions import Depends, Header, Query
from fastapi.routing import APIRouter

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.api.wrapper.openstack import OSPort, OSServer, OSVolume, OSVolumeSnapshot
from skyline_apiserver.api.wrapper.skyline import Port, Server, Service, Volume, VolumeSnapshot
from skyline_apiserver.client import utils
from skyline_apiserver.client.openstack import cinder, glance, keystone, neutron, nova
from skyline_apiserver.client.utils import generate_session, get_system_session
from skyline_apiserver.config import CONF
from skyline_apiserver.log import LOG
from skyline_apiserver.schemas.extension import (
    ComputeServicesResponseBase,
    PortsResponseBase,
    RecycleServersResponseBase,
)
from skyline_apiserver.types import constants
from skyline_apiserver.utils.roles import assert_system_admin_or_reader, is_system_reader_no_admin

router = APIRouter()

STEP = constants.ID_UUID_RANGE_STEP


@router.get(
    "/extension/servers",
    description="List Servers",
    responses={
        200: {"model": schemas.ServersResponse},
        400: {"model": schemas.BadRequestMessage},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.ServersResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_servers(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: Optional[int] = Query(
        None,
        description=(
            "Requests a page size of items. Returns a number of items up to a limit value."
        ),
        gt=constants.EXTENSION_API_LIMIT_GT,
    ),
    marker: Optional[str] = Query(None, description="The ID of the last-seen item."),
    sort_dirs: Optional[schemas.SortDir] = Query(
        None, description="Indicates in which directions to sort."
    ),
    sort_keys: List[schemas.ServerSortKey] = Query(
        None,
        description=(
            "Indicates in which attributes to sort. Host is only used for admin role users"
        ),
    ),
    all_projects: Optional[bool] = Query(None, description="List servers for all projects."),
    project_id: Optional[str] = Query(
        None,
        description=(
            "Filter the list of servers by the given project ID. "
            "Only works when the all_projects filter is also specified."
        ),
    ),
    project_name: Optional[str] = Query(
        None,
        description=(
            "Filter the list of servers by the given project name. "
            "Only works when the all_projects filter is also specified."
        ),
    ),
    name: Optional[str] = Query(
        None,
        description=("Filter the list of servers by the given server name. Support fuzzy query."),
    ),
    status: Optional[schemas.ServerStatus] = Query(
        None, description="Filter the list of servers by the given server status."
    ),
    host: Optional[str] = Query(
        None,
        description=(
            "Filter the list of servers by the given host. "
            "It will be ignored for non-admin user."
        ),
    ),
    flavor_id: str = Query(
        None, description="Filter the list of servers by the given flavor ID."
    ),
    uuid: str = Query(None, description="Filter the list of servers by the given server UUID."),
    ip: Optional[str] = Query(
        None,
        description=(
            "Filter the list of servers by the given IP address (only fixed, not floating). "
            "Also passed to Nova API if supported."
        ),
    ),
) -> schemas.ServersResponse:
    all_projects = all_projects or False
    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get servers for all projects.",
        )
    else:
        project_id = None
        project_name = None

    current_session = generate_session(profile)
    system_session = get_system_session()

    # Check first if we supply the project_name filter.
    if project_name:
        filter_projects = keystone.list_projects(
            profile=profile,
            session=system_session,
            global_request_id=x_openstack_request_id,
            all_projects=all_projects,
            search_opts={"name": project_name},
        )
        if not filter_projects:
            return schemas.ServersResponse(**{"servers": []})
        else:
            # Projects will not have the same name or same id in the same domain
            filter_project = filter_projects[0]
            # When we both supply the project_id and project_name filter, if the project's id does
            # not equal the project_id, just return [].
            if project_id and filter_project.id != project_id:
                return schemas.ServersResponse(**{"servers": []})
            project_id = filter_project.id

    search_opts = {
        "name": name,
        "status": status,
        "host": host,
        "flavor": flavor_id,
        "project_id": project_id,
        "all_tenants": all_projects,
        "uuid": uuid,
    }
    if ip is not None:
        search_opts["ip"] = ip
    servers = nova.list_servers(
        profile=profile,
        session=current_session,
        global_request_id=x_openstack_request_id,
        search_opts=search_opts,
        marker=marker,
        limit=limit,
        sort_keys=[sort_key.value for sort_key in sort_keys] if sort_keys else None,
        sort_dirs=[sort_dirs.value] if sort_dirs else None,
    )

    result: List = []
    server_ids = set()
    image_ids = set()
    root_device_ids = set()
    for server in servers:
        origin_data = OSServer(server).to_dict()
        server = Server(server).to_dict()
        server["origin_data"] = origin_data
        result.append(server)
        server_ids.add(server["id"])
        if server["image"] and server["image"] not in image_ids:
            image_ids.add(server["image"])
        for volume_attached in server["volumes_attached"]:
            root_device_ids.add(volume_attached["id"])

    # Get all images and merge image_mappings
    images = []
    image_ids_list = list(image_ids)
    for i in range(0, len(image_ids_list), STEP):
        images_batch = glance.list_images(
            profile=profile,
            session=system_session,
            global_request_id=x_openstack_request_id,
            filters={"id": "in:" + ",".join(image_ids_list[i : i + STEP])},
        )
        images.extend(images_batch)
    image_mappings = {
        image.id: {
            "name": image.name,
            "image_os_distro": getattr(image, "os_distro", None),
        }
        for image in images
    }

    # Get all root device volumes and merge ser_image_mappings
    root_device_ids_list = list(root_device_ids)
    volumes = []
    for i in range(0, len(root_device_ids_list), STEP):
        volumes_batch = cinder.list_volumes(
            profile=profile,
            session=system_session,
            global_request_id=x_openstack_request_id,
            search_opts={"id": root_device_ids_list[i : i + STEP], "all_tenants": True},
        )
        volumes.extend(volumes_batch)
    ser_image_mappings = {}
    for volume in volumes:
        image_meta = getattr(volume, "volume_image_metadata", None)
        for attachment in volume.attachments:
            if image_meta:
                ser_image_mappings[attachment["server_id"]] = {
                    "image": image_meta.get("image_id"),
                    "image_name": image_meta.get("image_name"),
                    "image_os_distro": image_meta.get("os_distro"),
                }

    # enrich server
    for server in result:
        server["host"] = server["host"] if all_projects else None
        server["project_name"] = None
        ser_image_mapping = ser_image_mappings.get(server["id"])
        if ser_image_mapping:
            server.update(ser_image_mapping)
        elif server["image"]:
            image_info = image_mappings.get(server["image"], {})
            server["image_name"] = image_info.get("name", "")
            server["image_os_distro"] = image_info.get("image_os_distro", "")
        else:
            server["image_name"] = None
            server["image_os_distro"] = None
    if all_projects:
        projects = keystone.list_projects(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            all_projects=True,
        )
        project_id_name_map = {project.id: project.name for project in projects}
        for server in result:
            server["project_name"] = project_id_name_map[server["project_id"]]

    return schemas.ServersResponse(**{"servers": result})


@router.get(
    "/extension/recycle_servers",
    description="List Recycle Servers",
    responses={
        200: {"model": schemas.RecycleServersResponse},
        400: {"model": schemas.BadRequestMessage},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.RecycleServersResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_recycle_servers(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: Optional[int] = Query(
        None,
        description=(
            "Requests a page size of items. Returns a number of items up to a limit value."
        ),
        gt=constants.EXTENSION_API_LIMIT_GT,
    ),
    marker: Optional[str] = Query(None, description="The ID of the last-seen item."),
    sort_dirs: Optional[schemas.SortDir] = Query(
        None, description="Indicates in which directions to sort."
    ),
    sort_keys: Optional[List[schemas.RecycleServerSortKey]] = Query(
        None,
        description=("Indicates in which attributes to sort. Updated_at is used as deleted_at"),
    ),
    all_projects: Optional[bool] = Query(
        None, description="List recycle servers for all projects."
    ),
    project_id: Optional[str] = Query(
        None,
        description=(
            "Filter the list of recycle servers by the given project ID. "
            "Only works when the all_projects filter is also specified."
        ),
    ),
    project_name: Optional[str] = Query(
        None,
        description=(
            "Filter the list of recycle servers by the given project name. "
            "Only works when the all_projects filter is also specified."
        ),
    ),
    name: Optional[str] = Query(
        None,
        description=(
            "Filter the list of recycle servers by the given server name. Support fuzzy query."
        ),
    ),
    uuid: Optional[str] = Query(
        None, description="Filter the list of recycle servers by the given recycle server UUID."
    ),
    ip: Optional[str] = Query(
        None,
        description=(
            "Filter the list of recycle servers by the given IP address "
            "(only fixed, not floating). Also passed to Nova API if supported."
        ),
    ),
) -> schemas.RecycleServersResponse:
    all_projects = all_projects or False
    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get recycle servers for all projects.",
        )
    else:
        project_id = None
        project_name = None

    current_session = generate_session(profile)
    system_session = get_system_session()

    # Check first if we supply the project_name filter.
    if project_name:
        filter_projects = keystone.list_projects(
            profile=profile,
            session=system_session,
            global_request_id=x_openstack_request_id,
            all_projects=all_projects,
            search_opts={"name": project_name},
        )
        if not filter_projects:
            return schemas.RecycleServersResponse(**{"recycle_servers": []})
        else:
            filter_project = filter_projects[0]
            if project_id and filter_project.id != project_id:
                return schemas.RecycleServersResponse(**{"recycle_servers": []})
            project_id = filter_project.id

    # The deleted args will be ignored if non-admin user. So we have to use system session.
    # System session don't have current project info. So we have to use all_tenants & project_id.
    search_opts = {
        "status": "soft_deleted",
        "deleted": True,
        "all_tenants": True,
        "name": name,
        "project_id": project_id,
        "uuid": uuid,
    }
    if ip is not None:
        search_opts["ip"] = ip
    if not all_projects:
        search_opts["project_id"] = profile.project.id
    servers = nova.list_servers(
        profile=profile,
        session=system_session,
        global_request_id=x_openstack_request_id,
        search_opts=search_opts,
        marker=marker,
        limit=limit,
        sort_keys=[sort_key.value for sort_key in sort_keys] if sort_keys else None,
        sort_dirs=[sort_dirs.value] if sort_dirs else None,
    )

    result: List[RecycleServersResponseBase] = []
    server_ids = []
    image_ids = []
    root_device_ids = []
    for server in servers:
        origin_data = OSServer(server).to_dict()
        server = Server(server).to_dict()
        server["origin_data"] = origin_data
        result.append(RecycleServersResponseBase.parse_obj(server))
        server_ids.append(server["id"])
        if server["image"] and server["image"] not in image_ids:
            image_ids.append(server["image"])
        for volume_attached in server["volumes_attached"]:
            root_device_ids.append(volume_attached["id"])

    # Get all images and merge image_mappings
    images = []
    for i in range(0, len(image_ids), STEP):
        images_batch = glance.list_images(
            profile=profile,
            session=system_session,
            global_request_id=x_openstack_request_id,
            filters={"id": "in:" + ",".join(image_ids[i : i + STEP])},
        )
        images.extend(images_batch)
    image_mappings = {
        image.id: {
            "name": image.name,
            "image_os_distro": getattr(image, "os_distro", None),
        }
        for image in images
    }

    # Get all root device volumes and merge ser_image_mappings
    root_device_ids = list(set(root_device_ids))
    volumes = []
    for i in range(0, len(root_device_ids), STEP):
        volumes_batch = cinder.list_volumes(
            profile=profile,
            session=system_session,
            global_request_id=x_openstack_request_id,
            search_opts={"id": root_device_ids[i : i + STEP], "all_tenants": True},
        )
        volumes.extend(volumes_batch)
    ser_image_mappings = {}
    for volume in volumes:
        image_meta = getattr(volume, "volume_image_metadata", None)
        for attachment in volume.attachments:
            if image_meta:
                ser_image_mappings[attachment["server_id"]] = {
                    "image": image_meta.get("image_id"),
                    "image_name": image_meta.get("image_name"),
                    "image_os_distro": image_meta.get("os_distro"),
                }

    # enrich server
    for recycle_server in result:
        recycle_server.host = recycle_server.host if all_projects else None
        recycle_server.project_name = None
        recycle_server.deleted_at = recycle_server.updated_at
        recycle_server.reclaim_timestamp = (
            parser.isoparse(str(recycle_server.updated_at or "")).timestamp()
            + CONF.openstack.reclaim_instance_interval
        )
        ser_image_mapping = ser_image_mappings.get(recycle_server.id)
        if ser_image_mapping:
            recycle_server.image = ser_image_mapping["image"]
            recycle_server.image_name = ser_image_mapping["image_name"]
            recycle_server.image_os_distro = ser_image_mapping["image_os_distro"]
        elif recycle_server.image:
            image_info = image_mappings.get(recycle_server.image, {})
            recycle_server.image_name = image_info.get("name", "")
            recycle_server.image_os_distro = image_info.get("image_os_distro", "")
        else:
            recycle_server.image_name = None
            recycle_server.image_os_distro = None
    if all_projects:
        projects = keystone.list_projects(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            all_projects=True,
        )
        project_id_name_map = {project.id: project.name for project in projects}
        for recycle_server in result:
            recycle_server.project_name = project_id_name_map.get(recycle_server.project_id)
    return schemas.RecycleServersResponse(recycle_servers=result)


@router.get(
    "/extension/volumes",
    description="List Volumes",
    responses={
        200: {"model": schemas.VolumesResponse},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.VolumesResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_volumes(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: Optional[int] = Query(
        None,
        description=(
            "Requests a page size of items. Returns a number of items up to a limit value."
        ),
        gt=constants.EXTENSION_API_LIMIT_GT,
    ),
    marker: Optional[str] = Query(None, description="The ID of the last-seen item."),
    sort_dirs: Optional[schemas.SortDir] = Query(
        None, description="Indicates in which directions to sort."
    ),
    sort_keys: Optional[List[schemas.VolumeSortKey]] = Query(
        None,
        description=("Indicates in which attributes to sort. Updated_at is used as deleted_at"),
    ),
    all_projects: Optional[bool] = Query(None, description="List volumes for all projects."),
    project_id: Optional[str] = Query(
        None,
        description="Filter the list of volumes by the given project ID.",
    ),
    name: Optional[str] = Query(
        None,
        description="Filter the list of volumes by the given server name.",
    ),
    multiattach: Optional[bool] = Query(
        None,
        description="Filter the list of volumes by the given multiattach.",
    ),
    status: Optional[schemas.VolumeStatus] = Query(
        None,
        description="Filter the list of volumes by the given status.",
    ),
    bootable: Optional[bool] = Query(
        None,
        description="Filter the list of volumes by the given bootable.",
    ),
    uuid: Optional[List[str]] = Query(
        None, description="Filter the list of volumes by the given volumes UUID."
    ),
) -> schemas.VolumesResponse:
    all_projects = all_projects or False
    current_session = generate_session(profile)
    system_session = get_system_session()
    cinder_session = current_session

    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get volumes for all projects.",
        )
        # if not is_admin, cinder will ignore the all_projects query param.
        # role:admin or role:cinder_system_admin is is_admin.
        # so here we just use skyline session to get all_projects' volumes.
        if is_system_reader_no_admin(profile=profile):
            cinder_session = system_session
    else:
        project_id = None

    sort = None
    if sort_keys:
        if sort_dirs:
            sort = ",".join([f"{sort_key}:{sort_dirs}" for sort_key in sort_keys])
        else:
            sort = ",".join(sort_keys)

    search_opts = {
        "with_count": True,
        "name": name,
        "multiattach": str(multiattach) if multiattach is not None else multiattach,
        "status": status,
        "all_tenants": all_projects,
        "project_id": project_id,
        "bootable": str(bootable) if bootable is not None else bootable,
        "id": uuid,
    }

    if uuid:
        # Here we use system_session to filter volume with id list.
        # So we need to set all_tenants as True to filter volume from
        # all volumes. Otherwise, we just filter volume from the user
        # of system_session.
        cinder_session = system_session
        if not search_opts["all_tenants"]:
            search_opts["project_id"] = profile.project.id
            search_opts["all_tenants"] = True

    volumes, count = cinder.list_volumes(
        profile=profile,
        session=cinder_session,
        global_request_id=x_openstack_request_id,
        limit=limit,
        marker=marker,
        search_opts=search_opts,
        sort=sort,
    )
    result = []
    server_ids_set = set()
    for volume in volumes:
        origin_data = OSVolume(volume).to_dict()
        volume = Volume(volume).to_dict()
        volume["origin_data"] = origin_data
        result.append(volume)
        for attachment in volume["attachments"]:
            server_id = attachment.get("server_id")
            if server_id:
                server_ids_set.add(server_id)

    # Sometimes, the servers have been soft deleted, but the volumes will
    # be still displayed on the volume page. If we do not get the recycle
    # servers, the attachment server name for those volumes which are attached
    # to these servers will be blank.
    server_ids = list(server_ids_set)
    server_name_map = {}
    servers = []
    for server_id in server_ids:
        normal_servers = nova.list_servers(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            search_opts={
                "uuid": server_id,
                "all_tenants": all_projects,
            },
        )
        if normal_servers:
            servers.extend(normal_servers)

    # Query soft deleted server
    for server_id in server_ids:
        soft_deleted_servers = nova.list_servers(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            search_opts={
                "uuid": server_id,
                "status": "soft_deleted",
                "deleted": True,
                "all_tenants": all_projects,
            },
        )
        if soft_deleted_servers:
            servers.extend(soft_deleted_servers)

    for server in servers:
        server_name_map[server.id] = server.name

    for volume in result:
        for attachment in volume["attachments"]:
            server_id = attachment.get("server_id")
            if server_id:
                attachment["server_name"] = server_name_map.get(server_id)

    return schemas.VolumesResponse(**{"count": count, "volumes": result})


@router.get(
    "/extension/volume_snapshots",
    description="List Volume Snapshots.",
    responses={
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.VolumeSnapshotsResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_volume_snapshots(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: Optional[int] = Query(
        None,
        description="Requests a page size of items. Return items up to the limit value.",
        gt=constants.EXTENSION_API_LIMIT_GT,
    ),
    marker: Optional[str] = Query(None, description="The ID of the last-seen item."),
    sort_dirs: Optional[schemas.SortDir] = Query(
        None, description="Indicates in which directions to sort."
    ),
    sort_keys: Optional[List[schemas.VolumeSnapshotSortKey]] = Query(
        None, description="Indicates in which attributes to sort."
    ),
    all_projects: Optional[bool] = Query(None, description="List snapshots for all projects."),
    project_id: Optional[str] = Query(
        None, description="Filter the list of snapshots by the given project ID."
    ),
    name: Optional[str] = Query(
        None, description="Filter the list of snapshots by the given snapshot name."
    ),
    status: Optional[schemas.VolumeSnapshotStatus] = Query(
        None, description="Filter the list of snapshots by the given snapshot status."
    ),
    volume_id: Optional[str] = Query(
        None, description="Filter the list of snapshots by the given volume ID."
    ),
    uuid: Optional[str] = Query(
        None, description="Filter the list of snapshots by the given snapshot UUID."
    ),
) -> schemas.VolumeSnapshotsResponse:
    all_projects = all_projects or False
    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get volume snapshots for all projects.",
        )
    else:
        project_id = None

    current_session = generate_session(profile=profile)
    system_session = get_system_session()

    sort = None
    if sort_keys:
        if sort_dirs:
            sort = ",".join([f"{sort_key}:{sort_dirs}" for sort_key in sort_keys])
        else:
            sort = ",".join(sort_keys)
    search_opts = {
        "with_count": True,
        "name": name,
        "status": status,
        "volume_id": volume_id,
        "all_tenants": all_projects,
        "project_id": project_id,
        "id": uuid,
    }

    snapshot_session = current_session
    if uuid:
        if not all_projects:
            # We need to check the project_id of volume snapshot is the same
            # of current project id.
            try:
                volume_snapshot = cinder.get_volume_snapshot(
                    session=current_session,
                    region=profile.region,
                    global_request_id=x_openstack_request_id,
                    snapshot_id=uuid,
                )
            except NotFound as ex:
                LOG.debug(f"Not found volume snapshot with id '{uuid}': {ex}")
                return schemas.VolumeSnapshotsResponse(count=0, volume_snapshots=[])
            if volume_snapshot.project_id != profile.project.id:
                LOG.debug(
                    f"Volume snapshot with id '{uuid}' is in project "
                    f"'{volume_snapshot.project_id}', not in '{profile.project.id}'"
                )
                return schemas.VolumeSnapshotsResponse(count=0, volume_snapshots=[])
        snapshot_session = get_system_session()
        search_opts["all_tenants"] = True

    volume_snapshots, count = cinder.list_volume_snapshots(
        profile=profile,
        session=snapshot_session,
        global_request_id=x_openstack_request_id,
        limit=limit,
        marker=marker,
        search_opts=search_opts,
        sort=sort,
    )
    result = []
    volume_ids = []
    snapshot_ids = []
    for volume_snapshot in volume_snapshots:
        origin_data = OSVolumeSnapshot(volume_snapshot).to_dict()
        volume_snapshot = VolumeSnapshot(volume_snapshot).to_dict()
        volume_snapshot["origin_data"] = origin_data
        result.append(volume_snapshot)
        volume_ids.append(volume_snapshot["volume_id"])
        snapshot_ids.append(volume_snapshot["id"])

    if all_projects:
        projects = keystone.list_projects(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            all_projects=all_projects,
        )
    else:
        projects = []

    volume_ids = list(set(volume_ids))
    all_volumes = []
    for i in range(0, len(volume_ids), STEP):
        # Here we use system_session to filter volume with id list.
        # So we need to set all_tenants as True to filter volume from
        # all volumes. Otherwise, we just filter volume from the user
        # of system_session.
        volumes = cinder.list_volumes(
            profile=profile,
            session=system_session,
            global_request_id=x_openstack_request_id,
            search_opts={"id": volume_ids[i : i + STEP], "all_tenants": True},
        )
        all_volumes.extend(volumes)

    all_volumes_from_snapshot = []
    for i in range(0, len(snapshot_ids), STEP):
        # Here we use system_session to filter volume with snapshot_id list.
        # So we need to set all_tenants as True to filter volume from
        # all volumes. Otherwise, we just filter volume from the user
        # of system_session.
        volumes_from_snapshot = cinder.list_volumes(
            profile=profile,
            session=system_session,
            global_request_id=x_openstack_request_id,
            search_opts={
                "snapshot_id": snapshot_ids[i : i + STEP],
                "all_tenants": True,
            },
        )
        all_volumes_from_snapshot.extend(volumes_from_snapshot)

    proj_mappings = {project.id: project.name for project in projects}
    vol_mappings = {}
    for volume in all_volumes:
        vol_mappings[volume.id] = {
            "name": volume.name,
            "host": getattr(volume, "os-vol-host-attr:host", None),
        }
    child_volumes: Dict[str, Any] = {}
    for volume in all_volumes_from_snapshot:
        child_volumes.setdefault(volume.snapshot_id, [])
        child_volumes[volume.snapshot_id].append(
            {"volume_id": volume.id, "volume_name": volume.name}
        )

    for snapshot in result:
        snapshot["project_name"] = proj_mappings.get(snapshot["project_id"])
        vol_mapping = vol_mappings.get(snapshot["volume_id"])
        if vol_mapping:
            snapshot["volume_name"] = vol_mapping["name"]
            snapshot["host"] = vol_mapping["host"] if all_projects else None
        snapshot["child_volumes"] = child_volumes.get(snapshot["id"], [])
    return schemas.VolumeSnapshotsResponse(**{"count": count, "volume_snapshots": result})


@router.get(
    "/extension/ports",
    description="List Ports.",
    responses={
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.PortsResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
def list_ports(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: Optional[int] = Query(
        None,
        description=(
            "Requests a page size of items. Returns a number of items up to a limit value."
        ),
        gt=constants.EXTENSION_API_LIMIT_GT,
    ),
    marker: Optional[str] = Query(None, description="The ID of the last-seen item."),
    sort_dirs: Optional[schemas.SortDir] = Query(
        None, description="Indicates in which directions to sort."
    ),
    sort_keys: Optional[List[schemas.PortSortKey]] = Query(
        None, description="Indicates in which attributes to sort."
    ),
    all_projects: Optional[bool] = Query(None, description="List ports for all projects."),
    project_id: Optional[str] = Query(
        None, description="Filter the list of ports by the given project ID."
    ),
    name: Optional[str] = Query(
        None, description="Filter the list of ports by the given port name."
    ),
    status: Optional[schemas.PortStatus] = Query(
        None, description="Filter the list of ports by the given port status."
    ),
    network_name: Optional[str] = Query(
        None, description="Filter the list of ports by the given network name."
    ),
    network_id: Optional[str] = Query(
        None, description="Filter the list of ports by the given network ID."
    ),
    device_id: Optional[str] = Query(
        None,
        description=(
            "The ID of the device that uses this port. For example, "
            "a server instance or a logical router."
        ),
    ),
    device_owner: Optional[List[schemas.PortDeviceOwner]] = Query(
        None, description="The entity type that uses this port."
    ),
    uuid: Optional[List[str]] = Query(
        None, description="Filter the list of ports by the given port UUID."
    ),
) -> schemas.PortsResponse:
    all_projects = all_projects or False
    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get ports for all projects.",
        )
    else:
        project_id = None

    current_session = generate_session(profile)

    kwargs: Dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if marker is not None:
        kwargs["marker"] = marker
    if not all_projects:
        kwargs["project_id"] = profile.project.id
    if project_id is not None:
        kwargs["project_id"] = project_id
    if name is not None:
        kwargs["name"] = name
    if status is not None:
        kwargs["status"] = status
    if device_owner is not None:
        kwargs["device_owner"] = device_owner
    if uuid is not None:
        kwargs["id"] = set(uuid)
    if network_name is not None:
        networks = neutron.list_networks(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            **{"name": network_name},
        )
        if not networks["networks"]:
            return schemas.PortsResponse(**{"ports": []})
        network_ids = [network["id"] for network in networks["networks"]]
        kwargs["network_id"] = network_ids
    if network_id is not None:
        network_ids = kwargs.get("network_id", [])
        if network_ids and network_id not in network_ids:
            return schemas.PortsResponse(**{"ports": []})
        elif not network_ids:
            network_ids.append(network_id)
        kwargs["network_id"] = network_ids
    if device_id is not None:
        kwargs["device_id"] = device_id
    if sort_keys is not None:
        sort_dir = []
        sort_dir.extend([sort_dirs if sort_dirs is not None else "asc"] * len(sort_keys))
        kwargs["sort_dir"] = sort_dir
        kwargs["sort_key"] = sort_keys

    ports = neutron.list_ports(
        current_session,
        profile.region,
        x_openstack_request_id,
        **kwargs,
    )

    server_ids = []
    network_ids = []
    result: List[PortsResponseBase] = []
    for port in ports.next().get("ports", []):
        origin_data = OSPort(port).to_dict()
        port = Port(port).to_dict()
        port["origin_data"] = origin_data
        result.append(PortsResponseBase.parse_obj(port))
        if port["device_owner"] == "compute:nova":
            server_ids.append(port["device_id"])
        network_ids.append(port["network_id"])

    network_params: Dict[str, Any] = {}
    shared_nets = neutron.list_networks(
        profile=profile,
        session=current_session,
        global_request_id=x_openstack_request_id,
        **{"shared": True},
    )
    networks_result = []
    shared_nets_list = shared_nets.get("networks", [])
    networks_result.extend(shared_nets_list)

    if not all_projects:
        network_params["project_id"] = profile.project.id
    network_ids = list(set(network_ids))
    # We should split the network_ids with 100 number.
    # If we do not do this, the length of url will be too long to do request.
    for i in range(0, len(network_ids), STEP):
        network_params["id"] = set(network_ids[i : i + STEP])
        nets = neutron.list_networks(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            **network_params,
        )
        nets_list = nets.get("networks", [])
        networks_result.extend(nets_list)

    server_ids = list(set(server_ids))
    ser_mappings = {}
    for server_id in server_ids:
        servers = nova.list_servers(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            search_opts={
                "uuid": server_id,
                "all_tenants": all_projects,
            },
        )
        if servers:
            server = servers[0]
            ser_mappings[server.id] = server.name
    network_mappings = {net["id"]: net["name"] for net in networks_result}
    for port in result:
        port.server_name = ser_mappings.get(port.device_id)
        port.network_name = network_mappings.get(port.network_id)
    return schemas.PortsResponse(ports=result)


@router.get(
    "/extension/compute-services",
    description="List compute services",
    responses={
        200: {"model": schemas.ComputeServicesResponse},
        401: {"model": schemas.UnauthorizedMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.ComputeServicesResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
    response_model_exclude_none=True,
)
def compute_services(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    binary: str = Query(
        None, description="Filter the list of compute services by the given binary."
    ),
    host: str = Query(None, description="Filter the list of compute services by the given host."),
) -> schemas.ComputeServicesResponse:
    assert_system_admin_or_reader(
        profile=profile,
        exception="Not allowed to get compute services.",
    )

    system_session = utils.get_system_session()

    kwargs = {}
    if binary is not None:
        kwargs["binary"] = binary
    if host is not None:
        kwargs["host"] = host
    services = nova.list_services(
        profile=profile,
        session=system_session,
        global_request_id=x_openstack_request_id,
        **kwargs,
    )
    services = [
        ComputeServicesResponseBase.parse_obj(Service(service).to_dict()) for service in services
    ]
    return schemas.ComputeServicesResponse(**{"services": services})

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

import asyncio
import math
from asyncio import gather
from functools import reduce
from typing import List

from dateutil import parser
from fastapi import APIRouter, Depends, Header, Query, status

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.api.v1.openstack.base import OSPort, OSServer, OSVolume, OSVolumeSnapshot
from skyline_apiserver.api.v1.utils import Port, Server, Service, Volume, VolumeSnapshot
from skyline_apiserver.client import utils
from skyline_apiserver.client.openstack import cinder, glance, keystone, neutron, nova
from skyline_apiserver.client.utils import generate_session, get_system_session
from skyline_apiserver.config import CONF
from skyline_apiserver.types import constants
from skyline_apiserver.utils.roles import assert_system_admin_or_reader, is_system_reader_no_admin

router = APIRouter()

STEP = constants.ID_UUID_RANGE_STEP


@router.get(
    "/extension/servers",
    description="""
List Servers.

*Notes*:
- The `host` of **sort_keys** is only used for admin/system_admin role users.
- The `name` is to support for fuzzy queries.
""",
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
async def list_servers(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: int = Query(None, gt=constants.EXTENSION_API_LIMIT_GT),
    marker: str = None,
    sort_dirs: schemas.SortDir = None,
    sort_keys: List[schemas.ServerSortKey] = Query(None),
    all_projects: bool = None,
    project_id: str = Query(
        None,
        description="Only works when the all_projects filter is also specified.",
    ),
    project_name: str = Query(
        None,
        description="Only works when the all_projects filter is also specified.",
    ),
    name: str = None,
    status: schemas.ServerStatus = None,
    host: str = Query(None, description="It will be ignored for non-admin user."),
    flavor_id: str = None,
    uuid: str = Query(None, description="UUID of server."),
) -> schemas.ServersResponse:
    """Extension List Servers.

    :param profile: Profile object include token, role and so on,
                    defaults to Depends(deps.get_profile_update_jwt)
    :type profile: schemas.Profile, optional
    :param limit: Limit count to fetch,
                  defaults to Query(None, gt=constants.EXTENSION_API_LIMIT_GT)
    :type limit: int, optional
    :param marker: Marker object to fetch, defaults to None
    :type marker: str, optional
    :param sort_dirs: Sort order, defaults to None
    :type sort_dirs: schemas.SortDir, optional
    :param sort_keys: Sort keys, defaults to Query(None)
    :type sort_keys: List[schemas.ServerSortKey], optional
    :param all_projects: All projects to fetch, defaults to None
    :type all_projects: bool, optional
    :param project_id: Filter by id of project which server belongs to,
                       defaults to Query(None, description="
                       Only works when the all_projects filter is also specified.")
    :type project_id: str, optional
    :param project_name: Filter by name of project which server belongs to,
                         defaults to Query(None, description="
                         Only works when the all_projects filter is also specified.")
    :type project_name: str, optional
    :param name: Filter by server name, defaults to None
    :type name: str, optional
    :param status: Filter by server status, defaults to None
    :type status: schemas.ServerStatus, optional
    :param host: Filter by host which server is located at,
                 defaults to Query(None, description="It will be ignored for non-admin user.")
    :type host: str, optional
    :param flavor_id: Filter by id of flavor which server is created by, defaults to None
    :type flavor_id: str, optional
    :param uuid: Filter by uuid, defaults to Query(None, description="UUID of server.")
    :type uuid: str, optional
    :raises HTTPException: HTTP Exception
    :return: Server List
    :rtype: schemas.ServersResponse
    """
    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get servers for all projects.",
        )

    current_session = await generate_session(profile=profile)
    system_session = get_system_session()

    # Check first if we supply the project_name filter.
    if project_name:
        filter_projects = await keystone.list_projects(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            all_projects=all_projects,
            search_opts={"name": project_name},
        )
        if not filter_projects:
            return {"servers": []}
        else:
            # Projects will not have the same name or same id in the same domain
            filter_project = filter_projects[0]
            # When we both supply the project_id and project_name filter, if the project's id does
            # not equal the project_id, just return [].
            if project_id and filter_project.id != project_id:
                return {"servers": []}
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
    servers = await nova.list_servers(
        profile=profile,
        session=current_session,
        global_request_id=x_openstack_request_id,
        search_opts=search_opts,
        marker=marker,
        limit=limit,
        sort_keys=sort_keys,
        sort_dirs=[sort_dirs] if sort_dirs else None,
    )

    result = []
    server_ids = []
    image_ids = []
    root_device_ids = []
    for server in servers:
        origin_data = OSServer(server).to_dict()
        server = Server(server).to_dict()
        server["origin_data"] = origin_data
        result.append(server)
        server_ids.append(server["id"])
        if server["image"] and server["image"] not in image_ids:
            image_ids.append(server["image"])
        for volume_attached in server["volumes_attached"]:
            root_device_ids.append(volume_attached["id"])

    if all_projects:
        tasks = [
            keystone.list_projects(
                profile=profile,
                session=current_session,
                global_request_id=x_openstack_request_id,
                all_projects=all_projects,
            ),
        ]
    else:
        tasks = [asyncio.sleep(0.01)]

    for i in range(0, len(image_ids), STEP):
        tasks.append(
            glance.list_images(
                profile=profile,
                session=system_session,
                global_request_id=x_openstack_request_id,
                filters={"id": "in:" + ",".join(image_ids[i : i + STEP])},
            ),
        )
    root_device_ids = list(set(root_device_ids))
    for i in range(0, len(root_device_ids), STEP):
        # Here we use system_session to filter volume with id list.
        # So we need to set all_tenants as True to filter volume from
        # all volumes. Otherwise, we just filter volume from the user
        # of system_session.
        tasks.append(
            cinder.list_volumes(
                profile=profile,
                session=system_session,
                global_request_id=x_openstack_request_id,
                search_opts={"id": root_device_ids[i : i + STEP], "all_tenants": True},
            ),
        )
    task_result = await gather(*tasks)

    projects = task_result[0] if task_result[0] else []
    proj_mappings = {project.id: project.name for project in projects}
    total_image_tasks = math.ceil(len(image_ids) / STEP)
    images = reduce(lambda x, y: list(x) + list(y), task_result[1 : 1 + total_image_tasks], [])
    volumes = reduce(lambda x, y: x + y, task_result[1 + total_image_tasks :], [])
    image_mappings = {
        image.id: {"name": image.name, "image_os_distro": getattr(image, "os_distro", None)}
        for image in list(images)
    }
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

    for server in result:
        server["host"] = server["host"] if all_projects else None
        server["project_name"] = proj_mappings.get(server["project_id"])
        ser_image_mapping = ser_image_mappings.get(server["id"])
        if ser_image_mapping:
            values = {
                "image": ser_image_mapping["image"],
                "image_name": ser_image_mapping["image_name"],
                "image_os_distro": ser_image_mapping["image_os_distro"],
            }
        elif server["image"]:
            values = {
                "image": server["image"],
                "image_name": image_mappings.get(server["image"], {}).get("name", ""),
                "image_os_distro": image_mappings.get(server["image"], {}).get(
                    "image_os_distro",
                    "",
                ),
            }
        else:
            values = {"image": None, "image_name": None, "image_os_distro": None}
        server.update(values)
    return {"servers": result}


@router.get(
    "/extension/recycle_servers",
    description="""
List Recycle Servers.

*Notes*:
- The `updated_at` of **sort_keys** is used as `deleted_at`.
- The `name` is to support for fuzzy queries.
""",
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
async def list_recycle_servers(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: int = Query(None, gt=constants.EXTENSION_API_LIMIT_GT),
    marker: str = None,
    sort_dirs: schemas.SortDir = None,
    sort_keys: List[schemas.RecycleServerSortKey] = Query(None),
    all_projects: bool = None,
    project_id: str = Query(
        None,
        description="Only works when the all_projects filter is also specified.",
    ),
    project_name: str = Query(
        None,
        description="Only works when the all_projects filter is also specified.",
    ),
    name: str = None,
    uuid: str = Query(None, description="UUID of recycle server."),
) -> schemas.RecycleServersResponse:
    """Extension List Recycle Servers.

    :param profile: Profile object include token, role and so on,
                    defaults to Depends(deps.get_profile_update_jwt)
    :type profile: schemas.Profile, optional
    :param limit: Limit count to fetch,
                  defaults to Query(None, gt=constants.EXTENSION_API_LIMIT_GT)
    :type limit: int, optional
    :param marker: Marker object to fetch, defaults to None
    :type marker: str, optional
    :param sort_dirs: Sort order, defaults to None
    :type sort_dirs: schemas.SortDir, optional
    :param sort_keys: Sort keys, defaults to Query(None)
    :type sort_keys: List[schemas.RecycleServerSortKey], optional
    :param all_projects: All projects to fetch, defaults to None
    :type all_projects: bool, optional
    :param project_id: Filter by id of project which recycle server belongs to,
                       defaults to Query(None, description="
                       Only works when the all_projects filter is also specified.")
    :type project_id: str, optional
    :param project_name: Filter by name of project which server belongs to,
                         defaults to Query(None, description="
                         Only works when the all_projects filter is also specified.")
    :type project_name: str, optional
    :param name: Filter by recycle server name, defaults to None
    :type name: str, optional
    :param uuid: Filter by uuid,
                 defaults to Query(None, description="UUID of recycle server.")
    :type uuid: str, optional
    :raises HTTPException: HTTP Exception
    :return: Recycle server list
    :rtype: schemas.RecycleServersResponse
    """

    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get recycle servers for all projects.",
        )

    current_session = await generate_session(profile=profile)
    system_session = get_system_session()

    # Check first if we supply the project_name filter.
    if project_name:
        filter_projects = await keystone.list_projects(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            all_projects=all_projects,
            search_opts={"name": project_name},
        )
        if not filter_projects:
            return {"recycle_servers": []}
        else:
            # Projects will not have the same name or same id in the same domain
            filter_project = filter_projects[0]
            # When we both supply the project_id and project_name filter, if the project's id does
            # not equal the project_id, just return [].
            if project_id and filter_project.id != project_id:
                return {"recycle_servers": []}
            project_id = filter_project.id

    search_opts = {
        "status": "soft_deleted",
        "deleted": True,
        "all_tenants": True,
        "name": name,
        "project_id": project_id,
        "uuid": uuid,
    }
    if not all_projects:
        search_opts["tenant_id"] = profile.project.id
    servers = await nova.list_servers(
        profile=profile,
        session=system_session,
        global_request_id=x_openstack_request_id,
        search_opts=search_opts,
        marker=marker,
        limit=limit,
        sort_keys=sort_keys,
        sort_dirs=[sort_dirs] if sort_dirs else None,
    )

    result = []
    server_ids = []
    image_ids = []
    root_device_ids = []
    for server in servers:
        origin_data = OSServer(server).to_dict()
        server = Server(server).to_dict()
        server["origin_data"] = origin_data
        result.append(server)
        server_ids.append(server["id"])
        if server["image"] and server["image"] not in image_ids:
            image_ids.append(server["image"])
        for volume_attached in server["volumes_attached"]:
            root_device_ids.append(volume_attached["id"])

    if all_projects:
        tasks = [
            keystone.list_projects(
                profile=profile,
                session=current_session,
                global_request_id=x_openstack_request_id,
                all_projects=all_projects,
            ),
        ]
    else:
        tasks = [asyncio.sleep(0.01)]

    for i in range(0, len(image_ids), STEP):
        tasks.append(
            glance.list_images(
                profile=profile,
                session=system_session,
                global_request_id=x_openstack_request_id,
                filters={"id": "in:" + ",".join(image_ids[i : i + STEP])},
            ),
        )
    root_device_ids = list(set(root_device_ids))
    for i in range(0, len(root_device_ids), STEP):
        # Here we use system_session to filter volume with id list.
        # So we need to set all_tenants as True to filter volume from
        # all volumes. Otherwise, we just filter volume from the user
        # of system_session.
        tasks.append(
            cinder.list_volumes(
                profile=profile,
                session=system_session,
                global_request_id=x_openstack_request_id,
                search_opts={"id": root_device_ids[i : i + STEP], "all_tenants": True},
            ),
        )
    task_result = await gather(*tasks)

    projects = task_result[0] if task_result[0] else []
    proj_mappings = {project.id: project.name for project in projects}
    total_image_tasks = math.ceil(len(image_ids) / STEP)
    images = reduce(lambda x, y: list(x) + list(y), task_result[1 : 1 + total_image_tasks], [])
    volumes = reduce(lambda x, y: x + y, task_result[1 + total_image_tasks :], [])
    image_mappings = {
        image.id: {"name": image.name, "image_os_distro": getattr(image, "os_distro", None)}
        for image in list(images)
    }
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

    for recycle_server in result:
        recycle_server["host"] = recycle_server["host"] if all_projects else None
        recycle_server["project_name"] = proj_mappings.get(recycle_server["project_id"])
        recycle_server["deleted_at"] = recycle_server["updated_at"]
        recycle_server["reclaim_timestamp"] = (
            parser.isoparse(recycle_server["updated_at"]).timestamp()
            + CONF.openstack.reclaim_instance_interval
        )
        ser_image_mapping = ser_image_mappings.get(recycle_server["id"])
        if ser_image_mapping:
            values = {
                "image": ser_image_mapping["image"],
                "image_name": ser_image_mapping["image_name"],
                "image_os_distro": ser_image_mapping["image_os_distro"],
            }
        elif recycle_server["image"]:
            values = {
                "image": recycle_server["image"],
                "image_name": image_mappings.get(recycle_server["image"], {}).get("name", ""),
                "image_os_distro": image_mappings.get(recycle_server["image"], {}).get(
                    "image_os_distro",
                    "",
                ),
            }
        else:
            values = {"image": None, "image_name": None, "image_os_distro": None}
        recycle_server.update(values)
    return {"recycle_servers": result}


@router.get(
    "/extension/volumes",
    description="List Volumes.",
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
async def list_volumes(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: int = Query(None, gt=constants.EXTENSION_API_LIMIT_GT),
    marker: str = None,
    sort_dirs: schemas.SortDir = None,
    sort_keys: List[schemas.VolumeSortKey] = Query(None),
    all_projects: bool = None,
    project_id: str = None,
    name: str = None,
    multiattach: bool = None,
    status: schemas.VolumeStatus = None,
    bootable: bool = None,
    uuid: List[str] = Query(None, description="UUID of volume."),
) -> schemas.VolumesResponse:
    """Extension List Volumes.

    :param profile: Profile object include token, role and so on,
                    defaults to Depends(deps.get_profile_update_jwt)
    :type profile: schemas.Profile, optional
    :param limit: Limit count to fetch,
                  defaults to Query(None, gt=constants.EXTENSION_API_LIMIT_GT)
    :type limit: int, optional
    :param marker: Marker object to fetch, defaults to None
    :type marker: str, optional
    :param sort_dirs: Sort order, defaults to None
    :type sort_dirs: schemas.SortDir, optional
    :param sort_keys: Sort keys, defaults to Query(None)
    :type sort_keys: List[schemas.VolumeSortKey], optional
    :param all_projects: All projects to fetch, defaults to None
    :type all_projects: bool, optional
    :param project_id: Filter by id of project which volume belongs to,
                       defaults to None
    :type project_id: str, optional
    :param name: Filter by volume name, defaults to None
    :type name: str, optional
    :param multiattach: Filter by multiattach that server is support multiattach or not,
                        defaults to None
    :type multiattach: bool, optional
    :param status: Filter by volume status, defaults to None
    :type status: schemas.VolumeStatus, optional
    :type bootable: Filter by bootable that server be used to create an instance quickly.
    :type bootable: bool, optional
    :param uuid: Filter by list uuid,
                 defaults to Query(None, description="UUID of volume.")
    :type uuid: List[str], optional
    :return: Volume list
    :rtype: schemas.VolumesResponse
    """
    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get volumes for all projects.",
        )

    current_session = await generate_session(profile=profile)
    system_session = get_system_session()

    sort = None
    if sort_keys:
        if sort_dirs:
            sort = ",".join([f"{sort_key}:{sort_dirs}" for sort_key in sort_keys])
        else:
            sort = ",".join(sort_keys)

    # If bootable is false, it is ineffective, due to existed issue of community
    # https://bugs.launchpad.net/python-cinderclient/+bug/1925737
    search_opts = {
        "with_count": True,
        "name": name,
        "multiattach": multiattach,
        "status": status,
        "all_tenants": all_projects,
        "project_id": project_id,
        "bootable": bootable,
        "id": uuid,
    }
    # if not is_admin, cinder will ignore the all_projects query param.
    # role:admin or role:cinder_system_admin is is_admin.
    # so here we just use skyline session to get all_projects' volumes.
    cinder_session = (
        system_session
        if all_projects and is_system_reader_no_admin(profile=profile)
        else current_session
    )

    if uuid:
        # Here we use system_session to filter volume with id list.
        # So we need to set all_tenants as True to filter volume from
        # all volumes. Otherwise, we just filter volume from the user
        # of system_session.
        cinder_session = system_session
        search_opts["all_tenants"] = True

    volumes, count = await cinder.list_volumes(
        profile=profile,
        session=cinder_session,
        global_request_id=x_openstack_request_id,
        limit=limit,
        marker=marker,
        search_opts=search_opts,
        sort=sort,
    )
    result = []
    server_ids = []
    # commit: https://review.opendev.org/c/openstack/python-cinderclient/+/767451
    # here is just a workaround way.
    while True:
        if volumes and isinstance(volumes[-1], int):
            volumes = volumes[0]
        else:
            break
    for volume in volumes:
        origin_data = OSVolume(volume).to_dict()
        volume = Volume(volume).to_dict()
        volume["origin_data"] = origin_data
        result.append(volume)
        for attachment in volume["attachments"]:
            if attachment["server_id"] not in server_ids:
                server_ids.append(attachment["server_id"])

    # Sometimes, the servers have been soft deleted, but the volumes will
    # be still displayed on the volume page. If we do not get the recycle
    # servers, the attachment server name for those volumes which are attached
    # to these servers will be blank.
    if all_projects:
        tasks = [
            keystone.list_projects(
                profile=profile,
                session=current_session,
                global_request_id=x_openstack_request_id,
                all_projects=all_projects,
            ),
        ]
    else:
        tasks = [asyncio.sleep(0.01)]
    # We should split the server_ids with 100 number.
    # If we do not do this, the length of url will be too long to do request.
    server_ids = list(set(server_ids))
    for i in range(0, len(server_ids), STEP):
        tasks.extend(
            [
                nova.list_servers(
                    profile=profile,
                    session=current_session,
                    global_request_id=x_openstack_request_id,
                    search_opts={
                        "uuid": server_ids[i : i + STEP],
                        "all_tenants": all_projects,
                    },
                ),
                nova.list_servers(
                    profile=profile,
                    session=current_session,
                    global_request_id=x_openstack_request_id,
                    search_opts={
                        "uuid": server_ids[i : i + STEP],
                        "status": "soft_deleted",
                        "deleted": True,
                        "all_tenants": all_projects,
                    },
                ),
            ],
        )
    task_result = await gather(*tasks)

    projects = [] if not task_result[0] else task_result[0]
    servers = reduce(lambda x, y: x + y, task_result[1:], [])
    proj_mappings = {project.id: project.name for project in projects}
    ser_mappings = {server.id: server.name for server in servers}

    for volume in result:
        volume["host"] = volume["host"] if all_projects else None
        volume["project_name"] = proj_mappings.get(volume["project_id"])
        for attachment in volume["attachments"]:
            attachment["server_name"] = ser_mappings.get(attachment["server_id"])
    return {"count": count, "volumes": result}


@router.get(
    "/extension/volume_snapshots",
    description="List Volume Snapshots.",
    responses={
        200: {"model": schemas.VolumeSnapshotsResponse},
        401: {"model": schemas.UnauthorizedMessage},
        403: {"model": schemas.ForbiddenMessage},
        500: {"model": schemas.InternalServerErrorMessage},
    },
    response_model=schemas.VolumeSnapshotsResponse,
    status_code=status.HTTP_200_OK,
    response_description="OK",
)
async def list_volume_snapshots(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: int = Query(None, gt=constants.EXTENSION_API_LIMIT_GT),
    marker: str = None,
    sort_dirs: schemas.SortDir = None,
    sort_keys: List[schemas.VolumeSnapshotSortKey] = Query(None),
    all_projects: bool = None,
    project_id: str = None,
    name: str = None,
    status: schemas.VolumeSnapshotStatus = None,
    volume_id: str = None,
) -> schemas.VolumeSnapshotsResponse:
    """Extension List Volume Snapshots.

    :param profile: Profile object include token, role and so on,
                    defaults to Depends(deps.get_profile_update_jwt)
    :type profile: schemas.Profile, optional
    :param limit: Limit count to fetch,
                  defaults to Query(None, gt=constants.EXTENSION_API_LIMIT_GT)
    :type limit: int, optional
    :param marker: Marker object to fetch, defaults to None
    :type marker: str, optional
    :param sort_dirs: Sort order, defaults to None
    :type sort_dirs: schemas.SortDir, optional
    :param sort_keys: Sort keys, defaults to Query(None)
    :type sort_keys: List[schemas.VolumeSnapshotSortKey], optional
    :param all_projects: All projects to fetch, defaults to None
    :type all_projects: bool, optional
    :param project_id: Filter by id of project which volume snapshots belongs to,
                       defaults to None
    :type project_id: str, optional
    :param name: Filter by volume snapshot name, defaults to None
    :type name: str, optional
    :param status: Filter by volume snapshot status, defaults to None
    :type status: schemas.VolumeSnapshotStatus, optional
    :param volume_id: Filter by volume id, defaults to None
    :type volume_id: str, optional
    :return: Volume snapshot list
    :rtype: schemas.VolumeSnapshotsResponse
    """
    if all_projects:
        assert_system_admin_or_reader(
            profile=profile,
            exception="Not allowed to get volume snapshots for all projects.",
        )

    current_session = await generate_session(profile=profile)

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
    }
    volume_snapshots, count = await cinder.list_volume_snapshots(
        profile=profile,
        session=current_session,
        global_request_id=x_openstack_request_id,
        limit=limit,
        marker=marker,
        search_opts=search_opts,
        sort=sort,
    )
    result = []
    volume_ids = []
    snapshot_ids = []
    # commit: https://review.opendev.org/c/openstack/python-cinderclient/+/767451
    # here is just a workaround way.
    while True:
        if volume_snapshots and isinstance(volume_snapshots[-1], int):
            volume_snapshots = volume_snapshots[0]
        else:
            break
    for volume_snapshot in volume_snapshots:
        origin_data = OSVolumeSnapshot(volume_snapshot).to_dict()
        volume_snapshot = VolumeSnapshot(volume_snapshot).to_dict()
        volume_snapshot["origin_data"] = origin_data
        result.append(volume_snapshot)
        volume_ids.append(volume_snapshot["volume_id"])
        snapshot_ids.append(volume_snapshot["id"])

    if all_projects:
        tasks = [
            keystone.list_projects(
                profile=profile,
                session=current_session,
                global_request_id=x_openstack_request_id,
                all_projects=all_projects,
            ),
        ]
    else:
        tasks = [asyncio.sleep(0.01)]

    volume_ids = list(set(volume_ids))
    for i in range(0, len(volume_ids), STEP):
        # Here we use system_session to filter volume with id list.
        # So we need to set all_tenants as True to filter volume from
        # all volumes. Otherwise, we just filter volume from the user
        # of system_session.
        tasks.append(
            cinder.list_volumes(
                profile=profile,
                session=get_system_session(),
                global_request_id=x_openstack_request_id,
                search_opts={"id": volume_ids[i : i + STEP], "all_tenants": True},
            ),
        )
    for i in range(0, len(snapshot_ids), STEP):
        tasks.append(
            cinder.list_volumes(
                profile=profile,
                session=current_session,
                global_request_id=x_openstack_request_id,
                search_opts={
                    "snapshot_id": snapshot_ids[i : i + STEP],
                    "all_tenants": all_projects,
                },
            ),
        )
    task_result = await gather(*tasks)

    projects = task_result[0] if task_result[0] else []
    total_volume_tasks = math.ceil(len(volume_ids) / STEP)
    volumes = reduce(lambda x, y: x + y, task_result[1 : 1 + total_volume_tasks], [])
    volumes_from_snapshot = reduce(lambda x, y: x + y, task_result[1 + total_volume_tasks :], [])

    proj_mappings = {project.id: project.name for project in projects}
    vol_mappings = {}
    for volume in volumes:
        vol_mappings[volume.id] = {
            "name": volume.name,
            "host": getattr(volume, "os-vol-host-attr:host", None),
        }
    child_volumes = {}
    for volume in volumes_from_snapshot:
        child_volumes.setdefault(volume.snapshot_id, [])
        child_volumes[volume.snapshot_id].append(volume.name)

    for snapshot in result:
        snapshot["project_name"] = proj_mappings.get(snapshot["project_id"])
        vol_mapping = vol_mappings.get(snapshot["volume_id"])
        if vol_mapping:
            snapshot["volume_name"] = vol_mapping["name"]
            snapshot["host"] = vol_mapping["host"] if all_projects else None
        snapshot["child_volumes"] = child_volumes.get(snapshot["id"], [])
    return {"count": count, "volume_snapshots": result}


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
async def list_ports(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    limit: int = Query(None, gt=constants.EXTENSION_API_LIMIT_GT),
    marker: str = None,
    sort_dirs: schemas.SortDir = None,
    sort_keys: List[schemas.PortSortKey] = Query(None),
    all_projects: bool = None,
    project_id: str = None,
    name: str = None,
    status: schemas.PortStatus = None,
    network_name: str = None,
    network_id: str = None,
    device_id: str = None,
    device_owner: List[schemas.PortDeviceOwner] = Query(None),
    uuid: List[str] = Query(None, description="UUID of port."),
) -> schemas.PortsResponse:
    """Extension List Ports.

    :param profile: Profile object include token, role and so on,
                    defaults to Depends(deps.get_profile_update_jwt)
    :type profile: schemas.Profile, optional
    :param limit: Limit count to fetch,
                  defaults to Query(None, gt=constants.EXTENSION_API_LIMIT_GT)
    :type limit: int, optional
    :param marker: Marker object to fetch, defaults to None
    :type marker: str, optional
    :param sort_dirs: Sort order, defaults to None
    :type sort_dirs: schemas.SortDir, optional
    :param sort_keys: Sort keys, defaults to Query(None)
    :type sort_keys: List[schemas.ExtServerSortKey], optional
    :param all_projects: All projects to fetch, defaults to None
    :type all_projects: bool, optional
    :param project_id: Filter by id of project which ports belongs to,
                       defaults to None
    :type project_id: str, optional
    :param name: Filter by port name, defaults to None
    :type name: str, optional
    :param status: Filter by port status, defaults to None
    :type status: schemas.PortStatus, optional
    :param network_name: Filter by name of network, defaults to None
    :type network_name: str, optional
    :param network_id: Filter by id of network, defaults to None
    :type network_id: str, optional
    :param device_id: Filter by id of device, defaults to None
    :type device_id: str, optional
    :param device_owner: Filter by device owner, defaults to Query(None)
    :type device_owner: List[schemas.PortDeviceOwner], optional
    :param uuid: Filter by list uuid,
                 defaults to Query(None, description="UUID of port.")
    :type uuid: List[str], optional
    :return: Port list
    :rtype: schemas.PortsResponse
    """
    current_session = await generate_session(profile=profile)

    kwargs = {}
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
        networks = await neutron.list_networks(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            **{"name": network_name},
        )
        if not networks["networks"]:
            return {"ports": []}
        network_ids = [network["id"] for network in networks["networks"]]
        kwargs["network_id"] = network_ids
    if network_id is not None:
        network_ids = kwargs.get("network_id", [])
        if network_ids and network_id not in network_ids:
            return {"ports": []}
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

    ports = await neutron.list_ports(
        current_session,
        profile.region,
        x_openstack_request_id,
        **kwargs,
    )

    server_ids = []
    network_ids = []
    result = []
    for port in ports.get("ports", []):
        origin_data = OSPort(port).to_dict()
        port = Port(port).to_dict()
        port["origin_data"] = origin_data
        result.append(port)
        if port["device_owner"] == "compute:nova":
            server_ids.append(port["device_id"])
        network_ids.append(port["network_id"])

    network_params = {}
    tasks = [
        neutron.list_networks(
            profile=profile,
            session=current_session,
            global_request_id=x_openstack_request_id,
            **{"shared": True},
        ),
    ]
    if not all_projects:
        network_params["project_id"] = profile.project.id
    network_ids = list(set(network_ids))
    # We should split the network_ids with 100 number.
    # If we do not do this, the length of url will be too long to do request.
    for i in range(0, len(network_ids), STEP):
        network_params["id"] = set(network_ids[i : i + STEP])
        tasks.append(
            neutron.list_networks(
                profile=profile,
                session=current_session,
                global_request_id=x_openstack_request_id,
                **network_params,
            ),
        )

    # We should split the server_ids with 100 number.
    # If we do not do this, the length of url will be too long to do request.
    server_ids = list(set(server_ids))
    for i in range(0, len(server_ids), STEP):
        tasks.append(
            nova.list_servers(
                profile=profile,
                session=current_session,
                global_request_id=x_openstack_request_id,
                search_opts={
                    "uuid": server_ids[i : i + STEP],
                    "all_tenants": all_projects,
                },
            ),
        )
    task_result = await gather(*tasks)

    total_network_tasks = math.ceil(len(network_ids) / STEP)
    servers = reduce(lambda x, y: x + y, task_result[1 + total_network_tasks :], [])
    ser_mappings = {server.id: server.name for server in servers}
    _networks = [net.get("networks", []) for net in task_result[1 : 1 + total_network_tasks]]
    shared_nets = task_result[0].get("networks", [])
    nets = reduce(lambda x, y: x + y, _networks, []) + shared_nets
    network_mappings = {net["id"]: net["name"] for net in nets}
    for port in result:
        port["server_name"] = ser_mappings.get(port["device_id"])
        port["network_name"] = network_mappings.get(port["network_id"])
    return {"ports": result}


@router.get(
    "/extension/compute-services",
    description="List compute services.",
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
async def compute_services(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
    x_openstack_request_id: str = Header(
        "",
        alias=constants.INBOUND_HEADER,
        regex=constants.INBOUND_HEADER_REGEX,
    ),
    binary: str = None,
    host: str = None,
) -> schemas.ComputeServicesResponse:
    """Extension List Compute Services.

    :param profile: Profile object include token, role and so on,
                    defaults to Depends(deps.get_profile_update_jwt)
    :type profile: schemas.Profile, optional
    :param binary: Filter by service binary name, defaults to None
    :type binary: str, optional
    :param host: Filter by host name, defaults to None
    :type host: str, optional
    :return: Compute service list
    :rtype: schemas.ComputeServicesResponse
    """
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
    services = await nova.list_services(
        profile=profile,
        session=system_session,
        global_request_id=x_openstack_request_id,
        **kwargs,
    )
    services = [Service(service).to_dict() for service in services]
    return {"services": services}

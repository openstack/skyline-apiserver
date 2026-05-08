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

import hashlib
import os
import re
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

import httpx

from skyline_apiserver.log import LOG

RACKSPACE_STATUS_FEED_URL = "https://rss.status.rackspace.com/snow/statusfeed"
RACKSPACE_STATUS_PRODUCT = "OpenStack Flex"
RACKSPACE_STATUS_TIMEOUT = 10.0

DATETIME_RE = re.compile(r"\b20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\b")
OUTAGE_RE = re.compile(r"\bOUT\d+\b")
CHANGE_RE = re.compile(r"\bCHG\d+\b")


class _TextExtractor(HTMLParser):
    block_tags = {
        "br",
        "div",
        "li",
        "p",
        "section",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
    }

    def __init__(self):
        super().__init__()
        self.parts: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self._skip_depth += 1
        if tag in self.block_tags:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
        if tag in self.block_tags:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip_depth:
            self.parts.append(data)

    def get_text(self) -> str:
        return unescape("".join(self.parts))


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


def _float_env(name: str, default: float) -> float:
    value = _env(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        LOG.warning(f"Ignoring invalid float value for {name}: {value}")
        return default


def _feed_url() -> str:
    return _env("RACKSPACE_STATUS_FEED_URL", RACKSPACE_STATUS_FEED_URL)


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return parser.get_text()


def _normalize_text(text: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _parse_datetime(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=timezone.utc
    )


def _parse_date_range(text: str) -> Optional[tuple[datetime, datetime]]:
    matches = DATETIME_RE.findall(text)
    if len(matches) < 2:
        return None
    return _parse_datetime(matches[0]), _parse_datetime(matches[-1])


def _split_title(title: str) -> List[str]:
    return [part.strip() for part in title.split("|") if part.strip()]


def _is_openstack_flex_item(title: str) -> bool:
    parts = _split_title(title)
    return bool(parts and parts[0].lower() == RACKSPACE_STATUS_PRODUCT.lower())


def _title_region(title: str) -> Optional[str]:
    parts = _split_title(title)
    if len(parts) < 2:
        return None
    return parts[1]


def _normalize_region(region: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", region.upper())


def regions_match(title_region: Optional[str], expected_region: Optional[str]) -> bool:
    if not expected_region:
        return True
    if not title_region:
        return False

    expected_region = _normalize_region(expected_region)
    title_regions = [
        _normalize_region(value)
        for value in re.split(r"[,/]", title_region)
        if value.strip()
    ]
    return expected_region in title_regions


def _extract_source_id(text: str, link: Optional[str]) -> str:
    outage_match = OUTAGE_RE.search(text)
    if outage_match:
        return outage_match.group(0)

    change_match = CHANGE_RE.search(text)
    if change_match:
        return change_match.group(0)

    raw_id = link or text
    digest = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()[:24]
    return f"rss-{digest}"


def _message_id(source_id: str) -> str:
    return f"rackspace-status-{source_id}"


def _message_type(text: str) -> str:
    if "maintenance" in text.lower():
        return "maintenance"
    return "notification"


def _message_text(title: str, description: str) -> str:
    match = re.search(r"\bRackspace will\b", description, re.IGNORECASE)
    message = description[match.start() :] if match else description
    message = DATETIME_RE.sub("", message).strip()
    return message or title


def _item_text(item: ElementTree.Element, tag: str) -> Optional[str]:
    value = item.findtext(tag)
    if value is None:
        return None
    return value.strip()


def _item_to_message_banner_values(
    item: ElementTree.Element,
) -> Optional[Dict[str, Any]]:
    title = _item_text(item, "title") or ""
    if not _is_openstack_flex_item(title):
        return None

    link = _item_text(item, "link")
    raw_description = _item_text(item, "description") or ""
    description = _normalize_text(_html_to_text(raw_description))
    date_range = _parse_date_range(description)
    if date_range is None:
        LOG.warning(f"Skipping Rackspace status feed item without date range: {title}")
        return None

    start_at, expires_at = date_range
    source_id = _extract_source_id(description, link)
    item_region = _title_region(title)
    return {
        "id": _message_id(source_id),
        "type": _message_type(f"{title}\n{description}"),
        "title": title,
        "message": _message_text(title, description),
        "impacted_service": RACKSPACE_STATUS_PRODUCT,
        "start_at": start_at,
        "expires_at": expires_at,
        "project_id": None,
        "region": item_region,
        "source": "rackspace_status",
        "source_id": source_id,
        "source_url": link,
        "enabled": True,
    }


def fetch_rackspace_status_message_banner_values() -> List[Dict[str, Any]]:
    """Fetch OpenStack Flex RSS feed items as DB-ready banner values."""

    try:
        with httpx.Client(
            timeout=_float_env("RACKSPACE_STATUS_TIMEOUT", RACKSPACE_STATUS_TIMEOUT),
        ) as client:
            response = client.get(_feed_url())
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
    except Exception as exc:
        LOG.warning(f"Failed to fetch Rackspace status feed: {exc}")
        return []

    banner_values = []
    seen_ids = set()
    for item in root.findall("./channel/item"):
        values = _item_to_message_banner_values(item)
        if values is None or values["id"] in seen_ids:
            continue

        seen_ids.add(values["id"])
        banner_values.append(values)

    return banner_values

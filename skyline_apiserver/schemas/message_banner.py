from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class MessageBannerBase(BaseModel):
    type: Literal["maintenance", "notification"] = Field(
        ..., description="Banner type"
    )
    title: Optional[str] = Field(None, description="Banner title")
    message: str = Field(..., description="Banner message/details")
    impacted_service: Optional[str] = Field(
        None, description="Impacted service for maintenance banners"
    )
    start_at: Optional[datetime] = Field(
        None, description="Start date/time in UTC"
    )
    expires_at: datetime = Field(
        ..., description="Expiration date/time in UTC"
    )
    region: Optional[str] = Field(
        None, description="Region. Null means all regions"
    )
    enabled: bool = Field(True, description="Whether banner is enabled")


class CreateMessageBanner(MessageBannerBase):
    """"""


class UpdateMessageBanner(MessageBannerBase):
    """"""


class MessageBanner(MessageBannerBase):
    id: str = Field(..., description="Banner ID")
    project_id: Optional[str] = Field(
        None, description="Project ID. Null means global/universal banner"
    )
    source: Literal["manual", "rackspace_status", "servicenow"] = Field(
        "manual", description="Banner source"
    )
    source_id: Optional[str] = Field(
        None, description="External source identifier"
    )
    source_url: Optional[str] = Field(
        None, description="External source URL"
    )
    created_at: datetime = Field(..., description="Created time")
    updated_at: datetime = Field(..., description="Updated time")


class MessageBanners(BaseModel):
    message_banners: List[MessageBanner] = Field(
        ..., description="Message banners"
    )

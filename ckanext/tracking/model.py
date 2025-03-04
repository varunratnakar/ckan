# encoding: utf-8
""" Tracking models

Tracking functinoality used to be implemented in core CKAN and it was
later moved to an extension during the development of CKAN 2.11.

Even when tracking models are defined here, the tables are still
being created in the database by core CKAN db migrations. This is not
ideal but it has been done this way to avoid breaking existing
installations.

If you are looking for the database migrations, you can find them in
the core CKAN folder:
ckan/migrations/versions/057_660a5aae527e_tracking.py
"""
from __future__ import annotations

import datetime

from sqlalchemy import types, Column, Table, text

from ckan.plugins.toolkit import BaseModel
from ckan.model import meta
from ckan.model import domain_object

__all__ = ['tracking_summary_table', 'TrackingSummary', 'tracking_raw_table']


tracking_raw_table = Table(
    'tracking_raw',
    meta.metadata,
    Column('user_key', types.Unicode(100), nullable=False),
    Column('url', types.UnicodeText, nullable=False),
    Column('tracking_type', types.Unicode(10), nullable=False),
    Column('access_timestamp', types.DateTime),
)


tracking_summary_table = Table(
    'tracking_summary',
    meta.metadata,
    Column('url', types.UnicodeText, primary_key=True, nullable=False),
    Column('package_id', types.UnicodeText),
    Column('tracking_type', types.Unicode(10), nullable=False),
    Column('count', types.Integer, nullable=False),
    Column('running_total', types.Integer, nullable=False),
    Column('recent_views', types.Integer, nullable=False),
    Column('tracking_date', types.DateTime),
)


class TrackingSummary(domain_object.DomainObject, BaseModel):  # type: ignore
    __tablename__ = 'tracking_summary'
    url: str
    package_id: str
    tracking_type: str
    # count attribute shadows DomainObject.count()
    count: int
    running_total: int
    recent_views: int
    tracking_date: datetime.datetime

    @classmethod
    def get_for_package(cls, package_id: str) -> dict[str, int]:
        obj = meta.Session.query(cls).autoflush(False)
        obj = obj.filter_by(package_id=package_id)
        data = obj.order_by(text('tracking_date desc')).first()
        if data:
            return {'total': data.running_total, 'recent': data.recent_views}

        return {'total': 0, 'recent': 0}

    @classmethod
    def get_for_resource(cls, url: str) -> dict[str, int]:
        obj = meta.Session.query(cls).autoflush(False)
        data = obj.filter_by(url=url).\
            order_by(text('tracking_date desc')).\
            first()
        if data:
            return {'total': data.running_total, 'recent': data.recent_views}

        return {'total': 0, 'recent': 0}

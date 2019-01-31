# -*- coding: utf-8 -*-
from plone.app.standardtiles import PloneMessageFactory as _
from plone.supermodel.model import Schema
from plone.tiles import Tile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import Interface
from plone.app.vocabularies.catalog import CatalogSource as CatalogSourceBase

from Acquisition import aq_parent
from plone.memoize.view import memoize
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from z3c.form import validator
from zExceptions import Unauthorized
from zope.component.hooks import getSite
from zope.interface import Invalid
from plone import api


def uuidToObject(uuid):
    """Given a UUID, attempt to return a content object. Will return
    None if the UUID can't be found. Raises Unauthorized if the current
    user is not allowed to access the object.
    """

    brain = uuidToCatalogBrainUnrestricted(uuid)
    if brain is None:
        return None

    return brain.getObject()


def uuidToCatalogBrainUnrestricted(uuid):
    """Given a UUID, attempt to return a catalog brain even when the object is
    not visible for the logged in user (e.g. during anonymous traversal)
    """

    site = getSite()
    if site is None:
        return None

    catalog = getToolByName(site, 'portal_catalog', None)
    if catalog is None:
        return None

    result = catalog.unrestrictedSearchResults(UID=uuid)
    if len(result) != 1:
        return None

    return result[0]


class CatalogSource(CatalogSourceBase):
    """ExistingContentTile specific catalog source to allow targeted widget
    """
    def __contains__(self, value):
        return True  # Always contains to allow lazy handling of removed objs


class INewsTile(Schema):
    """A tile that displays a listing of content items"""

    content_uid = schema.Choice(
        title=_(u"Select an existing content"),
        required=True,
        source=CatalogSource(),
    )

    limit = schema.Int(
        title=_(u'Limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=100,
        min=1,
    )

    limit_slider = schema.Int(
        title=_(u'Limit slider'),
        description=_(u'Number of element in slider'),
        required=False,
        default=100,
        min=1,
    )


class SameContentValidator(validator.SimpleFieldValidator):
    def validate(self, content_uid):
        super(SameContentValidator, self).validate(content_uid)
        context = aq_parent(self.context)  # default context is tile data
        if content_uid and IUUID(context, None) == content_uid:
            raise Invalid("You can not select the same content as "
                          "the page you are currently on.")


# Register validator
validator.WidgetValidatorDiscriminators(
    SameContentValidator,
    field=INewsTile['content_uid']
)


class INewsTileLayer(Interface):
    """Layer (request marker interface) for content listing tile views"""


class NewsTile(Tile):
    """A tile that displays a listing of content items"""

    template = ViewPageTemplateFile('templates/tile_news.pt')

    def __call__(self):
        return self.template()

    @property
    @memoize
    def content_context(self):
        uuid = self.data.get('content_uid')
        if uuid != IUUID(self.context, None):
            try:
                item = uuidToObject(uuid)
            except Unauthorized:
                item = None
                if not self.request.get('PUBLISHED'):
                    raise  # Should raise while still traversing
            if item is not None:
                return item
        return None

    def contents(self):
        uid = self.data["content_uid"]
        results = api.content.find(UID=uid)
        content = []
        limit = self.data["limit"]
        if results:
            content = results[0].getObject().getFolderContents({'portal_type': 'News Item'}, batch=True, b_size=limit or 4)
        return content

    def __getattr__(self, name):
        if name in ('data',
                    'content_context',
                    'default_view',
                    'item_macros',
                    'item_panels',
                    'getPhysicalPath',
                    'index_html',
                    ) or name.startswith(('_', 'im_', 'func_')):
            return Tile.__getattr__(self, name)
        return getattr(self.default_view, name)

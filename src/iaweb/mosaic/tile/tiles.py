# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.standardtiles import PloneMessageFactory as _
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.supermodel.model import Schema
from plone.tiles import Tile
from zope import schema


class INewsTile(Schema):
    """A tile that displays a listing of content items"""

    collection_uid = schema.Choice(
        title=_(u"Select an existing content"),
        required=True,
        vocabulary='plone.app.vocabularies.Catalog',
    )
    directives.widget(
        'collection_uid',
        RelatedItemsFieldWidget,
        pattern_options={'selectableTypes': ['Collection']},
    )

    limit = schema.Int(
        title=_(u'Limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=8,
        min=1,
    )

    limit_slider = schema.Int(
        title=_(u'Limit slider'),
        description=_(u'Number of element in slider'),
        required=False,
        default=4,
        min=1,
    )


class NewsTile(Tile):
    """A tile that displays a listing of content items"""

    template = ViewPageTemplateFile('templates/tile_news.pt')

    def __call__(self):
        return self.template()

    def contents(self):
        uid = self.data["collection_uid"]
        collection = api.content.get(UID=uid)
        limit = self.data["limit"]
        data = {
            'url': '',
            'results': [],
        }
        if collection:
            data["url"] = collection.absolute_url()
            data["results"] = collection.queryCatalog(batch=True, b_size=limit)
        return data

    @property
    def slider_limit(self):
        return self.data["limit_slider"]

    def slider_class(self):
        limit = self.data["limit_slider"]
        if limit == 1:
            return 'flexslider carousel one'
        else:
            return 'flexslider carousel multiple'

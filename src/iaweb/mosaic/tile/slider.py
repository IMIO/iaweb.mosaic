# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.supermodel.model import Schema
from plone.tiles import Tile
from plone import api
from zope import schema
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.app.standardtiles import PloneMessageFactory as _


class ISliderTile(Schema):
    """
    """
    collection_uid = schema.Choice(
        title=_(u"Select an existing content"),
        required=True,
        vocabulary="plone.app.vocabularies.Catalog",
    )
    directives.widget(
        "collection_uid",
        RelatedItemsFieldWidget,
        pattern_options={"selectableTypes": ["Collection"]},
    )

    infinite = schema.Bool(title=_(u"Infinite"), required=False, default=True)

    dots = schema.Bool(title=_(u"Dots"), required=False, default=True)

    slidesToShow = schema.Int(
        title=_(u"Show"),
        description=_(u"Slides to show"),
        required=False,
        default=4,
    )

    slidesToScroll = schema.Int(
        title=_(u"Scroll"),
        description=_(u"Slider to scroll"),
        required=False,
        default=4,
    )

    speed = schema.Int(
        title=_(u"Speed"),
        description=_(u"Speed"),
        required=False,
        default=300,
        min=100,
    )

    limit = schema.Int(
        title=_(u"Limit"),
        description=_(u"Limit of slides"),
        required=False,
        default=10,
    )


class SliderTile(Tile):
    """
    """

    template = ViewPageTemplateFile('templates/slider.pt')

    def __call__(self):
        return self.template()

    def contents(self):
        #import pdb; pdb.set_trace()
        uid = self.data["collection_uid"]
        attrs = (
            '{"infinite": "%s",'
            '"dots": "%s"}'
        ) % (str(self.data["infinite"]).lower(), str(self.data["dots"]).lower())
        #options = {
        #    'infinite': self.data["infinite"],
        #    'dots': 'false',
        #    'slidesToScroll': self.data["slidesToScroll"],
        #    'slidesToShow': self.data["slidesToShow"],
        #    'speed': self.data["speed"],
        #}
        data = {"url": "", "results": [], "options": attrs}
        limit = self.data["limit"]
        if uid and limit:
            collection = api.content.get(UID=uid)
            if collection:
                data["url"] = collection.absolute_url()
                if collection.portal_type == "Collection":
                    data["results"] = collection.queryCatalog(
                        batch=True, b_size=limit)
        return data

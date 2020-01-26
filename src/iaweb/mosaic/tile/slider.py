# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.supermodel.model import Schema
from plone.tiles import Tile


class ISliderTile(Schema):
    """
    """


class SliderTile(Tile):
    """
    """

    template = ViewPageTemplateFile('templates/slider.pt')

    def __call__(self):
        return self.template()
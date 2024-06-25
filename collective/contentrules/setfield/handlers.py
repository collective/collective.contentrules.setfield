# -*- coding:utf-8 -*-
from collective.contentrules.setfield.interfaces import IParentModifiedEvent
from plone.app.discussion.interfaces import IComment
from Products.CMFCore.interfaces import IContentish, IFolderish
from zope.interface.interfaces import ObjectEvent
from zope.event import notify
from zope.interface import implementer


def modified(event):
    """When an object is modified, fire the ParentModifiedEvent for its
    direct descendents.
    """
    obj = event.object
    if not (
        IContentish.providedBy(obj)
        or IComment.providedBy(obj)
        or IFolderish.providedBy(obj)
    ):
        return

    # IObjectModified event is called when a site is created, but before the
    # catalog has been initialised which throws an AttributeError exception.
    try:
        children = obj.getFolderContents()
    except AttributeError:
        return
    for child in children:
        notify(ParentModifiedEvent(child.getObject()))


@implementer(IParentModifiedEvent)
class ParentModifiedEvent(ObjectEvent):
    """An object has been created"""

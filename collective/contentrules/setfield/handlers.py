from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from plone.app.discussion.interfaces import IComment
from zope.component.interfaces import ObjectEvent
from zope.interface import implements
from collective.contentrules.setfield.interfaces import IParentModifiedEvent
from zope.event import notify


def modified(event):
    """ When an object is modified, fire the ParentModifiedEvent for its
        direct descendents.
    """
    obj = event.object
    if not (IContentish.providedBy(obj) or
            IComment.providedBy(obj) or
            IFolderish.providedBy(obj)):
        return

    # IObjectModified event is called when a site is created, but before the
    # catalog has been initialised which throws an AttributeError exception.
    try:
        children = obj.getFolderContents()
    except AttributeError:
        return
    for child in children:
        notify(ParentModifiedEvent(child.getObject()))


class ParentModifiedEvent(ObjectEvent):
    """An object has been created"""

    implements(IParentModifiedEvent)

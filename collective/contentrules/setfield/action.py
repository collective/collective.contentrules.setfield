# -*- coding:utf-8 -*-
from logging import getLogger


from OFS.SimpleItem import SimpleItem
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from collective.contentrules.setfield import SetFieldMessageFactory as _
from collective.contentrules.setfield.interfaces import ISetFieldAction

from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm

from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from zope.component import adapts
from zope.formlib import form
from zope.interface import Interface
from zope.interface import implements

logger = getLogger('collective.contentrules.setfield')


class SetFieldAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(ISetFieldAction, IRuleElementData)

    value_script = ""
    element = "collective.contentrules.setfield.ApplySetField"

    @property
    def summary(self):
        return _(u"Set field values",
                 mapping=dict(field=self.field))


class SetFieldActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, ISetFieldAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.request = getattr(self.context, 'REQUEST', None)
        self.event = event

    def __call__(self):
        obj = self.event.object
        field = getattr(self.element, 'field', False)
        bypasspermissions = getattr(self.element, 'bypasspermissions', False)
        # TODO: Handle execution of content rule
        return True

    def error(self, obj, error):

        title = utils.pretty_title_or_id(obj, obj)
        message = _(u"Unable to apply local roles on %s: %s" % (title, error))
        logger.error(message)
        if self.request is not None:
            IStatusMessage(self.request).addStatusMessage(message, type="error")


class SetFieldAddForm(AddForm):
    """An add form for local roles action.
    """
    form_fields = form.FormFields(ISetFieldAction)
    label = _(u"Add a Set Field Value Action")
    description = _(u"An action for setting the value of a field on an object.")
    schema = ISetFieldAction

    def create(self, data):
        a = SetFieldAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class SetFieldEditForm(EditForm):
    """An edit form for local roles action.
    """
    form_fields = form.FormFields(ISetFieldAction)
    label = _(u"Edit a Move to Field Action")
    description = _(u"An action for setting the value of a field on an object.")
    schema = ISetFieldAction

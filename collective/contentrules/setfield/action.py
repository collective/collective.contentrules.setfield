# -*- coding:utf-8 -*-
from logging import getLogger


from OFS.SimpleItem import SimpleItem
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from collective.contentrules.setfield import SetFieldMessageFactory as _
from collective.contentrules.setfield.interfaces import ISetFieldAction
from collective.contentrules.setfield.restricted import PyScript

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
        return _(u"Set field values")


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
        value_script = getattr(self.element, 'value_script', False)

        # Provide the current workflow state of the context
        state = ''
        wft = self.context.portal_workflow
        cur_wf = wft.getWorkflowsFor(obj)
        if len(cur_wf) > 0:
            cur_wf = cur_wf[0].id
            state = wft.getStatusOf(cur_wf, obj)['review_state']

        cp = PyScript(value_script)
        cp_globals = dict(context=obj,
                          state=state,
                          workflow=wft,
                          history={i: obj.workflow_history[i] for i in
                                   obj.workflow_history},
                          event=self.event,
                          values={})
        try:
            script = cp.execute(cp_globals)
        except Exception as e:
            self.error(obj, e)
            return False

        for v_key, value in script['values'].iteritems():
            logger.info('Setting %s to %s for %s' % (v_key, value, obj.id))
            setattr(obj, v_key, value)

        return True

    def error(self, obj, error):
        title = utils.pretty_title_or_id(obj, obj)
        message = _(u"Unable to set values on %s: %s, %s" % (title,
                                                             str(type(error)),
                                                             error))
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

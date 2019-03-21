# -*- coding:utf-8 -*-
from logging import getLogger


from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage
from collective.contentrules.setfield import SetFieldMessageFactory as _
from collective.contentrules.setfield.interfaces import ISetFieldAction
from collective.contentrules.setfield.restricted import PyScript

from plone.app.contentrules.browser.formhelper import AddForm
from plone.app.contentrules.browser.formhelper import EditForm
from plone import api
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.uuid.interfaces import IUUID
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.formlib import form
from zope.i18n import translate
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
        self.obj = self.event.object
        self.value_script = getattr(self.element, 'value_script', False)
        self.update_all = getattr(self.element, 'update_all_content', False)
        self.conditions = self.get_conditions()
        self.portal = api.portal.get()

        try:
            objects = self.get_objects()
        except Exception as e:
            self.error(self.obj, e)
            return False

        for item in objects:
            # Test the object against the conditions before updating
            passing = True
            if item != self.obj:
                self.event.object = item
                for condition in self.conditions:
                    executable = getMultiAdapter((item, condition, self.event),
                                                 IExecutable)
                    if not executable():
                        passing = False
                        break
                if passing is False:
                    logger.warning('Not executing setField action on %s' % item)
                    continue

            try:
                self.process_script(item)
            except Exception as e:
                self.error(self.obj, e)
                return False

        return True

    def error(self, obj, error):
        title = utils.pretty_title_or_id(obj, obj)
        message = _(u"Unable to set values on %s: %s, %s" % (title,
                                                             str(type(error)),
                                                             error))
        logger.error(message)
        if self.request is not None:
            IStatusMessage(self.request).addStatusMessage(message, type="error")

    def get_conditions(self):
        """ Returns the rules conditions for the executing action"""
        rules = queryUtility(IRuleStorage)
        rule = None
        for rule in rules.values():
            if self.element in rule.actions:
                break
        if not rule:
            raise Exception("Can't find rule for action %s"
                            % self.element.id)
        return rule.conditions

    def get_objects(self):
        query = {}
        if self.update_all is None or self.update_all == 'object':
            query['UID'] = IUUID(self.obj)

        if self.update_all and self.update_all == 'all':
            # Build query based on rule conditions. Each resulting item has
            # its rule checked, so the search can return extra items.
            portal_types = getToolByName(self.portal, 'portal_types')
            for condition in self.conditions:
                # content type
                if condition.element == 'plone.conditions.PortalType':
                    titles = []
                    for name in condition.check_types:
                        fti = getattr(portal_types, name, None)
                        if fti is not None:
                            title = translate(fti.Title(),
                                              context=self.portal.REQUEST)
                            titles.append(title)
                    query['Type'] = titles
                # TODO: file extension
                # TODO: user group
                # TODO: user role
                # TODO: workflow state
                # TODO: workflow transition

        logger.info('Searching with query: %s' % str(query))
        catalog = self.portal.portal_catalog
        object_search = catalog.search(query)
        return [brain.getObject() for brain in object_search]

    def process_script(self, item):
        state = ''
        wft = self.context.portal_workflow
        cur_wf = wft.getWorkflowsFor(item)
        if len(cur_wf) > 0:
            cur_wf = cur_wf[0].id
            state = wft.getStatusOf(cur_wf, item)['review_state']

        history = getattr(item, 'workflow_history', {})
        if len(history):
            history = {i: item.workflow_history[i] for i in
                       item.workflow_history}
        cp = PyScript(self.value_script)
        cp_globals = dict(context=item,
                          state=state,
                          workflow=wft,
                          history=history,
                          event=self.event,
                          values={})
        script = cp.execute(cp_globals)
        item_updated = False
        for v_key, value in script['values'].iteritems():
            if value is None and getattr(item, v_key, None) is None:
                continue
            logger.info('Setting %s to %s for %s' % (v_key, value, item.id))
            setattr(item, v_key, value)
            item_updated = True
        if item_updated:
            item.reindexObject()


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

# -*- coding:utf-8 -*-
from collective.contentrules.setfield import SetFieldMessageFactory as _
from collective.contentrules.setfield.interfaces import ISetFieldAction
from collective.contentrules.setfield.restricted import PyScript
from logging import getLogger
from OFS.SimpleItem import SimpleItem
from plone import api
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from plone.dexterity.utils import iterSchemata
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import pretty_title_or_id
from Products.statusmessages.interfaces import IStatusMessage
from six import iteritems
from z3c.form.interfaces import IDataManager
from zope.component import (
    adapts,
    getMultiAdapter,
    getUtility,
    queryMultiAdapter,
    queryUtility,
)
from zope.event import notify
from zope.formlib import form
from zope.i18n import translate
from zope.interface import implementer, Interface
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import ValidationError
from zope.schema.interfaces import IVocabularyFactory


logger = getLogger("collective.contentrules.setfield")


@implementer(ISetFieldAction, IRuleElementData)
class SetFieldAction(SimpleItem):
    """The actual persistent implementation of the action element."""

    value_script = None
    update_all = None
    preserve_modification_date = None
    element = "collective.contentrules.setfield.ApplySetField"

    @property
    def summary(self):
        return _(u"Set field values")


@implementer(IExecutable)
class SetFieldActionExecutor(object):
    """The executor for this action."""

    adapts(Interface, ISetFieldAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.request = getattr(self.context, "REQUEST", None)
        self.warnings = []
        self.event = event

    def __call__(self):
        self.obj = self.event.object
        self.value_script = getattr(self.element, "value_script", "")
        self.update_all = getattr(self.element, "update_all", "object")
        self.preserve_modification_date = getattr(
            self.element, "preserve_modification_date", False
        )
        self.vocabularies = getattr(self.element, "vocabularies", "")
        self.conditions = self.get_conditions()
        self.portal = api.portal.get()

        try:
            objects = self.get_objects()
        except Exception as e:  # noqa:B902
            self.error(self.obj, e)
            return False

        for item in objects:
            # Test the object against the conditions before updating
            passing = True
            if item != self.obj:
                self.event.object = item
                for condition in self.conditions:
                    executable = getMultiAdapter(
                        (item, condition, self.event), IExecutable
                    )
                    if not executable():
                        passing = False
                        break
                if passing is False:
                    logger.warning(
                        "Not executing setField action on %s" % item
                    )  # noqa: E501
                    continue

            old_date = None
            if self.preserve_modification_date is True:
                old_date = item.modification_date
            self.process_script(item)
            if self.preserve_modification_date is True:
                item.modification_date = old_date
                item.reindexObject(idxs="modified")

        # If there are < 5 warnings, display them as messages. Otherwise we
        # set a more generic message & point the user to the zope logs.
        if self.request is not None and len(self.warnings) > 0:
            if len(self.warnings) < 6:
                for warning in self.warnings:
                    IStatusMessage(self.request).addStatusMessage(
                        warning, type="warn"
                    )
            else:
                IStatusMessage(self.request).addStatusMessage(
                    _(
                        u"%i objects could not be updated. Please see the debug"  # noqa: E501
                        u"logs for more information." % len(self.warnings)
                    ),
                    type="warn",
                )

        return True

    def error(self, obj_being_processed, error):
        title = pretty_title_or_id(
            obj_being_processed,
            obj_being_processed,
        )
        message = _(
            u"Unable to set values on %s: %s, %s"
            % (title, str(type(error)), error),
        )
        logger.error(message)
        if self.request is not None:
            IStatusMessage(self.request).addStatusMessage(
                message, type="error"
            )  # noqa: E501

    def warn(self, url, warning):
        message = _(
            u"Unable to update %s - %s: %s"
            % (url, str(type(warning)), warning)  # noqa: E501
        )
        logger.warn(message)
        self.warnings.append(message)

    def get_conditions(self):
        """Returns the rules conditions for the executing action"""
        rules = queryUtility(IRuleStorage)
        rule = None
        for rule in rules.values():
            if self.element in rule.actions:
                break
        if not rule:
            raise Exception("Can't find rule for action %s" % self.element.id)
        return rule.conditions

    def get_objects(self):

        if self.update_all is None or self.update_all == "object":
            return [self.obj]

        query = {}
        if self.update_all and self.update_all == "all":
            # Build query based on rule conditions. Each resulting item has
            # its rule checked, so the search can return extra items.
            portal_types = getToolByName(self.portal, "portal_types")
            for condition in self.conditions:
                # content type
                if condition.element == "plone.conditions.PortalType":
                    titles = []
                    for name in condition.check_types:
                        fti = getattr(portal_types, name, None)
                        if fti is not None:
                            title = translate(
                                fti.Title(), context=self.portal.REQUEST
                            )
                            titles.append(title)
                    query["Type"] = titles
                # TODO: file extension
                # TODO: user group
                # TODO: user role
                # TODO: workflow state
                # TODO: workflow transition

        catalog = self.portal.portal_catalog
        object_search = catalog.search(query)
        objects = []
        # If the catalog is broken for some reason, we are likely to see
        # exceptions when calling getObject() on a brain. Instead of just
        # failing the whole operation, we warn the user and skip those items.
        for brain in object_search:
            try:
                objects.append(brain.getObject())
            except KeyError as keyerror:
                self.warn(brain.Title, keyerror)
        return objects

    def process_script(self, item):
        state = ""
        wft = self.context.portal_workflow
        cur_wf = wft.getWorkflowsFor(item)
        if len(cur_wf) > 0:
            cur_wf = cur_wf[0].id
            state = wft.getStatusOf(cur_wf, item)
            if state is not None:
                state = state["review_state"]

        history = getattr(item, "workflow_history", {})
        if len(history):
            history = {
                i: item.workflow_history[i] for i in item.workflow_history
            }
        vocabularies = {}
        if self.vocabularies:
            vocabs = self.vocabularies.split('\n')
            for vocabulary in vocabs:
                factory = getUtility(IVocabularyFactory, vocabulary)
                vocabularies[vocabulary] = {
                    key: val for val, key in factory(item).data.iteritems()
                }

        cp = PyScript(self.value_script)
        cp_globals = dict(
            context=item,
            state=state,
            workflow=wft,
            history=history,
            vocabularies=vocabularies,
            event=self.event,
            values={},
        )
        try:
            script = cp.execute(cp_globals)
        except Exception as e:  # noqa:B902
            self.error(item, e)
            return False

        fields = self._get_fields(item)
        item_updated = False
        for (v_key, value) in iteritems(script["values"]):
            # if value is None and getattr(item, v_key, None) is None:
            #     continue
            # if item.get(item, v_key, None) == value:
            #     continue

            # TODO: should validate against the content type otherwise
            #   this is a security problem
            if v_key not in fields:
                self.error(item, "Field '%s' not found so not set" % v_key)
                continue

            schema, field = fields[v_key]

            dm = queryMultiAdapter((item, field), IDataManager)
            # Handles case where old value is not set and new value is None
            if dm.get() == value:
                continue
            if dm is None or not dm.canWrite():
                self.error(item, "Not able to write %s" % v_key)
                continue
            # TODO: Could also check permission to write however should
            #   be checked against owner for content rule not current user.
            #   Owner is not kept

            bound = field.bind(self.context)
            try:
                bound.validate(value)
            except ValidationError as e:
                self.error(item, str(e))
                continue

            try:
                dm.set(value)
                item_updated = True
            except Exception as e:  # noqa:B902
                self.error(item, "Error setting %s: %s" % (v_key, str(e)))
        if item_updated:
            # TODO: shouldn't it reindex just the indexes for
            #   whats changed (and SearchableText)?
            # TODO: I think this is done in the handler below anyway
            item.reindexObject()
            notify(ObjectModifiedEvent(item))
        return True

    def _get_fields(self, context):
        fields = {}

        for schema in reversed(list(iterSchemata(context))):
            for fieldid, field in getFieldsInOrder(schema):
                fields[fieldid] = (schema, field)

        return fields


class SetFieldAddForm(AddForm):
    """An add form for local roles action."""

    form_fields = form.FormFields(ISetFieldAction)
    label = _(u"Add a Set Field Value Action")
    description = _(
        u"An action for setting the value of a field on an object."
    )  # noqa: E501
    schema = ISetFieldAction

    def create(self, data):
        a = SetFieldAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class SetFieldEditForm(EditForm):
    """An edit form for local roles action."""

    form_fields = form.FormFields(ISetFieldAction)
    label = _(u"Edit a Set Field Action")
    description = _(
        u"An action for setting the value of a field on an object."
    )  # noqa: E501
    schema = ISetFieldAction

import unittest

from collective.contentrules.setfield.testing import INTEGRATION_TESTING
from collective.contentrules.setfield.handlers import ParentModifiedEvent
from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class SetFieldAction(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(
            type="Folder", title="folder", container=self.portal
        )
        self.document = api.content.create(
            type="Document", title="document", container=self.folder
        )
        self.date_preserving_document = api.content.create(
            type="Document",
            title="date_preserving_document",
            container=self.portal,
        )
        self.portal.portal_setup.runAllImportStepsFromProfile(
            "profile-collective.contentrules.setfield:tests", purge_old=False
        )

    def test_trigger_script_on_object_modified(self):
        document = self.document

        title_before_action = document.title
        self.assertEqual(document.title, "document")

        notify(ObjectModifiedEvent(document))

        title_after_action = document.title
        self.assertEqual(document.title, "Title set by SetField")

        self.assertNotEqual(title_before_action, title_after_action)

    def test_trigger_script_on_object_parent_modified(self):
        parent = self.folder
        document = self.document

        title_before_parent_modified = document.title
        self.assertEqual(document.title, "document")

        notify(ParentModifiedEvent(document))

        title_after_parent_modified = document.title
        self.assertEqual(document.title, "Title set by SetField")

        self.assertNotEqual(
            title_before_parent_modified, title_after_parent_modified
        )

    def test_preserve_modification_date(self):
        document = self.date_preserving_document

        title_before_action = document.title
        self.assertEqual(document.title, "date_preserving_document")
        modification_date_before_action = (
            document.modification_date.asdatetime()
        )

        notify(ObjectModifiedEvent(document))

        title_after_action = document.title
        self.assertEqual(document.title, "Title set by SetField")
        modification_date_after_action = document.modification_date.asdatetime()

        self.assertNotEqual(title_before_action, title_after_action)
        self.assertNotEqual(
            modification_date_before_action, modification_date_after_action
        )

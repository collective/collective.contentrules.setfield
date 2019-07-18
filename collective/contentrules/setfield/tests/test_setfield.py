import unittest

from collective.contentrules.setfield.testing import INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class SetFieldAction(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

        self.portal.portal_setup.runAllImportStepsFromProfile(
            "profile-collective.contentrules.setfield:tests", purge_old=False
        )

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.folder = api.content.create(
            type="Folder", title="folder", container=self.portal
        )
        self.document = api.content.create(
            type="Document", title="document", container=self.folder
        )

    def test_trigger_script_on_object_modified(self):
        document = self.document

        title_before_action = document.title
        notify(ObjectModifiedEvent(document))

        title_after_action = document.title

        self.assertNotEqual(title_before_action, title_after_action)

from plone import api
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
)
from plone.testing import z2


class SetFieldLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Required by plone.app.contenttypes due to it's dependency plone.app.event
        z2.installProduct(app, "Products.DateRecurringIndex")
        import plone.app.contenttypes
        import collective.contentrules.setfield

        self.loadZCML(package=plone.app.contenttypes)
        self.loadZCML(package=collective.contentrules.setfield)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, "plone.app.contenttypes:default")

    def tearDownPloneSite(self, portal):
        self.applyProfile(portal, "plone.app.contenttypes:uninstall")


FIXTURE = SetFieldLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="collective.contentrules.setfield:IntegrationTests"
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="collective.contentrules.setfield:FunctionalTests"
)

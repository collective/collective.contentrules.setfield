from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting


class SetFieldLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.contentrules.setfield

        self.loadZCML(package=collective.contentrules.setfield)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, "plone.app.contenttypes:default")
        pass


FIXTURE = SetFieldLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="collective.contentrules.setfield:IntegrationTests"
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="collective.contentrules.setfield:FunctionalTests"
)

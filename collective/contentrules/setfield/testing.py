from plone import api
from plone.app.testing import (FunctionalTesting, IntegrationTesting,
                               PLONE_FIXTURE, PloneSandboxLayer)


class SetFieldLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import collective.contentrules.setfield

        self.loadZCML(package=collective.contentrules.setfield)

    def setUpPloneSite(self, portal):
        if api.env.plone_version().startswith("5"):
            self.applyProfile(portal, "plone.app.contenttypes:default")


FIXTURE = SetFieldLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,), name="collective.contentrules.setfield:IntegrationTests"
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,), name="collective.contentrules.setfield:FunctionalTests"
)

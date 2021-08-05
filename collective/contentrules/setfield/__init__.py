from zope.i18nmessageid import MessageFactory


SetFieldMessageFactory = MessageFactory("collective.contentrules.setfield")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

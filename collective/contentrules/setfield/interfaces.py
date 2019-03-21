from collective.contentrules.setfield import SetFieldMessageFactory as _
from zope import schema
from zope.interface import Interface


class ISetFieldAction(Interface):

    value_script = schema.Text(

        title=_(u"Value Script"),
        description=_(u"Enter PythonScript to calculate the values you want to "
                      u"set. Return a dictionary of {'field': value}. Available"
                      u"variables are: context, state, history, event"),
        default=_(u"""# values = {'field': some_value}"""),
        required=True)

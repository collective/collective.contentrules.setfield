from collective.contentrules.setfield import SetFieldMessageFactory as _
from plone.supermodel import model
from zope import schema
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

items = [('', u'Select'),
         ('object', u'Just the object'),
         ('all', u'All matching objects')]
terms = [SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
         for pair in items]


class ISetFieldAction(model.Schema):

    value_script = schema.Text(

        title=_(u"Value Script"),
        description=_(u"Enter PythonScript to calculate the values you want to "
                      u"set. Return a dictionary of {'field': value}. Available"
                      u"variables are: context, state, history, event"),
        default=_(u"""# values = {'field': some_value}"""),
        required=True)

    update_all = schema.Choice(
        title=_("Update all content?"),
        description=_(u""),
        vocabulary=SimpleVocabulary(terms)
    )

    model.fieldset(
        'script',
        label=_(u"Script"),
        fields=['value_script']
    )

    model.fieldset(
        'advanced',
        label=_(u"Advanced"),
        fields=['update_all']

    )
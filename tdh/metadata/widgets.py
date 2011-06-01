import zope.component
from z3c.form import interfaces
from z3c.form.widget import FieldWidget

from plone.formwidget.autocomplete.widget import \
        AutocompleteMultiSelectionWidget
from collective.z3cform.datagridfield import DataGridField

class AnzrscCodeDataGridField(DataGridField):
    code_type = ''
    code_levels = 3

class ForCodeDataGridField(AnzrscCodeDataGridField):
    code_type = 'for'

class SeoCodeDataGridField(AnzrscCodeDataGridField):
    code_type = 'seo'

@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def ForCodeDataGridFieldFactory(field, request):
    """IFieldWidget factory for DataGridField."""
    return FieldWidget(field, ForCodeDataGridField(request))

@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def SeoCodeDataGridFieldFactory(field, request):
    """IFieldWidget factory for DataGridField."""
    return FieldWidget(field, SeoCodeDataGridField(request))


class UnrestrictedAutocompleteSelectionWidget(AutocompleteMultiSelectionWidget):
    mustMatch = False

@zope.interface.implementer(interfaces.IFieldWidget)
def UnrestrictedAutocompleteMultiFieldWidget(field, request):
    """IFieldWidget factory for custom AutocompleteMultiFieldWidget."""
    return FieldWidget(field, \
                       UnrestrictedAutocompleteSelectionWidget(request))


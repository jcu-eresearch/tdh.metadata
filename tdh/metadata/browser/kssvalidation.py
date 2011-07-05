"""
    Browser view used to disable KSS validation on certain contexts.
"""

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import kssaction

class NullFormValidationView(PloneKSSView):

    @kssaction
    def validate_input(self, *args):
        """Make everything pass validation of input but doing nothing.
        """
        return


from five import grok

from tdh.metadata import rifcs_utils
from tdh.metadata.interfaces import IRifcsRenderable

class RifcsView(grok.View):
    grok.context(IRifcsRenderable)
    grok.require('zope2.View')
    grok.name('rifcs')

    def render(self):
        self.request.response.setHeader('Content-Type', 'application/xml')

        if 'download' in self.request.form:
            filename = '%s.xml' % self.context.id
            self.request.response.setHeader(
                'Content-Disposition',
                'attachment; filename="%s"' % filename)

        validate = 'val' in self.request.form
        return rifcs_utils.renderRifcs(self.getRenderables(), validate=validate)

    def getRenderables(self):
        """Return a list of contexts that can render RIF-CS (IRifcsRenderable).

        This method can be overridden for classes like the Repository, where
        multiple collections need to be outputted.
        """
        return [self.context,]


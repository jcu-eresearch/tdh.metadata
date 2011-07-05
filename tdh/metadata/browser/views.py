"""
    Viewlets related to application logic.
"""
import csv, os

# Zope imports
from zope.interface import Interface
from five import grok

from tdh.metadata.dataset_record import IDatasetRecord
from tdh.metadata.data_record_repository import IDataRecordRepository

# Use templates directory to search for templates.
grok.templatedir('templates')

#Helper functions
def loadAnzrcsCodes(anzrcs_code, filename):
    current_file = globals()['__file__']
    current_dir = os.path.split(current_file)
    csv_file = os.path.join(current_dir[0], filename)
    reader = csv.reader(open(csv_file, 'rb'), delimiter=',')

    sorted_codes = {}
    for row in reader:
        code, title = row
        #This is very, very hard-coded to be 3 levels at present.  Sigh.
        top_level = code[:2]
        interm_level = code[:4]
        if code.endswith('0000'):
            sorted_codes[top_level] = {'title': title,
                                       'codes': {}
                                      }
        elif code.endswith('00'):
            sorted_codes[top_level]['codes'][interm_level] = {'title': title,
                                                              'codes': {}
                                                             }
        else:
            #There's an issue here if we don't have a middle level.
            #Copy the parent if this is case.
            parent_level = sorted_codes[top_level]
            if interm_level not in parent_level['codes']:
                sorted_codes[top_level]['codes'][interm_level] = \
                        {'title': parent_level['title'].title(),
                         'codes': {}
                        }

            sorted_codes[top_level]['codes'][interm_level]['codes'][code] = {'title': title}

    return {'codes': sorted_codes}

def buildCodeSegments(seq, length):
    return [seq[:i+length] for i in range(0, len(seq), length)]


class AnzrcsCodesView(grok.View):
    """Render the option DOM elements for use by our dataset form
    """

    file_mapping = {'for': 'for_codes.csv',
                    'seo': 'seo_codes.csv',
                   }

    code_part_len = 2
    codes = []
    sorted_keys = []

    # The view is available on every content item type
    grok.template('anzrcs-codes')
    grok.name('anzrcs-codes')
    grok.context(Interface)

    def update(self):
        anzrcs_code = self.request.code
        code_segments = buildCodeSegments(anzrcs_code, self.code_part_len)

        filename = self.file_mapping.get(self.request.type)
        if filename:
            traversed_codes = loadAnzrcsCodes(anzrcs_code, filename)

            for code_part in code_segments:
                traversed_codes = traversed_codes['codes'][code_part]

            self.codes = traversed_codes['codes']
            self.sorted_keys = sorted(self.codes.keys())



class IntegrationJavascriptHelper(grok.View):
    """Used by portal_css and portal_javascripts to determine when to include our
       custom css and Javascript integration code.

    This view is referred from the expression in jsregistry.xml and cssregistry.xml.
    """

    # The view is available on every content item type
    grok.context(Interface)
    grok.name("dataset_form_resources")

    def render(self):
        """ Check if we are looking at a form for datasets or a data record repository page
        """
        path = self.request.get("PATH_INFO", "")
        return path.endswith("/++add++tdh.metadata.datasetrecord") or \
                IDatasetRecord.providedBy(self.context) or \
                IDataRecordRepository.providedBy(self.context)


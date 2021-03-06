"""
A newforms widget and field to allow multiple file uploads.

Created by Edward Dale (www.scompt.com)
Released into the Public Domain
"""

from django.utils.datastructures import MultiValueDict
from django.utils.translation import ugettext
from django.forms.fields import Field, EMPTY_VALUES
from django.core.files.uploadedfile import UploadedFile
from django.forms.widgets import FileInput
from django.forms.utils import ValidationError
from django.forms.utils import flatatt


class MultiFileInput(FileInput):
    """
    A widget to be used by the MultiFileField to allow the user to upload
    multiple files at one time.
    """

    def __init__(self, attrs=None):
        """
        Create a MultiFileInput.
        The 'count' attribute can be specified to default the number of
        file boxes initially presented.
        """
        super(MultiFileInput, self).__init__(attrs)
        self.attrs = {'count': 1}
        if attrs:
            self.attrs.update(attrs)

    def render(self, name, value, attrs=None):
        """
        Renders the MultiFileInput.
        Should not be overridden.  Instead, subclasses should override the
        js, link, and/or fields methods which provide content to this method.
        """
        # final_attrs = self.build_attrs(attrs, type=self.input_type,
        #                                name=name+'[]')
        # count = final_attrs['count']
        # if count < 1:
        #     count = 1
        # del final_attrs['count']

        final_attrs = self.build_attrs(attrs, {'type': self.input_type, 'name': name+'[]'})
        count = 1

        js = self.js(name, value, count, final_attrs)
        link = self.link(name, value, count, final_attrs)
        fields = self.fields(name, value, count, final_attrs)

        return js+fields+link

    def fields(self, name, value, count, attrs=None):
        """
        Renders the necessary number of file input boxes.
        """
        return ''.join(['<input%s />\n' %
                       flatatt(dict(attrs, id=attrs['id']+str(i)))
                       for i in range(count)])

    def link(self, name, value, count, attrs=None):
        """
        Renders a link to add more file input boxes.
        """
        return ("<a onclick=\"javascript:new_%(name)s()\">+</a>" %
                {'name': name})

    def js(self, name, value, count, attrs=None):
        """
        Renders a bit of Javascript to add more file input boxes.
        """
        return """
        <script type="text/javascript">
        <!--
        %(id)s_counter=%(count)d;
        function new_%(name)s() {
            b=document.getElementById('%(id)s0');
            c=b.cloneNode(false);
            c.id='%(id)s'+(%(id)s_counter++);
            b.parentNode.insertBefore(c,b.parentNode.lastChild.nextSibling);
        }
        -->
        </script>
        """ % {'id': attrs['id'], 'name': name, 'count': count}

    def value_from_datadict(self, data, files, name):
        """
        File widgets take data from FILES, not POST.
        """
        name = name+'[]'
        if isinstance(files, MultiValueDict):
            return files.getlist(name)
        else:
            return None

    def id_for_label(self, id_):
        """
        The first file input box always has a 0 appended to it's id.
        """
        if id_:
            id_ += '0'
        return id_
    id_for_label = classmethod(id_for_label)


class MultiFileField(Field):
    """
    A field allowing users to upload multiple files at once.
    """
    widget = MultiFileInput
    count = 1

    def __init__(self, count=1, strict=False, *args, **kwargs):
        """
        strict is whether the number of files uploaded must equal count
        """
        self.count = count
        self.strict = strict
        super(MultiFileField, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        """
        Adds the count to the MultiFileInput widget.
        """
        if isinstance(widget, MultiFileInput):
            return {'count': self.count}
        return {}

    def clean(self, data):
        """
        Cleans the data and makes sure that all the files had some content.
        Also checks whether a file was required.
        """
        super(MultiFileField, self).clean(data)

        if not self.required and data in EMPTY_VALUES:
            return None
        try:
            f = [UploadedFile(a['filename'], a['content']) for a in data]
        except TypeError:
            raise ValidationError(
                ugettext("No file was submitted. Check the "
                         "encoding type on the form."))
        except KeyError:
            raise ValidationError(ugettext("No file was submitted."))

        for a_file in f:
            if not a_file.content:
                raise ValidationError(ugettext("The submitted file is empty."))

        if self.strict and len(f) != self.count:
            raise ValidationError(ugettext("An incorrect number of files "
                                           "were uploaded."))

        return f


class FixedMultiFileInput(MultiFileInput):
    """
    A MultiFileInput widget that doesn't print the javascript code to allow
    the user to add more file input boxes.
    """

    def link(self, name, value, count, attrs=None):
        return ''

    def js(self, name, value, count, attrs=None):
        return ''

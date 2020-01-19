from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _ 
from django.conf import settings

from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

import os

from SnowVisionApp import models


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.') 
    
# forms.ClearableFileInput(attrs = {'class':'custom-file-input'}),

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)
        
        widgets = {
            # 'username': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'UserName'}),
            'first_name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}),
            'last_name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}),
            'email': forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email    '}),                }




class ExtFileField(forms.ClearableFileInput):
    """
    Same as forms.FileField, but you can specify a file extension whitelist.

    >>> from django.core.files.uploadedfile import SimpleUploadedFile
    >>>
    >>> t = ExtFileField(ext_whitelist=(".pdf", ".txt"))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.pdf', 'Some File Content'))
    >>> t.clean(SimpleUploadedFile('filename.txt', 'Some File Content'))
    >>>
    >>> t.clean(SimpleUploadedFile('filename.exe', 'Some File Content'))
    Traceback (most recent call last):
    ...
    ValidationError: [u'Not allowed filetype!']
    """
    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]

        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ExtFileField, self).clean(*args, **kwargs)
        filename = data.name
        ext = os.path.splitext(filename)[1]
        ext = ext.lower()
        if ext not in self.ext_whitelist:
            raise forms.ValidationError("Not allowed filetype!")

#-------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest, datetime
    doctest.testmod()


class SherdCreateForm(forms.ModelForm):
    class Meta:
        model = models.Sherd
        exclude= ["profile"]
        #     context = models.ForeignKey(Context)
        #
        # overstamped = models.BooleanField(blank=True)
        #     dimensional_data = models.FileField(blank=True)
        #     sherd_design = models.ManyToManyField('Design')
        #     sherd_image = models.ImageField(
        widgets = {
            'context': forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': True}),
            'overstamped': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'design': forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'image': forms.ClearableFileInput(attrs={'class': 'custom-file-input'}),
            'dimensional_data':forms.ClearableFileInput(attrs = {'class':'custom-file-input'}),
            'private': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'collection':forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            # forms.ChoiceField(widget= forms.Select(attrs={'class': 'form-control'})),
        }

        help_texts = {
            'design': ("Select one or many"),
            'image': ("Must be Image"),
            'dimensional_data': ("stl files only, less than 100 megabytes"),
            'private':("Check to hide your sherd data from other users and queries"),
        }

    def clean_dimensional_data(self):
        dimensional_data = self.cleaned_data['dimensional_data']

        if (dimensional_data):
            if "application/vnd.ms-pki.stl" == dimensional_data.content_type or "chemical/x-xyz" == dimensional_data.content_type:
                if dimensional_data._size > settings.MAX_FILE_SIZE:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_FILE_SIZE), filesizeformat(dimensional_data._size)))
            else:
                forms.ValidationError(_('Please submit .xyz or .stl. %s is not valid') % dimensional_data.content_type)

            filename = dimensional_data.name
            if not filename.endswith('.stl') and not filename.endswith('.xyz'):
                raise forms.ValidationError("File type in not valid. Please upload only .stl or .xyz files")

        return dimensional_data

    def clean_rgb_image(self):
        rgb_image = self.cleaned_data['rgb_image']

        if not rgb_image:
            raise forms.ValidationError(_('Please upload a an image of your sherd'))

        content_type = rgb_image.content_type.split('/')[0]
        if content_type == 'image':
            if rgb_image._size > settings.MAX_IMAGE_SIZE:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_IMAGE_SIZE), filesizeformat(sherd_image._size)))
        else:
            raise forms.ValidationError(_('Please submit an image'))


        return rgb_image

class SherdUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Sherd
        exclude= ["profile","context","uploaded_at","updated_at"]
        widgets = {
            'overstamped': forms.CheckboxInput( attrs={'class': 'form-check-input'}),
            'design': forms.Select( attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'sherd_image': forms.ClearableFileInput(attrs={'class': 'custom-file-input'}),
            'dimensional_data':forms.ClearableFileInput(attrs = {'class':'custom-file-input'}),
            'private': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            # forms.ChoiceField(widget= forms.Select(attrs={'class': 'form-control'})),
        }

        help_texts = {
            'sherd_design': ("Select one or many"),
            'sherd_image': ("Must be Image"),
            'dimensional_data': ("stl files only, less than 100 megabytes"),
            'private':("Check to hide your sherd data from other users and queries"),
        }

    def clean_dimensional_data(self):
        dimensional_data = self.cleaned_data['dimensional_data']

        if (dimensional_data):
            if "application/vnd.ms-pki.stl" == dimensional_data.content_type or "chemical/x-xyz" == dimensional_data.content_type:
                if dimensional_data._size > settings.MAX_FILE_SIZE:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_FILE_SIZE), filesizeformat(dimensional_data._size)))
            else:
                forms.ValidationError(_('Please submit .xyz or .stl. %s is not valid') % dimensional_data.content_type)

            filename = dimensional_data.name
            if not filename.endswith('.stl') and not filename.endswith('.xyz'):
                raise forms.ValidationError("File type in not valid. Please upload only .stl or .xyz files")

        return dimensional_data


    def clean_rgb_image(self):
        rgb_image = self.cleaned_data['rgb_image']

        if not rgb_image:
            raise forms.ValidationError(_('Please upload a an image of your sherd'))

        content_type = rgb_image.content_type.split('/')[0]
        if content_type == 'image':
            if rgb_image._size > settings.MAX_IMAGE_SIZE:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(settings.MAX_IMAGE_SIZE), filesizeformat(sherd_image._size)))
        else:
            raise forms.ValidationError(_('Please submit an image'))


        return rgb_image


class ContextCreateForm(forms.ModelForm):
    class Meta():
        model = models.Context
        exclude = ["profile",]
        widgets = {
            'site': forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'project': forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': True}),
            'recovery_method': forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'screen_type' : forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'curator' : forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'year_excavated': forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
        }

class ContextUpdateForm(forms.ModelForm):
    class Meta():
        model = models.Context
        exclude = ["profile","site","project",]
        widgets = {
            'recovery_method': forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'screen_type' : forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'curator' : forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
            'year_excavated': forms.Select(attrs={'class': 'js-example-basic-multiple js-states form-control', 'disabled': False}),
        }

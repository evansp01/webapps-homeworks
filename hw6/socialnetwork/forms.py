from django import forms
from django.contrib.auth.models import User
from socialnetwork.models import *

MAX_IMAGE_SIZE = 4194304

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['text']


class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
      super(ProfileForm, self).__init__(*args, **kwargs)
      self.fields['age'].required = False;
      self.fields['bio'].required = False;
      self.fields['image'].required = False;

    imageupdate = forms.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = ['first', 'last', 'age', 'bio', 'image']

    def clean_image(self):
        image = self.cleaned_data.get('image', False)
        if image and image._size > MAX_IMAGE_SIZE:
            raise ValidationError("Image file too large (must be less than 4mb)")
        return image



class RegisterForm(forms.ModelForm):
    username = forms.RegexField(
        label="Username",
        max_length=30,
        regex=r'^[a-zA-Z0-9_\-\.]+$',
        error_messages={'invalid':
                        "This value may contain only letters, numbers periods dashes and underscores."}
    )
    first_name = forms.RegexField(
        label="First Name",
        max_length=30,
        regex=r'^[a-zA-Z0-9_\-\.]+$',
        error_messages={'invalid':
                        "This value may contain only letters, numbers periods dashes and underscores."}
    )
    last_name = forms.RegexField(
        label="Last Name",
        max_length=30,
        regex=r'^[a-zA-Z0-9_\-\.]+$',
        error_messages={'invalid':
                        "This value may contain only letters, numbers periods dashes and underscores."}
    )
    password = forms.CharField(min_length=5, max_length=35,
                               label="Password",
                               widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=5, max_length=35,
                                label="Confirm Password",
                                widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password']

    def clean_password2(self):
        confirm_password = self.cleaned_data.get('password2')
        original_password = self.cleaned_data.get('password')
        if not confirm_password:
            raise forms.ValidationError("You must confirm your password")
        if original_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return self.cleaned_data

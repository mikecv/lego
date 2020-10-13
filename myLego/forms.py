from django import forms

# **************************************************************
# Class for form to search for a Lego set.
# **************************************************************
class AddSetForm(forms.Form):
    set_code = forms.CharField(label='Set code ', max_length=16)
    my_set = forms.BooleanField(label='Add to my parts', initial=False, required=False)

# **************************************************************
# Class for Lego part details for editing.
# **************************************************************
class EditPartForm(forms.Form):
    part_code = forms.CharField(label='Part code ', max_length=16, widget=forms.TextInput(attrs={'size':16, 'readonly':'True'}))
    part_description = forms.CharField(label='Part description ', max_length=64, widget=forms.TextInput(attrs={'size':64}))
    part_picture = forms.ImageField(label='Part picture')

from django import forms
# from .models import EditRequest,Komentar


class LinkBeritaForm(forms.Form):
    link = forms.CharField(
        label='Masukkan Link Berita',
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'border-radius: 20px;'})
    )

class BeritaSearchForm(forms.Form):
    search = forms.CharField(max_length=255, required=False)

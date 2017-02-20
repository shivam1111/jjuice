from django import forms
from models import CartItem

class ProductAddToCartForm(forms.Form):
    
    def __init__(self,request=None,*args,**kwargs):
        self.request = request
        super(ProductAddToCartForm,self).__init__(*args,**kwargs)
        
    quantity = forms.IntegerField(widget=forms.TextInput(attrs={'size':'2',  
'value':'1', 'class':'quantity', 'maxlength':'5'}),  error_messages={'invalid':'Please enter a valid quantity.'}, min_value=1)
    
#     user_id = forms.ModelChoiceField(queryset=CartItem.objects.all(), empty_label="(Nothing)")
        
    def clean(self):
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError("Cookies must be enabled")
        return self.cleaned_data    
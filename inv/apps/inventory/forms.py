from django import forms

from models import Item, SKU

class ItemForm( forms.ModelForm ):
    # in_stock = forms.BooleanField( label = 'In Stock' )
    
    class Meta:
        model = Item
        exclude = ( 'in_item', )
        widgets = {
            'notes': forms.Textarea( attrs={'cols': 60, 'rows': 5} ),
            }
 
class SystemForm( forms.Form ):
    system_type = forms.ModelChoiceField( SKU.objects.filter( category__name = 'System', active=True ),
                                          label = 'System Type',
                                          )
    tag = forms.CharField()
    # motherboard = forms.ChoiceField( label = 'Motherboard' )
    # case = forms.ChoiceField( label = 'Case' )


    def __init__( self, motherboards, cases, *args, **kwargs ):
        super( SystemForm, self).__init__( *args, **kwargs )
        # Create dynamically 
        self.fields[ 'motherboard' ] = \
                     forms.ModelChoiceField( motherboards )
        
        self.fields[ 'case' ] = \
                     forms.ModelChoiceField( cases )
                                                         


class SystemHardDriveForm( forms.Form ):
    quantity = forms.IntegerField( label = 'Qty',
                                   widget = forms.TextInput( attrs={'class': 'input-mini'}))
    
    def __init__( self, *args, **kwargs ):
        super( SystemHardDriveForm, self).__init__( *args, **kwargs )
        # Hack in, as can't figure out formsets with dynamic forms
        self.fields[ 'hard_drive' ] = \
                     forms.ModelChoiceField( Item.objects.filter( sku__category__name = 'Hard Drive', in_stock = True ) )
                                                        
        

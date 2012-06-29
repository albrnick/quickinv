from django.db import models

"""
type => System
Details => 2 Gig Enterprise
Tag => 12334

type => Hard Drive
Details => WD 
Tag => Dec 2012 Buyg
"""

# Create your models here.
class ItemCategory( models.Model ):
    name = models.CharField( max_length=100 )

    def __unicode__( self ):
        return( self.name )

    class Meta:
        ordering = [ 'name' ]


class SKU( models.Model ):
    category = models.ForeignKey( ItemCategory,
                                  db_index = True )
    
    code = models.CharField( max_length=100,
                             unique=True,
                             db_index = True,
                             help_text = 'Item Code/Identifier for the SKU.')
    description = models.CharField( max_length=200,
                                    help_text = 'Longer description of the SKU' )
    active = models.BooleanField( help_text = 'Can this item be ordered currently',
                                  default = True )
    
    def __unicode__( self ):
        return( self.code )


class Item( models.Model ):
    sku = models.ForeignKey( SKU,
                             db_index = True,
                             limit_choices_to = { 'active': True },
                             )
    tag = models.CharField( max_length = 1000,
                            help_text = 'System tag, or when ordered batch for Hard Drives, etc..' )
    quantity = models.IntegerField()
    status = models.CharField( max_length = 100,
                               #! MAKE INTO OBJECT!!
                               choices = (('On Order', 'On Order'),
                                          ('RMA', 'RMA'),
                                          ('Waiting to be built', 'Waiting to be built'),
                                          ('In Testing', 'In Testing'),
                                          ('Reserved', 'Reserved'),
                                          ('Ready to ship', 'Ready to ship'),
                                          ('In inventory', 'In inventory'),
                                          ('Shipped', 'Shipped'),
                                          ('In System', 'In System'),
                                          ),
                               db_index = True )
    in_item = models.ForeignKey( 'Item',
                                 db_index = True,
                                 blank = True,
                                 null = True,
                                 related_name = 'components')
    in_stock = models.BooleanField()
    refurb = models.BooleanField()
    notes = models.TextField( blank = True,
                              null = True )
    
    def __unicode__( self ):
        if self.sku.category.name == 'System':
            return( '%s (%s)' % ( self.sku.code, self.tag ))
        else:
            return( '%d x %s (%s)' % ( self.quantity, self.sku, self.tag ))

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.forms.formsets import formset_factory

from models import Item
from forms import ItemForm, SystemForm, SystemHardDriveForm


def home( request ):

    return( render( request, 'inventory/home.html'))


def inventory_view( request ):

    items = Item.objects.filter( in_stock = True ).order_by( 'sku__code' )
    
    return( render( request, 'inventory/view.html',
                    { 'items': items,
                      }))


def system_inventory_view( request ):

    items = Item.objects.filter( sku__category__name='System',
                                 in_stock = True ).order_by( 'sku__code' )
    
    return( render( request, 'inventory/view_systems.html',
                    { 'items': items,
                      }))

def system_inventory_overview( request ):

    systems = {}
    systems['rma'] = Item.objects.filter( sku__category__name='System',
                                          in_stock = True,
                                          status = 'RMA' ).order_by( 'sku__code' )

    systems['ready_to_ship'] = Item.objects.filter( sku__category__name='System',
                                                    in_stock = True,
                                                    status = 'Ready to Ship' ).order_by( 'sku__code' )

    systems['in_testing'] = Item.objects.filter( sku__category__name='System',
                                                 in_stock = True,
                                                 status = 'In Testing' ).order_by( 'sku__code' )

    systems['shipping'] = Item.objects.filter( sku__category__name='System',
                                               in_stock = True,
                                               status = 'Shipped' ).order_by( 'sku__code' )


    
    return( render( request, 'inventory/systems_overview.html',
                    { 'systems': systems,
                      }))

def item_view( request, id ):

    item = get_object_or_404( Item, pk=id )

    return( render( request, 'inventory/item_view.html',
                    { 'item': item,
                      }))
    

def item_add_edit( request, id=None ):

    item = get_object_or_404( Item, pk=id ) if id else None

    if request.method == 'POST':
        form = ItemForm( request.POST, instance=item )
        if form.is_valid():
            item = form.save()

            # Let them know it was saved properly!
            messages.success( request, 'Successfully saved item %d x %s.' % ( item.quantity, item.sku ))

            # If they ask to add again, give them to this page
            if request.POST.get( 'add_and_add', None ):
                return( HttpResponseRedirect( reverse( 'item_add' )))

            # Else return them to home page
            return( HttpResponseRedirect( reverse( 'home' )))
        else:
            # Let them know there is an error
            messages.error( request, 'There was an error.' )
    else:
        form = ItemForm( instance=item )

    return( render( request, 'inventory/item_add_edit.html',
                    { 'item_form': form,
                      'item': item,
                      }))


def system_build( request ):

    system_form = SystemForm( Item.objects.filter( sku__category__name = 'Motherboard', in_stock = True ),
                              Item.objects.filter( sku__category__name = 'Case', in_stock = True),
                              data = request.POST or None )
    
    SystemHardDriveFormSet = formset_factory( SystemHardDriveForm, extra = 3 )
    hard_drive_form_set = SystemHardDriveFormSet( data = request.POST or None ) 
    if request.method == 'POST':
        num_valid_hds = 0
        if hard_drive_form_set.is_valid():
            valid_hard_drive_reqs = [ form for form in hard_drive_form_set.cleaned_data if form ] 
            num_valid_hds = len( valid_hard_drive_reqs )
        
            
        if system_form.is_valid() and hard_drive_form_set.is_valid() and num_valid_hds:
            # Keep track of components and qty request for building later
            component2qty = {}

            # Ensure we have enough in stock to build the system
            system_data = system_form.cleaned_data

            has_errors = False
            component2qty[ system_data['case']] = 1
            if system_data['case'].quantity < 1:
                messages.error( request, 'Not enough stock of case: %s' % str(system_data['case']) )
                has_errors = True
                
            component2qty[ system_data['motherboard']] = 1
            if system_data['motherboard'].quantity < 1:
                messages.error( request, 'Not enough stock of motherboard: %s' % str(system_data['motherboard']) )
                has_errors = True

            # Check the total number of each type of hard drive
            #  Determine how much we want of each HD
            harddrive2qty = {}
            
            for hd_req in valid_hard_drive_reqs:
                harddrive2qty.setdefault( hd_req['hard_drive'], 0 )
                harddrive2qty[ hd_req['hard_drive'] ] += hd_req['quantity']

            #  See if we have enough of what is requested
            for (hd, qty) in harddrive2qty.items():
                component2qty[ hd ] = qty
                if qty > hd.quantity:
                    messages.error( request, 'Not enough stock of hard drive: %s.  Requested %d.' % ( str(hd), qty ) )
                    has_errors = True


            if not has_errors:
                # Build the system
                system = Item( sku = system_data['system_type'],
                               tag = system_data['tag'],
                               quantity = 1,
                               status = 'Waiting to be built',
                               in_stock = True,
                               refurb = False,
                               notes = '',
                               )
                system.save()

                # Then remove the items used from stock
                for (component, qty) in component2qty.items():
                    # First create the new items that are in the system
                    new_item = Item( sku = component.sku,
                                     tag = component.tag,
                                     quantity = qty,
                                     status = 'In System',
                                     in_item = system,
                                     in_stock = False,
                                     refurb = component.refurb,
                                     notes = component.notes
                                     )
                    new_item.save()
                    
                    # Now adjust or delete the source items
                    component.quantity -= qty
                    if component.quantity == 0:
                        component.delete()
                    else:
                        component.save()

                    
                # Let them know the system was build successfully
                messages.success( request, 'Successfully added system %s (%s).' % ( system.sku.code, system.tag ))
                

                # If they want to build again, return them to this page
                if request.POST.get( 'build_and_build', None ):
                    return( HttpResponseRedirect( reverse( 'system_build' )))

                # Else return them to home page
                return( HttpResponseRedirect( reverse( 'home' )))

        else:
            # Let them know there was an error
            if num_valid_hds == 0:
                messages.error( request, 'You need to add at least 1 hard drive.' )
            else:
                messages.error( request, 'There was an error.' )
    

    return( render( request, 'inventory/system_build.html',
                    { 'system_form': system_form,
                      'hard_drive_form_set': hard_drive_form_set,
                      }))
    
    


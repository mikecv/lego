from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.core.files.storage import default_storage

import logging
import pickle, zlib, base64

import os

from .models import Colour, PartType, MyPart, Set, SetPart
from .modellists import sortpartqtys
from .forms import AddSetForm, EditPartForm
from .getcols import getColours, getColour
from .addset import parseset
from .utils import serialseObject

from .mylegoconfig import *

# Get an instance of a logger
logger = logging.getLogger('legoLogger')

# **************************************************************
# Default index view.
# **************************************************************
@login_required
def index(request):

    # Generate count of colours
    num_colours = Colour.objects.all().count()

    # Generate count of parts
    num_parts = PartType.objects.all().count()

    # Generate count of my parts (parts held)
    num_myparts = MyPart.objects.all().count()

    # Generate count of sets
    num_sets = Set.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_colours': num_colours,
                 'num_parts': num_parts,
                 'num_myparts': num_myparts,
                 'num_sets': num_sets,
                 'num_visits': num_visits},
    )

# **************************************************************
# Lego colours view.
# **************************************************************
@login_required
def colours(request):
    """
    View function for all part colours.
    """

    # Generate counts of colours
    num_colours = Colour.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits_colours = request.session.get('num_visits_colours', 0)
    request.session['num_visits_colours'] = num_visits_colours + 1

    # Render the HTML template colours.html with the data in the context variable.
    return render(
        request,
        'colours.html',
        context={'num_colours': num_colours,
                 'colours_list': Colour.objects.all().order_by("code"),
                 'num_visits_colours': num_visits_colours},
    )

# **************************************************************
# Function to get Lego colours from the web.
# Results shown on colours view.
# **************************************************************
@login_required
def getcols(request):
    """
    View function to get all part colours from the Peeron website.
    """

    # If this is a POST request we need to process the form data
    if request.method != 'POST':
        # Call function to retrieve all the colour data from the net.
        getcol_status = getColours(logger)
        if getcol_status == GETCOLS_GOOD:
            # No errors, so return back to colours page.
            return HttpResponseRedirect('colours')
        else:
            # Error returned, so go to bad status page and display error.
            url = reverse('badfunc', kwargs={'status': getcol_status})
            return HttpResponseRedirect(url)
    # Else render colours page.
    else:
        colours(request)

# **************************************************************
# Lego parts view.
# **************************************************************
@login_required
def parts(request):
    """
    View function for Lego parts.
    """
    # Generate counts of parts
    num_parts = PartType.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits_parts = request.session.get('num_visits_parts', 0)
    request.session['num_visits_parts'] = num_visits_parts + 1

    # Render the HTML template parts.html with the data in the context variable.
    return render(
        request,
        'parts.html',
        context={'num_parts': num_parts,
                 'parts_list': PartType.objects.all().order_by("code"),
                 'num_visits_parts': num_visits_parts},
    )

# **************************************************************
# Lego part details view.
# **************************************************************
@login_required
def partdetails(request, code):
    """
    View function for when a particular part is selected for display.
    Display all the details for the part with the requested code.
    """

    # Render the HTML template partdetails.html with the data in the context variable.
    # The part code is passed as a URL parameter.
    return render(
        request,
        'partdetails.html',
        context={'part': PartType.objects.filter(code=code)[0]},
    )

# **************************************************************
# Lego part edit view.
# **************************************************************
@login_required
def partedit(request, code):
    """
    View function for when a particular part is edit.
    Display all the details for the part with the requested code,
    in a form so that they can be edited.
    """
    # If this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EditPartForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            data = form.cleaned_data
            existing_part = PartType.objects.get(code=code)
            new_description = data['part_description']
            new_picture = data['part_picture']
            # Check if the user changed the part description.
            if new_description != existing_part.description:
                existing_part.description = new_description
                existing_part.save()
                logger.info('User changed part description to: {0}'.format(new_description))
            else:
                logger.info('Part description not changed.')
            # Check if the user changed the part image.
            if new_picture != existing_part.picture:
                logger.info('New part picture selected: {0}'.format(new_picture))
                part_pic_type = os.path.splitext(new_picture.name)[1]
                # Check if set image already exists, if it does then overwrite.
                part_image_name = PARTPREFIX + code + part_pic_type
                absolute_path = PROJPATH + PARTPICLOCN + part_image_name
                if default_storage.exists(absolute_path) == False:
                    logger.info('Adding part image : {0}.'.format(part_image_name))
                    existing_part.picture.save(part_image_name, new_picture)
                else:
                    logger.info('Part image already exists,'
                                ' removing and then re-adding : {0}.'.format((PARTPICLOCN + part_image_name)))
                    os.remove(absolute_path)
                    existing_part.picture.save(part_image_name, new_picture)
            else:
                logger.info('Part picture not changed.')
            # No errors, so return back to part details page.
            url = reverse('partdetails', kwargs={'code': code})
            return HttpResponseRedirect(url)
        else:
            logger.info('Part edit form response is not valid.')

    # If a GET (or any other method) we'll create a blank form.
    else:
        part = PartType.objects.filter(code=code)[0]
        logger.info('Initial values for part: {0}, description: {1}, picture: {2}'.format(part.code, part.description, part.picture))
        form = EditPartForm(initial={'part_code': part.code, 'part_description': part.description, 'part_picture': part.picture})

    # Render the HTML template partedit.html with the data in the context variable.
    # The part code is passed as a URL parameter.
    return render(
        request,
        'partedit.html',
        context={'part': PartType.objects.filter(code=code)[0],
                 'form': form},
    )

# **************************************************************
# Lego parts marked as held (by me) view.
# **************************************************************
@login_required
def myparts(request):
    """
    View function for parts on hand.
    That is, part types held in particular colours.
    """
    # Generate counts of my parts
    num_myparts = MyPart.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits_myparts = request.session.get('num_visits_myparts', 0)
    request.session['num_visits_myparts'] = num_visits_myparts + 1

    # Get list of allocated and unallocated parts that I have.
    my_unallocated_parts = MyPart.objects.filter(allocation=None).order_by('part__code')
    num_unallocated_parts = len(my_unallocated_parts)
    unallocated_qty_list = sortpartqtys(False, logger)
    # Get list of allocated and allocated parts that I have.
    my_allocated_parts =  MyPart.objects.exclude(allocation=None).order_by('part__code')
    num_allocated_parts = len(my_allocated_parts)
    allocated_qty_list = sortpartqtys(True, logger)

    # Render the HTML template myparts.html with the data in the context variable.
    return render(
        request,
        'myparts.html',
        context={'num_myparts': num_myparts,
                 'num_unallocated_parts': num_unallocated_parts,
                 'num_allocated_parts': num_allocated_parts,
                 'my_unallocated_parts_list': unallocated_qty_list,
                 'my_allocated_parts_list': allocated_qty_list,
                 'num_visits_myparts': num_visits_myparts},
    )

# **************************************************************
# Lego sets view.
# **************************************************************
@login_required
def sets(request):
    """
    View function for all sets.
    """
    # Generate counts of sets
    num_sets = Set.objects.all().count()

    # Number of visits to this view, as counted in the session variable.
    num_visits_sets = request.session.get('num_visits_sets', 0)
    request.session['num_visits_sets'] = num_visits_sets + 1

    # Render the HTML template sets.html with the data in the context variable.
    return render(
        request,
        'sets.html',
        context={'num_sets': num_sets,
                 'sets_list': Set.objects.all().order_by("code"),
                 'num_visits_sets': num_visits_sets},
    )

# **************************************************************
# Particular set parts/details view.
# **************************************************************
@login_required
def setdetails(request, code):
    """
    View function for when a particular set is selected.
    Display all the details for the set, including parts to make the set.
    """

    # Render the HTML template setdetails.html with the data in the context variable.
    # The set number is passed as a URL parameter.
    this_set = Set.objects.get(code=code)
    set_parts = this_set.setpart_set.all()
    return render(
        request,
        'setdetails.html',
        context={'set': Set.objects.filter(code=code)[0], 'setparts': set_parts}
    )

# **************************************************************
# Function to present a form to search for a set on the web.
# Results shown on sets view.
# **************************************************************
@login_required
def addset(request):
    """
    View function for adding a new set.
    Via a form the user enters a set code to retrieve.
    Optionally, the user can indicate that this set is held, i.e. all parts
    are added to my parts.
    """

    # If this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddSetForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            data = form.cleaned_data
            set_code = data['set_code']
            my_set = data['my_set']
            logger.info('New set to add: {0}, My set: {1}'.format(set_code, my_set))
            # Check if we already have this set added.
            if Set.objects.filter(code=set_code).exists():
                logger.warning('Set \"{0}\" already exists, not adding.'.format(set_code))
                url = reverse('badfunc', kwargs={'status': PARSESET_EXISTS})
                return HttpResponseRedirect(url)
            else:
                # Call function to parse the selected set data from the net.
                result = parseset.delay(serialseObject(logger), set_code, my_set)
                # return render(request,
                #     'sets.html',
                #     context={'task_id': result.task_id}
                # )
                return render(request,
                    'progress.html',
                    context={'task_id': result.task_id}
                )

    # If a GET (or any other method) we'll create a blank form.
    else:
        form = AddSetForm()

    return render(
        request,
        'addset.html',
        context={'form': form},
    )

# **************************************************************
# Failed function view.
# **************************************************************
@login_required
def badfunc(request, status):
    """
    View function for when a function fails.
    Displays an error code and string to the user.
    """

    # Render the HTML template badfunction.html with the data in the context variable.
    # The status is passed as a URL parameter.
    return render(
        request,
        'badfunction.html',
        context={'code': int(status),
                 'status': bad_function_status[int(status)]},
    )
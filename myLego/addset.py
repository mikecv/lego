from .models import Colour, PartType, MyPart, Set, SetPart
from django.core.files import File
from django.core.files.storage import default_storage
from urllib.request import urlopen
from urllib.error import URLError
import os
from os.path import splitext
import io
import re
from .mylegoconfig import *
from .getcols import getColour, getContrastingcolour

# **************************************************************
# Function to get colour information from Peeron colours web page.
# Need to go to the Peeron lego colours web page.
# **************************************************************
def getcolour(part_colour, logger):

    # Function status default to good.
    func_status = GETCOLS_GOOD

    # Initialise return variables
    col_description = None
    col_rgb_colour = '#FFFFFF'
    contrast_col = '#000000'

    # Check for special case of 'Unknown' colour search requested.
    # Some sets actual have this colour for parts (mostly multi-colour decals),
    # but colour does not exist in the Peeron colour list.
    if part_colour == 'Unknown':
        col_description = 'Unknown'
        logger.warning('Unknown colour search requested, returning unknown.')
    else:
        # Attempt to read the Peeron colours web page.
        try:
            ureq = urlopen(coloursurl, data=None)
        except URLError as e:
            # Check for request exceptions.
            if hasattr(e, 'reason'):
                func_status = PARSESET_URLRES
                logger.error('Failed to reach server with reason code : {0}'.format(e.reason))
            elif hasattr(e, 'code'):
                func_status = PARSESET_URLCOD
                logger.error('Server could not fulfill request with error code : {0}'.format(e.code))
            # Return with error status.
            return (func_status, col_description, col_rgb_colour, contrast_col)
        else:
            ufile = io.TextIOWrapper(ureq, encoding='ISO-8859-1')
            coldata = ufile.read()

        # Check if the query to the website was successful.
        # Construct regex string with part colour code included.
        reg_string = '.+<tbody>.+?<td><a href=.+?>' + part_colour + '</a></td><td>([0-9]*?)</td><td>(.*?)</td><td>([0-9]*?)</td><td>([0-9]*?)</td><td>(<div.*?>)*?([0-9a-fA-F]*?)(</div>)*?</td>'
        reg_match = re.search(reg_string, coldata, re.DOTALL)
        if reg_match:
            parts_this_col = reg_match.group(1)
            col_description = reg_match.group(2)
            logger.info('Found colour with code: {0}, description : {1},'
                        ' Parts this colour : {2}'.format(part_colour, col_description, parts_this_col))

            # If no colour, then default to white, i.e. 0xFFFFFF.
            if reg_match.group(6) == "":
                col_rgb_colour = '#FFFFFF'
            else:
                col_rgb_colour = '#' + reg_match.group(6)
            # Determine contrasting colour (for display purposes).
            contrast_col = getContrastingcolour(logger, col_rgb_colour)
            logger.info('Found colour with code: {0}, description : {1},'
                        ' Parts this colour : {2}, RGB colour : {3}'.format(part_colour, col_description, parts_this_col, col_rgb_colour))
        else:
            logger.warning('Failed to find this part colour in the Peeron colour list: {0}'.format(part_colour))

    return (func_status, col_description, col_rgb_colour, contrast_col)

# **************************************************************
# Function to parse a lego html file (from Peeron website) and extract set details.
# Optionally add the set parts to my parts.
# **************************************************************
def parseset(set_id, my_set, logger):

    # Function status default to good.
    func_status = PARSESET_GOOD

    # Get the URL of the set to get.
    net_set = seturlbase + set_id
    logger.info('Set to get from the web : {0}'.format(net_set))

    # Attempt to read the web page for this set number.
    try:
        ureq = urlopen(net_set, data=None)
    except URLError as e:
        # Check for request exceptions.
        if hasattr(e, 'reason'):
            func_status = PARSESET_URLRES
            logger.error('Failed to reach server with reason code : {0}'.format(e.reason))
        elif hasattr(e, 'code'):
            func_status = PARSESET_URLCOD
            logger.error('Server could not fulfill request with error code : {0}'.format(e.code))
    else:
        ufile = io.TextIOWrapper(ureq, encoding='ISO-8859-1')
        setdata = ufile.read()

        # First check if the query to the website was successful.
        reg_string = '.+Your query resulted in no matches'
        reg_match = re.search(reg_string, setdata, re.DOTALL)
        if reg_match:
            # Query of the Peeron website yielded no results, so no set to get.
            func_status = PARSESET_QUERY
            logger.warning('Peeron web page returned an empty query for the set.')
        else:

            # Find set number and title.
            reg_string = '.+<h2 id=\"settitle\">Set # (.+?): (.+)</h2>.+?>Theme<'
            reg_match = re.search(reg_string, setdata, re.DOTALL)
            if reg_match:
                net_set_id = reg_match.group(1)
                net_set_name = reg_match.group(2)
                # Strip out non-printable characters from set name (have seen this on the Peeron website.
                net_set_name = "".join(c for c in net_set_name if c.isprintable())
                logger.info('Found Set: {0}, Description : {1}'.format(net_set_id, net_set_name))

                # Check if we already have this set added.
                if Set.objects.filter(code=net_set_id).exists():
                    # Set already exists so don't proceed further.
                    func_status = PARSESET_EXISTS
                else:
                    # Shorten the search string appropriatly for the next search.
                    setdata = setdata[len(reg_match.group(0)):]

                    # Find main set header information.
                    reg_string = '(.+?)>Year:.+?<b><a href.+?>([0-9]+).+?</li>.+?>Pcs:.+?<b>([0-9]+)(.+?)Peeron links'
                    reg_match = re.search(reg_string, setdata, re.DOTALL)
                    if reg_match:

                        # Create an empty list so set part objects that can be linked to the set.
                        set_parts_list = []

                        # Create an empty list so my parts can be linked to the set (if required to be allocated).
                        alloc_myparts_list = []

                        # Parse the Lego class string further.
                        lego_class_string = ""
                        num_classes = 0
                        reg_class_string = '.+?<a href=.+?>(.+?)<'
                        for class_match in re.finditer(reg_class_string, reg_match.group(1), re.DOTALL):
                            lego_class = class_match.group(1)
                            # Create a comma separated string of all Lego classes for this set.
                            if num_classes > 0:
                                lego_class_string += ", "
                            lego_class_string += lego_class
                            logger.info('Found Lego class: {0}'.format(lego_class))
                            num_classes += 1
                        # Get the year the set was introduced.
                        set_year = int(reg_match.group(2))
                        logger.info('Year set introduced : {0}'.format(set_year))
                        # Get the number of pieces in the set.
                        # Can use this later to check that parts list adds up.
                        num_pieces = int(reg_match.group(3))
                        logger.info('Number of pieces in set : {0}'.format(num_pieces))
                        # Get link to instructions if they exist.
                        # Need to check if a instruction download link exists.
                        instruction_string = '.+?Need building instructions.+?FREE Download:.+?<a href="(.+?)".+?'
                        inst_match = re.search(instruction_string, reg_match.group(4), re.DOTALL)
                        if inst_match:
                            # Note that reference in the website is relative to the Peeron home page.
                            instruction_ref = peeronurlbase + inst_match.group(1)
                            logger.info('Reference to instructions for this set : {0}'.format(instruction_ref))
                        else:
                            instruction_ref = ""
                            logger.info('No instructions found for this set.')

                        # Shorten the search string appropriatly for the next search.
                        setdata = setdata[len(reg_match.group(0)):]

                        # Find the link to the set image (if there is one).
                        set_img = None
                        reg_string = '.+?<a href="/inv/sets/.+?<img id="setpic" src="(.+?)"'
                        reg_match = re.search(reg_string, setdata, re.DOTALL)
                        if reg_match:
                            net_set_pic_ref = reg_match.group(1)
                            net_set_pic_type = splitext(net_set_pic_ref)[1]
                            logger.info('Set image reference found : {0}'.format(net_set_pic_ref))
                            logger.info('Image file extention is : {0}'.format(net_set_pic_type))
                            try:
                                set_img_file = urlopen(net_set_pic_ref)
                                set_img = io.BytesIO(set_img_file.read())
                            except:
                                logger.info('Failed to download set image.')

                            # Shorten the search string appropriatly for the next search.
                            # Do it here in case no set image string found.
                            setdata = setdata[len(reg_match.group(0)):]
                        else:
                            logger.info('No set image found.')

                        # Look for the parts in the sest.
                        # Jump over the table header info.
                        reg_string = '.+?<thead>.+?>Qty.+?>PartNum.+?>Color.+?>Description.+?>Picture.+?>Note.+?'
                        reg_match = re.search(reg_string, setdata, re.DOTALL)
                        if reg_match:
                            logger.info('Found parts table header.')
                            setdata = setdata[len(reg_match.group(0)):]

                            part_qty_chk = 0

                            reg_string = '.+?<tr.+?<td>([0-9]+?)</td><td>.+?>(.+?)</a></td><td>(.+?)</td><td>(.+?)</td><td>(.+?)</td><td>(.*?)</td>'
                            for part_match in re.finditer(reg_string, setdata, re.DOTALL):
                                part_qty = int(part_match.group(1))
                                part_id = part_match.group(2)
                                part_col = part_match.group(3)
                                part_desc = part_match.group(4)
                                part_note = part_match.group(6)
                                logger.info('Found part entry with Qty : {0},'
                                            ' Part : {1} : {2},'
                                            ' Colour : {3},'
                                            ' Note : {4}'.format(part_qty, part_id, part_desc, part_col, part_note))
                                part_qty_chk += part_qty

                                # The colour needs to exist before the part can be created.
                                # Check if the colour already exists in the database.
                                # Add the colour even if the set or parts in it have issues.
                                if Colour.objects.filter(code=part_col).exists():
                                    logger.info('Colour already exists in database, not adding.')
                                else:
                                    # Colour does not exist in the database, so add it.
                                    # Need to go to the Peeron lego colours web page.
                                    func_status = getColour(logger, part_col)

                                    # Check if colour search function failed or not.
                                    if func_status != GETCOLS_GOOD:
                                        return func_status

                                # The part also needs to exist before it can be added to a set.
                                # Check if the part already exists in the database.
                                if PartType.objects.filter(code=part_id).exists():
                                    logger.info('Part already exists in database, not adding.')
                                else:
                                    # Part does not exist in the database, so add it.
                                    logger.info('Adding new part : {0}.'.format(part_id))
                                    newpart = PartType(code=part_id, description=part_desc)
                                    newpart.save()

                                    # Find the link to the part image (if there is one).
                                    part_img = None
                                    reg_string = '.+?src="(.+?)"'
                                    part_pic_match = re.search(reg_string, part_match.group(5), re.DOTALL)
                                    if part_pic_match:
                                        part_pic_ref = part_pic_match.group(1)
                                        part_pic_type = splitext(part_pic_ref)[1]
                                        logger.info('Part image reference found : {0}'.format(part_pic_ref))
                                        logger.info('Image file extention is : {0}'.format(part_pic_type))

                                        try:
                                            part_img_file = urlopen(part_pic_ref)
                                            part_img = io.BytesIO(part_img_file.read())

                                            # If there was an image for this part then save it.
                                            if part_img != None:
                                                # Check if set image already exists, if it does then overwrite.
                                                part_image_name = PARTPREFIX + part_id + part_pic_type
                                                absolute_path = PROJPATH + PARTPICLOCN + part_image_name
                                                if default_storage.exists(absolute_path) == False:
                                                    logger.info('Adding part image : {0}.'.format(part_image_name))
                                                    newpart.picture.save(part_image_name, File(part_img))
                                                else:
                                                    logger.info('Part image already exists,'
                                                                ' removing and then re-adding : {0}.'.format((PARTPICLOCN + part_image_name)))
                                                    os.remove(absolute_path)
                                                    newpart.picture.save(part_image_name, File(part_img))
                                        except:
                                            logger.info('Failed to download part image.')
                                    else:
                                        logger.info('No part image found part: {0}'.format(part_id))

                                # We can create a list of parts in the set so that we can create and link to the set
                                # later when we create the set.
                                # Create a part(s) required object for this part, and add to the list so that it can be linked to the set later.
                                # This object covers the quantity of this part in the set.
                                logger.info('Creating a part required object for this set.')
                                new_set_part = SetPart(req_part=(PartType.objects.filter(code=part_id)[0]),
                                                       req_col=(Colour.objects.filter(code=part_col)[0]),
                                                       req_qty=(part_qty),
                                                       part_notes=part_note
                                                       )
                                new_set_part.save()
                                set_parts_list.append(new_set_part)

                                # Now that the part exists we need to check if this is a set we have.
                                # In which case we want to add the part as one of my parts, i.e. held me.
                                if my_set == True:
                                    # Set is one of my sets so add as one of my parts.
                                    logger.info('Adding new my part(s): {0},'
                                                ' Colour: {1},'
                                                ' Quantity: {2}.'.format(part_id, part_col, part_qty))
                                    for qty in range(0, part_qty):
                                        # Add part to my parts. An object for each part.
                                        new_my_part = MyPart(part=(PartType.objects.filter(code=part_id)[0]),
                                                             colour=(Colour.objects.filter(code=part_col)[0]))
                                        new_my_part.save()
                                        alloc_myparts_list.append(new_my_part)

                            # Check if the number of parts is as expected.
                            if part_qty_chk != num_pieces:
                                # Number of parts does not match.
                                # This is often because of extra parts shipped with sets.
                                logger.warning('Parts list count mismatch. Expected : {0},'
                                               ' Found : {1} '.format(num_pieces, part_qty_chk))

                            # Add the set to the database.
                            logger.info('Adding new set: {0}.'.format(net_set_id))
                            newset = Set(code=net_set_id,
                                         description=net_set_name,
                                         set_classes=lego_class_string,
                                         year_released=set_year,
                                         num_pieces=num_pieces,
                                         instructionURL=instruction_ref
                                         )
                            newset.save()

                            # Link the required parts objects to the new set.
                            for new_part in set_parts_list:
                                new_part.for_set = newset
                                new_part.save()

                            # If applicable link newly acquired parts to the set.
                            if my_set == True:
                                for my_part in alloc_myparts_list:
                                    my_part.allocation = newset
                                    my_part.save()

                            # If there was an image for this set then save it.
                            # Just check first if the set image already exists.
                            if set_img != None:
                                # Check if set image already exists, if it does then overwrite.
                                set_image_name = SETPREFIX + net_set_id + net_set_pic_type
                                absolute_path = PROJPATH + SETPICLOCN + set_image_name
                                if default_storage.exists(absolute_path) == False:
                                    logger.info('Adding set image: {0}.'.format(set_image_name))
                                    newset.picture.save(set_image_name, File(set_img))
                                else:
                                    logger.info('Set image already exists, removing and then re-adding : {0}.'.format((SETPICLOCN + set_image_name)))
                                    os.remove(absolute_path)
                                    newset.picture.save(set_image_name, File(set_img))
                        else:
                            # Could not find the header section of the parts list table.
                            logger.info('No parts table found for this set.')
                            func_status = PARSESET_NOPARTS
            else:
                func_status = PARSESET_NOSET
                logger.error('No Lego set ID or description found when parsing website.')

    return func_status

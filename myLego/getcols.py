from .models import Colour
from urllib.request import urlopen
from urllib.error import URLError
import io
import re
from .mylegoconfig import *

# **************************************************************
# Function to add colour.
# **************************************************************
def addColourToDB(logger, col_code, col_description, col_rgb_colour, contrast_col):
        logger.info('Adding new colour : {0}.'.format(col_code))
        newcol = Colour(code=col_code, description=col_description, rgb_colour=col_rgb_colour, contrast_colour=contrast_col)
        newcol.save()

# **************************************************************
# Function to get a contrasting text colour to the supplied background colour.
# Contrasting colour is either black or white depending on the 'brightness' of the background.
# **************************************************************
def getContrastingcolour(logger, bg_colour):

    # Determine contrasting colour (for display purposes).
    r_comp = int('0x' + bg_colour[1:3], 16)
    g_comp = int('0x' + bg_colour[3:5], 16)
    b_comp = int('0x' + bg_colour[5:], 16)
    col_brightness = ((r_comp * 299) + (g_comp * 587) + (b_comp * 114)) // 1000
    if col_brightness > CONTRAST_THRESHOLD:
        contrast_col = '#000000'
    else:
        contrast_col = '#FFFFFF'
    logger.info('Background colour : {0}, Brightness : {1}, Contrasting colour : {2}'.format(bg_colour, col_brightness, contrast_col))

    return contrast_col

# **************************************************************
# Function to parse Lego colours (from Peeron website) and extract details of all colours.
# **************************************************************
def getColours(logger):

    # Function status default to good.
    func_status = GETCOLS_GOOD

    # Attempt to read the Peeron colours web page.
    # Need to go to the Peeron lego colours web page.
    try:
        ureq = urlopen(coloursurl, data=None)
    except URLError as e:
        # Check for request exceptions.
        if hasattr(e, 'reason'):
            func_status = GETCOLS_URLRES
            logger.error('Failed to reach server with reason code : {0}'.format(e.reason))
        elif hasattr(e, 'code'):
            func_status = GETCOLS_URLCOD
            logger.error('Server could not fulfill request with error code : {0}'.format(e.code))
        # Return with error status.
        return func_status
    else:
        ufile = io.TextIOWrapper(ureq, encoding='ISO-8859-1')
        coldata = ufile.read()

    # Check if the query to the website was successful.
    reg_string = '.+?<title>Peeron Color List</title>.+?<tbody>'
    reg_match = re.search(reg_string, coldata, re.DOTALL)
    if reg_match:
        # Shorten the search string appropriatly for the next search.
        coldata = coldata[len(reg_match.group(0)):]

        # Create search string to iterate through all lines in the table.
        col_string = re.compile(r'^.*?<td><a href=.+?>(.+?)</a></td><td>.*?</td><td>(.*?)</td>(<td>.*?</td>){2}<td>(<div.*?>){0,1}([0-9a-fA-F]*?)(</div>){0,1}</td><td>.*?</td><td>(.*?)</td><td>(<div.*?>){0,1}([0-9a-fA-F]*?)(</div>){0,1}</td>(.*?)$', re.MULTILINE)

        # Iterate through table looking for colour entries.
        # Need to allow for missing entries.
        for col_match in re.finditer(col_string, coldata):
            col_code = col_match.group(1)
            col_description = col_match.group(2)
            col_ldRgb = col_match.group(5)
            lego_description = col_match.group(7)
            lego_rgb = col_match.group(9)

            # Attempt to tidy up after missing cells.
            # If no colour description, use Lego colour name, else just use the colour code.
            if col_description == "":
                if lego_description != "":
                    col_description = lego_description
                else:
                    col_description = col_code
            # If no colour RGB, use Lego colour RGB, else set to "N/A".
            # Format colour in hex.
            if col_ldRgb == "":
                if lego_rgb != "":
                    col_rgb_colour = '#' + lego_rgb
                else:
                    col_rgb_colour = 'N/A'
            else:
                col_rgb_colour = '#' + col_ldRgb

            # Determine contrasting colour (for display purposes).
            if col_rgb_colour != 'N/A':
                contrast_col = getContrastingcolour(logger, col_rgb_colour)
                logger.info('Found colour with code: {0}, description : {1}, RGB colour : {2}'.format(col_code, col_description, col_rgb_colour))
            else:
                contrast_col = getContrastingcolour(logger, "#FFFFFF")
                logger.warning('Found unspecified colour with code: {0}, description : {1}'.format(col_code, col_description))

            # Check if we already have this colour in the database.
            if Colour.objects.filter(code=col_code).exists():
                logger.info('Colour already exists in database, not adding.')
            else:
                # Colour does not exist in the database, so add it.
                addColourToDB(logger, col_code, col_description, col_rgb_colour, contrast_col)
                # logger.info('Adding new colour : {0}.'.format(col_code))
                # newcol = Colour(code=col_code, description=col_description, rgb_colour=col_rgb_colour, contrast_colour=contrast_col)
                # newcol.save()
    else:
        func_status = GETCOLS_NOHEAD
        logger.error('Failed to find header information in Peeron colours page.')

    return func_status

# **************************************************************
# Function to parse Lego colours (from Peeron website) and extract details for a specific colour.
# **************************************************************
def getColour(logger, col_code):

    # Function status default to good.
    func_status = GETCOLS_GOOD

    # Attempt to read the Peeron colours web page.
    # Need to go to the Peeron lego colours web page.
    try:
        ureq = urlopen(coloursurl, data=None)
    except URLError as e:
        # Check for request exceptions.
        if hasattr(e, 'reason'):
            func_status = GETCOLS_URLRES
            logger.error('Failed to reach server with reason code : {0}'.format(e.reason))
        elif hasattr(e, 'code'):
            func_status = GETCOLS_URLCOD
            logger.error('Server could not fulfill request with error code : {0}'.format(e.code))
        # Return with error status.
        return func_status
    else:
        ufile = io.TextIOWrapper(ureq, encoding='ISO-8859-1')
        coldata = ufile.read()

    # Check if the query to the website was successful.
    reg_string = '.+?<title>Peeron Color List</title>.+?<tbody>'
    reg_match = re.search(reg_string, coldata, re.DOTALL)
    if reg_match:
        # Shorten the search string appropriatly for the next search.
        coldata = coldata[len(reg_match.group(0)):]

        # Create search string to search for the colour code.
        specificColString = ("^.*?<td><a href=.+?>{0:s}</a></td><td>.*?</td><td>(.*?)</td>(<td>.*?</td>){{2}}<td>(<div.*?>){{0,1}}([0-9a-fA-F]*?)(</div>){{0,1}}</td><td>.*?</td><td>(.*?)</td><td>(<div.*?>){{0,1}}([0-9a-fA-F]*?)(</div>){{0,1}}</td>(.*?)$".format(col_code))
        col_string = re.compile(specificColString, re.MULTILINE)

        # Search for specific colour.
        col_match = re.search(col_string, coldata)

        if col_match:
            col_code = col_code
            col_description = col_match.group(1)
            col_ldRgb = col_match.group(4)
            lego_description = col_match.group(6)
            lego_rgb = col_match.group(8)

            # Attempt to tidy up after missing cells.
            # If no colour RGB, use Lego colour RGB, else set to "N/A".
            # Format colour in hex.
            if col_ldRgb == "":
                if lego_rgb != "":
                    col_rgb_colour = '#' + lego_rgb
                else:
                    col_rgb_colour = 'N/A'
            else:
                col_rgb_colour = '#' + col_ldRgb

            # Determine contrasting colour (for display purposes).
            if col_rgb_colour != 'N/A':
                contrast_col = getContrastingcolour(logger, col_rgb_colour)
                logger.info('Found colour with code: {0}, description : {1}, RGB colour : {2}'.format(col_code, col_description, col_rgb_colour))
            else:
                contrast_col = getContrastingcolour(logger, "#FFFFFF")
                logger.warning('Found unspecified colour with code: {0}, description : {1}'.format(col_code, col_description))

            # Check if we already have this colour in the database.
            if Colour.objects.filter(code=col_code).exists():
                logger.info('Colour already exists in database, not adding.')
            else:
                # Colour does not exist in the database, so add it.
                # logger.info('Adding new colour : {0}.'.format(col_code))
                # newcol = Colour(code=col_code, description=col_description, rgb_colour=col_rgb_colour, contrast_colour=contrast_col)
                # newcol.save()
                addColourToDB(logger, col_code, col_description, col_rgb_colour, contrast_col)
    else:
        func_status = GETCOLS_NOHEAD
        logger.error('Failed to find header information in Peeron colours page.')

    return func_status

# Peeron.com URLs
peeronurlbase = 'http://www.peeron.com'
seturlbase = peeronurlbase + '/inv/sets/'
coloursurl = 'http://www.peeron.com/inv/colors'

# Static file locations (relative to project).
PARTPICLOCN = 'myLego/media/parts/'
SETPICLOCN = 'myLego/media/sets/'

# Media file prefixes.
PARTPREFIX = 'Part-'
SETPREFIX = 'Set-'

# Absolute path to project.
PROJPATH = '/home/mike/python/django/djenv/lego/'

# Colour related constants
CONTRAST_THRESHOLD = 186

# Errors returned from function to add a new set.
PARSESET_GOOD = 0
PARSESET_EXISTS = 1
PARSESET_QUERY = 2
PARSESET_URLRES = 3
PARSESET_URLCOD = 4
PARSESET_NOSET = 5
PARSESET_NOPARTS = 6
PARSESET_NOCOL = 7
GETCOLS_GOOD = 8
GETCOLS_URLRES = 9
GETCOLS_URLCOD = 10
GETCOLS_NOHEAD = 11

bad_function_status = {
    PARSESET_GOOD : "Success.",
    PARSESET_EXISTS : "Set already exists.",
    PARSESET_QUERY : "Query of the Peeron website yielded no results.",
    PARSESET_URLRES : "Website request failed with URL response reason.",
    PARSESET_URLCOD : "Website request failed with URL response code.",
    PARSESET_NOSET : "No Lego set ID or description found parsing web page.",
    PARSESET_NOPARTS : "No parts table found for the set.",
    PARSESET_NOCOL : "Failed to find matching part colour.",
    GETCOLS_GOOD : "Success.",
    GETCOLS_URLRES : "Website request failed with URL response reason.",
    GETCOLS_URLCOD : "Website request failed with URL response code.",
    GETCOLS_NOHEAD : "No header information in the Peeron Lego colours page."
}

# Dictionary keys for sorted parts.
PART_OBJ = 'mypartobj'
PART_QTY = 'quantity'


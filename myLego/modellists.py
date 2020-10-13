from .models import Colour, PartType, MyPart, Set

from .mylegoconfig import *

# **************************************************************
# Function to organise parts by quantity of part type and colour.
# Can work with allocated or unallocated list depending on parameter.
# **************************************************************
def sortpartqtys(allocList, logger):

    sorted_list = []

    # Filter parts list by part type code, and then colour.
    if allocList == False:
        partlist = MyPart.objects.filter(allocation=None).order_by('part__code', 'colour__code')
    else:
        partlist = MyPart.objects.exclude(allocation=None).order_by('part__code', 'colour__code', 'allocation__code')

    # Go through parts in list and look for same code, colour, and set.
    # For unallocated parts list have a blank set code.

    if len(partlist) > 0:
        partqty = 1
        lastcode = None
        lastcol = None
        lastset = ""
        qty_total = 0
        for thispart in partlist:
            partcode = thispart.part.code
            partcol = thispart.colour.code
            if allocList == False:
                partset = ""
            else:
                partset = thispart.allocation.code
            if (partcode != lastcode) or (partcol != lastcol) or (partset != lastset):
                # First part of this type and colour,
                # So store the details of the count for previous part type, colour, and set.
                if lastcode != None:
                    qty_total += partqty
                    sorted_list.append({PART_OBJ: thispart, PART_QTY: partqty})
                # Initialise part type, colour, and set variables.
                lastcode = partcode
                lastcol = partcol
                lastset = partset
                partqty = 1
            else:
                # Increment part quantity of this part type, colour, and set.
                partqty += 1

        # Store the details of the count for the last part as no more.
        qty_total += partqty
        sorted_list.append({PART_OBJ: thispart, PART_QTY: partqty})
        logger.info('Parts unsorted: {0}, sorted: {1}'.format(len(partlist), qty_total))
    else:
        logger.info('Parts list empty, not sorting.')

    return (sorted_list)

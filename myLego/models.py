from django.db import models
from .mylegoconfig import *

# **************************************************************
# Class for Lego colours.
# **************************************************************
class Colour(models.Model):
    """
    Model representing all the colours parts can be.
    """
    code = models.CharField(max_length=20, help_text="Colour code.", unique=True)
    description = models.CharField(max_length=64, help_text="Colour description.", blank=True)
    rgb_colour = models.CharField(max_length=8, help_text="RGB colour.", blank=True)
    contrast_colour = models.CharField(max_length=8, help_text="Contrasting colour.", blank=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return "{0} : {1} : {2}".format(self.code, self.description, self.rgb_colour)

# **************************************************************
# Class for Lego part types, i.e. not of a particular colour.
# **************************************************************
class PartType(models.Model):
    """
    Model representing different part types.
    There are no physical parts of this class, that is, parts on hand have a part type
    and a colour (see MyPart).
    """
    code = models.CharField(max_length=20, help_text="Code.", unique=True)
    description = models.CharField(max_length=64, help_text="Description.")
    picture = models.ImageField(upload_to=PARTPICLOCN, help_text="Picture.", blank=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return "{0} : {1}".format(self.code, self.description)

# **************************************************************
# Class for Lego sets.
# **************************************************************
class Set(models.Model):
    """
    Model representing a Set, being a collection of physical parts, although not necessarily on hand.
    That is parts of a particular part type and colour.
    A set will have a requirement for a particular collection of parts, and optionally, parts on hand
    can be allocated to this set to build it. Required or allocated parts will be linked to a set
    via a foreign key.
    """
    code = models.CharField(max_length=20, help_text="Code.", unique=True)
    description = models.CharField(max_length=64, help_text="Description.")
    set_classes = models.CharField(max_length=80, help_text="Class(es).", blank=True)
    year_released = models.IntegerField(help_text="Year of release.", null=True, blank=True)
    num_pieces = models.IntegerField(help_text="Number of pieces.", default=0)
    picture = models.ImageField(upload_to=SETPICLOCN, help_text="Picture.", blank=True)
    instructionURL = models.URLField(help_text="URL to build instructions.", blank=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return "{0} : {1}".format(self.code, self.description)

# **************************************************************
# Class for parts in a Lego set.
# **************************************************************
class SetPart(models.Model):
    """
    Model representing parts required for a particular set.
    Each object will be a requirement for certain quantity of a particular part type in a particular colour.
    """
    for_set = models.ForeignKey(Set, help_text="For set.", on_delete=models.CASCADE, default=None, null=True, blank=True)
    req_part = models.ForeignKey(PartType, help_text="Part.", on_delete=models.CASCADE, default=None)
    req_col = models.ForeignKey(Colour, help_text="Colour.", on_delete=models.CASCADE, default=None)
    req_qty = models.IntegerField(help_text="Quantity.", default=0)
    part_notes = models.CharField(max_length=64, help_text="Notes.", blank=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return "{0} : {1} : {2} : {3} : {4}".format(self.for_set.__str__(), self.req_part.__str__(), self.req_col.__str__(), self.req_qty, self.part_notes)

# **************************************************************
# Class for Lego parts held by me.
# **************************************************************
class MyPart(models.Model):
    """
    Model representing actual parts held.
    These are pieces of a particular part type, and particular colour.
    They can also be allocated to a particular set.
    If not allocated to a particular set then then they are unallocated (on hand).
    """
    part = models.ForeignKey(PartType, help_text="Part type.", on_delete=models.CASCADE)
    colour = models.ForeignKey(Colour, help_text="Part colour.", on_delete=models.CASCADE)
    allocation = models.ForeignKey(Set, help_text="Allocated to set.", on_delete=models.CASCADE, default=None, null=True, blank=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return "{0} : {1} : {2}".format(self.part.__str__(), self.colour.__str__(), self.allocation.__str__())
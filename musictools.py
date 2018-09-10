from numpy import log2, power
from re import match
from time import sleep

__A4 = 440

def get_A4():
    global __A4
    return __A4

def set_A4(Hz):
    user_type = type(Hz)
    if user_type is not int and user_type is not float:
        raise ValueError('Hz value for A4 must be a positive number.')
    if Hz <= 0:
        raise ValueError('Hz value for A4 must be a positive number.')
    global __A4
    __A4 = Hz

class Note:

    """
    |  Create an object that represents a pitched note or rest.
    |
    | The optional octave value should be an integer repsenting the standard octave numbering system.
    | 
    | For the name, use 'R' for rest or 'A','C#','Eb','F##','Gbbb', etc.
    | Unlimited sharps and flats are permissible (though not always encouraged)
    |
    | Values for rhythm start at 0 for a double whole note, and then 1 for whole, 2 for half, and so on up to 10 for a 512th note.  Print Note.RHYTHM_SETTER_VALUES to view them all.
    |
    | Dots add a dot to the rhythm's value.
    |
    | Likewise, the triplet Boolean can set any rhythm as a 3:2 triplet.
    """

    class_name = "Note"

    RHYTHM_SETTER_VALUES = """
    Double whole: 0
    Whole: 1
    Half: 2
    Quarter: 3
    8th: 4
    16th: 5
    32nd: 6
    64th: 7
    128th: 8
    256th: 9
    512th: 10
    """

    __RHYTHM_VALUES = (
        ("double whole", 1024),
        ("whole", 512),
        ("half", 256),
        ("quarter", 128),
        ("8th", 64),
        ("16th", 32),
        ("32nd", 16),
        ("64th", 8),
        ("128th", 4),
        ("256th", 2),
        ("512th", 1),
    )
            
    __PITCH_VALUES = {
        'C': (0,0),
        'D': (2,1),
        'E': (4,2),
        'F': (5,3),
        'G': (7,4),
        'A': (9,5),
        'B': (11,6),
        'R': (None, None)
    }

    __NOTE_REGEX = r'[A-G](#|b)*$'

    def __init__(self,name,octave=None,rhythm=0,dots=0,triplet=False):

        if type(name) is not str:
            raise ValueError('Note name must be a string.')
        name = name.strip().upper()
        if not match(Note.__NOTE_REGEX,name) and name != "R":
            raise ValueError('Invalid note name.')
        if octave != None:
            if type(octave) is not int:
                raise ValueError('Octave value must be an integer.')
        if rhythm not in range(11):
            raise ValueError('Rhythm value must be an integer between 0 and 10.')
        if type(dots) is not int:
            raise ValueError('Dot value must be a positive integer or 0.')
        if dots < 0:
            raise ValueError('Dot value must be a positive integer or 0.')
        if type(triplet) is not bool:
            raise ValueError('Triplet value must be Boolean.')

        self.__name = name
        self.__octave = octave
        self.__rhythm = rhythm
        self.__dots = dots
        self.__triplet = triplet

    @property
    def is_rest(self):
        """Boolean.  Returns True if Note is a rest."""
        if self.__name == "R":
            return True
        return False

    @property
    def octave(self):
        """Returns the octave number that was set or None."""
        if self.is_rest:
            return None
        return self.__octave

    @octave.setter
    def octave(self,value):
        if self.is_rest:
            raise ValueError("Cannot set an octave value for a rest.")
        if type(value) is not int:
            raise ValueError('Octave value must be an integer.')
        self.__octave = value

    @property
    def dots(self):
        """Returns the number of dots set for the rhythm."""
        return self.__dots
    
    @dots.setter
    def dots(self,value):
        if type(value) is not int:
            raise ValueError("Dot value must be a positive integer or 0.")
        if value < 0:
            raise ValueError("Dot value must be a positive integer or 0.")
        self.__dots = value

    @property
    def triplet(self):
        """Returns True if the rhythm was set to a 3:2 triplet."""
        return self.__triplet
    
    @triplet.setter
    def triplet(self,value):
        if type(value) is not bool:
            raise ValueError("Triplet value must be Boolean.")
        self.__triplet = value
    
    @property
    def rhythm(self):
        """
        | Set the basic rhythm with an integer.  
        View Note.RHYTHM_SETTER_VALUES to see what number corresponds to which rhythm.
        |
        | Returns an object with three properties: name, size, and value
        |
        | .rhythm.name is a string describing the rhythm
        | .rhythm.size is a number that measures the rhythm in 512th notes
        | .rhythm.value is the original integer used to set the rhythm
        | 
        | .rhtyhm.size does take into account dot and triplet settings.
        """
        if not self.__rhythm: 
            return None
        (__rhy_name,__rhy_size) = Note.__RHYTHM_VALUES[self.__rhythm]
        if self.dots:
            if self.dots > 1:
                __rhy_name = f"dotted(x{self.dots}) " + __rhy_name
            else:
                __rhy_name = "dotted " + __rhy_name
            __orig_value = __rhy_size
            for __n in range(self.dots):
                __rhy_size += (__orig_value/(power(2,__n + 1)))
        if self.triplet:
            __rhy_name += " triplet"
            __rhy_size *= (2/3)
        return type('obj', (object,), {'name': __rhy_name, 'size': __rhy_size, 'value': self.__rhythm})

    @rhythm.setter
    def rhythm(self,value):
        if value not in range(11):
            raise ValueError('Rhythm value must be set with an integer between 0 and 10.')
        self.__rhythm = value

    @property
    def name(self):
        """A string describing the Note's main characteristics"""
        if self.is_rest:
            return self.rhythm.name + " rest"
        else:
            name = self.__name
            if self.octave != None:
                name += str(self.octave)
            if self.rhythm:
                name += " " + self.rhythm.name
        return name
    
    @property
    def letter(self):
        """An integer representing the alphabetical letter of the note, C starting with 0 up to 6 for B"""
        return Note.__PITCH_VALUES[self.__name[0]][1]

    @property
    def sharps(self):
        """An integer representing the number of sharps in the Note."""
        if self.is_rest:
            return None
        if len(self.__name) > 0 and "#" in self.__name:
            return len(self.__name) - 1
        return 0

    @property
    def flats(self):
        """An integer representing the number of flats in the Note."""
        if self.is_rest:
            return None
        if len(self.__name) > 0 and "b" in self.__name:
            return len(self.__name) - 1
        return 0

    @property
    def pitch(self):
        """Represents a relative value for a Note's pitch.  Any equivalent of C natural is 0, up to 11 for an equivalent of B natural."""
        if self.is_rest:
            return None
        pitch = Note.__PITCH_VALUES[self.__name[0]][0]
        if self.sharps:
            pitch += self.sharps
            if pitch > 11:
                pitch -= 12
        elif self.flats:
            pitch -= self.flats
            if pitch < 0:
                pitch += 12
        return pitch

    @property
    def pitch_offset(self):
        """Returns the number of half steps a Note is offset from its natural note, positive for sharp, negative for flat."""
        if self.is_rest:
            return None
        if self.sharps > 0:
            return self.sharps
        elif self.flats > 0:
            return -self.flats
        else:
            return 0
    
    @property
    def hard_pitch(self):
        """
        | Returns an integer representing a Note's pitch, taking into account octave value. 
        | 
        | C0 is 0, and any higher or lower notes are measured in half steps up or down.
        """
        if self.octave == None:
            return None
        return self.pitch + self.octave * 12
    
    @property
    def frequency(self):
        """
        | Returns The standard frequency measured in Hz. 
        |
        | Change the default for A4 (440Hz) with the global set_A4() function.
        """
        if self.octave == None:
            return None
        offset = self.hard_pitch - 57
        return get_A4() * power(2,(offset/12))

    def __len__(self):
        if self.is_rest:
            return None
        return len(self.__name)


class Interval:

    """
    | Use this class to create Interval objects, or take advantage of its class methods.
    | 
    | 
    | 
    | 
    | 
    | 
    | 
    """

    class_name = "Interval"

    BASE_INTERVALS: "uni, 2nd, 3rd, 4th, 5th, 6th, 7th"

    __BASE_INTERVALS = {
        "uni": 0,
        "2nd": (1,2),
        "3rd": (3,4),
        "4th": 5,
        "5th": 7,
        "6th": (8,9),
        "7th": (10,11),
    }

    __M_QUAL = ("2nd","3rd","6th","7th")

    __QUALITY_REGEX = r'(maj|min|per)$|(aug|dim)[\d]*$'

    __base_err = "Base interval must be a valid string. (see Interval.BASE_INTERVALS)"
    __quality_err = "Quality must be 'maj','min','per','aug', or 'dim'.\n Augmented and diminished intervals may be increased by adding an integer, such as 'aug2' for doubly augmented."
    __base_qual_err1 = "2nd/3rd/6th/7th cannot be perfect."
    __base_qual_err2 = "uni/4th/5th cannot be major or minor."
    __dir_err = "Direction must be 'a' for ascending or 'd' for descending."
    __dis_err = "Displacement of octave must be a positive integer."

    def __init__(self,quality,base,direction=None,displace=0):

        if type(base) is not str:
            raise ValueError(Interval.__base_err)
        base = base.strip().lower()
        if base not in Interval.__BASE_INTERVALS:
            raise ValueError(Interval.__base_err)
        if type(quality) is not str:
            raise ValueError(Interval.__quality_err)
        quality = quality.strip().lower()
        if not match(Interval.__QUALITY_REGEX,quality):
            raise ValueError(Interval.__quality_err)
        if base in Interval.__M_QUAL and quality == "per":
            raise ValueError(Interval.__base_qual_err1)
        elif base not in Interval.__M_QUAL and quality[0] == "m":
            raise ValueError(Interval.__base_qual_err2)
        if direction != None:
            if type(direction) is not str:
                raise ValueError(Interval.__dir_err)
            if direction != "a" and direction != "d":
                raise ValueError(Interval.__dir_err)
        if type(displace) is not int:
            raise ValueError(Interval.__dis_err)
        if displace < 0:
            raise ValueError(Interval.__dis_err)
        
        self.__quality = quality
        self.__base = base
        self.__direction = direction
        self.__displace = displace

    @property
    def quality(self):
        """The quality given for the interval (str)"""
        return self.__quality

    @property
    def base(self):
        """The base interval given for the interval (str)"""
        return self.__base

    @property
    def direction(self):
        """The direction given for the interval ('a' ascending, 'd' descending)"""
        return self.__direction
    
    @direction.setter
    def direction(self,value):
        if value != None:
            if type(value) is not str:
                raise ValueError(Interval.__dir_err)
            if value != "a" and value != "d":
                raise ValueError(Interval.__dir_err)
        self.__direction = value
    
    @property
    def displace(self):
        """The given number of octaves displaced (int)"""
        return self.__displace

    @property
    def difference(self):
        """Returns the difference in pitch of the interval measured in half steps (int)"""
        if self.quality == "per":
            return Interval.__BASE_INTERVALS[self.base] + 12 * self.displace
        if self.quality == "min":
            return Interval.__BASE_INTERVALS[self.base][0] + 12 * self.displace
        if self.quality == "maj":
            return Interval.__BASE_INTERVALS[self.base][1] + 12 * self.displace
        if self.quality[:3] == "aug":
            if len(self.quality) > 3:
                more = int(self.quality[3:]) if self.quality[3:] != "0" else 1
            else:
                more = 1
            if self.base in Interval.__M_QUAL:
                return Interval.__BASE_INTERVALS[self.base][1] + more + 12 * self.displace
            else:
                return Interval.__BASE_INTERVALS[self.base] + more + 12 * self.displace
        elif self.quality[:3] == "dim":
            if len(self.quality) > 3:
                less = int(self.quality[3:]) if self.quality[3:] != "0" else 1
            else:
                less = 1
            if self.base in Interval.__M_QUAL:
                return Interval.__BASE_INTERVALS[self.base][0] - less + 12 * self.displace
            else:
                return Interval.__BASE_INTERVALS[self.base] - less + 12 * self.displace
    
    @property
    def name(self):
        """A name for the interval more pleasing to the eye (str)"""
        if self.base == "uni" and self.quality == "per" and self.displace > 1:
            return f"{self.displace} octaves"
        if self.displace == 1:
            if self.base == "uni":
                base = "octave"
            else:
                base = str(int(self.base[0]) + 7) + "th"
        elif self.base == "uni":
            base = "unison"
        else:
            base = self.base
        if self.quality == "maj":
            quality = "Major"
        elif self.quality == "min":
            quality = "Minor"
        elif self.quality == "per":
            quality = "Perfect"
        elif self.quality[:3] == "aug":
            quality = "Augmented"
        else:
            quality = "Diminished"
        if len(self.quality) > 3:
            times = f"(x{self.quality[3:]})"
        else:
            times = ""
        name = quality + times + " " + base
        if self.displace > 1:
            name += f" plus {self.displace} octaves"
        return name
        
    __SIMPLE_INTVLS = (
        ("per","uni"),
        ("min","2nd"),
        ("maj","2nd"),
        ("min","3rd"),
        ("maj","3rd"),
        ("per","4th"),
        ("aug","4th"),
        ("per","5th"),
        ("min","6th"),
        ("maj","6th"),
        ("min","7th"),
        ("maj","7th"),
        )
    
    @classmethod
    def from_notes(self,note_obj1,note_obj2,simple=None):
        """
        | Return an interval object measured between two Note objects.
        | Set simple to 'a'(ascend) or 'd'(descend) to calculate an interval 
        that is calculated independant of octave value or strict enharmonic naming.
        | Otherwise, both Note objects (see Note class) must have octave values.
        """
        try:
            assert note_obj1.class_name == "Note" and note_obj2.class_name == "Note"
        except:
            raise ValueError("Arguments must be Note objects")
        if simple:
            if simple != "a" and simple != "d":
                raise ValueError("Set simple only to 'a' for ascending or 'd' for descending.")
            if simple == 'a':
                pitch_diff = note_obj2.pitch - note_obj1.pitch
            else:
                pitch_diff = note_obj1.pitch - note_obj2.pitch
            return Interval(Interval.__SIMPLE_INTVLS[pitch_diff][0],Interval.__SIMPLE_INTVLS[pitch_diff][1])














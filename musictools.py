from numpy import log2, power
from re import match
from time import sleep

__A4 = 440

def get_A4():
    global __A4
    return __A4

def set_A4(Hz):
    if type(Hz) is not int and type(Hz) is not float:
        raise ValueError('Hz value for A4 must be a positive number.')
    if Hz <= 0:
        raise ValueError('Hz value for A4 must be a positive number.')
    global __A4
    __A4 = Hz

class _Meta:
    __locked = False
    __RESTRICTED = (
        "enharmonic",
    )
    def __setattr__(self, name, value):
        if self.__locked and name not in dir(self) or name in _Meta.__RESTRICTED or name.startswith("__"):
            raise AttributeError(f"Cannot set attribute '{name}'.")
        object.__setattr__(self, name, value)

    def _lock(self):
        self.__locked = True

class Note(_Meta):

    """
    |  Create an object that represents a pitched note or rest.  Also see class methods.
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

    __PITCH_VALUES = (
        ("C",0),
        ("D",2),
        ("E",4),
        ("F",5),
        ("G",7),
        ("A",9),
        ("B",11),
    )

    __NOTE_REGEX = r'[A-G](#|b)*$'

    def __init__(self,name,octave=None,rhythm=0,dots=0,triplet=False):
        if type(name) is not str:
            raise ValueError('Note name must be a string.')
        name = name.strip().capitalize()
        if not match(Note.__NOTE_REGEX,name) and name != "R":
            raise ValueError('Invalid note name.')
        if octave != None:
            if type(octave) is not int:
                raise ValueError('Octave value must be an integer.')
        if rhythm not in range(11):
            raise ValueError('Rhythm value must be an integer between 0 and 10. See Note.RHYTHM_SETTER_VALUES')
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

        self._lock()

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
        if type(value) is not int and value != None:
            raise ValueError('Octave value must be an integer or None.')
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
        if value not in range(11) and value != None:
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
    def note_name(self):
        """Only the name of the note (letter and sharps/flats), without any other description"""
        return self.__name

    @property
    def letter(self):
        """An integer representing the alphabetical letter of the note, C starting with 0 up to 6 for B"""
        i = 0
        for note in Note.__PITCH_VALUES:
            if self.__name[0] == note[0]:
                return i
            i += 1
        else:
            return None

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
        for note in Note.__PITCH_VALUES:
            if self.__name[0] == note[0]:
                pitch = note[1]
                break
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
    
    __GROSS_ROOTS = {"B":"Cb","C":"B#","E":"Fb","F":"E#"}
    __NON_NATURAL = (1,3,6,8,10)

    def enharmonic(self,prefer=None, gross=False):
        """
        | Return an enharmonic version of the note.
        | Does not change the original object.
        | 'gross' set to True allows B to convert to Cb, E to Fb, C to B#, F to E#.
        | Set 'prefer' to '#' or 'b' to force a return of only a certian enharmonic.
        | Multiple sharps/flats will reduce to 1 or 0.
        | Preserves the original object's octave and rhythm
        """
        if self.pitch == None:
            raise Exception("'enharmonic' is unusable on a rest.")
        if prefer:
            if prefer not in ("#","b"):
                raise ValueError("Set prefer to '#' or 'b'.")
        if type(gross) is not bool:
            raise ValueError("'gross' must be Boolean.")
        if gross and self.note_name in Note.__GROSS_ROOTS:
            new_name = Note.__GROSS_ROOTS[self.note_name]
            if "#" in new_name and prefer == 'b':
                return self
            elif 'b' in new_name and prefer == '#':
                return self
            else:
                new_note = Note(new_name)
        elif len(self.note_name) == 1:
            return self
        elif len(self.note_name) == 2:
            if "#" in self.note_name:
                if prefer == '#':
                    return self
                new_letter = self.letter + 1
                if new_letter > 6:
                    new_letter -= 7
            else:
                if prefer == 'b':
                    return self
                new_letter = self.letter - 1
                if new_letter < 0:
                    new_letter += 7
            new_note = Note.from_values(new_letter,self.pitch)
        else:
            new_note = self
            new_letter = self.letter
            limit = 2 if self.pitch in Note.__NON_NATURAL else 1
            while len(new_note.note_name) > limit:
                if "#" in self.note_name:
                    new_letter += 1
                    if new_letter > 6:
                        new_letter -= 7
                else:
                    new_letter -= 1
                    if new_letter < 0:
                        new_letter += 7
                new_note = Note.from_values(new_letter,self.pitch)
            if "#" in new_note.name and prefer == "b":
                new_note = Note.from_values(new_letter + 1, self.pitch)
            elif "b" in new_note.name and prefer == "#":
                new_note = Note.from_values(new_letter - 1, self.pitch)
        new_note.octave = self.octave
        if self.rhythm:
            new_note.rhythm = self.rhythm.value
        new_note.dots = self.dots
        new_note.triplet = self.triplet
        
        return new_note

    @classmethod
    def sorter_by_hard_pitch(self,note_object):
        """
        | A function that can be used for in a sort function.
        | Cannot be used for Notes with no octave values.
        """
        if note_object.octave == None:
            raise ValueError("Can't sort Notes without octave values by hard pitch.")
        return note_object.hard_pitch
    
    def sorter_from_root(self,note_object):
        """
        | A function that can be used for in a sort function.
        | Used as a method from a specific object to act as the root.
        | Sorts notes like a scale ascending from a root.
        """
        if note_object.pitch < self.pitch:
            return note_object.pitch + 12
        return note_object.pitch


    def __add__(self,interval):
        """Add an Interval object to a Note to return the note ascended from that interval."""
        try:
            assert interval.class_name == "Interval"
        except:
            raise ValueError("__add__ method for Note requires an Interval object.")

        letter = self.letter + interval.letter_difference
        if letter > 6:
            letter -= 7

        if self.octave:
            pitch = self.hard_pitch + interval.difference
            new_note = Note.from_hard_pitch(pitch)
            if new_note.letter != letter:
                new_note = new_note.enharmonic()
        else:
            pitch = self.pitch + interval.difference
            if interval.displace > 0:
                pitch -= interval.displace * 12
            if pitch > 11:
                pitch -= 12
            new_note = Note.from_values(letter,pitch)

        if self.rhythm:
            new_note.rhythm = self.rhythm.value
        new_note.dots = self.dots
        new_note.triplet = self.triplet

        return new_note
    
    def __sub__(self,interval):
        """Subtract an Interval object to a Note to return the note descended from that interval."""
        try:
            assert interval.class_name == "Interval"
        except:
            raise ValueError("__add__ method for Note requires an Interval object.")

        letter = self.letter - interval.letter_difference
        if letter < 0:
            letter += 7

        if self.octave:
            pitch = self.hard_pitch - interval.difference
            new_note = Note.from_hard_pitch(pitch)
            if new_note.letter != letter:
                new_note = new_note.enharmonic()
        else:
            pitch = self.pitch - interval.difference
            if interval.displace > 0:
                pitch -= interval.displace * 12
            if pitch < 0:
                pitch += 12
            new_note = Note.from_values(letter,pitch)

        if self.rhythm:
            new_note.rhythm = self.rhythm.value
        new_note.dots = self.dots
        new_note.triplet = self.triplet

        return new_note
        

    @classmethod
    def from_values(self,letter,pitch):
        """Returns a Note object matching the values for 'letter' and 'pitch' given (no octave value given)."""
        if letter not in range(7):
            raise ValueError("Letter argument should be an integer between 0 and 6, 0 for C, 1 for B, etc.")
        if pitch not in range(12):
            raise ValueError("Pitch argument should be an integer between 0 and 11, 0 for C natural (or equivalent), 1 for C#/Db, etc.")
        note_values = Note.__PITCH_VALUES[letter]
        letter_str = note_values[0]
        expected_pitch = note_values[1]
        pitch_offset = pitch - expected_pitch
        if pitch_offset > 5:
            pitch_offset -= 12
        elif pitch_offset < -6:
            pitch_offset += 12
        if pitch_offset == 0:
            return Note(letter_str)
        if pitch_offset < 0:
            return Note(letter_str + "b" * (-1 * pitch_offset))
        return Note(letter_str + "#" * pitch_offset)

    @classmethod
    def from_hard_pitch(self,hard_pitch,prefer_flat=False):
        """
        | Returns a Note object (octave valued) matching a hard pitch value.
        | Hard pitch starts at 0 for C0, and increases or decreases per half step.
        | Will return a sharp note unless prefer_flat is set to True
        """
        if type(hard_pitch) is not int:
            raise ValueError("Hard pitch argument must be an integer.")
        if type(prefer_flat) is not bool:
            raise ValueError("prefer_flat must be Boolean.")
        octave = hard_pitch // 12
        pitch = hard_pitch % 12
        index = 0
        for note in Note.__PITCH_VALUES:
            if pitch == note[1]:
                return Note(note[0],octave=octave)
            if pitch == note[1] + 1:
                if prefer_flat:
                    return Note(Note.__PITCH_VALUES[index + 1][0] + "b",octave=octave)
                return Note(note[0] + "#",octave=octave)
            index += 1
    
    @classmethod
    def from_frequency(self,Hz):
        if type(Hz) is not int and type(Hz) is not float:
            raise ValueError("Please provide a positive number for the Hz value.")
        if Hz <= 0:
            raise ValueError("Please provide a positive number for the Hz value.")
        return Note.from_hard_pitch(int(round(12 * (log2(Hz) - log2(get_A4()))) + 57))
    
class Interval(_Meta):

    class_name = "Interval"

    """
    | Use this class to create Interval objects, or take advantage of its class methods.
    | 
    | For the 'quality', use "maj"(major), "min"(minor), "per"(perfect), "aug"(augmented), or "dim"(diminished).
    | 
    | For the 'base', use "uni"(unison),"2nd","3rd","4th", and so on up to "7th."
    | 
    | Set 'displace' to a number to displace an interval by a number of octaves.
    | For example, a unison that is displaced by 1 is the same as a perfect octave.
    """

    class_name = "Interval"

    BASES = ("uni", "2nd", "3rd", "4th", "5th", "6th", "7th")

    __BASE_INTERVALS = {
        "uni": (0,),
        "2nd": (1,2),
        "3rd": (3,4),
        "4th": (5,),
        "5th": (7,),
        "6th": (8,9),
        "7th": (10,11),
    }

    __M_QUAL = ("2nd","3rd","6th","7th")

    __QUALITY_REGEX = r'(maj|min|per)$|(aug|dim)[\d]*$'

    __base_err = "Base interval must be a valid string. (see Interval.BASES)"
    __quality_err = "Quality must be 'maj','min','per','aug', or 'dim'.\n Augmented and diminished intervals may be increased by adding an integer, such as 'aug2' for doubly augmented."
    __base_qual_err1 = "2nd/3rd/6th/7th cannot be perfect."
    __base_qual_err2 = "uni/4th/5th cannot be major or minor."
    __dis_err = "Displacement of octave must be a positive integer."

    def __init__(self,quality,base,displace=0):

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
        if type(displace) is not int:
            raise ValueError(Interval.__dis_err)
        if displace < 0:
            raise ValueError(Interval.__dis_err)
        
        self.__quality = quality
        self.__base = base
        self.__displace = displace

        self._lock()

    @property
    def quality(self):
        """The quality given for the interval (str)"""
        return self.__quality

    @property
    def base(self):
        """The base interval given for the interval (str)"""
        return self.__base
    
    @property
    def displace(self):
        """The given number of octaves displaced (int)"""
        return self.__displace

    @property
    def difference(self):
        """Returns the difference in pitch of the interval measured in half steps (int)"""
        if self.quality == "per" or self.quality == "min":
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
                return Interval.__BASE_INTERVALS[self.base][0] + more + 12 * self.displace
        elif self.quality[:3] == "dim":
            if len(self.quality) > 3:
                less = int(self.quality[3:]) if self.quality[3:] != "0" else 1
            else:
                less = 1
            return Interval.__BASE_INTERVALS[self.base][0] - less + 12 * self.displace
    
    @property
    def letter_difference(self):
        """The number of note letter degrees changed by the interval."""
        return Interval.BASES.index(self.base)


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

        if not note_obj1.octave or not note_obj2.octave:
            raise ValueError("Interval cannot be determined for Notes with no octave values, unless 'simple' parameter is set.")
        
        if note_obj2.hard_pitch > note_obj1.hard_pitch:
            higher = note_obj2
            lower = note_obj1
        else:
            higher = note_obj1
            lower = note_obj2

        letter_diff = higher.letter - lower.letter
        pitch_diff = higher.hard_pitch - lower.hard_pitch

        base = Interval.BASES[letter_diff]
        expect = Interval.__BASE_INTERVALS[base]

        displace = pitch_diff // 12
        pitch_diff %= 12

        if pitch_diff in expect:
            if len(expect) == 2:
                if pitch_diff == expect[0]:
                    quality = "min"
                elif pitch_diff == expect[1]:
                    quality = "maj"
            else:
                if pitch_diff == expect[0]:
                    quality = "per"
        else:
            if len(expect) == 2 and pitch_diff > expect[1]:
                aug = True
                offset = pitch_diff - expect[1]
            else:
                aug = True if pitch_diff > expect[0] else False
                offset = pitch_diff - expect[0] if aug else expect[0] - pitch_diff
            if offset == 1:
                quality = "aug" if aug else "dim"
            else:
                quality = f"aug{offset}" if aug else f"dim{offset}"
        
        return Interval(quality,base,displace=displace)

MODES = {
    "ionian": (2,2,1,2,2,2,1),
    "major": "ionian1",
    "dorian": "ionian2",
    "phrygian": "ionian3",
    "lydian": "ionian4",
    "mixolydian": "ionian5",
    "aeolian": "ionian6",
    "minor": "ionian6",
    "locrian": "ionian7",
    "major pentatonic": (2,2,3,2,3),
    "minor pentatonic": "major pentatonic5",
    "major blues": (2,1,1,3,2,3),
    "minor blues": "major blues6",
    "blues": "major blues6",
    "harmonic minor": (2,1,2,2,1,3),
    "melodic minor": (2,1,2,2,2,2,1),
    "dorian flat 2": "melodic minor2",
    "lydian sharp 5": "melodic minor3",
    "lydian dominant": "melodic minor4",
    "mixolydian flat 6": "melodic minor5",
    "locrian sharp 2": "melodic minor6",
    "super locrian": "melodic minor7",
    "altered": "melodic minor7",
    "chromatic": (1,1,1,1,1,1,1,1,1,1,1),
    "whole tone": (2,2,2,2,2),
    "whole-half diminished": (2,1,2,1,2,1,2,1),
    "half-whole diminished": (1,2,1,2,1,2,1,2),
    "whole-half octatonic": "whole-half diminished1",
    "half-whole octatonic": "half-whole diminished1",
    "augmented": (3,1,3,1,3,1),
}

MODE_LETTER_SPELLINGS = {
    "ionian": (1,1,1,1,1,1,1),
    "major pentatonic": (1,1,2,1,2),
    "major blues": (1,0,1,2,1,2),
    "harmonic minor": (1,1,1,1,1,1,1),
    "melodic minor": (1,1,1,1,1,1,1),
    "augmented": (2,0,2,0,2,1),
}

class Mode(_Meta):

    class_name = "Mode"

    """
    | Create a Mode
    | Use a Note object for the 'root' and a string for the 'mode'.
    | Check the MODES dictionary.  The keys are built-in mode names.
    | You can add a mode to the MODES dictionary by using its name for a key and a tuple of integers for step-lengths for its spelling.
    | It is generally encouraged to add a letter spelling for a new mode to MODE_LETTER_SPELLINGS with the same name as a key.
    | Use a tuple of integers that describes how many alphabetical letters increase for each scale degree.
    """

    def __init__(self,root,mode):

        try:
            assert root.class_name == "Note"
        except:
            raise ValueError("Root of a Mode must be a Note object.")
        if mode not in MODES:
            raise KeyError("Mode not found.  View the MODES dictionary to see/add modes.")

        self.root = root
        self.mode = mode

        self._lock()
    
    @property
    def name(self):
        """Returns a string describing the Mode"""
        return self.root.note_name + " " + self.mode
    
    @property
    def spelling(self):
        """A tuple of Note objects that spell the Mode"""
        spelling = [self.root]

        if type(MODES[self.mode]) is str:
            parent_name = MODES[self.mode][:len(MODES[self.mode])-1]
            offset = int(MODES[self.mode][-1]) - 1
        elif type(MODES[self.mode]) is tuple:
            parent_name = self.mode
            offset = 0
        else:
            raise ValueError("Invalid Mode pattern. (Check MODES dictionary)")
        parent = MODES[parent_name]
        for item in parent:
            if type(item) is not int:
                raise ValueError("Invalid Mode pattern. (Check MODES dictionary)")
        
        next_pitch = self.root.pitch
        next_letter = self.root.letter
        index = offset
        n = 1
        if parent_name in MODE_LETTER_SPELLINGS:
            for step in parent:
                if index == len(parent):
                    index -= len(parent)
                if n == len(parent):
                    break
                next_pitch += parent[index]
                next_letter += MODE_LETTER_SPELLINGS[parent_name][index]
                if next_pitch < 0:
                    next_pitch += 12
                elif next_pitch > 11:
                    next_pitch -= 12
                if next_letter < 0:
                    next_letter += 7
                elif next_letter > 6:
                    next_letter -= 7
                spelling.append(Note.from_values(next_letter,next_pitch))
                index += 1
                n += 1
        else:
            flats = False if "b" not in self.root.note_name else True
            sharps = False if "#" not in self.root.note_name else True
            for step in parent:
                if index == len(parent):
                    index -= len(parent)
                if n == len(parent):
                    break
                next_pitch += parent[index]
                next_letter += 1
                if next_pitch < 0:
                    next_pitch += 12
                elif next_pitch > 11:
                    next_pitch -= 12
                if next_letter < 0:
                    next_letter += 7
                elif next_letter > 6:
                    next_letter -= 7
                next_note = Note.from_values(next_letter,next_pitch)
                if len(next_note.note_name) > 2:
                    next_note = next_note.enharmonic()
                if next_note.note_name in ("B#","Cb","E#","Fb"):
                    next_note = next_note.enharmonic()
                if "#" in next_note.note_name:
                    if flats:
                        next_note = next_note.enharmonic()
                    if not flats and not sharps:
                        sharps = True
                if "b" in next_note.note_name:
                    if sharps:
                        next_note = next_note.enharmonic()
                    if not flats and not sharps:
                        flats = True
                index += 1
                n += 1
                spelling.append(next_note)
                
        return tuple(spelling)
    
    @property
    def string_spelling(self):
        """A tuple of note names as strings"""
        string_spelling = []

        for note in self.spelling:
            string_spelling.append(note.note_name)
        
        return tuple(string_spelling)

EXTENSIONS = {
    "b9": ("min","2nd"),
    "addb9": ("min","2nd"),
    "2": ("maj","2nd"),
    "9": ("maj","2nd"),
    "add9": ("maj","2nd"),
    "#9": ("aug","2nd"),
    "add4": ("per","4th"),
    "add11": ("per","4th"),
    "#11": ("aug","4th"),
    "b5": ("dim","5th"),
    "#5": ("aug","5th"),
    "b6": ("min","6th"),
    "b13": ("min","6th"),
    "6": ("maj","6th"),
    "13": ("maj","6th"),
    "dim7": ("dim","7th"),
    "7": ("min","7th"),
    "maj7": ("maj","7th"),
}

QUALITIES = (
    "maj",
    "min",
    "aug",
    "dim",
    "sus",
    "5",
)

class Chord(_Meta):

    """
    | Create a Chord from a root Note, quality, and extensions.
    | Pass extensions (str) as args.  Check out EXTENSIONS's keys for valid input.
    | For 'quality', use 'maj','min','aug','dim','sus',or '5'.
    | Keep in mind that some extensions imply and automatically add others (like '13').
    | Uncommon, strange, repetitious, or ridiculous combinations of extensions might not work as expected.
    """

    def __init__(self,root,quality,*extensions):

        try:
            assert root.class_name == "Note"
        except:
            raise ValueError("Root of a Chord must be a Note object.")
        if quality not in QUALITIES:
            raise ValueError("Invalid chord quality. (use 'maj','min','aug','dim','sus',or'5')")
        for extension in extensions:
            if extension not in EXTENSIONS:
                raise ValueError("Invalid extension.  See EXTENSIONS dictionary.")
        
        self._root = root
        self._quality = quality
        self._extensions = extensions
        notes = [root]
        dictionary = {}

        if self.quality == "maj":
            third = Interval("maj","3rd")
            fifth = Interval("per","5th")
        elif self.quality == "min":
            third = Interval("min","3rd")
            fifth = Interval("per","5th")
        elif self.quality == "aug":
            third = Interval("maj","3rd")
            fifth = Interval("aug","5th")
        elif self.quality == "dim":
            third = Interval("min","3rd")
            fifth = Interval("dim","5th")
        elif self.quality == "sus":
            third = Interval("per","4th")
            fifth = Interval("per","5th")
        else:
            third = None
            fifth = Interval("per","5th")
        if third:
            dictionary["third"] = third
        dictionary["fifth"] = fifth

        need7 = False
        need9 = False
        for ext13 in ("13","b13"):
            if ext13 in extensions:
                dictionary["13th"] = Interval(*EXTENSIONS[ext13])
                need7 = True
                need9 = True
                break
        for ext9 in ("9","#9","b9"):
            if ext9 in extensions:
                dictionary["9th"] = Interval(*EXTENSIONS[ext9])
                need7 = True
                need9 = False
                break
        else:
            if need9:
                dictionary["9th"] = Interval("maj","2nd")

        for ext7 in ("7","maj7","dim7"):
            if ext7 in extensions:
                dictionary["7th"] = Interval(*EXTENSIONS[ext7])
                need7 = False
                break
        else:
            if need7:
                if quality == "dim":
                    dictionary["7th"] = Interval("maj","6th")
                else:
                    dictionary["7th"] = Interval("min","7th")
        for ext2 in ("2","addb9","add9"):
            if ext2 in extensions:
                dictionary["2nd"] = Interval(*EXTENSIONS[ext2])
                break
        
        for ext5 in ("b5","#5"):
            if ext5 in extensions:
                dictionary["fifth"] = Interval(*EXTENSIONS[ext5])

        for ext in ("addb9","add9","2","add4","#11","b6","6"):
            if ext in extensions:
                dictionary[ext] = Interval(*EXTENSIONS[ext])
        

        for intvl in dictionary:
            note = root + dictionary[intvl]
            notes.append(note)
        

        notes.sort(key=root.sorter_from_root)
        previous_note = root
        first = True
        for note in notes:
            if first:
                first = False
                continue
            if previous_note.pitch == note.pitch:
                notes.remove(note)
            previous_note = note
        
        self._dictionary = dictionary
        self._notes = tuple(notes)
        self._lock()
    
    @property
    def root(self):
        """The Note that was given as the root."""
        return self._root
    
    @property
    def quality(self):
        """The quality that was given at initialization."""
        return self._quality
    
    @property
    def extensions(self):
        """The extensions given at initialization."""
        return self._extensions

    @property
    def dictionary(self):
        """A dictionary of chord tones and their respective Interval objects."""
        return self._dictionary
    
    @property
    def notes(self):
        """A tuple containing all the Note objects of the Chord."""
        return self._notes
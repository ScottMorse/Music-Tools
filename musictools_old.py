from numpy import power, log2
import re as _re
import threading as _threading
import time as _time

"""
MusicTools offers a variety of music-related functions that can be used in things such as notation software or music-theory related software.
The goal has been to create classes and functions that reflects the manner in which an expert in written music thinks of music theory,
so it can be intuitively utilized by a studied musician.  A single Note as an object potentially contains a wealth of data found in its
properties.  There is a heirarchy to some of the classes that have to do with sheet music.  A Piece is like a container for Staff objects,
which contains Measure objects, which can contain Note objects.
"""

_A4 = 440

def setA4(frequency):
    global _A4
    _A4 = frequency

_LETTERS = {"C":(0,0),"D":(1,2),"E":(2,4),"F":(3,5),"G":(4,7),"A":(5,9),"B":(6,11)}

_LETTER_IND = ("A","B","C","D","E","F","G")

_RHYTHMS = ("double whole","whole","quarter","8th","16th","32nd","64th","128th","256th","512th")

_NATURALS = {"B":"Cb","C":"B#","E":"Fb","F":"E#"}

_GROSS = ("B#","Cb","E#","Fb")

_INTVL_REGEX = r"(perfect|major|minor|((augmented|diminished)(\(x\d\))?)) (unison|2nd|3rd|4th|5th|6th|7th)"

_DIFFERENCES = {
    "unison": (0,0),
    "2nd": (1,1),
    "3rd": (2,3),
    "4th": (3,5),
    "5th": (4,7),
    "6th": (5,8),
    "7th": (6,10)
}

class Note:

    """
    name: a string representing the note name "A","Db","G#","Ebb",etc. or "R" for rest

    octave: any integer, 4 representing the "middle" octave, as is common practice

    rhythm: an integer between 0 and 10, 0 representing a double whole note, 1 for a whole, 2 for quarter, and so on up to 10 for a 512th note.
    
    dot: a positive integer that 'dots' any rhythm
    
    triplet: when set to True, makes the rhythm a triplet
    
    Other attributes on initialization:
        self.full_name: a string giving a full description of the note
        self.letter: A letter representing a note's letter, 0 for A up to 6 for G
        self.rhy_val: A number representing a rhythm's relative length, measured in 512th notes
    """
    
    _REGEX = r"#+$|b+$"

    def __init__(self,name,octave=None,rhythm=None,dots=0,triplet=False):

        if name != str(name):
            raise ValueError("Note name must be a string.")
        self.name = name.capitalize()
        if self.name[0] not in _LETTERS and self.name != "R":
            raise ValueError("Note name must use a letter from A to G or be set as 'R' for a rest.")
        try:
            assert dots > -1
        except:
            raise ValueError("Dot value must be a positive integer")
        try:
            assert triplet == bool(triplet)
        except:
            raise ValueError("Triplet value must be Boolean.")
        self._octave = octave
        self._rhythm = rhythm
        if self._rhythm:
            if rhythm not in range(11):
                raise ValueError("Rhythm value must be an integer between 0 and 10.")
        self._dots = dots
        self._triplet = triplet
        if self.name == "R":
            self.name = "Rest"
            self._octave = None
            self.letter = None
        else:
            if len(self.name) > 1:
                check = _re.match(Note._REGEX,self.name[1:])
                if not check:
                    raise ValueError("Invalid note name.")
            self.letter = _LETTERS[self.name[0]][0]
    
    @property
    def pitch(self):
        if self.name.startswith("R"):
            return None
        _pitch = _LETTERS[self.name[0]][1]
        if len(self.name) == 1:
            return _pitch
        else:
            if self.name[1] == "#":
                _sharps = len(self.name) - 1
                _pitch += _sharps
                if _pitch > 11:
                    _pitch -= 12
            else:
                _flats = len(self.name) - 1
                _pitch -= _flats
                if _pitch < 0:
                    _pitch += 12
            return _pitch
    
    @property
    def octave(self):
        return self._octave

    @octave.setter
    def octave(self,value):
        self._octave = value

    @property
    def dots(self):
        return self._dots
    
    @dots.setter
    def dots(self,value):
        self._dots = value

    @property
    def triplet(self):
        return self._triplet

    @triplet.setter
    def triplet(self,value):
        self._triplet = value

    @property
    def rhythm(self):
        if not self._rhythm:
            return None
        if self._rhythm not in range(11):
            raise ValueError("Rhythm value must be an integer between 0 and 10.")
        rhy_val = 1024 / (power(2,self._rhythm))
        name = ""
        if self.dots:
            orig_value = rhy_val
            for i in range(self.dots):
                rhy_val += (orig_value/(power(2,i + 1)))
            if self.dots == 1:
                name = "dotted "
            elif self.dots > 1:
                name += f"dotted(x{self.dots}) "
        name += _RHYTHMS[self._rhythm]
        if self.triplet:
            rhy_val *= (2/3)
            name += " triplet"
        return type('rhythm',(object,),{'value':rhy_val,'name':name,'num':self._rhythm})

    @rhythm.setter
    def rhythm(self,value):
        self._rhythm = value
    
    @property
    def full_name(self):
        full_name = self.name
        if self.octave:
            full_name += str(self.octave)
        if self.rhythm:
            full_name += " " + self.rhythm.name
        return full_name

    @property
    def hard_pitch(self):
        """
        The hard pitch takes into account the octave value in order to give an integer that allows for the comparing of pitch between notes of specific octaves.
        """
        if self.octave != None:
            return self.pitch + 12 * self.octave
        else:
            raise AttributeError("A Note object must be pitched and have an octave value in order to use the hard_pitch property.")
    
    @property
    def sharps(self):
        """
        Returns number of sharps in the note
        """
        if len(self.name) == 1:
            return 0
        elif "#" in self.name:
            return len(self.name) - 1
        else:
            return 0
    
    @property
    def flats(self):
        """
        Returns the number of flats in the note
        """
        if len(self.name) == 1:
            return 0
        elif "b" in self.name:
            return len(self.name) - 1
        else:
            return 0
    
    @property
    def pitch_position(self):
        """
        Returns the number of half steps a note is offset from its natural note.
        """
        if self.sharps > 0:
            return self.sharps
        elif self.flats > 0:
            return -self.flats
        else:
            return 0
        
    #!WRONG SAD CHANGE FREQUENCY
    @property
    def frequency(self):
        global _A4
        if self.octave == None:
            raise AttributeError('Frequency value cannot be determined without an octave value for a Note')
        offset = self.hard_pitch - 56
        return _A4 * power(2,(offset/12))

    def __add__(self, other):
        """
        Add two Notes to return an ascending Interval instance.
        """
        return Interval(self,other)

    def __sub__(self, other):
        """
        Subtract two Notes to return a descending Interval instance.
        """
        return Interval(self,other,descending=True)

A4 = Note("A",octave=4)



def get_note(pitch,letter):
    if pitch not in range(12):
        raise ValueError("Pitch must be an integer between 0 and 11.")
    if letter not in range(7):
        raise ValueError("Letter value must be an integer between 0 and 6")
    
    letter_name = _LETTER_IND[letter]
    base_pitch = _LETTERS[letter_name][1]

    if pitch == base_pitch:
        return Note(letter_name)
    else:
        if pitch > base_pitch:
            difference = pitch - base_pitch
            over_length = bool(difference > 6)
            suffix = "#" if not over_length else "b"
        else:
            difference = base_pitch - pitch
            over_length = bool(difference > 6)
            suffix = "b" if not over_length else "#"
        if over_length:
            suffix_num = 12 - difference
        else:
            suffix_num = difference
        
        return Note(letter_name + suffix * suffix_num)

def get_hard_note(hard_pitch,pref_sharp=True):
    """
    Give a hard pitch of a note (integer) that represents a note's specific octave-sensitive pitch (different from frequency, see the Note hard_pitch property)
    """
    octave_level = hard_pitch // 12
    offset = hard_pitch % 12
    if pref_sharp:
        hard_note = enharmonic(get_note(offset,5),prefer_sharp=True)
    else:
        hard_note = enharmonic(get_note(offset,5),prefer_flat=True)
    hard_note.octave = octave_level
    return hard_note

def enharmonic(note_obj,gross_notes=False,prefer_sharp=False,prefer_flat=False):
    """
    Give a Note object and receive an enharmonic equivalent.  
    
    Will not return any notes with more than one sharp or flat and will simplify any multi-sharp or flat note into a note with one or zero sharps or flats.  
    
    gross_notes will tolerate B#,Cb,E#, and Fb.

    prefer_sharp will return a sharp note if a note is not natural, and similarly prefer_flat will return a flat.
    """


    if len(note_obj.name) == 1:
        if gross_notes:
            if note_obj.name in _NATURALS:
                new_note = _NATURALS[note_obj.name]
                return new_note
        else:
            new_note = note_obj.name
    else:
        if "#" in note_obj.name:
            new_letter = note_obj.letter + 1
            if new_letter > 6:
                new_letter -= 7
        else:
            new_letter = note_obj.letter - 1
            if new_letter < 0:
                new_letter += 7
        
        new_note = get_note(note_obj.pitch,new_letter)
        
        if len(new_note.name) > 2:
            new_note = enharmonic(new_note)
        if not gross_notes:
            if new_note in _GROSS:
                new_note = enharmonic(new_note)
        if "#" in new_note.name and prefer_flat:
            new_note = enharmonic(new_note)
        if "b" in new_note.name and prefer_sharp:
            new_note = enharmonic(new_note)
        
        if note_obj.rhythm:
            new_note.rhythm = note_obj.rhythm.num
        new_note.dots = note_obj.dots
        new_note.triplet = note_obj.triplet
        new_note.octave = note_obj.octave

    return new_note

class Interval:
    
    """
    You can create an Interval by adding or subtracting two Note objects (Note class magic methods).
    
    An Interval needs the difference in pitch and difference in letter between two Notes, and whether the interval is descending and whether octave needs to be taken into consideration.

    The simple_interval property returns an interval name that disregards the Notes' letters, which is useful when enharmonics aren't important.

    The strict_interval property returns the strict name of the interval, based on the letter and pitch change.
    """
    
    _SIMPLE_INTERVAL_NAMES = {
        0: "perfect unison",
        1: "minor 2nd",
        2: "major 2nd",
        3: "minor 3rd",
        4: "major 3rd",
        5: "perfect 4th",
        6: "tritone",
        7: "perfect 5th",
        8: "minor 6th",
        9: "major 6th",
        10: "minor 7th",
        11: "major 7th",
    }

    _BASE_LETTER_CHANGES = {
        0:"unison",
        1:"2nd",
        2:"3rd",
        3:"4th",
        4:"5th",
        5:"6th",
        6:"7th",
    }

    _REPLACEMENTS = {
        "unison": "octave",
        "2nd": "9th",
        "3rd": "10th",
        "4th": "11th",
        "5th": "12th",
        "6th": "13th",
        "7th": "14th",
    }

    def __init__(self,note_obj_1,note_obj_2,descending=False):
        self.note1 = note_obj_1
        self.note2 = note_obj_2
        if descending:
            pitch_diff = note_obj_1.pitch - note_obj_2.pitch
            letter_diff = note_obj_1.letter - note_obj_2.letter
        else:
            pitch_diff = note_obj_2.pitch - note_obj_1.pitch
            letter_diff = note_obj_2.letter - note_obj_1.letter
        if pitch_diff > 11:
            pitch_diff -= 12
        if pitch_diff < 0:
            pitch_diff += 12
        if letter_diff > 6:
            letter_diff -= 7
        if letter_diff < 0:
            letter_diff += 7
        self.pitch_diff = pitch_diff
        self.letter_diff = letter_diff
        self.descending = descending
    
    @property
    def simple_interval(self):
        return Interval._SIMPLE_INTERVAL_NAMES[self.pitch_diff]
    
    @property
    def strict_interval(self):
        base_interval = Interval._BASE_LETTER_CHANGES[self.letter_diff]
        if base_interval == "unison":
            if self.pitch_diff == 0:
                interval_name = "perfect unison"
                return interval_name
            times = ""
            if self.pitch_diff > 0 and self.pitch_diff < 7:
                interval_type = "unison"
                if self.descending == True:
                    quality = "diminished"
                else:
                    quality = "augmented"
            else:
                quality = "diminished"
                interval_type = "octave"
            if self.pitch_diff > 1 and self.pitch_diff < 11:
                num = self.pitch_diff
                if num > 6 and num < 11:
                    num = abs(num - 12)
                times = "(x{})".format(str(num))
            interval_name = quality + times + " " + interval_type
            return interval_name

        maj_quals = ["2nd","3rd","6th","7th"]
        per_quals = ["4th","5th"]

        rng2nd = [1,2]
        ex2nd = bool(self.pitch_diff in rng2nd)
        rng3rd = [3,4]
        ex3rd = bool(self.pitch_diff in rng3rd)
        rng4th = 5
        ex4th = bool(self.pitch_diff == rng4th)
        rng5th = 7
        ex5th = bool(self.pitch_diff == rng5th)
        rng6th = [8,9]
        ex6th = bool(self.pitch_diff in rng6th)
        rng7th = [10,11]
        ex7th = bool(self.pitch_diff in rng7th)
        expecteds = {"2nd":(ex2nd,rng2nd),"3rd":(ex3rd,rng3rd),"4th":(ex4th,rng4th),"5th":(ex5th,rng5th),"6th":(ex6th,rng6th),"7th":(ex7th,rng7th)}

        #this defines a string of the final name of the interval_name using common practice music theory
        major = [2,4,9,11]
        minor = [1,3,8,10]

        isexpected = bool(expecteds[base_interval][0] == True)
        range_ = expecteds[base_interval][1]

        if base_interval in maj_quals:
            if isexpected:
                if self.pitch_diff in major:
                    interval_name = "major " + base_interval
                if self.pitch_diff in minor:
                    interval_name = "minor " + base_interval
        if base_interval in per_quals:
            if isexpected:
                interval_name = "perfect " + base_interval
        if not isexpected:
            times = ""
            if self.pitch_diff < range_[0]:
                diff = range_[0] - self.pitch_diff
                if diff > 6:
                    diff = 11 - diff
                    adj = "augmented"
                else:
                    adj = "diminished"
            if self.pitch_diff > range_[1]:
                diff = self.pitch_diff - range_[1]
                if diff > 6:
                    diff = 11 - diff
                    adj = "diminished"
                else:
                    adj = "augmented"
            if diff > 1:
                times = "("+str(diff)+"x)"
            interval_name = adj + times + " "+ base_interval
        return interval_name
    
    @property
    def hard_interval(self):
        """
        A hard interval is an octave-sensitive interval.

        An octave-sensitive interval does not use the descending parameter, since the exact pitches determine which note is higher already.
        
        Some special cases may not result as strictly as possible for less practical octave displaced intervals, like a diminished 9th, which will simply return "octave."
        """
        if not (self.note1.hard_pitch and self.note2.hard_pitch):
            raise NotImplementedError("Both Note objects must have octave values to use a hard_interval property")
        if self.note1.hard_pitch > self.note2.hard_pitch:
            higher_note = self.note1
            lower_note = self.note2
        elif self.note1.hard_pitch == self.note2.hard_pitch:
            return "perfect unison"
        else:
            higher_note = self.note2
            lower_note = self.note1
        hard_difference = higher_note.hard_pitch - lower_note.hard_pitch
        if hard_difference < 12:
            return self.strict_interval
        if hard_difference == 12:
            return "octave"
        strct_intvl = Interval(lower_note,higher_note).strict_interval
        octaves_displaced = hard_difference // 12
        
        remainder = hard_difference % 12
        if octaves_displaced == 1:
            for strng in Interval._REPLACEMENTS:
                if strng in strct_intvl:
                    return strct_intvl.replace(strng,Interval._REPLACEMENTS[strng])
        else:
            if remainder == 0:
                return f"octave x{octaves_displaced}"
            return strct_intvl + f" + {octaves_displaced} octaves"

def note_from_interval(note_obj,intvl_name,descending=False):
    """
    Denote the interval quantities other than unison/octave with '2nd','3rd','4th',etc.
    
    Denote doubly/beyond augumented diminished qualitys by putting '(x2)','(x3)', etc. immediately following the quality.

    Octave displacements not currently supported.

    Examples: "major 3rd", "perfect unison", "augmented(x2) unison", "diminished 5th", "diminished(x3) 2nd"
    """
    if not _re.match(_INTVL_REGEX,intvl_name):
        raise ValueError("Invalid interval name")
    m_named = bool("major" in intvl_name or "minor" in intvl_name)
    p_qual = bool("unison" in intvl_name or "4th" in intvl_name or "5th" in intvl_name)
    if m_named and p_qual:
        raise ValueError("Invalid interval name")
    m_qual = not p_qual
    for name in _DIFFERENCES:
        if name in intvl_name:
            base_intvl = name
    letter_change = _DIFFERENCES[base_intvl][0]
    pitch_change = _DIFFERENCES[base_intvl][1]
    if m_qual:
        if "major" in intvl_name:
            pitch_change += 1
        elif "augmented " in intvl_name:
            pitch_change += 2
        elif "diminished " in intvl_name:
            pitch_change -= 1
        elif "augmented(" in intvl_name:
            pitch_change += 2 + int(intvl_name[10]) - 1
        elif "diminished(" in intvl_name:
            pitch_change -= 1 + int(intvl_name[11]) - 1
    else:
        if "augmented " in intvl_name:
            pitch_change += 1
        elif "diminished " in intvl_name:
            pitch_change -= 1
        elif "augmented(" in intvl_name:
            pitch_change += 1 + int(intvl_name[10]) - 1
        elif "diminished(" in intvl_name:
            pitch_change -= 1 + int(intvl_name[11]) - 1
    if descending:
        letter_change = -letter_change
        pitch_change = -pitch_change
    new_pitch = note_obj.pitch + pitch_change
    new_letter = note_obj.letter + letter_change
    if new_pitch > 11:
        new_pitch -= 12
    elif new_pitch < 0:
        new_pitch += 12
    if new_letter > 6:
        new_letter -= 7
    elif new_letter < 0:
        new_letter += 7
    return get_note(new_pitch,new_letter)

class Mode:
    
    """
    Initialize a mode with a note name(str) and a supported mode quality (str) such as "major" or "dorian".
    Mode qualities currently supported can be seen by viewing musictools.Mode._SUPPORTED_QUALITIES.
    If 
    """
    _SUPPORTED_QUALITIES = {
        "major": "diatonic",
        "ionian": "diatonic",
        "minor": "diatonic",
        "dorian": "diatonic",
        "phrygian": "diatonic",
        "lydian": "diatonic",
        "mixolydian": "diatonic",
        "aeolian": "diatonic",
        "locrian": "diatonic",
        "harmonic minor": "harmonic minor",
        "melodic minor": "melodic minor",
        "dorian flat 2": "melodic minor",
        "lydian sharp 5": "melodic minor",
        "lydian dominant": "melodic minor",
        "mixolydian flat 6": "melodic minor",
        "locrian natural 2": "melodic minor",
        "super locrian": "melodic minor",
        "altered": "melodic minor",
        "major pentatonic": "pentatonic",
        "minor pentatonic": "pentatonic",
        "major blues": "blues",
        "minor blues": "blues",
        "blues": "blues",
        "chromatic": "chromatic",
        "augmented": "augmented",
    }

    _DIATONIC_OFFSETS = {
        "major": 0,
        "ionian": 0,
        "dorian": 1,
        "phrygian": 2,
        "lydian": 3,
        "mixolydian": 4,
        "aeolian": 5,
        "minor": 5,
        "locrian": 6,
    }

    _MELODIC_MINOR_OFFSETS = {
        "melodic minor": 0,
        "dorian flat 2": 1,
        "lydian sharp 5": 2,
        "lydian dominant": 3,
        "mixolydian flat 6": 4,
        "locrian natural 2": 5,
        "super locrian": 6,
        "altered": 6,
    }

    _PENTATONIC_OFFSETS = {
        "major pentatonic": 0,
        "minor pentatonic": 4,
    }

    _BLUES_OFFSETS = {
        "major blues": 0,
        "minor blues": 5,
        "blues": 5,
    }

    #note for future mode types: the last step that goes up to the root must be included


    _OFFSETTER_MATCHER = {
        "diatonic": _DIATONIC_OFFSETS,
        "melodic minor": _MELODIC_MINOR_OFFSETS,
        "pentatonic": _PENTATONIC_OFFSETS,
        "blues": _BLUES_OFFSETS,
    }

    #note for future mode types: the last step that goes up to the root must be included
    _SCALE_STEPS = {
        "diatonic": (2,2,1,2,2,2,1),
        "harmonic minor": (2,1,2,2,1,3,1),
        "melodic minor": (2,1,2,2,2,2,1),
        "pentatonic": (2,2,3,2,3),
        "blues": (2,1,1,3,2,3),
        "chromatic":(1,1,1,1,1,1,1,1,1,1,1,1),
        "augmented":(3,1,3,1,3,1)
    }

    def __init__(self,root,quality):
        try:
            root = root.capitalize()
            root = Note(root)
        except:
            raise ValueError("Invalid note given for Mode's root argument")
        try:
            quality = quality.lower()
            assert quality in Mode._SUPPORTED_QUALITIES
        except:
            raise ValueError("Unsupported mode-quality argument given")
        
        self.root = root
        self.quality = quality
    
    @property
    def name(self):
        return self.root + " " + self.quality
    
    @property
    def spelling(self):
        """
        Returns a list of note names as strings present in the mode
        """
        root_object = self.root
        mode_type = Mode._SUPPORTED_QUALITIES[self.quality]
        mode_speller = Mode._SCALE_STEPS[mode_type]
        if mode_type in Mode._OFFSETTER_MATCHER:
            offset = Mode._OFFSETTER_MATCHER[mode_type][self.quality]
        else:
            offset = 0

        scale = [root_object]

        next_pitch = root_object.pitch
        next_letter = root_object.letter
        mode_length = len(mode_speller)
        heptatonic = False
        previous_letter = None
        previous_step = None
        if mode_length == 7:
            heptatonic = True
        for i in range(mode_length - 1):
            #just wanted VS to shut up about me not using i
            i = i
            step = mode_speller[offset]
            offset += 1
            if offset > (mode_length - 1):
                offset -= mode_length
            next_pitch += step
            if heptatonic:
                next_letter += 1
            else:
                if step > 2:
                    next_letter += 2
                else:
                    next_letter += 1
            if next_pitch > 11:
                next_pitch -= 12
            if next_letter > 6:
                next_letter -= 7
            if step == 1 and previous_step == 1:
                next_letter = previous_letter
                if len(get_note(next_pitch,next_letter)) > 2:
                    next_letter += 1
                    if next_letter > 6:
                        next_letter -= 7
            next_note = get_note(next_pitch,next_letter)
            if mode_type == "augmented":
                if "b" in self.root:
                    next_note = enharmonic(next_note,prefer_flat=True)
                else:
                    next_note = enharmonic(next_note,prefer_sharp=True)
            if mode_type == "chromatic":
                next_note = enharmonic(next_note,prefer_sharp=True)
            scale.append(next_note)
            previous_letter = next_letter
            previous_step = step
        return scale

    @property
    def chord_scale(self):
        """
        Gives most accurate results with diatonic modes.
        """
        chord_scale = []
        i = 0
        for note in self.spelling:
            sec_index = i + 2
            thi_index = i + 4
            if sec_index >= len(self.spelling):
                sec_index -= len(self.spelling)
            if thi_index >= len(self.spelling):
                thi_index -= len(self.spelling)
            third = self.spelling[sec_index].name
            fifth = self.spelling[thi_index].name
            chord_scale.append(Chord(note.name,third,fifth))
            return Chord(note.name,self)

    def __len__(self):
        return len(self.spelling)

    def __iter__(self):
        return iter(self.spelling)
    
    def __getitem__(self,index):
        return self.spelling[index]

class Chord:
    """
    This takes note names (strings, not Note objects) as individual arguments and defines a chord
    from them.  root can be set, or the first argument given will be the root,
    and the bass argument writes the chord symbol as an inversion.
    The description property contains information about the chord, which is also
    used to create its symbol property, which attempts to create an appropriate
    chord symbol as would be seen on a jazz-style lead sheet.
    """
    def __init__(self,*notes,root=None,bass=None,):
        if notes[0] == tuple(notes[0]):
            spread = []
            for note in notes[0]:
                spread.append(note)
            notes = tuple(spread)
        if root:
            if root not in notes:
                spread = []
                spread.append(root)
                for note in notes:
                    spread.append(note)
                notes = tuple(spread)
            self.root = root
            self.notes = notes
        else:
            self.notes = notes
            self.root = self.notes[0]
        self.bass = bass

    def __len__(self):
        return len(self.notes)

    @property
    def sorted_notes(self):
        """
        The notes in ascending order from the root
        """
        keyed_notes = {}
        keys = []
        sorted_notes = []
        root_pitch = Note(self.root).pitch
        for note in self.notes:
            relative_pitch = Note(note).pitch - root_pitch
            if relative_pitch < 0:
                relative_pitch += 12
            keyed_notes[relative_pitch] = note
            keys.append(relative_pitch)
        keys = sorted(keys)
        for key in keys:
            sorted_notes.append(keyed_notes[key])
        sorted_notes = tuple(sorted_notes)
        return sorted_notes

    @property
    def note_objects(self):
        objs = []
        for note in self.sorted_notes:
            objs.append(Note(note))
        return objs

    @property
    def chord_intervals(self):
        """
        All intervals between the root and the other notes present
        """
        intvls = []
        for note in self.sorted_notes:
            intvl = (Note(self.root) + Note(note)).simple_interval
            if intvl != "Unison":
                intvls.append(intvl)
        intvls = tuple(intvls)
        return intvls

    @property
    def intvl_note_dict(self):
        """
        A dictionary associating each note with a key from the name of the 
        interval between it and the root
        """
        intvl_note_dict = {}
        i = 0
        for intvl in self.chord_intervals:
            if self.sorted_notes[i] == self.root:
                i += 1
            intvl_note_dict[intvl] = self.sorted_notes[i]
            i += 1
        return intvl_note_dict

    @property
    def description(self):
        
        """
        values in the dictionary:

        triad (major, minor, diminished, or augmented)
        sus (bool)
        seventh chord (bool)
        sixth chord (bool)
        diminished type (half or fully or empty)
        extensions (string of chord symbol extensions)


        """

        description = {}
        description["extensions"] = ""
        description["true root"] = self.root
        description["seventh chord"] = False
        description["sixth chord"] = False
        description["diminished type"] = ""

        intvls = self.chord_intervals

        #these booleans helped make the code neater and easier to write
        m2 = bool("minor 2nd" in intvls)
        M2 = bool("major 2nd" in intvls)
        has2 = bool(m2 or M2)
        m3 = bool("minor 3rd" in intvls)
        M3 = bool("major 3rd" in intvls)
        has3 = bool(m3 or M3)
        P4 = bool("perfect 4th" in intvls)
        TT = bool("tritone" in intvls)
        P5 = bool("perfect 5th" in intvls)
        m6 = bool("minor 6th" in intvls)
        M6 = bool("major 6th" in intvls)
        has6 = bool(m6 or M6)
        m7 = bool("minor 7th" in intvls)
        M7 = bool("major 7th" in intvls)
        has7 = bool(m7 or M7)

        #the following handle inversions
        if not has3:
            if P4 and P5:
                description["sus"] = True
                description["extensions"] += "(sus)"
            elif P4 and has6:
                return Chord(self.notes,root=self.intvl_note_dict["Perfect 4th"],bass=self.root).description
            #!Be more specific with 3rd inversion
            elif has2 and (P4 or TT) and has6:
                if m2:
                    return Chord(self.notes,root=self.intvl_note_dict["Minor 2nd"],bass=self.root).description
                else:
                    return Chord(self.sorted_notes,root=self.intvl_note_dict["Major 2nd"],bass=self.root).description
        elif has3 and has6 and not TT and not P5:
            if m6:
                return Chord(self.notes,root=self.intvl_note_dict["Minor 6th"],bass=self.root).description
            else:
                return Chord(self.notes,root=self.intvl_note_dict["Major 6th"],bass=self.root).description
        else:
            #The four main triad descriptions:
            if M3:
                if m6 and not P5:
                    description["triad"] = "augmented"
                else:
                    description["triad"] = "major"
            elif m3:
                if not TT or P5:
                    description["triad"] = "minor"
                else:
                    description["triad"] = "diminished"
            #6th chords (and fully diminished)
            if has6 and not has7:
                if description["triad"] == "diminished" and M6:
                    description["seventh chord"] = True
                    description["diminished type"] = "fully"
                else:
                    description["sixth chord"] = True
                    if M6:
                        if M2:
                            description["extensions"] += "(6/9)"
                        else:
                            description["extensions"] += "6"
                    elif m6:
                        description["extensions"] += "(b6)"
            #extensions common only to non-sevenths
            if not has7:
                if TT and not P5 and description["triad"] != "diminished":
                    description["extensions"] += "(b5)"
                if m2:
                    description["extensions"] += "(addb9)"
                elif M2 and not M6:
                    description["extensions"] += "(add9)"
            #handling diminished
            if description["triad"] == "diminished" and m7:
                description["diminished type"] = "half"
            #seventh chords
            if has7:
                if M3 and M7:
                    description["extensions"] += "maj"
                if M6:
                    description["extensions"] += "13"
                elif M2:
                    description["extensions"] += "9"
                if not M3 and M7:
                    description["extensions"] += "(maj7)"
                elif not M6 and not M2:
                    description["extensions"] += "7"
                if TT and not P5 and description["triad"] != "diminished":
                    description["extensions"] += "(b5)"
                if m2:
                    description["extensions"] += "(b9)"
                if m6:
                    description["extensions"] += "(b13)"
            #fully diminished 7th
            if description["diminished type"] == "fully":
                if M2:
                    description["extensions"] += "9"
                if M7:
                    description["extensions"] += "(maj7)"
                else:
                    if not M2:
                        description["extensions"] += "7"
                if m2:
                    description["extensions"] += "(b9)"
            #extensions independent of chord type
            if M3 and m3:
                description["extensions"] += "(#9)"
            if P4 and has3:
                description["extensions"] += "(add4)"
            if M3 and m3:
                description["extensions"] += "(#9)"
            if TT and P5:
                description["extensions"] += "(#11)"
            #slash notation for inversions
            if self.bass:
                description["extensions"] += "/" + self.bass
        
        return description
    
    @property
    def symbol(self):
        symbol = self.description["true root"]
        triad = self.description["triad"]

        if triad == "minor":
            symbol += "m"
        elif triad == "augmented":
            symbol += "+"
        elif triad == "diminished":
            if self.description["diminished type"] == "half":
                #!needs to never be an actual '%' on a real lead sheet
                symbol += "%"
            else:
                symbol += "°"

        symbol += self.description["extensions"]

        return symbol

class TimeSignature:
    
    """
    All that is needed to create a time signature is the two
    numbers that are used to write it, from top to bottom,
    such as TimeSignature(4,4) for common time and TimeSignature(3,4)
    for waltz time.  A tempo bpm can be included to add a Tempo object
    as a property.  The == magic method returns True if 
    two TimeSignatures are a perfect metric modulation of each other or not. 
    If tempos are not assigned, only the metric length is checked.
    """

    def __init__(self,top,bottom,tempo_bpm=None):
        self.name = str(top) + "/" + str(bottom)
        self.beats_per_measure = top
        self.gets_beat = Note("R",rhythm=log2(bottom*2))
        self.measure_len = self.gets_beat.rhythm.value * top
        if tempo_bpm:
            self.tempo = Tempo(tempo_bpm)
        else:
            self.tempo = None
    
    def __eq__(self,other):
        if self.tempo and other.tempo:
            if self.tempo.beat_len * self.beats_per_measure == other.tempo.beat_len * other.beats_per_measure:
                return True
        if self.measure_len == other.measure_len and self.tempo == other.tempo:
            return True
        return False
    
    @property
    def tempo(self):
        return self._tempo
    
    @tempo.setter
    def tempo(self,Tempo_object):
        self._tempo = Tempo_object

class Tempo:
    
    """
    A tempo is a simple object intialized with a bpm value (beats per minute),
    and a "beat" is the length of a beat of tempo in seconds.
    A Metronome object can be set as a property of the Tempo using the bpm provided.
    """

    def __init__(self,bpm):
        self.bpm = bpm
        self.beat_len = 60 / bpm

    def set_metronome(self,count,func=None,*params,condition=True):
        """
        See the Metronome class for more information
        """
        self.metronome = Metronome(self.beat_len,count,func,*params,condition)
        return self.metronome

class Metronome(_threading.Thread):
    """
    A metronome needs the arguments of a "beat_len" (measured in seconds),
    a countfor number of times it will click(can be None, but may create an infinite loop
    if no condition is given), a function to pass every click (or will just print a message), 
    optional paramaters for the function to pass, and an optional condition for running the 
    clicking loop function 'self.on()'.  It can be created more easily through
    a Tempo object's set_metronome method, which uses its bpm attribute for the length.
    """
    def __init__(self, beat_len, count, func, *params):
        self.beat_len = beat_len
        self.count= count
        self.func = func
        if params:
            self.params = list(params)
        else:
            self.params = []
        _threading.Thread.__init__(self,name = "Metronome")
        self.setDaemon(1)

    def on(self): 
        if not self.count:
            count = -1
        else:
            count = self.count
        while count != 0:
            _time.sleep(self.beat_len)
            if self.func:
                if self.params:
                    self.func(*(self.params))
                else:
                    self.func()
            else:
                print('(Metronome object clicking)')
            count -= 1

class KeySignature(Mode):
    
    """
    This uses a mode object for initialization.  In general for music
    writing, a diatonic mode like C major or Bb minor will work best, 
    since most common practice theory works with 'keys' as coming from 
    heptatonic diatonic modes.
    """

    def __init__(self,mode):
        self.name = mode.name
        self.key_notes = mode.spelling
    
    @property
    def key_note_names(self):
        key_note_names = []
        for note in self.key_notes:
            key_note_names.append(note.name)
        return key_note_names

    @property
    def sharps(self):
        sharps = 0
        for note in self.key_notes:
            sharps += note.sharps
        if sharps == 0:
            return None
        return sharps
    
    @property
    def flats(self):
        flats = 0
        for note in self.key_notes:
            flats += note.flats
        if flats == 0:
            return None
        return flats
    
    def is_in_key(self,note):
        """
        Boolean expression for whether the note is
        part of the key or not
        """
        if note.name in self.key_note_names:
            return True
        return False
    
    def scale_degree_of(self,note_obj):
        """
        This returns a "key quality" for a Note,
        describing its relationship to the mode given for the
        key.  A C in C major results in "natural 1" and a C#
        would result in "sharp 1".  A Gbb would result in "flat(2x) 5"
        """
        i = 1
        for note in self.key_notes:
            if note_obj.name == note.name:
                return 'natural ' + str(i)
            if note_obj.name[0] == note.name[0]:
                if note_obj.pitch_position > note.pitch_position:
                    difference = note_obj.pitch_position - note.pitch_position
                    if difference > 1:
                        return 'sharp({}x) '.format(difference) + str(i)
                    return 'sharp ' + str(i)
                else:
                    difference = note.pitch_position - note_obj.pitch_position
                    if difference > 1:
                        return 'flat({}x) '.format(difference) + str(i)
                    return 'flat ' + str(i)
            i += 1

class Clef:

    _CLEFS = {'bass':10,'treble':-3,'alto':-4,'tenor':-2,'treble 8vb':4}

    def __init__(self,clef_name):
        self._clef = clef_name
    
    @property
    def clef(self):
        if self._clef not in Clef._CLEFS:
            raise ValueError('Unsupported clef')
        
def transpose(original_key,new_key,*note_objs):
    """
    Needs to use KeySignature objects
    """
    scale_degrees = []
    new_notes = []
    for note in note_objs:
        scale_degrees.append(original_key.scale_degree_of(note))
    for key in scale_degrees:
        splitter = key.split()
        scale_degree = int(splitter[1])
        quality = splitter[0]
        new_note = new_key.key_notes[scale_degree - 1]
        if quality == "sharp":
            new_note = get_note(new_note.pitch + 1,new_note.letter_num)
        elif quality == "flat":
            new_note = get_note(new_note.pitch - 1,new_note.letter_num)
        new_notes.append(new_note)
    return new_notes

class Measure:
        
    """
    Measure objects are mostly intended to be
    manipulated through the Song class.
    The length attribute corresponds to the number of 
    512th notes that can fill the measure, and the number
    attribute is used like an ID for looking up the measure
    from a Song instance.  The description gives a string
    describing the Note and Rhythm objects contained in self.notes,
    Rhythm objects representing rests.  A Note object must have a
    valid rhythm attribute.
    """

    def __init__(self,length,number):
        try:
            assert length == int(length)
            assert number == int(number)
        except:
            raise ValueError("Arguments for initializing a Measure must be integers")
        self.length = length
        self.number = number
        self.notes = []
    
    @property
    def fullness(self):
        fullness = 0
        for note in self.notes:
            fullness += note.value
        return fullness

    @property
    def emptiness(self):
        return self.length - self.fullness

    def add_note(self,obj,_before_index=None):
        if obj.rhythm.value + self.fullness > self.length:
            raise NotImplementedError("Measure {} ".format(self.number) + "is too full to include this rhythm")
        if _before_index:
            if _before_index == 0:
                index = 0
            elif _before_index >= len(self.notes):
                index = len(self.notes) - 1
            else:
                index = _before_index
            self.notes.insert(index,obj)
            return
        self.notes.append(obj)

    @property
    def is_full(self):
        if self.fullness == self.length:
            return True
        return False
    
    @property
    def description(self):
        if not self.notes:
            return None
        description = ""
        i = 1
        for obj in self.notes:
            description += obj.full_name + " " + obj.rhythm.name
            if i != len(self.notes):
                description += ","
            i += 1
        return description

    def clear_notes(self):
        self.notes.clear()
    
    def delete_note(self,index):
        self.notes.remove(self.notes[index])

class Staff:
    
    """
    A measure in a song can be accessed with the measure method,
    which takes the measure number (starting at 1 rather than 0, like in a piece
    of music) and returns a Measure object dealing with that specific measure.
    Many methods for manipulating data within a specific measure are found in the 
    Measure class.
    """

    def __init__(self,time_sig_obj):
        self.timesig = time_sig_obj
        self.measures = []
    
    def add_measure(self,number_of=None):
        if number_of:
            for i in range(number_of):
                self.measures.append(Measure(self.timesig.measure_len,i + 1))
        else:
            self.measures.append(Measure(self.timesig.measure_len,len(self.measures)))

    def measure(self,num):
        return self.measures[num - 1]
    
    def delete_measure(self,num):
        self.measures.remove(self.measures[num-1])
    
    def add_to_end(self,obj):
        if not self.measures or self.measure(self.num_measures).is_full:
            self.add_measure()
        self.measure(self.num_measures).add_note(obj)

    def clear_all_notes(self):
        if self.measures:
            for meas in self.measures:
                meas.clear_notes()

    @property
    def num_measures(self):
        return len(self.measures)
    
    @property
    def description(self):
        if not self.measures:
            return None
        description = ""
        i = 1
        for meas in self.measures:
            description += meas.description
            if i != len(self.measures):
                description += ";"
            i += 1
        return description

class Piece:

    """
    The Piece class allows for the manipulation of multiple staves for multiple instruments, and 
    accommodates the KeySignature class in a practical manner.
    """

    def __init__(self,key_signature,*staves):
        if not staves:
            raise ValueError('Please include at least one staff in a Piece')
        self._staves = staves
        self._key_signature = key_signature
        self._staff_count = len(self._staves)


if __name__ == "__main__":
    print("At the bottom of musictools.py, read the comments on these examples.")

    #The Note class

    #Example 1

    print("\nExample 1: Simple Note objects\n")
    #a simple instance of the note A
    A = Note("A")

    #A's pitch value is 0 and it's letter value is 0.
    print(f"A pitch: {A.pitch}, A letter: {A.letter}")

    #These values are only relative, for comparison with other notes, like C or F#

    #An instance of the note Bb
    Bb = Note("Bb")

    #Bb is one pitch higher than A, and the letter B is the next in the alphabet, so it's pitch is 1 and it's letter is 1
    print(f"Bb pitch: {Bb.pitch}, Bb letter: {Bb.letter}")

    #B then has the same letter value as Bb, but one pitch value higher
    B = Note("B")
    print(f"B pitch: {B.pitch}, B letter: {B.letter}")

    # A# has the same pitch as Bb, but the same letter as A
    As = Note("A#")
    print(f"A# pitch: {As.pitch}, A# letter: {As.letter}")

    #Example 2

    print("\nExample 2: Octave-sensitive Note objects\n")

    #An instance of the note A4
    A4 = Note("A",octave=4)

    #A4 has the same pitch and letter values, but also two more new properites in addition to octave: hard_pitch, and frequency
    #The hard_pitch property simply is an integer representing the pitch of an octave-valued note, so it can be compared with others
    #A0 has a hard_pitch of 0, and the value increases by 1 for each note above it, or deceases into negative values for lower notes.
    #A4 is four octaves higher than A0, or 48 half steps higher, so it has a hard_pitch of 48

    print(f"A4's hard_pitch: {A4.hard_pitch}")
    Gs3 = Note("G#",octave=3)
    print(f"G#3's hard_pitch: {Gs3.hard_pitch}")

    #The frequency property calculates what the frequency of an octave-valued note would be.  
    # By default, A4 is 440 Hz, but it can be reset with the function setA4(frequency)

    print(f"A4: {A4.frequency}")
    setA4(442)
    print(f"A4: {A4.frequency}")
    
#!CHORD ERROR A C F
import note

note_names = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
pitch_offset = [0, 2, 4, 5, 7, 9, 11]

# parse a string of the form ++b-
# octave offset, pitch class, accidental
#
def parse_note(s):
    got_pitch = False
    off = [0,0]
    for c in s:
        if c in note_names:
            if got_pitch:
                raise Exception('already have pitch')
            pitch_class = pitch_offset[note_names.index(c)]
            got_pitch = True
        elif c == '+':
            i = 1 if got_pitch else 0
            if off[i] < 0:
                raise Exception('bad offset')
            off[i] += 1
        elif c == '-':
            i = 1 if got_pitch else 0
            if off[i] > 1:
                raise Exception('bad offset')
            off[i] -= 1
    return [pitch_class, off[0], off[1]]

# if octave_offset is 0,
# return instance of the pitch class closest to the current pitch (tie: upward)
# if it's -1, return the first instance below the current pitch;
# -2, the octave below that etc.
#
def next_pitch(cur_pitch, pitch_class, octave_offset):
    cur_pitch_class = cur_pitch % 12
    cur_octave = cur_pitch // 12
    if octave_offset == 0:
        if pitch_class == cur_pitch_class:
            return cur_pitch
        elif pitch_class < cur_pitch_class:
            diff = cur_pitch_class - pitch_class
            if diff  > 6:
                return pitch_class + 12*(cur_octave+1)
            else:
                return pitch_class + 12*cur_octave
        else:
            diff = pitch_class - cur_pitch_class
            if diff > 6:
                return pitch_class + 12*(cur_octave-1)
            else:
                return pitch_class + 12*cur_octave
    elif octave_offset < 0:
        if pitch_class < cur_pitch_class:
            next_down = pitch_class + 12*cur_octave
        else:
            next_down = pitch_class + 12*(cur_octave-1)
        if octave_offset < -1:
            return next_down  + 12*(octave_offset+1)
        else:
            return next_down
    else:
        if pitch_class > cur_pitch_class:
            next_up = pitch_class + 12*(cur_octave)
        else:
            next_up = pitch_class + 12*(cur_octave+1)
        if octave_offset > 1:
            return next_up + 12*(octave_offset-1)
        else:
            return next_up
    
# textual note specification
def n(s):
    s = s.replace('[', ' [ ')
    s = s.replace(']', ' ] ')
    notes = []
    cur_pitch = 60
    cur_time = 0
    in_chord = False
    vol = 64
    dur = 1
    for t in s.split(' '):
        if not t: continue
        if t == '[':
            if in_chord:
                raise Exception("Can't nest [")
            in_chord = True
            chord_dur = dur
        elif t == ']':
            if not in_chord:
                raise Exception("] not in chord")
            in_chord = False
            cur_time += dur
        elif t == '_':
            cur_time -= dur
        elif '/' in t:
            # rhythm notation
            a = t.split('/')
            num = 1 if a[0] == '' else int(a[0])
            denom = int(a[1])
            d = num/denom
            if in_chord:
                chord_dur = d
            else:
                dur = d
        elif t == '.':
            if in_chord:
                raise Exception('no rests in chords')
            cur_time += dur
        else:
            # note
            x = parse_note(t)
            pitch_class = x[0]
            octave_offset = x[1]
            accidental = x[2]
            pitch_class += accidental
            pitch_class = (pitch_class + 12) % 12
            pitch = next_pitch(cur_pitch, pitch_class, octave_offset)
            d = chord_dur if in_chord else dur
            n = note.Note(cur_time, d, pitch, vol)
            notes.append(n)
            if not in_chord:
                cur_time += dur
            cur_pitch = pitch
    return notes

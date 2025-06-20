import pretty_midi
import matplotlib.pyplot as plt
from collections import defaultdict


# TIME_RESOLUTION = 100  # 和tokenizer保持一致

class Note:
    def __init__(self, onset, duration, abs_pitch):
        self.onset = onset
        self.duration = duration
        self.abs_pitch = abs_pitch
    def __repr__(self):
        return f"Note(onset={self.onset}, duration={self.duration}, abs_pitch={self.abs_pitch})"

class Instrument:
    def __init__(self, name, notes):
        self.name = name
        self.notes = notes  # List[Note]
    def __repr__(self):
        return f"Instrument({self.name!r}, {self.notes!r})"
    
class MelodyContourExtractor:
    def __init__(self, raw_melody_sequence, smooth_window=3, merge_threshold=0):
        self.raw_melody_sequence = raw_melody_sequence
        # self.tempo = self.melody_sequence.estimate_tempo()
        self.melody_notes = self.extract_main_melody_track()
        if self.melody_notes is None:
            raise ValueError("No melody track found.")
        self.melody_notes.sort(key=lambda n: n.onset)
        self.smooth_window = smooth_window
        self.merge_threshold = merge_threshold


    def extract_main_melody_track(self):
        instrument_dict = defaultdict(list)
        # for a in self.raw_melody_sequence:
            # print('a:', a) [onset, duration, abs_pitch, instrument]
        for onset, duration, abs_pitch, instrument in self.raw_melody_sequence:
            instrument_dict[instrument].append(Note(onset, duration, abs_pitch))

        melody_sequence = [Instrument(name, notes) for name, notes in instrument_dict.items()]

        
        melody_score = []
        for inst in melody_sequence:
            # 调试信息！ inst: [Note(onset=50, duration=50, abs_pitch=57), 
            # print('inst:', inst.notes) # original ；Note(start=1.200000, end=1.505000, pitch=61, velocity=72)
            if inst.name == -84:  # -84 drum
                continue
            pitches = [n.abs_pitch for n in inst.notes]
            durations = [n.duration for n in inst.notes]
            pitch_range = max(pitches) - min(pitches)
            avg_dur = sum(durations) / len(durations)
            avg_pitch = sum(pitches) / len(pitches)
            score = pitch_range + avg_dur * 10 + avg_pitch * 0.1
            melody_score.append((score, inst))
        if not melody_score:
            return None
        melody_instr = max(melody_score, key=lambda x: x[0])[1]
        
        # ---- Step 2: resolve polyphony using pitch priority ----
        notes = sorted(melody_instr.notes, key=lambda n: (n.onset, -n.abs_pitch))  # higher pitch first if same onset
        monophonic = []
        last_end = -1

        for note in notes:
            if note.onset >= last_end:
                monophonic.append(note)
                last_end = note.onset + note.duration
            
        return monophonic
    
    # def __init__(self, midi_file, smooth_window=3, merge_threshold=0):
    #     self.pm = pretty_midi.PrettyMIDI(midi_file)
    #     self.tempo = self.pm.estimate_tempo()
    #     self.melody_notes = self.extract_main_melody_track()
    #     if self.melody_notes is None:
    #         raise ValueError("No melody track found.")
    #     self.melody_notes.sort(key=lambda n: n.start)
    #     self.smooth_window = smooth_window
    #     self.merge_threshold = merge_threshold

    # def extract_main_melody_track(self):
    #     melody_score = []
    #     for inst in self.pm.instruments:
    #         print('inst:', inst)
    #         if inst.is_drum or not inst.notes:
    #             print('non note instrument:', inst)
    #             continue
    #         pitches = [n.pitch for n in inst.notes]
    #         durations = [n.end - n.start for n in inst.notes]
    #         pitch_range = max(pitches) - min(pitches)
    #         avg_dur = sum(durations) / len(durations)
    #         avg_pitch = sum(pitches) / len(pitches)
    #         score = pitch_range + avg_dur * 10 + avg_pitch * 0.1
    #         melody_score.append((score, inst))
    #     if not melody_score:
    #         return None
    #     melody_instr = max(melody_score, key=lambda x: x[0])[1]
    #     return melody_instr.notes

    def smooth_melody(self):
        pitches = [n.abs_pitch for n in self.melody_notes]
        smoothed = []
        half = self.smooth_window // 2
        for i in range(len(pitches)):
            start = max(0, i - half)
            end = min(len(pitches), i + half + 1)
            smoothed.append(sum(pitches[start:end]) / (end - start))
        return smoothed

    def simplify_contour_smoothed(self, smoothed_pitches):
        notes = self.melody_notes
        if len(notes) < 2:
            return []
        # quarter_duration = 60.0 / self.tempo
        simplified = []
        start_idx = 0
        direction = None
        for i in range(1, len(notes)):
            delta = smoothed_pitches[i] - smoothed_pitches[i - 1]
            curr_dir = 'up' if delta > 0 else 'down' if delta < 0 else 'flat'
            if direction is None:
                direction = curr_dir
            is_last = (i == len(notes) - 1)
            dir_changed = (curr_dir != direction)
            if dir_changed or is_last:
                end_idx = i if dir_changed else i + 1
                # end_time = notes[end_idx - 1].end if not is_last else notes[-1].end
                start_pitch = notes[start_idx].abs_pitch
                end_pitch = notes[end_idx - 1].abs_pitch
                interval = end_pitch - start_pitch
                start_time = notes[start_idx].onset
                # duration_beats = notes[start_idx].duration / quarter_duration
                # duration_tokenizer_unit = int((notes[start_idx].duration) * TIME_RESOLUTION)
                # simplified.append((interval, duration_tokenizer_unit))
                simplified.append((start_time, interval, notes[start_idx].duration))
                start_idx = i
                direction = curr_dir
        return simplified

    def merge_small_intervals(self, contour):
        if not contour:
            return []
        merged = []
        for start_time, interval, dur in contour:
            if merged and abs(interval) <= self.merge_threshold:
                prev_iv, prev_dur = merged[-1]
                merged[-1] = (prev_iv, prev_dur + dur)
            else:
                # merged.append((start_time, interval, dur))
                merged.append((start_time, interval))
        return merged

    def get_final_contour(self):
        smoothed = self.smooth_melody()
        simplified = self.simplify_contour_smoothed(smoothed)
        merged = self.merge_small_intervals(simplified)
        
        # total_beats_original = (self.melody_notes[-1].end - self.melody_notes[0].start) / (60.0 / self.tempo)
        # summed = sum(d for _, d in merged)
        # if summed < total_beats_original:
        #     remaining = total_beats_original - summed
        #     merged.append((0, remaining))
        
        return merged

    # def plot_with_duration_axis(self, contour=None):
    #     if contour is None:
    #         contour = self.get_final_contour()
    #     notes = self.melody_notes
    #     tempo = self.tempo
    #     beat_times = [(n.onset - notes[0].onset)  for n in notes]
    #     original_pitches = [n.pitch for n in notes]
    #     intervals, durations = zip(*contour)
    #     contour_times = [0]
    #     for d in durations:
    #         contour_times.append(contour_times[-1] + d)
    #     contour_times = contour_times[:-1]
    #     abs_path = [0]
    #     for iv in intervals:
    #         abs_path.append(abs_path[-1] + iv)
    #     abs_path = abs_path[:-1]
    #     plt.figure(figsize=(14, 6))
    #     plt.plot(beat_times, original_pitches, label="Original MIDI Pitch", marker='o')
    #     plt.plot(contour_times, intervals,   label="Final Contour Intervals", marker='x')
    #     plt.plot(contour_times, abs_path,     label="Absolute Interval Path", marker='^')
    #     plt.title("Original Melody vs. Final Simplified Contour vs. Absolute Path")
    #     plt.xlabel("Time (beats)")
    #     plt.ylabel("Pitch / Interval")
    #     plt.legend()
    #     plt.grid(True)
    #     plt.tight_layout()
    #     plt.show()

    def print_final_contour(self):
        final_contour = self.get_final_contour()
        print(final_contour)
        print("Final Simplified Contour (interval, duration in tokenizer units - 0.01s):")
        # for i, (start_time, iv, dur) in enumerate(final_contour):
        for i, (start_time, iv) in enumerate(final_contour):
            # print(f"{i:2d}: Interval: {iv:+}, Duration: {dur:.2f}")
            print(f"{i:2d}: start_time: {start_time}, Interval: {iv:+}")
        start_times = [start_time for start_time, _ in final_contour]
        contour_intervals = [iv for _, iv in final_contour]
        # contour_durations = [dur for _, _, dur in final_contour]
        print("\nCopy-paste ready:")
        print("start_times =", start_times)
        print("contour_intervals =", contour_intervals)
        # print("contour_durations =", contour_durations)

# # 用法示例
# if __name__ == "__main__":
#     # midi_file = "/import/c4dm-datasets/URMP/Dataset/01_Jupiter_vn_vc/Sco_01_Jupiter_vn_vc.mid"
#     raw_melody_sequence = [[0, 25, 48, 0],
#  [25, 25, 55, 0],
#  [50, 25, 60, 0],
#  [50, 25, 55, 0],
#  [75, 25, 50, 0],]
    
#     extractor = MelodyContourExtractor(raw_melody_sequence)
#     # extractor.get_final_contour()
#     extractor.print_final_contour()
#     # extractor.plot_with_duration_axis()  # 如需可视化
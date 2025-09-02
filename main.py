import librosa
import numpy as np
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
import os
import glob

CAMELOT_MAP = {
    ('C', 'maj'): '8B', ('C#', 'maj'): '3B', ('D', 'maj'): '10B', ('D#', 'maj'): '5B',
    ('E', 'maj'): '12B', ('F', 'maj'): '7B', ('F#', 'maj'): '2B', ('G', 'maj'): '9B',
    ('G#', 'maj'): '4B', ('A', 'maj'): '11B', ('A#', 'maj'): '6B', ('B', 'maj'): '1B',
    ('A', 'min'): '8A', ('A#', 'min'): '3A', ('B', 'min'): '10A', ('C', 'min'): '5A',
    ('C#', 'min'): '12A', ('D', 'min'): '7A', ('D#', 'min'): '2A', ('E', 'min'): '9A',
    ('F', 'min'): '4A', ('F#', 'min'): '11A', ('G', 'min'): '6A', ('G#', 'min'): '1A',
}
PITCH_CLASSES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def analyze_track(track_path):

    print(f"Analyzing: {os.path.basename(track_path)}")
    try:
        y, sr = librosa.load(track_path)
        tempo = librosa.feature.tempo(y=y, sr=sr)[0]
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        
        key_chroma = np.sum(chroma, axis=1)
        tonic_idx = np.argmax(key_chroma)
        tonic = PITCH_CLASSES[tonic_idx]
        
        major_third_idx = (tonic_idx + 4) % 12
        minor_third_idx = (tonic_idx + 3) % 12
        mode = 'maj' if key_chroma[major_third_idx] > key_chroma[minor_third_idx] else 'min'
        
        camelot = CAMELOT_MAP.get((tonic, mode), "Unknown")
        
        print(f"  -> OK. Tempo: {tempo:.2f} BPM, Key: {tonic} {mode} ({camelot})")
        return {'path': track_path, 'camelot': camelot}
    except Exception as e:
        print(f"  -> ERROR: Could not analyze file. Skipping. Reason: {e}")
        return None

def are_keys_compatible(camelot1, camelot2):
    if camelot1 == "Unknown" or camelot2 == "Unknown": return False
    num1, letter1 = int(camelot1[:-1]), camelot1[-1]
    num2, letter2 = int(camelot2[:-1]), camelot2[-1]
    if num1 == num2: return True
    if letter1 == letter2 and (abs(num1 - num2) == 1 or abs(num1 - num2) == 11): return True
    return False

def intelligent_eq_mix(track1, track2, duration_ms=10000, crossover_freq=800):
    actual_duration = min(duration_ms, len(track1), len(track2))
    if actual_duration < duration_ms:
        print(f"  -> WARNING: A track is shorter than the desired transition. Using {actual_duration}ms instead.")

    transition1 = track1[-actual_duration:]
    transition2 = track2[:actual_duration]

    s1_low = transition1.low_pass_filter(crossover_freq)
    s1_high = transition1.high_pass_filter(crossover_freq)
    s2_low = transition2.low_pass_filter(crossover_freq)
    s2_high = transition2.high_pass_filter(crossover_freq)
    
    high_transition = s1_high.fade_out(actual_duration).overlay(s2_high.fade_in(actual_duration))
    
    half_dur = actual_duration // 2
    bass_transition = s1_low[:half_dur].fade_out(half_dur) + s2_low[half_dur:].fade_in(half_dur)
    
    final_transition = high_transition.overlay(bass_transition)
    
    return track1[:-actual_duration] + final_transition + track2[actual_duration:]

def find_harmonic_path(track_infos):
    if not track_infos: return []
    ordered_playlist = []
    remaining_tracks = track_infos.copy()
    current_track = remaining_tracks.pop(0)
    ordered_playlist.append(current_track)

    while remaining_tracks:
        found_next = False
        for i, next_track in enumerate(remaining_tracks):
            if are_keys_compatible(current_track['camelot'], next_track['camelot']):
                current_track = remaining_tracks.pop(i)
                ordered_playlist.append(current_track)
                found_next = True
                break
        if not found_next:
            break 
            
    ordered_playlist.extend(remaining_tracks) 
    return ordered_playlist

def main():
    songs_folder = "songs_to_mix"
    playlist_paths = sorted(glob.glob(os.path.join(songs_folder, "*.mp3")))

    if not playlist_paths:
        print(f"Error: No MP3 files found in the '{songs_folder}' folder.")
        return

    print("---smooth DJ---")
    print(f"Found {len(playlist_paths)} MP3 files to process.")
    
    print("\n[PHASE 1: Key Analysis]")
    all_track_infos = [info for info in (analyze_track(p) for p in playlist_paths) if info is not None]

    if len(all_track_infos) < 2:
        print("\nError: Could not find at least two valid songs to mix. Exiting.")
        return

    print(f"\nSuccessfully analyzed {len(all_track_infos)} tracks.")
    
    print("\n[PHASE 2: Finding Harmonic Path]")
    ordered_tracks = find_harmonic_path(all_track_infos)
    
    print("\nAlgorithm has determined the following mix order:")
    for i, track in enumerate(ordered_tracks):
        print(f"  {i+1}. {os.path.basename(track['path'])} (Key: {track['camelot']})")

    print("\n[PHASE 3: Building Mix at Original Tempos]")
    try:
        print(f"Loading first track: {os.path.basename(ordered_tracks[0]['path'])}")
        mix_so_far = AudioSegment.from_mp3(ordered_tracks[0]['path'])
    except Exception as e:
        print(f"FATAL ERROR: Could not load the first track of the playlist: {e}")
        return
    
    for i in range(len(ordered_tracks) - 1):
        incoming_track_info = ordered_tracks[i+1]
        
        print(f"\nMixing in: '{os.path.basename(incoming_track_info['path'])}'")
        
        try:
            incoming_track = AudioSegment.from_mp3(incoming_track_info['path'])
            mix_so_far = intelligent_eq_mix(mix_so_far, incoming_track)
        except Exception as e:
            print(f"  -> ERROR: Could not load or mix this track. Skipping. Reason: {e}")
            continue 
    print("\n[PHASE 4: Final Export]")
    output_filename = "Your playlist.mp3"
    try:
        mix_so_far.export(output_filename, format="mp3", bitrate="320k")
        print(f"\n--- SUCCESS! ---")
        print(f"Your mix has been saved as '{output_filename}'")
    except Exception as e:
        print(f"\n--- ERROR ---")
        print(f"Could not export the final mix. Reason: {e}")

if __name__ == "__main__":
    main()
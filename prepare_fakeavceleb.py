import os
import random
import pandas as pd
import cv2
from moviepy import VideoFileClip
from facenet_pytorch import MTCNN
from tqdm import tqdm
from PIL import Image
import torch

N_SAMPLES = 50
META_DATA_PATH = "FakeAVCeleb_v1.2/meta_data.csv"
OUTPUT_DIR = "processed_data"

def init_dirs():
    os.makedirs(f"{OUTPUT_DIR}/audio", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/frames", exist_ok=True)

def process_video(video_path, output_name, mtcnn):
    audio_out = os.path.join(OUTPUT_DIR, "audio", f"{output_name}.wav")
    frames_dir = os.path.join(OUTPUT_DIR, "frames", output_name)
    os.makedirs(frames_dir, exist_ok=True)
    
    # Check if already processed
    if os.path.exists(audio_out) and len(os.listdir(frames_dir)) > 0:
        return True

    # 1. Extract audio
    try:
        clip = VideoFileClip(video_path)
        if clip.audio is not None:
            clip.audio.write_audiofile(audio_out, fps=16000, logger=None)
        else:
            print(f"No audio in {video_path}")
            return False
    except Exception as e:
        print(f"Error extracting audio from {video_path}: {e}")
        return False
        
    # 2. Extract and align faces
    try:
        vid = cv2.VideoCapture(video_path)
        frame_count = 0
        while True:
            ret, frame = vid.read()
            if not ret:
                break
            
            # Subsample frames to save time (e.g., 5 frames per second if 25fps -> every 5th)
            if frame_count % 5 == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                
                # Detect and align face
                face = mtcnn(pil_img)
                if face is not None:
                    # face is a torch tensor [-1, 1] of shape (3, 160, 160) by default
                    # We need to save it as an image, but MTCNN already normalizes.
                    # Alternatively, use mtcnn to just crop and return PIL
                    pass 
                
                # Better: let MTCNN directly save the cropped face
                save_path = os.path.join(frames_dir, f"{frame_count:04d}.jpg")
                mtcnn(pil_img, save_path=save_path)
            
            frame_count += 1
        vid.release()
    except Exception as e:
        print(f"Error processing frames for {video_path}: {e}")
        return False

    return True

def main():
    init_dirs()
    print("Loading data...")
    df = pd.read_csv(META_DATA_PATH)
    
    # Fix paths
    df['full_path'] = df.apply(lambda row: os.path.join("FakeAVCeleb_v1.2", row['Unnamed: 9'].replace("FakeAVCeleb/", ""), row['path']), axis=1)
    
    scenarios = {
        'S1': 'FakeVideo-RealAudio',
        'S2': 'RealVideo-FakeAudio',
        'S3': 'FakeVideo-FakeAudio'
    }
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # We want 112x112 for RJCA
    mtcnn = MTCNN(image_size=112, margin=14, keep_all=False, device=device)
    
    evaluation_pairs = []
    
    # Grab real videos for enrollment
    real_df = df[df['type'] == 'RealVideo-RealAudio']
    
    print("Sampling and processing...")
    for s_name, s_type in scenarios.items():
        subset = df[df['type'] == s_type]
        sampled = subset.sample(n=min(N_SAMPLES, len(subset)), random_state=42)
        
        for _, row in tqdm(sampled.iterrows(), total=len(sampled), desc=f"Processing {s_name}"):
            fake_vid_path = row['full_path']
            source_id = row['source']
            
            # Find a real video for enrollment
            enroll_options = real_df[real_df['source'] == source_id]
            if len(enroll_options) == 0:
                continue
            enroll_row = enroll_options.iloc[0]
            enroll_vid_path = enroll_row['full_path']
            
            # Unique names
            fake_name = f"{s_name}_{source_id}_{row['path'].split('.')[0]}"
            enroll_name = f"Enroll_{source_id}_{enroll_row['path'].split('.')[0]}"
            
            # Process Fake Video
            ok1 = process_video(fake_vid_path, fake_name, mtcnn)
            # Process Enroll Video
            ok2 = process_video(enroll_vid_path, enroll_name, mtcnn)
            
            if ok1 and ok2:
                evaluation_pairs.append({
                    'scenario': s_name,
                    'enroll_name': enroll_name,
                    'test_name': fake_name,
                    'source_id': source_id
                })
                
    pairs_df = pd.DataFrame(evaluation_pairs)
    pairs_df.to_csv(os.path.join(OUTPUT_DIR, "evaluation_pairs.csv"), index=False)
    print(f"Prepared {len(pairs_df)} pairs for evaluation.")

if __name__ == "__main__":
    main()

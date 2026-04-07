import os
import sys
import glob
import torch
import numpy as np
import pandas as pd
import soundfile
import cv2
import tqdm
import torch.nn as nn
import torch.nn.functional as F

sys.path.append('RJCAforSpeakerVerification')
from audiomodel import ECAPA_TDNN
from visualmodel import IResNet
from orig_cam import CAM
from ASP import Attentive_Statistics_Pooling

class FusionModel(nn.Module):
    def __init__(self):
        super(FusionModel, self).__init__()
        self.JCA_model = CAM()
        self.asp = Attentive_Statistics_Pooling(704)
        self.linear = nn.Linear(1408, 512)

    def forward(self, a_feat, v_feat):
        AV_feats = self.JCA_model(a_feat, v_feat)
        AV_feats = self.asp(AV_feats)
        AV_embeddings = self.linear(AV_feats)
        return AV_embeddings

def load_audio(file_path):
    # From dataLoader.py: takes frame_len * 8 sized segment
    frame_len = 100 * 160 + 240
    try:
        utterance, sr = soundfile.read(file_path)
        if len(utterance.shape) > 1:
            utterance = utterance.mean(axis=1)
    except:
        return None
    if len(utterance) < (frame_len * 8):
        _utterance = np.zeros(frame_len * 8)
        _utterance[-len(utterance):] = utterance
        utterance = _utterance
    
    framelen = int(np.floor(len(utterance) / 8))
    audio_segments = []
    for i in range(8):
        if framelen <= frame_len:
            segment = np.array(utterance[int(i*frame_len):int((i*frame_len)+frame_len)])
        else:
            audio_segment = np.array(utterance[int(i*framelen):int((i*framelen)+framelen)])
            if audio_segment.shape[0] - frame_len > 0:
                startframe = np.random.choice(range(0, audio_segment.shape[0] - frame_len))
                segment = np.array(audio_segment[int(startframe):int(startframe)+frame_len])
            else:
                segment = audio_segment
        if len(segment) < frame_len:
            segment = np.pad(segment, (0, max(0, frame_len - len(segment))), 'wrap')
        audio_segments.append(segment)
    return torch.FloatTensor(np.array(audio_segments)).unsqueeze(0) # (1, 8, seq_len)

def load_face(frames_dir):
    frames = glob.glob(os.path.join(frames_dir, "*.jpg"))
    if len(frames) == 0:
        return None
    frames = sorted(frames)
    face_images = np.zeros((32, 3, 112, 112), dtype=np.uint8)
    face_frames = []
    
    images = []
    for frame_path in frames:
        frame = cv2.imread(frame_path)
        if frame is None: continue
        face = cv2.resize(frame, (112, 112))
        face = np.transpose(face, (2, 0, 1))
        images.append(face)
    images = np.array(images)
    if len(images) == 0: return None
    
    if images.shape[0] <= 32:
        face_images[-images.shape[0]:,:,:,:] = images
        images = face_images

    for i in range(8):
        if images.shape[0] <= 32:
            indices = list(range(i*4, (i*4)+4))
            random_index = indices[0:1] # Just take first or random
        else:
            win_length = int(np.floor(images.shape[0] / 8))
            indices = list(range(i*win_length, (i*win_length)+win_length))
            random_index = indices[0:1]
        face_frames.append(images[random_index, :, :, :])
    
    faces = torch.FloatTensor(np.array(face_frames)) # (8, 1, 3, 112, 112)
    faces = faces.div_(255).sub_(0.5).div_(0.5)
    return faces.unsqueeze(0) # (1, 8, 1, 3, 112, 112)

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print("Loading Models...")
    # Initialize Backbones
    speaker_encoder = ECAPA_TDNN(model='ecapa1024').to(device)
    try:
        face_encoder = IResNet(model='res50').to(device)
    except:
        face_encoder = IResNet(model='res18').to(device)
    fusion_model = FusionModel().to(device)
    
    # Load Weights
    # According to trainer.py parameter loading code
    a_state = torch.load('RJCAforSpeakerVerification/models/audio_model.model', map_location=device, weights_only=False)
    v_state = torch.load('RJCAforSpeakerVerification/models/visual_model.model', map_location=device, weights_only=False)
    f_state = torch.load('RJCAforSpeakerVerification/models/fusion_model.model', map_location=device, weights_only=False)
    
    # Prune unexpected keys that belonged to loss functions in checkpoint
    def load_substate(model, state_dict, prefix):
        new_state = {}
        for k, v in state_dict.items():
            if prefix in k:
                new_state[k.replace(prefix, '')] = v
        model.load_state_dict(new_state, strict=False)

    load_substate(speaker_encoder, a_state, 'speaker_encoder.')
    load_substate(face_encoder, v_state, 'face_encoder.')
    fusion_model.load_state_dict(f_state['net'], strict=False)
    
    speaker_encoder.eval()
    face_encoder.eval()
    fusion_model.eval()

    pairs = pd.read_csv("processed_data/evaluation_pairs.csv")
    scores = {'S1': [], 'S2': [], 'S3': []}
    
    results = []

    print("Evaluating Scenarios...")
    for idx, row in tqdm.tqdm(pairs.iterrows(), total=len(pairs)):
        scenario = row['scenario']
        enroll_name = row['enroll_name']
        test_name = row['test_name']
        
        # Load Enroll
        e_audio = load_audio(f"processed_data/audio/{enroll_name}.wav")
        e_face = load_face(f"processed_data/frames/{enroll_name}")
        
        # Load Test
        t_audio = load_audio(f"processed_data/audio/{test_name}.wav")
        t_face = load_face(f"processed_data/frames/{test_name}")
        
        if e_audio is None or e_face is None or t_audio is None or t_face is None:
            continue
            
        with torch.no_grad():
            # Get Enroll Embeddings
            # e_audio shape: (1, 8, seq) => forward on (8, seq)
            e_a_data = e_audio.squeeze(0).to(device)
            e_v_data = e_face.squeeze(0).squeeze(1).to(device) # (8, 3, 112, 112)
            
            e_a_emb = speaker_encoder(e_a_data) # (8, 192)
            e_v_emb = face_encoder(e_v_data) # (8, 512)
            
            e_a_emb = e_a_emb.unsqueeze(0) # (1, 8, 192)
            e_v_emb = e_v_emb.unsqueeze(0) # (1, 8, 512)
            
            e_av_emb = fusion_model(e_a_emb, e_v_emb)
            e_av_emb = F.normalize(e_av_emb, p=2, dim=1)
            
            # Get Test Embeddings
            t_a_data = t_audio.squeeze(0).to(device)
            t_v_data = t_face.squeeze(0).squeeze(1).to(device)
            
            t_a_emb = speaker_encoder(t_a_data)
            t_v_emb = face_encoder(t_v_data)
            
            t_a_emb = t_a_emb.unsqueeze(0)
            t_v_emb = t_v_emb.unsqueeze(0)
            
            t_av_emb = fusion_model(t_a_emb, t_v_emb)
            t_av_emb = F.normalize(t_av_emb, p=2, dim=1)
            
            score = torch.mean(torch.matmul(e_av_emb, t_av_emb.T)).item()
            scores[scenario].append(score)
            results.append({'scenario': scenario, 'enroll': enroll_name, 'test': test_name, 'score': score})
            
    # Calculate False Accept Rate for a nominal threshold.
    # Usually EER thresholds are found on validation. We will just use 0.5 or find distribution mean
    print("\\n=== Evaluation Results ===")
    overall_threshold = 0.35 # Just for demonstration, exact EER thresh might differ
    
    for s_name in ['S1', 'S2', 'S3']:
        s_scores = scores[s_name]
        if len(s_scores) > 0:
            mean_score = np.mean(s_scores)
            far = sum(1 for x in s_scores if x > overall_threshold) / len(s_scores)
            print(f"{s_name} - Pairs Tested: {len(s_scores)}, Mean RJCA Fusion Score: {mean_score:.4f}, Verification Rate @ 0.35: {far*100:.2f}%")
        else:
            print(f"{s_name} - No valid pairs tested.")

    pd.DataFrame(results).to_csv("processed_data/final_scores.csv", index=False)

if __name__ == '__main__':
    main()

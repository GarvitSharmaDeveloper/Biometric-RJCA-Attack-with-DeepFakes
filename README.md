# Biometric Security Project - Deepfake Robustness Evaluation

This repository contains the codebase and data engineering scripts used to evaluate the vulnerability of the **Recursive Joint Cross-Attention (RJCA)** audio-visual speaker verification model against robust deepfake impersonation attacks. This research project was conducted as part of the CS 228 (Biometric Security with AI) coursework.

## Abstract
Audio-visual authentication systems have historically relied on lip-voice temporal synchronization to defend against presentation attacks. Our implementation stress-tests the state-of-the-art RJCA framework across three deepfake environments simulated via the `FakeAVCeleb` dataset. 
- **S1**: Fake Face, Real Voice 
- **S2**: Real Face, Fake Voice
- **S3**: Fake Face, Fake Voice (Fully Synthetic)

We established a dynamic Equal Error Rate (EER) threshold of **0.65** by evaluating a live Genuine distribution against 300 Zero-Effort Imposters. We empirically showcase that out-of-the-box cross-attention models are highly susceptible to modern generative impersonation artifacts. Specifically, **S2 attacks achieved a 100% Attack Success Rate**, perfectly overlapping the genuine validation matrices without requiring algorithmic modifications like White-Box adversarial gradients (FGSM) or Spatial Blurring natively.

## Structure
```
.
├── RJCAforSpeakerVerification/   # Forked/Cloned Audio-Visual Backbone (ECAPA-TDNN & IResNet50)
├── FakeAVCeleb_v1.2/             # Local deepfake dataset containing Real and Fake audio-video samples
├── processed_data/               # Outputs of the data engineering process (Face alignments, Extracted audio)
├── requirements.txt              # Standard Python dependencies
├── Project_Execution.ipynb       # Unified master notebook (End-to-End pipeline)
└── README.md
```

## Setup Instructions

### 1. Environment Configuration
We recommend using a localized `venv` environment or a Conda environment strictly to avoid dependency conflicts with other ML projects.

```sh
# Create and activate virtual environment
python -m venv biometric_env
source biometric_env/bin/activate

# Install dependencies  (Notice: Due to torch constraints, numpy must be < 2.0)
pip install -r requirements.txt
```
*Note: Our `requirements.txt` natively embeds the PyTorch `extra-index-url` pointing to `cu121`. This is strictly required to prevent fatal `libcudart.so` downgrades when resolving `facenet-pytorch` via pip.*

### 2. Dataset Setup
1. Unzip your `FakeAVCeleb_v1.2` dataset directory into the root of this project.
2. Verify that `FakeAVCeleb_v1.2/meta_data.csv` exists at that exact path.

### 3. Model Weights Download
The pre-trained checkpoints for the Audio Encoder, Visual Encoder, and the Fusion core are required. Download them manually and place them in the models directory securely.
- Ensure the following files exist:
  - `RJCAforSpeakerVerification/models/audio_model.model`
  - `RJCAforSpeakerVerification/models/visual_model.model`
  - `RJCAforSpeakerVerification/models/fusion_model.model`

## Execution Guide

### Unified Execution (Recommended)
This assignment evaluates deepfake capabilities entirely through a single foundational notebook interface. Launch **`Project_Execution.ipynb`** via Jupyter Notebook or import directly into Google Colab.

The `Project_Execution.ipynb` systematically executes the following pipeline automatically:
1. **Dependency Validation:** Dynamically upgrades and pins standard mathematical environments utilizing `cu121` constraints.
2. **Exploratory Data Analysis (EDA):** Visualizes the native modalities encoded within the `FakeAVCeleb` directory, analyzing class imbalances and video distributions.
3. **Data Scrubbing (MTCNN):** Leverages a rigorous boolean filter (`while` loop) evaluating 300 explicit enrollment vs simulated pairings, ensuring the Multi-Task Cascaded Convolutional framework yields exact bounding limits for both audio and visual parameters.
4. **Baseline Inference Inference:** Iterates the fully processed arrays across the isolated RJCA ECAPA-TDNN and IResnet backbones.
5. **Threshold Generation:** Dynamically generates an overlapping KDE chart, proving the S2 bypass utilizing exclusively the Cosine Score margins calculated directly on your active GPU instance.

*Note: Depending on system architecture, extracting, cropping faces, and computing the massive spatial-temporal iterations will take several minutes. Ensure your accelerator hardware (CUDA) is activated.*

## Acknowledgements
- [RJCA for Speaker Verification (Praveen et al.)](https://github.com/praveena2j/RJCAforSpeakerVerification) - Provided the zero-shot baseline authentication model.
- [FakeAVCeleb Dataset](https://github.com/DASH-Lab/FakeAVCeleb) - Supplied the multi-modal deepfake samples.

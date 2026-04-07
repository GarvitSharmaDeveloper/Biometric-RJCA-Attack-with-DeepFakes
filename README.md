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
├── eda_plots/                    # Exploratory Data Analysis PNG visualizations
├── requirements.txt              # Standard Python dependencies
├── prepare_fakeavceleb.py        # Custom data provisioning, pair sampling, and MTCNN alignment script
├── eval_scenarios.py             # Inference baseline logic driving RJCA and scoring Cosine Similarities
├── Project_Execution.ipynb       # Unified master notebook (End-to-End pipeline)
├── EDA.ipynb                     # Jupyter Notebook for visual analysis of FakeAVCeleb modalities
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
For a cohesive experience, launch the **`Project_Execution.ipynb`** Jupyter Notebook. This notebook consolidates:
- Exploratory Data Analysis (EDA)
- Automated Data Engineering
- RJCA Inference
- Scoring and Result Visualization

### Individual Script Execution (Manual)
If you prefer running standalone scripts:

#### 1. Exploratory Data Analysis (EDA)
To view the underlying parameters, class balances, and features guiding our sampling, launch the `EDA.ipynb` via Jupyter:
```sh
jupyter notebook EDA.ipynb
```

#### 2. Data Engineering & Subsampling (Run Once)
To dynamically slice 300 enrollment/testing pairs from FakeAVCeleb, and extract + align faces via MTCNN, run the preparation step.
```sh
python prepare_fakeavceleb.py
```
*Note: Depending on system architecture, extracting and cropping faces iteratively will take several minutes. Outputs will be populated in `processed_data/`*.

#### 3. Baseline Verification (Inference)
Execute the scenario evaluation against the localized RJCA implementation:
```sh
python eval_scenarios.py
```
This command feeds paired deepfake-vs-enrollment alignments into the ECAPA-TDNN and IResNet50 backbones, projects their dimensions into the Fusion pool, and extracts target Cosine Similarities printing the overall `FAR` (False Accept Rates).

## Acknowledgements
- [RJCA for Speaker Verification (Praveen et al.)](https://github.com/praveena2j/RJCAforSpeakerVerification) - Provided the zero-shot baseline authentication model.
- [FakeAVCeleb Dataset](https://github.com/DASH-Lab/FakeAVCeleb) - Supplied the multi-modal deepfake samples.

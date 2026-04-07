---
title: "Project Proposal: Robust Audio-Visual Biometric Verification Under Modality-Specific Deepfakes using Uncertainty-Aware Fusion and Deepfake-Aware Decision Policies"
course: "CS 228 — Biometric Security with AI"
---

# CS 228 — Biometric Security with AI
## Project Proposal

---

**Title:**
Robust Audio-Visual Biometric Verification Under Modality-Specific Deepfakes Using Uncertainty-Aware Fusion and Deepfake-Aware Decision Policies

**Team Member:**
Garvit Sharma

---

## Section A — Literature Review (≈ 1 Page)

The following three papers form the foundation of this project. They span audio-visual identity verification, multi-modal deepfake datasets, and audio spoofing detection—covering the three pillars the proposed system must address.

---

### Paper 1
**Title:** *Audio-Visual Person Verification based on Recursive Fusion of Joint Cross-Attention*
**Venue:** IEEE International Conference on Automatic Face and Gesture Recognition (FG 2024)

**Summary:**
The authors address the challenge of fusing heterogeneous audio and visual streams for speaker verification. Rather than relying on simple score-level combination, they introduce a Recursive Joint Cross-Attention (RJCA) mechanism that iteratively refines face and voice representations by allowing each modality to attend to the other. In essence, the face embedding can "query" temporal segments of the voice embedding and vice versa, enabling the model to discover complementary discriminative cues that neither modality encodes on its own. The fused representation is passed through a cosine-similarity-based verification head. Results on VoxCeleb-based evaluations demonstrate consistent improvement over both unimodal and score-fusion baselines.

**Strengths:**
- The iterative cross-attention architecture captures fine-grained inter-modal correspondences that simpler fusion (score addition, concatenation) cannot.
- Strong empirical gains on a well-established benchmark make the reported improvements credible and reproducible.
- The method is modular: any pre-trained face or voice encoder can serve as a drop-in backbone.

**Weaknesses:**
- Evaluation is conducted only on genuine audio-visual pairs; no adversarial or deepfake conditions are tested, leaving the robustness of the learned fusion unknown.
- The cross-attention mechanism substantially increases computational cost, which may limit real-time deployment.
- There is limited ablation on how the number of recursive iterations affects the quality-vs-speed trade-off.

---

### Paper 2
**Title:** *FakeAVCeleb: A Novel Audio-Video Multimodal Deepfake Dataset*
**Venue:** NeurIPS 2021 Datasets & Benchmarks Track

**Summary:**
FakeAVCeleb is introduced as the first large-scale multimodal deepfake dataset providing all four manipulated combinations: real audio + real video (genuine), fake audio + real video, real audio + fake video, and fake audio + fake video. The authors generate video fakes using face-swap and face re-enactment methods and voice fakes using voice conversion networks, seeding both from VoxCeleb celebrity identities. The dataset is paired with benchmark deepfake detection experiments at both the unimodal and multimodal level, revealing that detectors trained on single-modality fakes often fail to generalize when the complementary modality is also manipulated.

**Strengths (Research Contribution):**
- Fills a significant gap: prior deepfake datasets address either face or voice but rarely both in a controlled cross-modal manner.
- The four-class experimental matrix enables systematic study of how detectors behave under partial versus total manipulation.
- Building on VoxCeleb ensures identity diversity and known splits, facilitating fair comparison.

**Weaknesses:**
- Due to licensing restrictions, distribution is limited; researchers must request access, which can delay reproducibility.
- The generation methods used to produce fakes were state-of-the-art at the time of release; newer, more realistic generators may expose further detection gaps not benchmarked here.

---

### Paper 3 — Survey Paper
**Title:** *ASVspoof 2021: Accelerating Progress in Spoofed and Deepfake Speech Detection*
**Venue:** IEEE/ACM Transactions on Audio, Speech, and Language Processing (TASLP), 2022 (post-challenge release)

**Summary:**
ASVspoof 2021 serves as both an evaluation campaign and a comprehensive survey of audio spoofing and deepfake speech detection. The paper reviews the evolution of speech anti-spoofing from physical-access replay attacks through logical-access text-to-speech and voice conversion, culminating in a dedicated deepfake telephony task featuring codec-compressed speech. It surveys the architectures, front-ends (LFCC, MFCC, raw waveform), and back-ends (LCNN, ResNet, ECAPA) that dominated submissions, synthesizes common failure patterns—particularly under codec distortion and domain mismatch—and benchmarks submitted systems using min-tDCF and EER. The survey character of the paper lies in its breadth: it contextualizes each task within the historical trajectory of ASVspoof and connects individual system choices to broader trends in the field.

**Note:** As a survey/campaign paper, the per-paper strengths/weaknesses criteria are less applicable. The work's primary value is its aggregated empirical analysis and forward-looking research recommendations across many submitted systems.

---

## Section B — Project Proposal (≈ 2–3 Pages)

### 1. Project Overview and Problem Statement

Modern identity verification over digital channels increasingly relies on audio-visual biometrics—a combination of a person's face and voice captured simultaneously via webcam or mobile camera. Banks use this for remote account opening; call centers use it for customer authentication; enterprises use it for secure conferencing. The implicit assumption in nearly all deployed systems is that both the face and voice signals arriving at the verification engine belong to the same genuine person.

This assumption is breaking down. Deepfake technology now allows an adversary to clone a target's voice from a few seconds of audio and overlay a face swap onto an existing video with startling realism. Critically, state-of-the-art audio-visual fusion systems were designed and evaluated under the premise that both modalities are trustworthy. When only *one* modality is manipulated—say, a cloned voice paired with a genuine face—the system can still assign a high fused confidence score and incorrectly grant access. In plain terms: a verification gatekeeper that trusts both channels equally becomes easier to fool by attacking just one of them.

**Nature of Project:** *Attack characterization and defense — systematically stress-test audio-visual biometric verification systems under modality-specific deepfake substitution, quantify their failure modes, and propose an uncertainty-aware fusion strategy with a deepfake-aware accept/reject/step-up decision policy to reduce unauthorized access without degrading legitimate user experience.*

---

### 2. Key Modules and Components

The project is structured into five interconnected modules:

| Module | Description |
|---|---|
| **M1 — Enrollment Engine** | Registers per-user templates: a face embedding computed from a short enrollment clip and a speaker embedding from a reference audio segment. Templates are stored in a secure embedding database. |
| **M2 — Unimodal Verification Branches** | **Face Branch:** Detects and aligns faces per frame → extracts embeddings via a pretrained face model → aggregates (mean/attention pooling) → computes cosine similarity to the enrolled face template. **Voice Branch:** Runs Voice Activity Detection (VAD) → extracts speaker embeddings (ECAPA-TDNN style) → computes cosine similarity to the enrolled voice template. |
| **M3 — Fusion Module** | Three fusion strategies are implemented as baselines: (1) *Score Fusion* — fixed weighted sum of face and voice scores; (2) *Learned Fusion* — a small MLP trained on [s_face, s_voice, q_face, q_voice]; (3) *Cross-Attention Fusion* — recursive joint cross-attention (RJCA baseline from FG 2024). The quality terms q_face, q_voice capture signal reliability (blur, pose, SNR) and feed directly into uncertainty-weighted fusion as the primary proposed improvement. |
| **M4 — Deepfake Attack Test Harness** | Implements five controlled scenarios using FakeAVCeleb and ASVspoof 2021: S0 (genuine pair), S1 (fake video + real audio), S2 (real video + fake audio), S3 (both fake), S4 (cross-identity mismatch — face from person A, voice from person B). Metrics: False Accept Rate (FAR), Attack Success Rate (ASR), Equal Error Rate (EER), and Expected Calibration Error (ECE). |
| **M5 — Decision Policy** | A rule-based policy layer on top of the fused score: ACCEPT if fused score exceeds threshold and deepfake probability is low; REJECT if deepfake probability is high regardless of score; STEP-UP/RETRY if quality is low or the score is ambiguous. An optional integration with a video deepfake detector (MINTIME, TIFS) and an audio-visual deepfake detector (AVFF, arXiv 2024) gates decisions with an explicit manipulation signal. |

---

### 3. Tentative Timeline

| Phase | Weeks | Key Deliverables |
|---|---|---|
| **Phase 1 — Baselines** | Weeks 1–2 | Face-only and voice-only verification pipelines; score fusion and MLP fusion implemented; clean-data EER/FAR established on VoxCeleb genuine pairs |
| **Phase 2 — Attack Harness** | Weeks 3–4 | FakeAVCeleb and ASVspoof 2021 data loaders; S0–S4 substitution scenarios; first failure matrix table (FAR/ASR by scenario for all three fusion baselines) |
| **Phase 3 — Limitation Analysis** | Weeks 5–6 | Calibration analysis (ECE, reliability curves); compression and noise sweep (bitrate reduction, SNR degradation); unseen-generator generalization split |
| **Phase 4 — Proposed Improvements** | Weeks 7–9 | Uncertainty/quality-aware fusion (quality-gated weights replacing fixed α); deepfake-aware decision policy; optional MINTIME/AVFF gate; updated FAR/ASR/ECE tables |
| **Phase 5 — Final Evaluation & Write-up** | Weeks 10–12 | Full ablations (which quality signals help most; policy threshold trade-off curves); final comparative tables; paper-grade report and presentation slides |

---

### 4. Datasets

**Primary — Genuine Audio-Visual Identity Data:**
- **VoxCeleb / VoxCeleb2** (University of Oxford VGG Group). Audio-visual speaking face tracks harvested from YouTube interviews. VoxCeleb2 contains over 1 million utterances spanning 6,112 identities. Used as the genuine enrollment and verification set for all baselines and improvements.

**Deepfake Test Data:**
- **FakeAVCeleb** (NeurIPS 2021). Multimodal deepfake dataset providing fake audio, fake video, and both-fake combinations seeded from VoxCeleb identities. Forms the primary adversarial stress-test corpus for the S1–S3 attack scenarios.

**Voice Spoof/Deepfake Stress Test:**
- **ASVspoof 2021** (LA + DF tasks). Logical-access (text-to-speech, voice conversion) and deepfake telephony conditions. Provides an out-of-domain voice-only spoof test for measuring audio-branch vulnerability (S2 scenario).

**Optional — Deepfake Detector Benchmarking:**
- **DeepfakeBench** (NeurIPS 2023). Standardized evaluation framework for visual deepfake detectors. Will be used if fine-grained visual deepfake detector comparisons are added in Phase 4.

---

### 5. Nature of the Project and Expected Contributions

This project sits at the intersection of *biometric security* and *adversarial machine learning*. Its primary thrust is:

> **"Stress-test and harden audio-visual biometric verification systems against modality-specific deepfake substitution attacks."**

The work is empirical-first: baselines are established, attacked systematically, and their failure modes are quantified before any improvement is proposed. This methodology ensures that proposed defenses address real, measured weaknesses rather than hypothetical ones.

Three concrete contributions are anticipated:

1. **A structured multimodal threat evaluation** covering all practically relevant deepfake substitution scenarios (S0–S4), with standardized FAR/ASR/EER/ECE metrics across three fusion architectures.

2. **Quantification of fusion failure modes** — specifically overconfidence under single-modality deepfakes, calibration degradation, and generalization gaps to unseen deepfake generators and codec conditions.

3. **A quality-aware fusion strategy and deepfake-aware decision policy** that measurably reduce False Accept Rate and Attack Success Rate under adversarial conditions while maintaining usability (low step-up frequency) for genuine users.

The tech stack is **PyTorch**-based, with pretrained models for the face branch (e.g., MagFace) and voice branch (ECAPA-TDNN), custom-implemented fusion layers, and evaluation scripts for security and calibration metrics.

---

## References

1. G. P. Rajasekhar and J. Alam, "Audio-Visual Person Verification based on Recursive Fusion of Joint Cross-Attention," *Proc. IEEE 18th Int. Conf. Automatic Face and Gesture Recognition (FG)*, 2024.

2. H. Khalid, S. Tariq, M. Kim, and S. S. Woo, "FakeAVCeleb: A Novel Audio-Video Multimodal Deepfake Dataset," *Proc. NeurIPS Datasets and Benchmarks Track*, 2021.

3. X. Liu, X. Wang, M. Sahidullah, J. Patino, H. Delgado, T. Kinnunen, M. Todisco, J. Yamagishi, N. Evans, A. Nautsch, and K. A. Lee, "ASVspoof 2021: Towards Spoofed and Deepfake Speech Detection in the Wild," *IEEE/ACM Trans. Audio, Speech, Language Process.*, vol. 31, pp. 2507–2522, 2023, doi: 10.1109/TASLP.2023.3285283.

4. A. Nagrani, J. S. Chung, W. Xie, and A. Zisserman, "VoxCeleb: Large-Scale Speaker Verification in the Wild," *Comput. Speech Lang.*, vol. 60, 2020. (VoxCeleb2: J. S. Chung et al., INTERSPEECH 2018).

5. Z. Yan, Y. Zhang, X. Yuan, S. Lyu, and B. Wu, "DeepfakeBench: A Comprehensive Benchmark of Deepfake Detection," *Proc. Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track*, vol. 36, 2023.

6. T. Oorloff, S. Koppisetti, N. Bonettini, D. Solanki, B. Colman, Y. Yacoob, A. Shahriyari, and G. Bharaj, "AVFF: Audio-Visual Feature Fusion for Video Deepfake Detection," *arXiv:2406.02951*, 2024.

7. D. A. Coccomini, G. Kordopatis-Zilos, G. Amato, R. Caldelli, F. Falchi, and S. Papadopoulos, "MINTIME: Multi-Identity Size-Invariant Video Deepfake Detection," *IEEE Trans. Inf. Forensics Security (TIFS)*, 2024.

8. Q. Meng, S. Zhao, Z. Huang, and F. Zhou, "MagFace: A Universal Representation for Face Recognition and Quality Assessment," *Proc. IEEE/CVF Conf. Computer Vision and Pattern Recognition (CVPR)*, 2021.

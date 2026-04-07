# 🎤 Speaker Notes — Biometric Security Presentation
### Robust Audio-Visual Biometric Verification Under Deepfake Attacks
**CS 228 | Garvit Sharma | March 5, 2026**

---

## How to Use This Document

Read each section before its corresponding slide. The **"Say this"** blocks are natural-language scripts you can speak from. Everything is explained in plain English — no assumed knowledge.

---

## Slide 1 — Title

**Say this:**
> "Good morning/afternoon everyone. My name is Garvit Sharma and today I'll be presenting my project on robust audio-visual biometric verification. The full title is a mouthful, but the idea is simple: modern systems that use both your face and your voice to verify your identity can be tricked if an attacker forges just one of those two signals. My project is about figuring out exactly *how* they fail, *how badly*, and *how we can fix it*."

---

## Slide 2 — Contents (Agenda)

**Say this:**
> "Here's what I'll cover. We'll start with a quick background on the problem, look at three key research papers that informed this project, then go into the datasets and models we'll use, the system pipeline, the attack scenarios we'll test, and finally the timeline. Let me get started."

---

## Slide 3 — Background

**Say this:**
> "So why does this problem exist? Deepfake technology — the ability to synthetically generate a convincing face or voice — has advanced dramatically. You can now clone someone's voice from just a few seconds of audio. Face-swap is available in consumer apps. Meanwhile, the biometric verification systems used in banks, hospitals, and enterprise login still operate under a dangerous implicit assumption: that when a face and a voice arrive together, *both* belong to a real, live person. My project challenges that assumption. Our pipeline will characterize attacks, quantify failures, and propose a smarter decision policy."

**Key points to emphasize:**
- "Deepfake tech is cheap and accessible — this is not a theoretical concern"
- "Banking eKYC, call-centre auth, secure conferencing — these are real deployments at risk"
- "A *partial* deepfake — only the face or only the voice is fake — is often enough to fool a fusion system"

---

## Slide 4 — Problem Statement

**Say this:**
> "Let me make the problem concrete. When you enroll in a biometric system, it stores a template of your face embedding and voice embedding. When you try to verify later, it computes a similarity score for your face and a similarity score for your voice, and *fuses* them into one number. If that number is above a threshold — you're in. The problem: if an attacker submits a real voice but a fake face — or vice versa — the one real signal can carry enough weight in the fusion that the combined score still crosses the threshold. The system says 'ACCEPT' when it should say 'REJECT'."

**Key terms:**
- **Embedding** — A numerical vector (list of numbers) that represents a face or voice as a point in high-dimensional space. Similar faces/voices have embeddings close to each other.
- **Cosine similarity** — A way to measure how similar two vectors are. Score of 1 = identical, 0 = completely different, -1 = opposite.
- **Threshold** — A cut-off score. If similarity > threshold → accept. Otherwise → reject.
- **Fusion score** — The combined score from face + voice. Usually a weighted average.

---

---

## 📄 RESEARCH PAPERS (Slides 5, 6, 7)

---

## Slide 5 — Paper 1: RJCA Fusion (IEEE FG 2024)

### Full Title
*"Audio-Visual Person Verification based on Recursive Fusion of Joint Cross-Attention"*

### What is it about?
Traditional audio-visual verification takes a face score (0–1) and a voice score (0–1) and simply adds them with some weights (e.g., 0.6 × face + 0.4 × voice). This is called **score-level fusion** and it's very basic. RJCA (Recursive Joint Cross-Attention) does something more sophisticated: it lets the *face features directly interact with the voice features* at the embedding level, before any scoring happens.

Specifically:
- The face embedding "queries" different time segments of the voice to find which voice segments are most relevant to recognizing the person's identity.
- The voice then does the same back to the face.
- This is done **recursively** — multiple passes, each refining the representation.
- The result is a unified embedding that captures correlated face+voice cues.
- This is passed through a cosine-similarity head to get the final score.

### Why are we using this paper?
RJCA is the **state-of-the-art** for audio-visual person verification. We use it as our primary research **baseline** to compare against. Our goal isn't to beat it on clean data — it's to show what happens to its performance *when one modality is fake*.

### What do we get from it?
- A pretrained cross-attention fusion architecture we can use directly
- A benchmark result on clean data to compare against our adversarial results
- The conceptual framework for multi-level feature fusion

### Pros
- Captures fine-grained relationships between face and voice at the feature level — much more powerful than score fusion
- Modular: you can swap in any face or voice encoder and the cross-attention still works
- Published results show consistent gains over all simpler baselines

### Cons
- The evaluation **never tests deepfakes**. All results are on genuine (real face + real voice) pairs. We don't know how it behaves when one is fake.
- Cross-attention is computationally heavy — harder to deploy in real-time systems
- No analysis of how the quality of each modality affects the fusion result

**Say this:**
> "This paper by Rajasekhar and Alam from IEEE FG 2024 introduces RJCA — Recursive Joint Cross-Attention. Think of it as a conversation between your face features and your voice features. Rather than just averaging two scores, the face asks the voice 'which part of you helps identify this person?' and vice versa. This back-and-forth happens multiple times, producing a much richer combined representation. We'll use this as our fusion baseline — then stress-test it against deepfake attacks."

---

## Slide 6 — Paper 2: FakeAVCeleb (NeurIPS 2021)

### Full Title
*"FakeAVCeleb: A Novel Audio-Video Multimodal Deepfake Dataset"*

### What is it about?
This paper introduces the **first large-scale dataset** that provides **all four combinations** of real/fake audio and real/fake video:

| Combo | Video | Audio |
|---|---|---|
| RR | Real | Real |
| RF | Real | Fake (voice converted) |
| FR | Fake (face-swapped) | Real |
| FF | Fake | Fake |

This is built on top of the VoxCeleb celebrity dataset — so the identities and the evaluation protocol are already well-established. The deepfakes use face-swap, face re-enactment (for video) and voice conversion networks (for audio).

### Why are we using this paper / dataset?
It directly maps to our **S0–S4 attack scenarios** (our threat matrix). Without this dataset, we'd have no adversarial test data that gives us all four AV modality combinations. It lets us systematically test the fusion system under every kind of manipulation.

### What do we get from it?
- A ready-made adversarial test corpus aligned to VoxCeleb (same celebrity identities)
- The ability to run S1 (fake video only), S2 (fake audio only), S3 (both fake), S4 (cross-identity mismatch) experiments with real deepfake samples
- Published baselines showing that single-modality detectors fail when both modalities are manipulated

### Pros
- Only dataset covering all 4 AV manipulation combos as of 2021
- VoxCeleb-aligned — we can compare results fairly to other published work
- Directly answers our research question at the data level

### Cons
- Access is **request-only** (you have to email the authors and wait for approval) — this can delay experiments
- Generated with 2021-era deepfake tools; newer and more realistic fakes may expose even larger gaps

**Say this:**
> "The second paper is FakeAVCeleb from NeurIPS 2021. It's actually a dataset paper — its primary contribution is a systematic, large-scale collection of audio-visual deepfakes across all four combinations: real face + real voice, real face + fake voice, fake face + real voice, and fake face + fake voice. This is exactly the data we need to run our experiments. We'll use it as the main adversarial corpus for our threat matrix."

---

## Slide 7 — Paper 3: ASVspoof 2021 (IEEE/ACM TASLP 2022)

### Full Title
*"ASVspoof 2021: Accelerating Progress in Spoofed and Deepfake Speech Detection"*

### What is it about?
This is a **survey paper and evaluation campaign** — not a single model, but a systematic benchmarking exercise covering dozens of submitted anti-spoofing systems. It covers:

- **PA (Physical Access)** — replay attacks where someone plays a recording of your voice through a speaker
- **LA (Logical Access)** — synthesized or voice-converted speech (TTS, VC)
- **DF (Deepfake)** task — a new track added in 2021 for deepfake speech distributed over telephone codecs

It reviews which front-ends (LFCC, MFCC, raw waveform) and back-end classifiers (LCNN, ResNet, ECAPA) work best, and benchmarks them all with standardized metrics.

**Key finding:** The biggest failure mode is **codec distortion** (telephone compression changes the audio in ways that confuse detectors) and **domain mismatch** (a model trained on studio audio fails on noisy real-world audio).

### Why are we using this paper?
It guides our **voice branch evaluation**. The ASVspoof 2021 dataset's LA and DF tasks serve as our S2 (fake audio only) stress test. The paper also tells us which front-end features and metrics to use.

### What do we get from it?
- The ASVspoof 2021 dataset for voice-only spoof testing (S2 scenario)
- Guidance on using LFCC as an audio front-end
- Standardized metrics: EER and min-tDCF (explained below)
- A map of known failure modes to look for in our own experiments

### Pros
- Aggregates results across many systems — gives us a realistic sense of what "hard" looks like for voice spoofing
- Identifies practical failure modes (codec, domain shift) we can replicate
- Freely available dataset

### Cons
- It's a survey/campaign paper — it doesn't introduce one novel model or approach, so "strengths vs. weaknesses" framing is less direct
- 2021-era data: neural codec language models (like VALL-E, which can clone voices in 3 seconds) were not yet available when this was run

**Say this:**
> "The third paper is ASVspoof 2021. This is a benchmarking campaign that systematically tested dozens of systems against synthetic and deepfake speech. Think of it as a standardized exam for anti-spoofing models. It revealed that codec compression and domain mismatch are the main killers — a system trained on clean audio often fails on telephone-quality speech. We'll use their dataset for our voice-only attack scenario, and adopt their metrics: EER and min-tDCF."

---

---

## 📊 METRICS GLOSSARY — Explained in Plain English

### FAR — False Accept Rate
**What it is:** The percentage of impostor (fake/attacker) attempts that the system incorrectly *accepts*.

**Example:** If 100 attackers try to log in and the system lets 5 of them through → FAR = 5%.

**Why it matters:** A high FAR = the system is easily fooled. Under deepfake attack, FAR shoots up dramatically — that's what we're measuring.

---

### FRR — False Reject Rate
**What it is:** The percentage of genuine users that the system incorrectly *rejects*.

**Example:** You're trying to log in with your real face and voice, but the system says "no" → FRR.

**Why it matters:** FAR and FRR trade off. Lowering the threshold reduces FRR but increases FAR and vice versa.

---

### EER — Equal Error Rate
**What it is:** The point where FAR = FRR. A single number that summarizes a system's overall accuracy across all possible threshold settings.

**Example:** EER = 3% means at the optimal threshold, both the false accept rate and false reject rate are 3%.

**Why it matters:** Lower EER = better system. It's the most common metric in biometric and speaker verification papers. We'll report EER before and after deepfake attacks to show the degradation.

---

### ASR — Attack Success Rate
**What it is:** The percentage of deepfake attack attempts that successfully fool the system (i.e., get accepted).

**Example:** 100 fake-face attempts → 40 accepted → ASR = 40%.

**Why it matters:** Directly measures how vulnerable the system is to each specific attack type (S1, S2, S3, S4).

**Difference from FAR:** FAR is computed over all impostor attempts. ASR is specifically computed only over *deepfake* impostor attempts.

---

### ECE — Expected Calibration Error
**What it is:** A measure of how well the system's *confidence score* matches reality. A well-calibrated system that says "I'm 80% sure this is genuine" should be correct 80% of the time.

**Why it matters:** Even if a system has a decent EER, it may be poorly calibrated — reporting high confidence on incorrect decisions. This is dangerous in a security context. Our uncertainty-aware fusion should reduce ECE.

**Formula (simplified):** Average absolute difference between predicted confidence and actual accuracy across score bins.

---

### min-tDCF — Minimum Tandem Detection Cost Function
**What it is:** A metric used in ASVspoof that jointly evaluates the anti-spoofing system *alongside* the speaker verification system. It penalizes spoofing attacks that fool both components.

**Why it matters:** It captures the total cost in a real deployed system where both layers must work together. We'll use it for voice-branch-specific evaluation.

**Simpler version:** Think of it as a weighted sum of FAR and FRR, with weights tuned to the cost of each error in a real security scenario.

---

---

## 🗄️ DATASETS EXPLAINED

| Dataset | What it contains | Why we use it |
|---|---|---|
| **VoxCeleb2** | Video + audio clips of 6,112 celebrities from YouTube. Genuine, unmanipulated. | Enrollment + genuine verification baseline — the "ground truth" for real A/V pairs. |
| **FakeAVCeleb** | All 4 AV combos (RR, RF, FR, FF) built on VoxCeleb identities using deepfake tools. | Main adversarial test corpus for S1, S2, S3, S4 scenarios. |
| **ASVspoof 2021** | Synthesized and deepfake speech datasets (PA, LA, DF tracks). Freely downloadable. | S2 (fake audio) stress test. Also our source of out-of-domain voice spoofing samples. |
| **FaceForensics++ (FF++)** | 1,000 real videos + deepfake versions (FaceSwap, DeepFakes, Face2Face, NeuralTextures). | Video deepfake generalization test for S1. Checks if our system transfers to unseen video fakes. |
| **DFDC** | Facebook's Deepfake Detection Challenge dataset. ~100K videos. Free on Kaggle. | Large-scale robustness test — much more varied than FakeAVCeleb. |
| **WaveFake** | Fake speech generated by 6 different neural vocoders (GAN-based, diffusion, etc.). Free. | Unseen vocoder generalization — tests if our voice branch detects fakes from *new* synthesis systems. |
| **LFW** | 13,000+ face images of public figures. Standard face verification benchmark. | EER baseline for our face branch before integrating voice. |

---

---

## ⚙️ MODELS EXPLAINED

### 1. MagFace (Face Embedder + Quality Score)
**What it does:** Takes a face image and produces two outputs:
1. A **face embedding vector** — encodes who the person is (identity)
2. A **face quality score q_face** — encodes *how good* the face image is (is it blurry? occluded? badly lit?)

**Why it's special:** Most face recognition models only give you an embedding. MagFace also gives you a quality estimate, which is critical for our *uncertainty-aware fusion*. If q_face is low (bad image), we should trust the voice branch more.

**Training data:** MS1MV2 (a cleaned version of MS-Celeb-1M with ~5.8M face images of 85K celebrities).

**Availability:** Free, open-source on GitHub. Pretrained weights available for download.

---

### 2. ECAPA-TDNN (Speaker Embedder)
**Full name:** Emphasized Channel Attention, Propagation and Aggregation — Time Delay Neural Network

**What it does:** Takes raw audio (waveform or spectrogram) and produces a **speaker embedding** — a vector that encodes "who is speaking" regardless of what words are being said. Similar to MagFace but for voices.

**Why it's good:** ECAPA-TDNN introduced channel attention (the model focuses on the most informative frequency channels) and multi-scale feature aggregation (it looks at patterns across different time scales simultaneously). This gives it state-of-the-art performance on speaker verification benchmarks.

**How to load it:** One line via SpeechBrain or HuggingFace. Pretrained on VoxCeleb2.

**Availability:** Free. `pip install speechbrain` then `EncoderClassifier.from_hparams("speechbrain/spkrec-ecapa-voxceleb")`

---

### 3. RetinaFace (Face Detection & Alignment)
**What it does:** Detects faces in an image/frame and returns:
- Bounding boxes (where the face is)
- Five facial landmarks (eye corners, nose tip, mouth corners)
- Uses landmarks to align ("straighten") the face before passing it to MagFace

**Why we need it:** MagFace expects a cleanly cropped, aligned face. RetinaFace ensures this preprocessing happens correctly even with different head poses and lighting.

**Availability:** Free. `pip install retina-face`

---

### 4. Silero VAD (Voice Activity Detection)
**Full name:** Silero Voice Activity Detector

**What it does:** Listens to an audio clip and labels each short segment as "speech" or "silence/noise." We use it to extract only the parts where the person is actually speaking before passing audio to ECAPA-TDNN.

**Why we need it:** If we include silence or background noise in the voice embedding, it hurts accuracy. VAD pre-filters the audio to only speech segments.

**Availability:** Free. `torch.hub.load('snakers4/silero-vad', 'silero_vad')`

---

### 5. RJCA (Recursive Joint Cross-Attention Fusion)
*Already covered in Paper 1 section above.*

**In summary:** Takes face embedding + voice embedding and fuses them via a cross-attention mechanism that lets each modality selectively focus on informative parts of the other. We use the official implementation from the paper authors' GitHub as our primary fusion baseline.

---

### 6. PyTorch
**What it is:** The core deep learning framework used throughout the project for:
- Loading and running pretrained models (MagFace, ECAPA-TDNN, RJCA)
- Implementing our custom fusion layers (MLP fusion, uncertainty-weighted fusion)
- Training our deepfake-aware decision policy
- Running all evaluation scripts

**Why not TensorFlow?** All the models we've chosen have official PyTorch implementations. SpeechBrain, which provides ECAPA-TDNN, is PyTorch-native.

---

---

## 🏗️ SLIDE 9 — 5-Module Pipeline — DEEP DIVE

This is the architecture of our system. Think of it as a factory with 5 stations that a verification request passes through in order.

---

### M1 — ENROLL (Enrollment Engine)

**What happens:**
When you sign up for the system, it asks you to record a short video clip (a few seconds, saying your name or a phrase). The system:
1. Runs RetinaFace to detect and align your face from each frame
2. Runs MagFace to get a face embedding and quality score per frame
3. Aggregates the per-frame embeddings (e.g., average pooling) into one enrolled **face template** + mean quality
4. Runs Silero VAD to extract speech-only segments from the audio
5. Runs ECAPA-TDNN to get a voice embedding
6. Stores `{user_id: (face_template, voice_template)}` in the **embedding database**

This happens once per user, offline. The database is then used for all future verifications.

---

### M2 — VERIFY (Unimodal Verification Branches)

**What happens at verification time (two parallel branches):**

**Face branch:**
1. RetinaFace detects + aligns face from the incoming video
2. MagFace produces: embedding `e_face` and quality `q_face`
3. Cosine similarity computed between `e_face` and the enrolled face template → gives `s_face` (score 0–1)

**Voice branch:**
1. Silero VAD extracts speech segments from incoming audio
2. ECAPA-TDNN produces voice embedding `e_voice` and quality can be estimated from embedding norm
3. Cosine similarity computed between `e_voice` and enrolled voice template → gives `s_voice` (score 0–1)

At this point we have: `(s_face, q_face, s_voice, q_voice)` — four numbers.

---

### M3 — FUSE (Three Fusion Strategies)

We test three ways of combining `s_face` and `s_voice`:

**Strategy 1 — Score Fusion (fixed α)**
```
s_fused = α × s_face + (1 - α) × s_voice
```
Simple weighted average. α is a hyperparameter (e.g., 0.6). No learning involved, fastest to deploy.

**Strategy 2 — Learned MLP**
```
s_fused = MLP([s_face, s_voice, q_face, q_voice])
```
A small neural network trained to combine the four inputs into one score. The MLP can learn that *when q_face is low, trust s_voice more*. This is our **uncertainty-aware fusion** — quality scores feed directly into the decision.

**Strategy 3 — RJCA (Research Baseline)**
The full recursive cross-attention mechanism from Paper 1 — operates at the embedding level, not the score level. More powerful but more compute-heavy.

By comparing all three, we can show exactly *how much* of the improvement comes from richer fusion architecture vs. uncertainty awareness.

---

### M4 — ATTACK (Deepfake Test Harness)

This module doesn't run at inference time — it's the **evaluation framework** we set up to systematically attack M1–M3.

**What it does:**
- Loads adversarial test data from FakeAVCeleb, ASVspoof 2021, FF++, WaveFake
- Constructs test pairs for each of the 5 scenarios:

| Scenario | Video | Audio |
|---|---|---|
| S0 | Real | Real |
| S1 | Fake face | Real voice |
| S2 | Real face | Fake voice |
| S3 | Fake face | Fake voice |
| S4 | Person A's face | Person B's voice (mismatch) |

- Runs each test pair through M2 + M3 and records whether the system accepted or rejected
- Computes FAR, ASR, EER, ECE for each (scenario × fusion strategy) combination

---

### M5 — POLICY (Deepfake-Aware Decision Policy)

**The problem with M3 alone:** The fusion score tells us *how confident the system is that this person is genuine*, but it doesn't know *whether a deepfake attack is occurring*.

**The solution:** Add a parallel deepfake detector signal. Optionally integrate an off-the-shelf deepfake detector (e.g., AVFF or MINTIME) that outputs `p_fake` — the probability that the video/audio is fake.

**Three-way policy decision:**

| Condition | Decision |
|---|---|
| `s_fused > θ_accept` AND `p_fake < θ_fake` AND `q_face, q_voice > θ_q` | ✅ ACCEPT |
| `p_fake > θ_fake` (even if s_fused is high) | ❌ REJECT |
| `q_face < θ_q` OR `q_voice < θ_q` OR `θ_low < s_fused < θ_high` | 🔄 STEP-UP (challenge user for extra verification) |

**Why this is better than a fixed threshold:**
- Old approach: reject for low score, accept for high score — a single knob
- New approach: reject if *deepfake detected*, step up if *uncertain*, accept only if *all signals agree*
- This lets us dramatically cut FAR under deepfake attack without degrading the experience of genuine users

---

## Slide 10 — Attack Scenarios Table

Read the table row by row and explain:
- **S0 (Genuine baseline):** This is our control. Normal system operation — both face and voice are real. We verify the system works correctly before any attacks.
- **S1 (Video deepfake):** The attacker uses target person's real voice (stolen from a call recording) but substitutes a face-swapped video. Simulates a social engineering attack over a video call.
- **S2 (Audio deepfake):** Attacker shows their real face but plays a voice-cloned audio clip. The face might not match the voice of the target.
- **S3 (Full deepfake):** Both modalities are fake. Most complex attack to pull off, but also the most damaging if successful.
- **S4 (Cross-identity):** No deepfake involved — attacker claims to be the target, uses their own face and own voice. Tests the most basic verification failure mode.

---

## Slide 11 — Timeline

Walk through each phase briefly:
- **Phase 1 (Wks 1–2):** Set up the full pipeline, establish clean baselines — EER and FAR with no attacks. This is our reference point.
- **Phase 2 (Wks 3–4):** Build the adversarial test harness. Load all datasets, run S0–S4 evaluations. Produce first failure tables.
- **Phase 3 (Wks 5–6):** Deep analysis — calibration (ECE), codec robustness sweeps, unseen vocoder tests (WaveFake).
- **Phase 4 (Wks 7–9):** Implement the improvements — uncertainty-aware MLP fusion, deepfake-aware policy.
- **Phase 5 (Wks 10–12):** Full ablations, write the report, finalize the presentation.

---

## Slide 12 — Thank You / Questions

**Likely questions and answers:**

**Q: "How do you collect the deepfake data — do you generate it yourself?"**
> "For most data we use pre-existing datasets — FakeAVCeleb, ASVspoof 2021, FF++. These are research datasets generated by the original paper authors. We don't generate new deepfakes ourselves, which keeps our evaluation consistent with previous literature."

**Q: "Is this system ready to deploy?"**
> "Not yet — this is a research evaluation project. We're quantifying failure modes and proposing improvements. A deployed system would require additional work: latency optimization, live camera/microphone handling, compliance with biometric data regulations, etc."

**Q: "What's the most interesting result you expect to find?"**
> "I expect S1 (fake video only) to be the most dangerous scenario, because face recognition systems tend to have higher weights in AV fusion (faces are considered more reliable than voices). A convincing face-swap with real voice might score very high and easily cross the acceptance threshold."

---

## Key Acronyms — Quick Reference Card

---

## ❓ Your Questions — Detailed Answers

---

### Q1. What is Cross-Attention and Cross-Attention Fusion?

**Attention (the basic idea):**
Imagine reading a sentence and trying to understand the word "bank". You don't weigh every other word equally — you pay more *attention* to words like "money", "loan", "river" depending on context. In deep learning, an **attention mechanism** does the same: it assigns different weights (importance scores) to different positions in a sequence, allowing the model to focus on the most relevant parts.

**Self-Attention:** A sequence attending to *itself* (e.g., a sentence figuring out which words matter for understanding each other word). Used in Transformers.

**Cross-Attention:** One sequence *query-ing* a *different* sequence. Sequence A (e.g., face features) computes what's most important in Sequence B (voice features), and vice versa.

> **Analogy:** You're reading subtitles while watching a lip-sync video. Your eyes jump back and forth: the subtitle word "run" makes you look at the part of the video where the lips are moving fast. That selective looking is cross-attention.

**Cross-Attention Fusion (in our context):**
In RJCA, face embeddings and voice embeddings cross-attend to each other:
1. Face features ask: *"Which voice segment is most informative for identifying this person?"*
2. Voice features ask: *"Which face feature activations support what we're hearing?"*
3. This is done **recursively** — multiple rounds of back-and-forth, each refining the representation.
4. Final fused embedding encodes correlated face+voice identity cues — much more powerful than just averaging two scores.

**vs. simple score fusion:** Score fusion = 0.6 × face_score + 0.4 × voice_score. No information exchange between modalities. Cross-attention actually lets the modalities *talk to each other* at the feature level.

---

### Q2. What is VoxCeleb / VoxCeleb2?

VoxCeleb is a large-scale, publicly available **speaker recognition dataset** created by researchers at Oxford University.

- **Source:** Automatically scraped from YouTube — interviews, red-carpet events, talk shows of celebrities.
- **VoxCeleb1 (2017):** ~1,251 celebrities, ~145K utterances.
- **VoxCeleb2 (2018):** Expanded to **6,112 celebrity speakers, over 1 million utterances** across diverse ethnicities, ages, accents, and recording conditions.
- **Why celebrities?** Easy to verify identity from public records. Also, YouTube content has varied audio quality, background noise, and head poses — making it a realistic "in the wild" benchmark.
- **Why we use it:** VoxCeleb2 gives us genuine (unmanipulated) face+voice clips to train and evaluate our baseline verification system. FakeAVCeleb is *built on top of VoxCeleb* identities, so our genuine data and deepfake data share the same speaker pool — making comparisons fair.

---

### Q3. Elaboration: "Reviews front-ends (LFCC, MFCC, raw) and back-ends (LCNN, ResNet, ECAPA)"

In audio anti-spoofing, the pipeline has two stages: **front-end** (feature extraction) and **back-end** (classifier/embedder).

#### Front-ends (How to represent audio):

**MFCC — Mel-Frequency Cepstral Coefficients**
- The most classic audio feature. Mimics how the human ear perceives sound — uses a non-linear frequency scale (Mel scale) weighted towards lower frequencies where speech is most informative.
- Process: audio → spectrogram → filter by Mel filter bank → log → Discrete Cosine Transform → compact vector per frame.
- Used in traditional speech/speaker recognition for decades.

**LFCC — Linear Frequency Cepstral Coefficients**
- Same idea as MFCC, but the frequency bins are **linearly spaced** rather than perceptually scaled.
- Shown to work better for **anti-spoofing** because synthetic speech often has artifacts at higher frequencies that MFCC's Mel scale de-emphasizes — LFCC catches them better.
- ASVspoof campaigns popularized LFCC for countermeasure systems.

**Raw waveform**
- Feed the raw audio signal (just numbers: amplitude at each millisecond) directly into a neural network.
- No manual feature engineering. The network learns its own features.
- More computationally intensive but can capture subtle artifacts not visible in spectrograms.

#### Back-ends (The classifier/embedder):

**LCNN — Light Convolutional Neural Network**
- A CNN with special "Max-Feature-Map" activation that selects the most discriminative neurons.
- Lightweight and fast. Widely used as the baseline back-end in ASVspoof campaigns.

**ResNet — Residual Network**
- Deep CNN with skip connections ("shortcuts" that add the input of a layer to its output). Prevents the vanishing gradient problem, enabling much deeper networks.
- In audio: applied to spectrograms as if they were images. Various depths: ResNet-18, ResNet-34, etc.
- Gives stronger classification performance than LCNN on most benchmarks.

**ECAPA-TDNN — Emphasized Channel Attention, Propagation and Aggregation TDNN**
- State-of-the-art for speaker recognition. Adds channel attention (focuses on the most informative frequency channels), multi-scale feature aggregation, and better temporal modeling.
- We use this as our **voice embedder** (M2 module). It was pretrained on VoxCeleb2 and is available off-the-shelf via SpeechBrain.

---

### Q6. What is FF++ (FaceForensics++)?

**Full name:** FaceForensics++ (published at ICCV 2019 by Rössler et al.)

**What it contains:**
- 1,000 real YouTube video sequences
- Manipulated versions generated by **4 different forgery methods:**
  1. **DeepFakes** — face-swap using autoencoders (the original deepfake method)
  2. **FaceSwap** — graphics-based face replacement
  3. **Face2Face** — facial expression transfer (re-enactment)
  4. **NeuralTextures** — neural rendering of face texture
- Each video at multiple compression levels (raw, light compression, heavy compression)

**Why it's important:**
FF++ became the de-facto standard benchmark for video deepfake detection. Most published deepfake detection papers report results on FF++, so it allows fair comparison to published work.

**Why we use it:**
For our **S1 scenario (fake video, real audio)** — FF++ gives us video deepfakes generated by tools *different* from FakeAVCeleb. Testing on both checks if our system generalizes across different manipulation methods, not just the ones it was trained/evaluated on.

---

### Q7. What is Uncertainty-Aware Fusion?

**The problem with fixed-weight fusion:**
Simple score fusion does: `s_fused = 0.6 × s_face + 0.4 × s_voice`
This assumes face is always 60% reliable and voice is always 40% reliable — regardless of image quality, lighting, audio noise, etc.

**The idea:**
Uncertainty-aware fusion adapts the weights based on *how confident* we are in each signal:
- If the face is blurry or occluded (low quality → low q_face) → reduce face weight, trust voice more
- If audio is noisy or clipped (low quality → low q_voice) → reduce voice weight, trust face more
- If both are high quality → standard fusion

**How we implement it:**
MagFace gives us `q_face` (face quality score) and ECAPA embedding norms can proxy voice quality. We train a small **Learned MLP** that takes `[s_face, s_voice, q_face, q_voice]` as input and learns the optimal fusion weights from data.

The MLP can learn things like: *"When q_face < 0.4, ignore s_face and rely on s_voice"* — something a hardcoded 60/40 split can never do.

**Why it matters under deepfake attack:**
Deepfake faces often have subtle quality artifacts (blurring around edges, inconsistent lighting). A quality-aware system automatically down-weights a suspicious-quality face signal — inadvertently reducing its attack surface even before applying a deepfake detector.

---

### Q8. What is a Deepfake-Aware Decision Policy?

**Standard biometric decision:** Single threshold θ. If `s_fused > θ` → ACCEPT, else → REJECT. One knob, binary outcome.

**The problem:** Even if `s_fused` is high, it doesn't mean the *content is genuine*. A deepfake attack can produce a high fusion score while the video/audio is entirely synthetic.

**The deepfake-aware policy adds a second signal:** `p_fake` — the probability that the presented face/voice is a deepfake, estimated by an optional detector (e.g., AVFF, MINTIME).

**Three-way decision gate:**

| Condition | Decision | Why |
|---|---|---|
| `s_fused > θ_accept` AND `p_fake < θ_fake` AND quality ok | ✅ **ACCEPT** | All signals agree: high similarity, low deepfake probability, good quality |
| `p_fake > θ_fake` (even if s_fused is high) | ❌ **REJECT** | Deepfake detected — block regardless of score |
| Score ambiguous OR quality low | 🔄 **STEP-UP** | Ask for additional challenge (PIN, OTP, re-record) before final decision |

**Why this is powerful:**
- Eliminates the scenario where a highly convincing deepfake gets through just because the score is high
- The STEP-UP state is a key innovation — instead of hard ACCEPT/REJECT, it gracefully escalates uncertain cases
- Genuine users with low-quality inputs get a STEP-UP (fair) rather than REJECT (frustrating)
- Attackers with convincing deepfakes get REJECTED outright (secure)

**In plain words:** "If the system smells a deepfake, reject immediately. If it's unsure, ask for more proof. Only ACCEPT when all signs clearly point to genuine."

---

### Q10. What does "Ablation" mean here?

"Ablation" comes from medical science — surgically removing a part to study its function. In ML/AI research it means:

> **Systematically removing or disabling one component at a time to see how much each part contributes to the overall performance.**

**Example in our project:**
Our full system has: quality-aware fusion + deepfake-aware policy + uncertainty weighting.

An ablation study would run:
1. Full system → EER = X%
2. Remove deepfake policy (only quality-aware fusion) → EER goes up to Y%
3. Remove quality weighting (only fixed fusion) → EER goes up to Z%
4. Remove both (bare score fusion) → EER = baseline

The gaps between these reveal the individual contribution of each component.

**Why it matters:** Without ablation, you can't tell if your improvement comes from the fusion design, the policy, the datasets, or just luck. Ablation is how you *prove* each module is earning its keep.

**In plain words:** "Turn things off one by one to prove that each piece actually matters."

---

| Acronym | Full Form | One-Line Definition |
|---|---|---|
| AV | Audio-Visual | Face + Voice together |
| FAR | False Accept Rate | % of impostors wrongly accepted |
| FRR | False Reject Rate | % of genuine users wrongly rejected |
| EER | Equal Error Rate | Point where FAR = FRR — overall accuracy |
| ASR | Attack Success Rate | % of deepfake attacks that fool the system |
| ECE | Expected Calibration Error | How well confidence matches actual accuracy |
| min-tDCF | Minimum Tandem Detection Cost Function | Combined cost of spoofing + speaker verification failure |
| RJCA | Recursive Joint Cross-Attention | Cross-modal fusion architecture (Paper 1) |
| TDNN | Time Delay Neural Network | Architecture for sequential audio data |
| ECAPA | Emphasized Channel Attention, Propagation and Aggregation | Specific TDNN variant for speaker recognition |
| TTS | Text-to-Speech | AI generating synthetic speech from text |
| VC | Voice Conversion | AI transforming one person's voice to sound like another |
| VAD | Voice Activity Detection | Detecting which parts of audio contain speech |
| PA | Physical Access (ASVspoof context) | Replay attack using a speaker/recording |
| LA | Logical Access (ASVspoof context) | Synthesized/converted speech attack |
| DF | Deepfake (ASVspoof context) | Neural deepfake speech track |
| MLP | Multi-Layer Perceptron | Simple neural network (fully connected layers) |
| LFCC | Linear Frequency Cepstral Coefficients | Audio feature representation derived from spectrogram |
| MFCC | Mel-Frequency Cepstral Coefficients | Common audio feature, perceptually weighted |
| FF++ | FaceForensics++ | Video deepfake dataset (ICCV 2019) |
| DFDC | DeepFake Detection Challenge | Facebook's large-scale deepfake dataset |

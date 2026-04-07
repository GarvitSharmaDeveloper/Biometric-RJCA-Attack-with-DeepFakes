# 🎙️ 15-Minute Presentation Script
### Robust Audio-Visual Biometric Verification Under Deepfake Attacks
**CS 228 | Garvit Sharma | March 5, 2026**

---

> **Pacing guide:** 15 min = 900 seconds. Each slide gets a time budget below.
> Speak at ~130 words/minute. Pause 2–3 seconds between slides.
> Bold text = **emphasise these words** when speaking.

---

## 🟣 SLIDE 1 — Title ⏱️ ~30 sec

*[Click to open. Let the slide render. Make eye contact with the room.]*

> "Good [morning / afternoon] everyone. My name is **Garvit Sharma**, and I'm presenting my project for CS 228 — Biometric Security with AI.
>
> The title is a mouthful, so let me break it down in one sentence: **Modern face-and-voice verification systems can be tricked by deepfakes — and my project is about figuring out exactly how, and what we can do about it.**
>
> Let's get started."

---

## 🟣 SLIDE 2 — Contents ⏱️ ~30 sec

> "Here's the roadmap for today. I'll start with a quick background about me and then motivate the problem. Then we'll go through the system I'm building, the attack scenarios I'll test, the datasets and models, the three key research papers that shaped this work, and finally a proposed timeline.
>
> Let's dive in."

---

## 🟣 SLIDE 3 — About Me ⏱️ ~60 sec

> "A bit about me. I'm a graduate student here focusing on adversarial machine learning and multi-modal AI. I've worked as a Student Assistant at IMS and as an Adobe Ambassador on campus.
>
> On the industry side, I spent time at **Deloitte USI** in Cyber Risk and Advisory — so I've seen firsthand how real the security stakes are. I also co-founded **Covid Yodha**, a social-impact volunteer network during the pandemic, and I founded the **Coding Ninjas Club** at SRM University.
>
> This project sits squarely at the intersection of my cybersecurity background and my AI research interests. Deepfakes are not a theoretical concern — they are being actively used to bypass deployed biometric systems in banking and enterprise environments, and that's exactly the problem I want to tackle."

---

## 🟣 SLIDE 4 — Background ⏱️ ~60 sec

> "So here's the context. Deepfake technology has evolved dramatically. You can now **clone someone's voice from just a few seconds of audio**. Face-swap is available in consumer apps for free. Meanwhile, audio-visual biometric verification — the kind used in remote KYC for banks, call-center authentication, and enterprise secure login — operates under a dangerous implicit assumption: that when a face and a voice arrive together, both belong to a real, live person.
>
> My project challenges that assumption. I'll build a pipeline that characterizes exactly how these systems fail when one or both modalities are forged, quantify those failures with rigorous metrics, and propose a smarter decision policy to defend against them."

---

## 🟣 SLIDE 5 — Problem Statement ⏱️ ~90 sec

> "Let me make the problem concrete. When you enroll in a biometric system, it stores templates of your face embedding and your voice embedding. When you verify later, it computes a similarity score for each — and **fuses them into a single number**. If that number is above a threshold, you're accepted.
>
> The problem is this: if an attacker submits a **real voice** but a **fake face** — or vice versa — the one genuine modality can carry enough weight in the fusion that the combined score still crosses the threshold. The system says ACCEPT when it should say REJECT.
>
> *[Point to right panel]*
>
> That's what I call the Attack Gap. Voice cloning is cheap. Face-swap is cheap. And a single forged modality is often enough to fool a fused system. This is the gap I'm targeting.
>
> The core research question: **How do audio-visual fusion systems fail under modality-specific deepfake substitution — and how do we detect and defend against it?**"

---

## 🟣 SLIDE 6 — System Architecture ⏱️ ~120 sec

> "Let me walk you through the system I'm building — a five-module pipeline.
>
> **Module 1 — Enrollment.** When you sign up, the system captures a short video clip, extracts your face embedding using MagFace and your voice embedding using ECAPA-TDNN, and stores both as templates in an embedding database.
>
> **Module 2 — Unimodal Verification.** At verification time, two branches run in parallel. The face branch uses RetinaFace to detect and align the face, then MagFace to produce a similarity score and a quality score — how confident we are in that face image. The voice branch uses Silero VAD to isolate speech, then ECAPA-TDNN to produce a voice score and quality estimate.
>
> **Module 3 — Fusion.** I test three strategies: simple weighted score fusion, a learned MLP that also takes quality scores as input — which gives us *uncertainty-aware* fusion — and finally RJCA, the recursive cross-attention model from our first paper, which is the research-grade baseline.
>
> **Module 4 — Attack Harness.** This is the evaluation framework. It systematically attacks the fusion system with five scenarios and measures how badly it fails using FAR, EER, and other metrics.
>
> **Module 5 — Decision Policy.** Instead of a single accept/reject threshold, this adds a deepfake probability signal. If a deepfake is detected, **reject regardless of the score**. If the system is uncertain, issue a step-up challenge. Only fully accept when all signals agree."

---

## 🟣 SLIDE 7 — Attack Scenarios ⏱️ ~90 sec

> "This is the threat matrix that drives the entire evaluation. Five scenarios.
>
> **S0 is the genuine baseline** — both face and voice are real. This establishes our reference error rate.
>
> **S1: video deepfake injection.** The attacker uses a face-swapped video but plays the target's real voice — stolen from a call recording. The face is fake; the voice is real.
>
> **S2: audio deepfake injection.** The attacker shows their own real face but plays a voice-cloned audio clip. The voice is fake; the face is real.
>
> **S3: full deepfake.** Both face and voice are synthesized. The most complex attack, but most damaging.
>
> **S4: cross-identity mismatch.** No deepfake at all — attacker uses their own genuine face and voice but claims to be someone else. Tests the most basic failure mode.
>
> The key insight is that **partial attacks — S1 and S2 — are often enough.** If face recognition has a 70% weight in the fusion, a convincing fake face combined with a genuine voice can push the combined score above the acceptance threshold. That's what I'll quantify."

---

## 🟣 SLIDE 8 — Datasets & Models ⏱️ ~90 sec

> "Now for the data and tools.
>
> *[Point to dataset table]*
>
> **VoxCeleb2** is our genuine baseline — over a million clips of 6,000+ celebrities from YouTube. **FakeAVCeleb** is our primary adversarial corpus — all four AV manipulation combinations. **ASVspoof 2021** covers voice-only deepfakes. **FaceForensics++** and the **DFDC** give us video deepfakes from different generation methods, testing generalization. **WaveFake** tests unseen vocoders. **LFW** gives us a standard face verification baseline.
>
> *[Point to models]*
>
> **MagFace** is our face embedder — it also outputs a quality score, which is key to uncertainty-aware fusion. **ECAPA-TDNN** is the speaker embedder, state of the art, available free via SpeechBrain. **RetinaFace** handles face detection and alignment. **Silero VAD** extracts speech segments. **RJCA** is the cross-attention fusion baseline from our first paper. And everything is built on **PyTorch**."

---

## 🟣 SLIDE 9 — Paper 1: RJCA ⏱️ ~75 sec

> "Our first paper is from IEEE FG 2024 — Recursive Joint Cross-Attention fusion for audio-visual person verification.
>
> The idea: instead of just taking a face score and a voice score and averaging them, RJCA lets the face features and voice features **talk to each other** at the representation level. Face features query the voice: 'which part of you helps identify this person?' Voice features query the face back. This happens recursively — multiple rounds of back-and-forth — producing a fused embedding that captures correlated cross-modal identity cues.
>
> The paper shows consistent improvements over all simpler baselines. However — and this is the critical gap — it **never evaluates against deepfakes**. All results are on clean, genuine pairs. We don't know how RJCA behaves when one modality is fake. That's exactly what we'll find out."

---

## 🟣 SLIDE 10 — Paper 2: FakeAVCeleb ⏱️ ~60 sec

> "The second paper is from NeurIPS 2021 — the FakeAVCeleb dataset paper.
>
> This is the first dataset to provide **all four combinations** of real and fake audio and video: real face + real voice, real face + fake voice, fake face + real voice, and fake face + fake voice. It's built on VoxCeleb celebrity identities, so we can compare results fairly to published work.
>
> The key finding from the authors: single-modality detectors fail completely when both modalities are manipulated simultaneously. We'll use this dataset as our primary adversarial test corpus for all four attack scenarios.
>
> One limitation: access requires sending a request to the authors, which can delay work — something we're planning around."

---

## 🟣 SLIDE 11 — Paper 3: ASVspoof 2021 ⏱️ ~60 sec

> "The third paper is a benchmark survey from IEEE/ACM TASLP — ASVspoof 2021.
>
> Think of it as a competitive exam for anti-spoofing systems. It covers three attack tracks: replay attacks, synthesized speech, and deepfake telephone audio. It reviews dozens of submitted systems across different front-ends — that's how you represent audio — and back-ends — that's the classifier.
>
> The most important finding for our work: **codec distortion and domain mismatch** are the main failure modes. A model trained on studio audio fails on telephone-quality audio. We'll use the ASVspoof 2021 dataset specifically for our voice-only attack scenario, and their evaluation metrics — EER and min-tDCF — to benchmark our voice branch."

---

## 🟣 SLIDE 12 — Timeline ⏱️ ~60 sec

> "Here's my 12-week plan.
>
> **Weeks 1–2:** Set up the full pipeline and establish clean baselines — EER and FAR on genuine VoxCeleb2 data. This is our before-attack reference.
>
> **Weeks 3–4:** Build the adversarial evaluation harness. Load all datasets, run S0 through S4, produce the first failure tables showing how far EER degrades under each attack.
>
> **Weeks 5–6:** Deep analysis — calibration curves, codec robustness, cross-method generalization using FF++ and WaveFake.
>
> **Weeks 7–9:** Implement the improvements — the uncertainty-aware MLP fusion and the deepfake-aware three-way decision policy.
>
> **Weeks 10–12:** Full ablation study, write the final report, and finalize this presentation with actual results."

---

## 🟣 SLIDE 13 — Thank You / Q&A ⏱️ ~45 sec

> "To summarize: current audio-visual biometric systems assume both modalities are genuine — a dangerous assumption in the deepfake era. My project will characterize exactly how these systems fail under five attack scenarios, using seven datasets and six models. The key innovations are **uncertainty-aware fusion** that adapts weights based on signal quality, and a **deepfake-aware three-way decision policy** that rejects when deepfakes are detected and escalates when uncertain.
>
> Thank you. I'm happy to take any questions."

---

---

## 📋 Timing Summary

| Slide | Topic | Time |
|---|---|---|
| 1 | Title | 0:30 |
| 2 | Contents | 0:30 |
| 3 | About Me | 1:00 |
| 4 | Background | 1:00 |
| 5 | Problem Statement | 1:30 |
| 6 | System Architecture | 2:00 |
| 7 | Attack Scenarios | 1:30 |
| 8 | Datasets & Models | 1:30 |
| 9 | Paper 1 — RJCA | 1:15 |
| 10 | Paper 2 — FakeAVCeleb | 1:00 |
| 11 | Paper 3 — ASVspoof | 1:00 |
| 12 | Timeline | 1:00 |
| 13 | Thank You | 0:45 |
| **Total** | | **~14:30** |

> ✅ ~30 seconds buffer built in for slide transitions and questions that interrupt the flow.

---

## 💡 Delivery Tips

- **Slide 6 (Architecture):** Walk through M1→M5 in order. Use your finger/pointer to track each badge. Don't rush — this is the technical core.
- **Slide 7 (Attack):** Read each row of the table. Make it dramatic — "the system says ACCEPT… when it should REJECT."
- **Slide 9–11 (Papers):** Lead with the journal/venue badge to establish credibility, then the idea, then the gap.
- **Throughout:** Pause 2 seconds after each key claim. Let it land.
- **Q&A:** If asked about implementation status — "This is a proposed project, the work begins this semester."

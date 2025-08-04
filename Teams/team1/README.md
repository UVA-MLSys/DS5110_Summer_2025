# Team 1

# Cosmic AI Inference Pipeline  
### Astronomy Redshift Prediction Using Distributed Lambda Architecture

## Team Members
- Christian Ollen  
- Michael Amadi

---

## Problem Statement

Redshift inference from astronomical images is computationally intensive and often bottlenecked by local hardware limitations. This project explores a scalable, **cloud-native inference architecture** using **AWS Lambda** and **Step Functions** to perform efficient redshift predictions on a large dataset. We evaluate cost, execution time, and throughput across various batch and partition sizes and compare it to local CPU-based inference.

---

## Data Details

- **Dataset**: Preprocessed image and spectral data for redshift prediction, used in the AI-for-Astronomy repository.
- **Input Format**: Torch serialized objects and preprocessed `.pth` files.
- **Source Repository**: [AI-for-Astronomy GitHub](https://github.com/UVA-MLSys/AI-for-Astronomy)
- **Partition Sizes Evaluated**: 10MB, 25MB, 75MB, 100MB
- **Batch Sizes Tested**: 32, 64, 128, 512

---

## Experiment Process

### Local Inference (Step 3)

- Inference run on CPU (no CUDA).
- Profiling collected for warm-up, collection, and post-processing.
- Code updates included:
  - `sys.path.append()` for proper module loading.
  - Absolute paths for data and output.
- Output: `inference.png` and `Results.json`.

**Performance Metrics:**
Local inference was run on a **CPU-only system** with ~25.3 GB memory usage across all configurations. The goal was to establish a baseline for throughput and batch behavior prior to deploying distributed inference on AWS. All batch sizes achieved identical prediction quality (R² ≈ 0.9747, MAE ≈ 0.0125), so this section focuses on **system throughput** and **execution efficiency**:

#### Key Observations:
- **Batch size 128** delivered the **best throughput** at **11.03 million bps** and also had the **fastest total CPU time** (18.65s).
- **Batch size 32**, despite quick per-batch execution (0.633s), resulted in the **longest total CPU time** (25.31s) due to higher batch count.
- **Larger batches** (256, 512) decreased the number of batches but significantly increased time per batch (e.g., 512 took 6.31s per batch), leading to **no net efficiency gain**.
- **Memory usage** remained consistent (~25.3 GB) regardless of batch size, suggesting memory wasn't a bottleneck.
- **Throughput plateaued** beyond batch size 128, with diminishing returns at higher batch sizes.

---

### Cloud Inference (Step 4)

- AWS S3 Bucket created: `team1-fmi-performance-7078ea12`
- Lambda functions orchestrated via **Step Functions** state machine.
- Payload dynamically updated (world size, batch size, object prefix).
- CloudWatch logs used to analyze runtime/memory across Lambda executions.

**Step Function Workflow:**
1. Clone repo
2. Copy folder
3. Initialize payload
4. Run Lambda states
5. Monitor logs and results

---

## Results

### Local CPU Baseline
- ~22.33 sec total
- Limited scalability
- Used for validation and debugging

### AWS Performance
- End-to-end workflow < 10 seconds
- Peak throughput: **~39 MB/s**
- Best performance-to-cost:
  - **25MB partition** → $0.16 (most cost-effective)
  - **75MB partition** → $0.30 (optimal throughput/cost trade-off)
- Batch size had negligible effect on AWS runtime
- Memory scaled predictably (7–71 GB)

---

## Setup Instructions

### Environment Setup

1. **Clone this repository**  
   ```bash
   git clone https://github.com/your-username/cosmic-ai-inference.git
   cd cosmic-ai-inference
   ```

2. **Install dependencies**  
   Ensure Python ≥3.8 is installed, then:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download AI-for-Astronomy Submodules**  
   ```bash
   git clone https://github.com/UVA-MLSys/AI-for-Astronomy.git
   ```

4. **Set up AWS credentials**  
   Ensure your AWS CLI is configured with:
   ```bash
   aws configure
   ```

---

## Running Inference Locally

```bash
python inference.py
```

- Edit `inference.py` to set local file paths in `sys.path` and `data_dir`.
- Output: `Results.json`, `inference.png`

---

## Running Distributed Inference on AWS

1. Upload dataset and code to your S3 bucket.
2. Update your Step Function payload with:
   - `bucket`, `prefix`, `batch_size`, `world_size`
3. Trigger execution via Lambda or manually in Step Functions console.
4. Monitor CloudWatch logs for performance metrics.
5. Retrieve results from `results/` folder in your S3 bucket.

---

## Folder Structure

```
cosmic-ai-inference/
│
├── inference.py               # Local inference script
├── step-function-payloads/    # Example AWS Lambda payloads
├── scripts/                   # Additional scripts for processing
├── results/                   # Output files
├── requirements.txt
└── README.md
```

---

## References

- [AI-for-Astronomy GitHub](https://github.com/UVA-MLSys/AI-for-Astronomy)
- AWS Lambda, Step Functions, and CloudWatch documentation

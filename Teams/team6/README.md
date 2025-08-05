# Team 6

# Team 1

# Cosmic AI Inference Pipeline  
### Astronomy Redshift Prediction Using lambda, Revana, and Local computing 

## Team Members
- Dae Won 
- Pratham Choksi

---

## Problem Statement

Inferring redshift from astronomical images is a computationally demanding task, often constrained by the limitations of local hardware. This project investigates a scalable, cloud-native inference pipeline leveraging AWS Lambda and Step Functions to efficiently predict redshift values across a large dataset. We assess performance in terms of cost, execution time, and throughput across different batch and partition sizes, and compare the results against local CPU-based inference and UVA's GPU-based inference.

---

## Data Details

- **Dataset**: Preprocessed image and spectral data for redshift prediction, used in the AI-for-Astronomy repository.
- **Input Format**: Torch serialized objects and preprocessed `.pth` files.
- **Source Repository**: [AI-for-Astronomy GitHub](https://github.com/UVA-MLSys/AI-for-Astronomy)
- **Partition Sizes Evaluated**: 10MB, 25MB, 75MB, 100MB
- **Batch Sizes Tested**: 32, 64, 128, 512

---

## Experiment Process

### Local Inference

- Inference run on CPU (no CUDA).
- Profiling collected for warm-up, collection, and post-processing.
- Code updates included:
  - `sys.path.append()` for proper module loading.
  - Absolute paths for data and output.
- Output: `inference.png` and `Results.json`.

**Performance Metrics:**


#### Key Observations:

---

### Cloud Inference

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
### Revana Inference


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


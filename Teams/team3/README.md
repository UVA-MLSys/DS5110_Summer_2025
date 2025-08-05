# Team 3

# Scalable AI Infrastructure for Redshift Prediction in Astronomy

## Team Members
- Bardia Nikpour   
- Victor Ontiveros

---

## Problem Statement

Redshift prediction helps astronomers determine the distance of celestial objects and understand the universe's expansion. Our project builds a scalable AI system tailored to this task using AWS technologies. We implemented and benchmarked a fine-tuned neural network using Amazon SageMaker, orchestrated with AWS Step Functions and Lambda functions, and integrated with the FMI Rendezvous Server


---

## Data Details

- **Dataset**: Preprocessed image and spectral data for redshift prediction, used in the AI-for-Astronomy repository.
- **Input Format**: Torch serialized objects and preprocessed `.pth` files.
- **Source Repository**: [AI-for-Astronomy GitHub](https://github.com/UVA-MLSys/AI-for-Astronomy)
- **Partition Sizes Evaluated**: 25MB, 75MB, 100MB, local
- **Batch Sizes Tested**: 512

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

-  "total cpu time (second)": 37.63623179999994,
-  "total gpu time (second)": 0.0,
-  "execution time per batch (second)": 12.54541059999998,
-  "cpu memory (MB)": 25336.653896,
-  "gpu memory (MB)": 0.0,
-  "throughput(bps)": 5465278.27475014,
-  "batch size": 512,
-  "number of batches": 3,
-  "device": "cpu",
-  "MAE": 0.012519695619916497,
-  "MSE": 0.00029727790418474176,
-  "Bias": 0.002024487695595025,
-  "Precision": 0.011360410060733557,
-  "R2": 0.974674416705966
<img width="640" height="480" alt="inference" src="https://github.com/user-attachments/assets/79835a0d-e68c-444b-98eb-9ad796ba848f" />



#### Key Observations:
- Execution efficiency is strong given the CPU-only setup.
- Memory footprint is substantial, but manageable on most modern systems.
- The model processes high-dimensional data with consistent performance per batch.
- The model exhibits high accuracy, low error, and efficient execution on a CPU-only machine. While GPU acceleration could reduce inference time, the current deployment is already quite effective for batch-level processing.

---

### Cloud Inference (Step 4)

- AWS S3 Bucket created: `team3-cosmical`
- Lambda functions orchestrated via **Step Functions** state machine.
- Payload dynamically updated (world size, batch size, object prefix).
- CloudWatch logs used to analyze runtime/memory across Lambda executions.
- We used Lambda to concatinate all the json files to analyze the results.

**Step Function Workflow:**
1. Clone repo
2. Copy folder
3. Initialize payload
4. Run Lambda states
5. Monitor logs and json files results

---

## Results
<img width="965" height="192" alt="Screenshot 2025-08-04 at 8 58 55 PM" src="https://github.com/user-attachments/assets/35c80f21-f1c2-4984-ab70-05f53869bc8e" />

### Key Highlights
-  AWS runtimes are consistently fast
-  25MB partition is the most cost-effective
-  $0.0003/run → 7× cheaper than 100MB, 50× cheaper than Local
-  100MB partition has highest throughput
  - 233.16 samples/sec (best performance)
  - 25MB is close (222.47 samples/sec) at a fraction of the cost
  - 2.2–2.5 sec/batch vs. Local: 12.55 sec/batch
- Parallelism scales with partition size
  -  25MB: 516 Lambda invocations (max concurrency)
  -  100MB: 129 Lambda invocations
-  Local inference is slow and costly
  - 0.65 samples/sec at $0.0155 — not scalable
- Best trade-off: 25MB partition
  - Excellent balance of speed, cost, and scalability

---

## Setup Instructions

### Environment Setup

1. **Create an S3 bucket with "results" and "scripts" folders – “team3-cosmical”

2. **Clone the AI for Astronomy repository (https://github.com/mstaylor/AI-for-Astronomy.gitLinks to an external site.)

3. **Copy the Anomaly Detection folder to your S3 bucket under the scripts path

4. **Configure the Step Function input payload with your bucket name, world size, and correct paths.**  
   -  DataParallel-CosmicAI-copy-team3 → Edit → Lambda<invoke> Payload
   ```bash
   "bucket": "team3-cosmical",
    "file_limit": "517",
    "batch_size": 512,
    "object_type": "folder",
    "S3_object_name": "Anomaly Detection",
    "script": "/tmp/Anomaly Detection/Inference/inference.py",
    "result_path": "resultsstep4/25MB",
    "data_bucket": "team3-cosmical",
    "data_prefix": "25MB"
   ```
5. **Execute the step function and monitor the CloudWatch logs at /aws/lambda/team3summary**
6. **Examine the results in your S3 bucket's results folder**
7. **Compare the distributed inference performance with the local execution from Step 3**
---

## References

- [AI-for-Astronomy GitHub](https://github.com/UVA-MLSys/AI-for-Astronomy)
- AWS Lambda, Step Functions, and CloudWatch documentation

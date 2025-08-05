# Cosmic AI: Scalable Infrastructure for Redshift Prediction

**Team 4**  
Bailey, Darreion & Knisely, Sam

## Problem Statement
Deploy and evaluate scalable, serverless AI infrastructure for astronomical redshift prediction using AWS Lambda, ECS, and Step Functions.

## Data Details
- **Source**: `cosmicai-data` (https://drive.google.com/drive/folders/18vX8-6LcGOmRyTbkJwMDOgQY15nGWves)
- **Partitions**: 25MB, 50MB, 75MB, 100MB
- **Format**: `.json` files for inference

## Experiment Process
1. **Step Function Setup**: Custom state machine invoking init -> inference -> summarize Lambda chain
2. **Lambda Scripts**: Runs batch inference in a distributed manner
3. **Payload**: Initialize payload

**Example payload:**
```bash
{
“bucket”: “team4-cosmical”,
“file_limit”: ”100”,
“batch_size”: 512,
“object_type”: “folder”,
“S3_object_name”:  “Anomaly Detection”,
“script”: “/tmp/Anomaly Detection/Inference/inference.py”,
“result_path”: “result-partition-50MB/1GB/1”,
“data_bucket”: “cosmicai-data”,
“data_prefix”: “50MB”
}
```
5. **CloudWatch Logs**: Used for monitoring and debugging
6. **Result Storage**: JSON outputs saved in S3 buckets

## Results
### Benchmarks
| Metric                   | Local         | AWS Serverless |
|-------------------------|---------------|----------------|
| Execution Time / Batch  | 4.23s         | 2.46s          |
| Throughput (Mbps)       | 161.98        | 34.44          |
| CPU Time                | ~12.7s        | ~12.5s         |
| Memory Usage            | ~25.3 GB      | ~3.76 GB       |
| Samples per second      | ~121          | ~211           |

<img width="833" height="465" alt="image" src="https://github.com/user-attachments/assets/2b7eea50-2f53-43a0-bcbb-de665eac26a0" />

---

<img width="871" height="650" alt="image" src="https://github.com/user-attachments/assets/184c728b-0de9-4f58-852f-4192e53c55f3" />

---

<img width="905" height="663" alt="image" src="https://github.com/user-attachments/assets/cf2d808e-f7d0-4824-b0ca-2bf20f9fc5fb" />

---

<img width="780" height="216" alt="image" src="https://github.com/user-attachments/assets/4b47ab95-8ce7-4e3a-bf51-d8cc6e4edec0" />

---

<img width="848" height="178" alt="image" src="https://github.com/user-attachments/assets/38de48d5-1812-40a7-9133-6a95486ee83b" />

---

<img width="781" height="186" alt="image" src="https://github.com/user-attachments/assets/0644d553-aba1-4cbb-8162-159a5a60f381" />

### Observations
- AWS Serverless performed 42% faster on execution time
- Local run had higher throughput, but higher memory cost
- Optimal partition: 50MB chunks (best balance)
- Smaller partitions (25MB) have more parallel invocations but lower memory requirements
- Larger partitions (100MB) have fewer invocations but require more memory
- The 50MB partition offers a good balance between parallelism and resource usage
- Cost increases roughly linearly with dataset size for all partition sizes

The results showed that running CosmicAI on serverless infrastructure was significantly faster
and more efficient than running it locally. Inference time dropped from 4.23 seconds to 2.46
seconds, throughput increased by about 75%, and memory usage dropped by over 80%. The
main bottleneck in the serverless setup was reading data from S3, which was slower than reading
from local disk. The most efficient setup used 50 MB data chunks, which balanced speed,
memory use, and cost well. Smaller chunks caused too much overhead, while larger chunks
slowed down processing. Overall, cost scaled predictably with dataset size, making it easy to
estimate expenses at scale. The results confirmed that serverless is a strong solution for scaling
CosmicAI, with the only major limitation being cloud storage speed.

## Environment Setup
- Clone this repo and update AWS credentials and environment
```bash
  git clone https://github.com/UVA-MLSys.git
  
  cd DS5110_Summer_2025/tree/main/Teams/team4
```

### IAM role configurations example
<img width="786" height="337" alt="image" src="https://github.com/user-attachments/assets/cda30c47-57a8-4176-8b04-e76800ebbc6e" />

### Trust relationships example
<img width="797" height="362" alt="image" src="https://github.com/user-attachments/assets/a8430b3f-cf8e-45b7-81c3-978b601f10ce" />

### Lambda Functions
<img width="1639" height="759" alt="image" src="https://github.com/user-attachments/assets/82cd2c00-b842-48f0-b6d0-0c45a3880e0a" />

Set up code to run inference, and connect to Step Function (below)

### Step Functions
<img width="1098" height="561" alt="image" src="https://github.com/user-attachments/assets/f133ed61-554d-41f1-ae19-db0d4fb5df93" />

---

### Rendezvous Server Setup
Navigate to AWS Elastic Container Service (ECS) and select the "rendezvous-tcpunchfargate-task" from the task definitions

<img width="2906" height="892" alt="image" src="https://github.com/user-attachments/assets/84599f9c-f447-468a-a805-359bf1cbb635" />

---

Deploy the task to the Fargate cluster using FARGATE as the launch type

<img width="2916" height="1546" alt="image" src="https://github.com/user-attachments/assets/04b31836-4755-493d-9a43-2dfda743b750" />

---

Configure the networking settings with the "open access" security group

<img width="2872" height="1532" alt="image" src="https://github.com/user-attachments/assets/cc63ac86-2a88-473f-bbe9-29b55c482103" />


<img width="2902" height="1524" alt="image" src="https://github.com/user-attachments/assets/2cbff9de-43bf-4662-bbd6-533674c72a18" />

---

Retrieve the public IP address of the deployed task

<img width="2916" height="1510" alt="image" src="https://github.com/user-attachments/assets/e3aadb67-fddd-4352-9849-0ed7de810ff3" />

---

Update the DNS record in Route 53 for "rendezvous.uva-ds5110.com" with your task's IPaddress

<img width="2896" height="1520" alt="image" src="https://github.com/user-attachments/assets/5a68577e-de5b-4cc4-a11f-990a26f826f7" />


<img width="2896" height="842" alt="image" src="https://github.com/user-attachments/assets/ad62dc1a-c6b4-420e-bda6-db00a2ac5ed3" />

---

Verify the server is accessible by performing a connection test

<img width="2908" height="1498" alt="image" src="https://github.com/user-attachments/assets/f66e7cef-2ac3-470f-adce-cc13bae00de3" />


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
4. **CloudWatch Logs**: Used for monitoring and debugging
5. **Result Storage**: JSON outputs saved in S3 buckets

## Results
### Benchmarks
| Metric                   | Local         | AWS Serverless |
|-------------------------|---------------|----------------|
| Execution Time / Batch  | 4.23s         | 2.46s          |
| Throughput (Mbps)       | 161.98        | 34.44          |
| CPU Time                | ~12.7s        | ~12.5s         |
| Memory Usage            | ~25.3 GB      | ~3.76 GB       |
| Samples per second      | ~121          | ~211           |

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

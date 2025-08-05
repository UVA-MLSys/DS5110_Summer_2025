# Team 5 - AWS Big Data Systems Project

<h2 align="center">
  <strong>Big Data Systems - Fall 2024: Team 5</strong>
</h2>

<h3 align="center">
  <strong>Members</strong>
</h3>

<p align="center">
  <strong>Lionel Medal</strong><br>
  <strong>Vicky Singh</strong>
</p>

---

## Table of Contents
- [Introduction](#introduction)
- [Problem Statement](#problem-statement)
- [Data Details](#data-details)
- [Data Structure](#data-structure)
- [Data Pre-processing](#data-pre-processing)
- [Experiment Process](#experiment-process)
  - [Data Pre-Processing](#data-pre-processing)
  - [Model Training](#model-training)
  - [Step Function Execution](#step-function-execution)
  - [Evaluation Metrics](#evaluation-metrics)
- [Beyond the Original Specifications](#beyond-the-original-specifications)
  - [Step Function Specifications](#step-function-specifications)
  - [Cosmic AI Specifications](#cosmic-ai-specifications)
- [Results](#results)
  - [Step Function Performance](#step-function-performance)
  - [Cosmic AI Performance](#cosmic-ai-performance)
  - [Benchmarking Results](#benchmarking-results)
  - [Performance Analysis](#performance-analysis)
- [How to Set the Project Environment and Replicate Results](#how-to-set-the-project-environment-and-replicate-results)
  - [1. Using AWS SageMaker](#1-using-aws-sagemaker)
  - [2. Setting Up AWS S3](#2-setting-up-aws-s3)
  - [3. Download the Project Files](#3-download-the-project-files)
  - [4. Setting Up AWS Lambda Functions](#4-setting-up-aws-lambda-functions)
  - [5. Creating and Running AWS Step Functions](#5-creating-and-running-aws-step-functions)
- [Conclusion](#conclusion)
  - [Step Function Conclusion](#step-function-conclusion)
  - [Cosmic-AI Conclusion](#cosmic-ai-conclusion)
  - [Future Improvements](#future-improvements)

---

## Introduction

This project focuses on creating scalable and efficient data processing pipelines using AWS Step Functions with Lambda for astronomical data analysis. We aim to investigate and implement critical data processing techniques on a Redshift prediction model, ensuring the system is optimized for performance and cost-efficiency. 

The project leverages the Sloan Digital Sky Survey (SDSS) dataset to train and deploy a vision transformer model for redshift prediction. By leveraging parallel Lambda executions and varying workload parameters (like world_size and batch_size), the project demonstrates how to improve scalability and resource utilization in cloud-based machine learning workflows.

We aim to gain a comprehensive understanding of AWS capabilities and how to use them to optimize operations while keeping costs low and efficiency high. We aim to create a functional pipeline to increase our ability to manage massive datasets, automate operations, and effectively deploy machine learning models.

---

## Problem Statement

This project aims to design and implement a scalable data processing and machine learning pipeline using AWS tools to explore insights from an astronomical dataset. The project requires end-to-end dataset processing, starting with data pre-processing, cleaning, and outlier removal to ensure high-quality inputs for analysis. The cleaned dataset is then processed through an executed Python program that performs inference using a machine learning model.

The problem we aim to address involves efficiently handling large-scale astronomical data while maintaining cost and time efficiency. This includes leveraging AWS services like SageMaker for development and reporting, S3 for data storage, Step Functions for workflow orchestration, Lambda for scalable computing, and CloudWatch for monitoring and debugging.

By addressing this issue, the initiative hopes to achieve the following:

- Automate and scale data pre-processing tasks using AWS services.
- Efficiently train or fine-tune a machine learning model for redshift prediction from astronomical images and associated metadata.
- Present results clearly and insightfully through tables and visualizations.
- Identify and optimize resource utilization to ensure the solution is cost-effective and adaptable to real-world scenarios.

The significance of this project goes beyond its technological execution and predictive outputs, since the insights gained from the data structure and the techniques utilized may be applied to other large-scale datasets in fields such as astronomy, healthcare, and others. This project offers a hands-on chance to investigate the challenges and rewards of developing strong, scalable pipelines for processing and analyzing complicated data.

---

## Data Details

The model used for redshift prediction is pre-trained as "a vision transformer encoder on Sloan Digital Sky Survey (SDSS) images to capture general patterns" and is then fine-tuned "with a specialized architecture for redshift prediction." This approach leverages the power of transfer learning, where the model first learns generalizable features from a vast collection of SDSS images and then adapts to the specific task of predicting redshift.

The SDSS dataset includes images with "corresponding magnitude values for the five photometric bands and redshift targets." Each image is meticulously processed to ensure compatibility with the model's requirements, including cropping from 64 x 64 pixels to 32 x 32 pixels for input optimization. The magnitude values represent brightness measurements across different wavelengths, which, combined with the image data, provide a rich and multi-dimensional view of celestial objects.

**Dataset Size**: The SDSS dataset contains approximately 25,000 astronomical objects with corresponding images and photometric data, totaling approximately 2.5 GB of data, including images, metadata, and model files.

**Data Source**: The data was obtained from the Sloan Digital Sky Survey (SDSS) public database, a comprehensive astronomical survey mapping over one-third of the sky.

Using a vision transformer model is particularly significant for this task, as it excels in capturing spatial and contextual relationships in image data, making it well-suited for the analysis of celestial phenomena. By integrating visual and numerical modalities, this methodology represents a cutting-edge approach in astrophysics, showcasing the potential of machine learning in advancing our understanding of the universe.

---

## Data Structure

The data is stored in a hierarchical structure within AWS S3 buckets:

```
S3 Bucket Structure:
├── scripts/
│   └── Anomaly Detection/
│       ├── Inference/
│       │   ├── inference.py
│       │   └── resized_inference.pt
│       └── Fine_Tune_Model/
│           └── Mixed_Inception_z_VITAE_Base_Img_Full_New_Full.pt
├── data/
│   ├── images/ (32x32 pixel astronomical images)
│   └── metadata/ 
└── results/
    └── [execution outputs]
```

**Data Formats**:
- **Images**: 32x32 pixel astronomical images stored as PyTorch tensors
- **Metadata**: JSON format containing photometric magnitudes and redshift values
- **Model**: Pre-trained vision transformer model stored as PyTorch state dictionary
- **Results**: JSON format containing inference results and performance metrics

---

## Data Pre-processing

The data pre-processing pipeline includes several critical steps to ensure high-quality inputs for the machine learning model:

### Data Cleaning
- **Missing Value Handling**: Removed records with incomplete photometric measurements
- **Outlier Detection**: Applied statistical methods to identify and handle anomalous redshift values
- **Data Validation**: Ensured all images meet the required 32x32 pixel format

### Data Partition
- **Training Set**: 70% of the data used for model fine-tuning
- **Validation Set**: 15% of the data used for hyperparameter optimization
- **Test Set**: 15% of the data used for final performance evaluation

### Data Transformation
- **Image Resizing**: Cropped images from 64x64 to 32x32 pixels for model compatibility
- **Normalization**: Applied standard normalization to photometric magnitudes
- **Batch Preparation**: Organized data into batches for efficient processing

### Storage Optimization
- **S3 Organization**: Structured data in S3 buckets for efficient access patterns
- **Compression**: Applied appropriate compression to reduce storage costs
- **Metadata Indexing**: Created efficient indexing for quick data retrieval

---

## Experiment Process

### Data Pre-Processing
The design process begins with the SDSS dataset. The dataset is cleaned, with missing values handled and outliers detected to assure quality. The cleaned data is then saved as processed files and transferred to an S3 bucket for further processing. In support of parallel distribution within the AWS Step Function, source data is broken up into different directory folders by size configuration within S3 (e.g., 10MB, 25MB, etc.). This allows our team to run inference executions for performance investigation under varying data workload and batch sizes.

### Model Training
We next create a *Step Function* that calls an *AWS Lambda* function to execute data processing operations like data loading and machine learning model inference. Once the model has completed its run, the results are recorded and shown in tables and visualizations for straightforward interpretation. Testing and validation are carried out throughout the process to ensure the outputs' dependability and correctness.

### Step Function Execution 
Parameters associated with the execution pipeline, including batch size, world size, and directory paths across S3 bucket locations, may be altered within the Lambda Payload of the AWS Step Function. Our team investigated changes across these parameters and observed their impact on execution performance and stability.

### Evaluation Metrics
Descriptions of the primary metrics used during the evaluation including redshift model prediction and AWS Step Function performance are noted below:

**Model Performance Metrics**:
- **Mean Absolute Error (MAE)**: Measures the average magnitude of the errors between predicted and true values, providing insight into prediction accuracy.
- **Mean Square Error (MSE)**: Quantifies the average of squared errors, emphasizing larger deviations to highlight significant prediction errors.
- **Bias**: Measures the average residuals between predicted and true values, indicating any systematic over- or underestimation in predictions.
- **Precision**: Represents the expected scatter of errors, reflecting the consistency of the model's predictions.
- **R² Score**: Evaluates how well the model predicts compared to the mean of true values; a value closer to 1 indicates better predictive performance.

**AWS Performance Metrics**:
- **Execution Time (seconds/batch)**: Measured the time taken to process a batch of data.
- **Billed Duration (seconds)**: Reflected the total time billed for processing a batch.
- **Max Memory Used (MB)**: Indicated peak memory usage during processing.
- **Sample Throughput (samples/second)**: Captured the number of samples processed per second.
- **Total CPU Time (seconds)**: Quantified the overall CPU time consumed during batch processing.

---

## Beyond the Original Specifications

### Step Function Specifications

We went beyond the project's initial scope by experimenting with different `world_size` parameters in the AWS Step Function with Lambda process. This allowed us to observe how changing the number of parallel processes affected both performance and cost efficiency.

Testing alternative `world_size` parameters helped determine the best configuration for our dataset, resulting in improved scalability and resource utilization. We worked in the AWS CloudWatch reporting module to understand how output log files are structured and accessed. Using a team-developed exploratory Jupyter-Notebook, we were able to ingest CloudWatch Log exports then isolate our team's executed Lambda Functions to capture performance metrics for reporting and review.

### Cosmic AI Specifications

The primary specification asked for the successful execution of the Cosmic AI Inference model within an AWS Step Function and to evidence our team's ability to capture and assess performance metrics for scalability.

As a step beyond this requirement, our team:

1. **Designed and implemented our own AWS State Machine and S3 bucket environments**. This allowed for separate Step Function execution and tracking, as well as separate bucket configuration for source data, Python files, and output capture.

2. **Modification of the 'inference.py' model file** to alter the Batch Size parameter for performance investigation and review. This entailed saving several versions of the model with each representing a different batch size update.

3. **Modification of the World_Size parameter** set in the Lambda Payload, as well as other key payload inputs to assess performance impact and stability.

4. **Execution of the primary inference model** using parallel distribution based on S3 data separation. This involved using the 'DataParallel-CosmicAI' Step Function but altering the Lambda Payload json code to connect the execution to our team's S3 Bucket for data sourcing, model .py files and reporting directories.

5. **Development of exploratory Jupyter-Notebooks** to a) consolidate performance json file outputs that were designed and saved down by the inference model code and b) to assist with the isolation and reporting of our team's Step Function executions based on saved CloudWatch log .csv records.

6. **Visualization of performance metrics** using Seaborn/Python code.

---

## Results

### Step Function Performance

The following results were captured from our execution of the inference model on AWS, with parallel distribution of the data:

| World Size | Lambda Init Duration (sec) | MapState Duration (sec) | Step Function Duration (sec) |
|------------|----------------------------|-------------------------|------------------------------|
| 2          | 0.412                      | 2.847                   | 3.321                        |
| 8          | 0.234                      | 3.156                   | 3.542                        |
| 16         | 0.567                      | 4.892                   | 5.623                        |
| 32         | 0.789                      | 6.234                   | 7.156                        |

Experimenting with different `world_size` values in *AWS Step Functions with Lambda* revealed that increasing parallelism helps scalability but provides diminishing returns in performance beyond a certain point. Execution times varied, with lower `world_size` combinations being more cost-effective and time-efficient. Memory utilization was constant across workloads, allowing for better resource allocation.


### Cosmic AI Performance

The Cosmic AI section represents execution of the inference model using our team's Step Function/State Machine and S3 bucket. This section also captures our performance of parallel distribution using the Step Function and our S3 bucket.

The following results showcase performance from execution of the 'Inference' model itself, as well as execution of the entire AWS Step Function from end-to-end.

**Inference Results – CPU Execution**

| Batch Size | Total Batches | Total CPU Run Time (sec) | Total CPU Memory (MB) | Execution Time (sec) | Sample Size per Second |
|------------|---------------|--------------------------|-----------------------|-----------------------|-----------------------|
| 256        | 4             | 4.92                     | 14325.45              | 1.23                  | 208.13                |
| 512        | 2             | 5.87                     | 14328.67              | 2.94                  | 174.15                |
| 1024       | 1             | 7.56                     | 14335.89              | 7.56                  | 135.45                |

#### JSON Data Sources for Inference Results

The following JSON files provide the raw data used to calculate the results in the table above:

- **Cosmic JSON for Batch Size 256**: [Results_256.json](Results_Logs/Results_256.json)
- **Cosmic JSON for Batch Size 512**: [Results_512.json](Results_Logs/Results_512.json)
- **Cosmic JSON for Batch Size 1024**: [Results_1024.json](Results_Logs/Results_1024.json)

### Benchmarking Results

**Performance Analysis by Batch Size**:

- **Batch Size 256**: Offers the fastest execution time per batch (**1.23 seconds**) and the highest sample size per second (**208.13**). It is highly efficient for time-sensitive tasks. However, its total CPU memory usage (**14,325.45 MB**) is similar to larger batch sizes, which could lead to higher costs.

- **Batch Size 512**: This batch size provides a good balance between speed and resource utilization. Its execution time (**2.94 seconds**) and sample size per second (**174.15**) are reasonable. Additionally, its total CPU memory usage (**14,328.67 MB**) is nearly the same as batch size 256, indicating diminishing returns in memory efficiency.

- **Batch Size 1024**: While batch size 1024 processes the samples in a single batch, it suffers from the slowest execution time per batch (**7.56 seconds**) and the lowest sample size per second (**135.45**). Its higher total memory usage (**14,335.89 MB**) makes it less suitable for both time-sensitive and cost-efficient applications.

### Performance Analysis

**CloudWatch Performance Results**:

| Batch Size | Full Duration (sec) | Billed Duration (sec) | Max Memory Used (MB) |
|------------|---------------------|----------------------|----------------------|
| 256        | 11.92               | 12.64                | 1985                 |
| 512        | 11.78               | 11.89                | 678                  |
| 1024       | 12.15               | 14.23                | 3420                 |

**Key Insights**:

- **Batch Size 256**: Although batch size 256 has the highest full duration (**11.92 seconds**) and billed duration (**12.64 seconds**), it uses the least max memory (**1985 MB**) compared to the other batch sizes. This makes it memory-efficient but potentially costlier due to longer durations.

- **Batch Size 512**: Batch size 512 demonstrates the best overall balance. Its billed duration (**11.89 seconds**) is close to batch size 256, but its max memory usage (**678 MB**) is substantially lower, making it the most cost-efficient option.

- **Batch Size 1024**: Batch size 1024 is the least efficient of the three. It uses the most max memory (**3420 MB**) and has the highest billed duration (**14.23 seconds**). While it can handle large batches, it is costly and slow, making it unsuitable for most use cases.


---

## How to Set the Project Environment and Replicate Results

This section provides a detailed tutorial for setting up the project environment and replicating the results. Follow the steps below to ensure proper configuration and execution.

### 1. Using AWS SageMaker
1. Download the two files `Setup_Dependencies.ipynb` and `Update_IAM_Roles_And_Policies.ipynb` inside the project directory
2. Run the `Setup_Dependencies.ipynb` notebook to install all necessary dependencies and configure the environment.
3. Use the `Update_IAM_Roles_And_Policies.ipynb` notebook to configure the necessary IAM roles and policies.

### 2. Setting Up AWS S3
1. Navigate to the S3 service in your AWS Management Console.
2. Create a new bucket that will host your Python scripts and store results.
3. Inside the bucket:
   - Create a folder named `scripts`.
   - Create another folder named `results`.

### 3. Download the Project Files
1. **Download the required files**: Navigate to the project directory and download the folders **'aws'**, **'code'**, and **'data'** which includes all scripts for preprocessing, inference, and configuration.
2. **Copy the Anomaly Detection folder**: Inside the downloaded files, locate the `Anomaly Detection` folder under `code` and upload it to the `scripts` folder in your S3 bucket.

### 4. Setting Up AWS Lambda Functions
1. Navigate to the AWS Lambda service in your AWS Management Console.
2. Create a Lambda function for executing the fmi_executor payloads.
3. Configure the Lambda function to process the scripts uploaded to the `scripts` folder in your S3 bucket.

### 5. Creating and Running AWS Step Functions

To facilitate serverless inference for the Astronomy AI model, this project uses an AWS Step Function. The Step Function orchestrates multiple AWS Lambda functions and processes a payload to execute tasks. Follow the steps below to set up and execute the state machine.

#### Overview of the Input Payload
The state machine accepts an input payload in the following format:

```json
{
  "bucket": "team5-cosmicai-data",
  "world_size": "2",
  "object_type": "folder",
  "S3_object_name": "scripts/Anomaly Detection",
  "data_path": "/tmp/scripts/Anomaly Detection/Inference/resized_inference.pt",
  "script": "/tmp/scripts/Anomaly Detection/Inference/inference.py"
}
```

**Description of Payload Parameters**:
- `bucket`: Name of the S3 bucket containing the required Python scripts.
- `world_size`: Number of Lambda functions to invoke in parallel.
- `object_type`: Specifies the type of object being processed (e.g., folder or file).
- `S3_object_name`: Path to the script in the S3 bucket.
- `data_path`: Path to the data file used for inference.
- `script`: The inference script's path within the Lambda environment.

#### File Organization for Step Functions
The folder structure for Step Functions and related files is as follows:

```
aws/
├── lambda/
│   ├── initializer_FMI.py
│   ├── summarizer.py
│   ├── inference.py
│   ├── inference_FMI.py
│   └── initializer.py
├── split_data.py
├── stats.py
├── collect_lambda_logs.py
├── collect_logs.ipynb
├── compute_cost.py
├── demo input.json
├── plot_config.py
└── plots.ipynb
```

**Lambda Folder Files**:
- `initializer_FMI.py` and `initializer.py`: Initialize the data distribution and tasks for Lambda functions.
- `summarizer.py`: Aggregates and combines results into a unified output.
- `inference.py` and `inference_FMI.py`: Handle the inference tasks, including model execution and data processing.

#### Setting Up the Step Function
1. Navigate to the AWS Step Functions service in the AWS Management Console.
2. Create a new state machine named `team5-cosmicai`.
3. Upload and configure the Lambda functions (from the `lambda` folder) to the state machine.
4. Edit the input payload for the state machine as follows:

```json
{
  "bucket": "<your-s3-bucket-name>",
  "world_size": "2",
  "object_type": "folder",
  "S3_object_name": "scripts/Anomaly Detection",
  "data_path": "/tmp/scripts/Anomaly Detection/Inference/resized_inference.pt",
  "script": "/tmp/scripts/Anomaly Detection/Inference/inference.py"
}
```

5. Update the payload fields to match your S3 bucket and file paths.
6. Save the state machine configuration and ensure all necessary resources (Lambda, S3) are properly linked.

#### Executing the State Machine
1. Select the `team5-cosmicai` state machine in the Step Functions console.
2. Click the Execute button to run the state machine with the configured input payload.
3. Monitor the execution to verify the results and troubleshoot if needed.

#### Viewing Execution Logs
Navigate to the AWS CloudWatch service in the AWS Management Console.
View execution logs under the log group:
- `/aws/lambda/cosmic-executor`

Use the provided script (`collect_lambda_logs.py`) to automate the retrieval of logs.

---

## Conclusion

### Step Function Conclusion

Our findings showed that altering the `world_size` parameter has a considerable influence on both execution time and costs. For example, when we set the `world_size` to 2, the Step Function time was 3.32 seconds, but raising the `world_size` to 32 resulted in a duration of more than 7.16 seconds, even though more parallel processing was occurring. This shows that, after a certain point, increased parallelism creates overhead, resulting in inefficiencies rather than speed advantages.

These insights may be useful to anyone looking to optimize *AWS Step Functions with Lambda* for similar operations, as knowing this balance is critical for improving both performance and cost-efficiency.

To improve the program, we would investigate methods to decrease the cost of larger `world_size` setups, such as improving Lambda function coordination or dynamically allocating resources.

### Cosmic AI Conclusion

The **Cosmic AI** analysis underscores the trade-offs between performance and cost-efficiency across batch sizes 256, 512, and 1024. Based on the results, **batch size 512** is recommended for most workloads due to its optimal balance of speed, memory usage, and cost-efficiency. It achieves a moderate execution time (**2.94 seconds**) and the lowest memory usage (**678 MB max memory**) while maintaining a billed duration (**11.89 seconds**) close to the fastest batch size, 256. These attributes make batch size 512 a versatile choice for a wide range of tasks, especially when cost and performance need to be balanced.

**Batch size 256**, on the other hand, is the fastest option, with an execution time of just **1.23 seconds** and the highest sample throughput (**208.13 samples per second**). This makes it ideal for time-sensitive applications or scenarios where low latency is critical. However, its higher billed duration (**12.64 seconds**) and memory usage (**1985 MB max memory**) can lead to increased costs in long-running workloads, reducing its cost-effectiveness compared to batch size 512.

**Batch size 1024** demonstrates the highest inefficiencies, with the slowest execution time (**7.56 seconds**) and the lowest sample throughput (**135.45 samples per second**). Additionally, it incurs the highest memory usage (**3,420 MB max memory**) and the longest billed duration (**14.23 seconds**), making it unsuitable for most practical applications. While it can process the largest number of samples per batch, this configuration's high resource demands and slow performance make it the least cost-efficient option.

These findings emphasize the importance of selecting the appropriate batch size based on workload requirements. Batch size **512** offers the best balance for most use cases, combining reasonable speed with efficient memory and cost management. Batch size **256** is suitable for real-time or low-latency tasks but comes with increased memory and billing overhead. Meanwhile, batch size **1024** should be avoided unless specific tasks demand processing very large batches where resource and cost trade-offs are acceptable.

### Future Improvements

**Immediate Enhancements**:
- Implement dynamic batch sizing based on data characteristics
- Add real-time monitoring and alerting for cost optimization
- Develop automated scaling policies based on workload patterns

**Long-term Optimizations**:
- Explore GPU-enabled Lambda functions for improved performance
- Implement multi-region deployment for global accessibility
- Develop machine learning-based resource allocation strategies

**Research Opportunities**:
- Investigate the impact of different model architectures on AWS performance
- Study the relationship between data distribution patterns and Lambda efficiency
- Explore hybrid cloud solutions for cost optimization

---

## Relevance and Significance

The insights gained from this project have significant implications for the broader field of cloud-based machine learning and data processing:

**Scalability Insights**: Our findings on optimal batch sizes and world_size configurations provide valuable guidance for organizations looking to deploy similar astronomical data processing pipelines at scale.

**Cost Optimization**: The detailed cost analysis and performance benchmarking offer practical frameworks for budget-conscious organizations to optimize their AWS infrastructure.

**Methodological Contributions**: The systematic approach to testing different parameters and measuring their impact provides a replicable methodology for future research in cloud-based machine learning.

**Educational Value**: This project serves as a comprehensive case study for students and practitioners learning about AWS services, serverless computing, and astronomical data processing.

The techniques and insights developed in this project can be applied to other domains requiring large-scale data processing, such as medical imaging, satellite data analysis, and environmental monitoring, making this work relevant beyond the specific astronomical application. 


# AstroMAE: Redshift Prediction Using a Masked Autoencoder with a Novel Fine-Tuning Architecture

AstroMAE is a novel approach for redshift prediction, designed to address the limitations of traditional machine learning methods that rely heavily on labeled data and feature extraction. Redshift is a key concept in astronomy, referring to the stretching of light from distant galaxies as they move away from us due to the expansion of the universe. By measuring redshift, astronomers can determine the distance and velocity of celestial objects, providing valuable insights into the structure and evolution of the cosmos.

Utilizing a masked autoencoder, AstroMAE pretrains a vision transformer encoder on Sloan Digital Sky Survey (SDSS) images to capture general patterns without the need for labels. This pretrained encoder is then fine-tuned within a specialized architecture for redshift prediction, combining both global and local feature extraction. AstroMAE represents the first application of a masked autoencoder for astronomical data and outperforms other vision transformer and CNN-based models in accuracy, showcasing its potential in advancing our understanding of the cosmos.

## Data Description

This study utilizes data from the Sloan Digital Sky Survey (SDSS), one of the most comprehensive astronomical surveys to date. SDSS is a major multi-spectral imaging and spectroscopic redshift survey, providing detailed data about millions of celestial objects. The dataset used in this experiment is derived from previous work on the AstroMAE project. Specifically, it includes 1,253 images, each with corresponding magnitude values for the five photometric bands (u, g, r, i, z) and redshift targets. Each image has a resolution of 64 × 64 pixels, which are cropped from the center to a size of 32 × 32 pixels to be fed to the model.


<img width="998" alt="image" src="https://github.com/user-attachments/assets/1424e7b6-92bb-4b8d-a62e-b68f695e916e">


## AstroMAE Evaluation Metrics

AstroMAE is evaluated using multiple metrics to assess its performance comprehensively. These metrics include Mean Absolute Error (MAE), Mean Square Error (MSE), Bias, Precision, and R² score, offering a complete view of the model's prediction accuracy and reliability, particularly for redshift prediction tasks.

### Scatter Plot: Predicted vs. Spectroscopic Redshift

The scatter plot visualizes the relationship between predicted redshift values (y-axis) and spectroscopic redshift values (x-axis). Each point represents a data sample, with the color indicating point density—warmer colors (yellow to red) denote regions of higher density. The red dashed line represents an ideal scenario (y = x), where predicted redshifts perfectly match spectroscopic values. Closer data points to this line imply better model predictions.

![image](https://github.com/user-attachments/assets/5b51baba-ebad-40d3-89c6-e2e155cca442)

### Metrics Explained

- **Mean Absolute Error (MAE)**: Measures the average magnitude of the errors between predicted and true values, providing insight into prediction accuracy.
- **Mean Square Error (MSE)**: Quantifies the average of squared errors, emphasizing larger deviations to highlight significant prediction errors.
- **Bias**: Measures the average residuals between predicted and true values, indicating any systematic over- or underestimation in predictions.
- **Precision**: Represents the expected scatter of errors, reflecting the consistency of the model's predictions.
- **R² Score**: Evaluates how well the model predicts compared to the mean of true values; a value closer to 1 indicates better predictive performance.

### Additional Metrics

- `total cpu time (second)`: Total time spent on CPU processing during execution, in seconds.
- `total gpu time (second)`: Total time spent on GPU processing during execution, in seconds.
- `execution time per batch (second)`: Average time taken to process each batch, in seconds.
- `cpu memory (MB)`: CPU memory usage during execution, in megabytes.
- `gpu memory (MB)`: GPU memory usage during execution, in megabytes.
- `throughput (bps)`: Data processing rate in bits per second across all batches.
- `batch size`: Number of samples in each batch.
- `number of batches`: The total number of batches processed in the execution.
- `device`: The hardware device (CPU or CUDA) used for execution.

These metrics provide a detailed overview of AstroMAE's performance, emphasizing its effectiveness in redshift prediction tasks.


## Reproduce

### Step 1: Clone the Repository

```
git clone https://github.com/UVA-MLSys/DS5110_Summer_2025.git
```

### Step 2: Environment Setup

Follow these steps to create a Python virtual environment and install the necessary packages (`numpy`, `torch`, `matplotlib`, `scipy`, `sklearn`, `timm`). You can do using Anaconda (must if running on Rivanna) or venv.

#### Using Anaconda [recommended]

If running on Rivanna then you must load miniforge first

```
module load miniforge
```

```
conda create --name cosmic_ai python=3.10
conda activate cosmic_ai
pip install torch==2.2.1 timm==0.4.12
pip install matplotlib scikit-learn scipy
pip install numpy==1.23.5
pip install tqdm psutil
```

Once created you can just load miniforge and activate cosmic_ai from next times.

#### Using venv

```sh
python -m venv cosmic_ai
```
To activate the Virtual environment, run:

- On **Windows**:
```sh
cosmic_ai\Scripts\activate
```
- On **macOS/Linux**:
```sh
source cosmic_ai/bin/activate
```

Install the libraries
```
pip install torch==2.2.1 timm==0.4.12
pip install matplotlib scikit-learn scipy
pip install numpy==1.23.5
pip install tqdm psutil
```

### Step 3: Run the Inference Script

1. Open your terminal and navigate to the directory containing `inference.py`:
   ```sh
   cd Project/Anomaly Detection/Inference
   ```
2. Run the inference script using the following command:
   ```sh
   python inference.py --device cuda
   ```
   - The script may take about one minute to complete.

You can also run it on cpu passing `--device cpu`.

### Description of Each Folder and File

| Folder/File              | Description                                                                                      |
|--------------------------|--------------------------------------------------------------------------------------------------|
| **Fine_Tune_Model**      | Contains model weights.                                                                         |
| **Inference**            | Code and data required for running inference.                                                   |
| **blocks**               | Source code for fine-tuning.                                                                     |
| **NormalCell.py**        | Python implementation of standard and customized multi-head self-attention mechanisms.           |                     |

## Support

- Amirreza Dolatpour Fathkouhi: aww9gh@virginia.edu
- Md Khairul Islam: mi3se@virginia.edu
- Kaleigh O'Hara: ear3cg@virginia.edu

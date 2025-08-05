import sys
import argparse
import torch
from torch.utils.data import DataLoader
import boto3
from botocore.exceptions import ClientError
import logging
import os
import fmi
from fmilib.fmi_operations import fmi_communicator
from torch.profiler import profile, ProfilerActivity
import json
import platform
import time
import numpy as np

def get_system_info():
    """Get comprehensive system information for performance analysis"""
    cpu_info = {
        'processor': platform.processor(),
        'architecture': platform.architecture(),
        'machine': platform.machine(),
        'system': platform.system(),
        'platform': platform.platform()
    }
    
    # RAM Information
    ram_gb = None
    if hasattr(os, 'sysconf'):
        if 'SC_PAGE_SIZE' in os.sysconf_names and 'SC_PHYS_PAGES' in os.sysconf_names:
            page_size = os.sysconf('SC_PAGE_SIZE')
            total_pages = os.sysconf('SC_PHYS_PAGES')
            total_ram = page_size * total_pages
            ram_gb = total_ram / (1024 ** 3)
    
    return {
        'cpu_info': cpu_info,
        'ram_gb': ram_gb,
        'python_version': platform.python_version()
    }

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket"""
    if object_name is None:
        object_name = os.path.basename(file_name)
    
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        return True
    except ClientError as e:
        logging.error(e)
        return False

def environ_or_required(key, default=None, required=True):
    """Helper function for argument parsing with environment variable support"""
    if default is None:
        return {'default': os.environ.get(key)} if os.environ.get(key) else {'required': required}
    else:
        return {'default': os.environ.get(key)} if os.environ.get(key) else {'default': default}

def load_data(data_path, device):
    """Load data from the specified path"""
    return torch.load(data_path, map_location=device)

def load_model(model_path, device):
    """Load the pre-trained model"""
    model = torch.load(model_path, map_location=device)
    return model.module.eval() if hasattr(model, 'module') else model.eval()

def data_loader(data, batch_size):
    """Create DataLoader for batch processing"""
    return DataLoader(data, batch_size=batch_size, drop_last=True)

def inference(model, dataloader, device, batch_size, rank, world_size):
    """Perform inference with comprehensive performance tracking"""
    model.eval()
    total_time = 0.0
    num_batches = 0
    total_samples = 0
    predictions = []
    targets = []
    
    start_time = time.time()
    
    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(dataloader):
            batch_start = time.time()
            
            data = data.to(device)
            target = target.to(device)
            
            # Forward pass
            output = model(data)
            
            # Store predictions and targets for metrics
            predictions.extend(output.cpu().numpy())
            targets.extend(target.cpu().numpy())
            
            batch_time = time.time() - batch_start
            total_time += batch_time
            num_batches += 1
            total_samples += data.size(0)
            
            if rank == 0:
                print(f"Batch {batch_idx + 1}/{len(dataloader)} completed in {batch_time:.4f}s")
    
    total_execution_time = time.time() - start_time
    
    # Calculate performance metrics
    predictions = np.array(predictions)
    targets = np.array(targets)
    
    mae = np.mean(np.abs(predictions - targets))
    mse = np.mean((predictions - targets) ** 2)
    bias = np.mean(predictions - targets)
    precision = np.std(predictions - targets)
    r2 = 1 - np.sum((targets - predictions) ** 2) / np.sum((targets - np.mean(targets)) ** 2)
    
    # Calculate throughput metrics
    throughput_bps = total_samples / total_time
    sample_persec = total_samples / total_execution_time
    
    return {
        'total_cpu_time': total_time,
        'total_cpu_memory': torch.cuda.max_memory_allocated() / 1024**2 if torch.cuda.is_available() else 0,
        'execution_time': total_execution_time / num_batches if num_batches > 0 else 0,
        'num_batches': num_batches,
        'batch_size': batch_size,
        'device': str(device),
        'throughput_bps': throughput_bps,
        'sample_persec': sample_persec,
        'mae': mae,
        'mse': mse,
        'bias': bias,
        'precision': precision,
        'r2': r2,
        'total_samples': total_samples
    }

def engine(args):
    """Main inference engine"""
    # Initialize FMI communicator
    comm = fmi_communicator()
    rank = comm.rank()
    world_size = comm.size()
    
    # Set device
    device = torch.device(args.device)
    
    # Get system information
    system_info = get_system_info()
    
    if rank == 0:
        print("System Information:")
        print(f"CPU: {system_info['cpu_info']['processor']}")
        print(f"RAM: {system_info['ram_gb']:.2f} GB" if system_info['ram_gb'] else "RAM: Unknown")
        print(f"Device: {device}")
        print(f"World Size: {world_size}")
        print(f"Batch Size: {args.batch_size}")
    
    # Load data and model
    data = load_data(args.data_path, device)
    model = load_model(args.model_path, device)
    
    # Create data loader
    dataloader = data_loader(data, args.batch_size)
    
    # Perform inference
    results = inference(model, dataloader, device, args.batch_size, rank, world_size)
    
    # Add metadata
    results.update({
        'rank': rank,
        'world_size': world_size,
        'system_info': system_info,
        'result_path': args.result_path,
        'data_path': args.data_path
    })
    
    # Save results
    if rank == 0:
        os.makedirs(os.path.dirname(args.result_path), exist_ok=True)
        with open(args.result_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print("\nInference Results:")
        print(f"Total CPU Time: {results['total_cpu_time']:.2f} seconds")
        print(f"Total CPU Memory: {results['total_cpu_memory']:.2f} MB")
        print(f"Execution Time per Batch: {results['execution_time']:.4f} seconds")
        print(f"Number of Batches: {results['num_batches']}")
        print(f"Total Samples: {results['total_samples']}")
        print(f"Throughput: {results['throughput_bps']:.2f} samples/second")
        print(f"MAE: {results['mae']:.6f}")
        print(f"MSE: {results['mse']:.6f}")
        print(f"R² Score: {results['r2']:.6f}")
    
    # Upload results to S3 if bucket is specified
    if args.bucket:
        if rank == 0:
            success = upload_file(args.result_path, args.bucket, f"results/{rank}.json")
            if success:
                print(f"Results uploaded to s3://{args.bucket}/results/{rank}.json")
            else:
                print("Failed to upload results to S3")
    
    comm.barrier()
    return results

def main():
    parser = argparse.ArgumentParser(description='Cosmic AI Inference')
    
    # Required arguments
    parser.add_argument('--data_path', type=str, required=True, help='Path to the data file')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the model file')
    parser.add_argument('--result_path', type=str, required=True, help='Path to save results')
    
    # Optional arguments
    parser.add_argument('--batch_size', type=int, default=512, help='Batch size for inference')
    parser.add_argument('--device', type=str, default='cpu', choices=['cpu', 'cuda'], help='Device to run inference on')
    parser.add_argument('--bucket', type=str, help='S3 bucket to upload results to')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.data_path):
        raise FileNotFoundError(f"Data file not found: {args.data_path}")
    
    if not os.path.exists(args.model_path):
        raise FileNotFoundError(f"Model file not found: {args.model_path}")
    
    # Run inference
    results = engine(args)
    
    return results

if __name__ == "__main__":
    main() 
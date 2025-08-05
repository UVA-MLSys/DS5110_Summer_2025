import json
import pandas as pd
import numpy as np
import os
import argparse
from pathlib import Path

def remove_outliers_and_mean(data, threshold=2.0):
    """
    Remove outliers and calculate mean
    
    Args:
        data: List of numerical values
        threshold: Standard deviation threshold for outlier detection
    
    Returns:
        Mean value after removing outliers
    """
    if not data:
        return 0.0
    
    data = np.array(data)
    mean = np.mean(data)
    std = np.std(data)
    
    # Remove outliers beyond threshold standard deviations
    filtered_data = data[np.abs(data - mean) <= threshold * std]
    
    return np.mean(filtered_data) if len(filtered_data) > 0 else mean

def aggregate_batch_results(base_path, data_sizes, batch_sizes, runs=3):
    """
    Aggregate results for different batch sizes
    
    Args:
        base_path: Base path for results
        data_sizes: List of data sizes to process
        batch_sizes: List of batch sizes to process
        runs: Number of runs per configuration
    """
    all_results = []
    
    for data_size in data_sizes:
        for batch_size in batch_sizes:
            batch_results = []
            
            for run in range(1, runs + 1):
                combined_file = f'{base_path}/{data_size}/Batches/{batch_size}/{run}/combined_data.json'
                
                if os.path.exists(combined_file):
                    with open(combined_file, 'r') as f:
                        data = json.load(f)
                        batch_results.append(data)
            
            if batch_results:
                # Aggregate metrics across runs
                aggregated = {
                    'data_size': data_size,
                    'batch_size': batch_size,
                    'num_runs': len(batch_results)
                }
                
                # Aggregate performance metrics
                keys = ['total_cpu_time (seconds)', "total_cpu_memory (MB)", "throughput_bps"]
                for key in keys:
                    values = [run.get(key, 0) for run in batch_results]
                    aggregated[key] = remove_outliers_and_mean(values)
                
                # Calculate total bits processed
                all_results.append(aggregated)
    
    return pd.DataFrame(all_results)

def aggregate_scaling_results(base_path, partitions, data_sizes, runs=3):
    """
    Aggregate results for different partition sizes (scaling analysis)
    
    Args:
        base_path: Base path for results
        partitions: List of partition sizes in MB
        data_sizes: List of data sizes to process
        runs: Number of runs per configuration
    """
    all_results = []
    
    for partition in partitions:
        for data_size in data_sizes:
            partition_results = []
            
            for run in range(1, runs + 1):
                combined_file = f'{base_path}/result-partition-{partition}MB/{data_size}/{run}/combined_data.json'
                
                if os.path.exists(combined_file):
                    with open(combined_file, 'r') as f:
                        data = json.load(f)
                        partition_results.append(data)
            
            if partition_results:
                # Aggregate metrics across runs
                aggregated = {
                    'partition_size_mb': partition,
                    'data_size_gb': data_size,
                    'num_runs': len(partition_results)
                }
                
                # Aggregate performance metrics
                keys = ['total_cpu_time (seconds)', "total_cpu_memory (MB)", "throughput_bps"]
                for key in keys:
                    values = [run.get(key, 0) for run in partition_results]
                    aggregated[key] = remove_outliers_and_mean(values)
                
                # Calculate total bits processed
                aggregated['total_bits'] = aggregated['throughput_bps'] * aggregated['total_cpu_time (seconds)']
                
                all_results.append(aggregated)
    
    return pd.DataFrame(all_results)

def calculate_cost_efficiency(df):
    """
    Calculate cost efficiency metrics
    
    Args:
        df: DataFrame with performance metrics
    
    Returns:
        DataFrame with cost efficiency metrics added
    """
    # AWS Lambda pricing (US East 1)
    LAMBDA_PRICE_PER_GB_SEC = 0.0000166667
    LAMBDA_PRICE_PER_REQUEST = 0.0000002
    
    def calculate_cost(row):
        duration_seconds = row['total_cpu_time (seconds)']
        memory_gb = row['total_cpu_memory (MB)'] / 1024
        gb_seconds = duration_seconds * memory_gb
        
        compute_cost = gb_seconds * LAMBDA_PRICE_PER_GB_SEC
        request_cost = LAMBDA_PRICE_PER_REQUEST
        total_cost = compute_cost + request_cost
        
        return pd.Series({
            'compute_cost': compute_cost,
            'request_cost': request_cost,
            'total_cost': total_cost,
            'gb_seconds': gb_seconds,
            'cost_per_gb_second': total_cost / gb_seconds if gb_seconds > 0 else 0
        })
    
    cost_df = df.apply(calculate_cost, axis=1)
    return pd.concat([df, cost_df], axis=1)

def generate_summary_statistics(df, output_file):
    """
    Generate summary statistics and save to CSV
    
    Args:
        df: DataFrame with performance and cost data
        output_file: Output CSV file path
    """
    # Calculate summary statistics
    summary = {
        'total_experiments': len(df),
        'avg_execution_time': df['total_cpu_time (seconds)'].mean(),
        'avg_memory_usage': df['total_cpu_memory (MB)'].mean(),
        'avg_throughput': df['throughput_bps'].mean(),
        'avg_cost': df['total_cost'].mean() if 'total_cost' in df.columns else 0,
        'best_performance_config': df.loc[df['throughput_bps'].idxmax()].to_dict() if len(df) > 0 else {},
        'most_cost_efficient_config': df.loc[df['total_cost'].idxmin()].to_dict() if 'total_cost' in df.columns and len(df) > 0 else {}
    }
    
    # Save detailed results
    df.to_csv(output_file, index=False)
    
    # Save summary
    summary_file = output_file.replace('.csv', '_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Results saved to {output_file}")
    print(f"Summary saved to {summary_file}")
    
    return summary

def main():
    parser = argparse.ArgumentParser(description='Aggregate and analyze performance results')
    parser.add_argument('--base_path', required=True, help='Base path for results')
    parser.add_argument('--output_dir', required=True, help='Output directory for analysis')
    parser.add_argument('--analysis_type', choices=['batch', 'scaling'], required=True, 
                       help='Type of analysis to perform')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    if args.analysis_type == 'batch':
        # Batch size analysis
        data_sizes = ['1GB']
        batch_sizes = [32, 64, 128, 256, 512]
        
        df = aggregate_batch_results(args.base_path, data_sizes, batch_sizes)
        df = calculate_cost_efficiency(df)
        
        output_file = os.path.join(args.output_dir, 'batch_varying_results.csv')
        summary = generate_summary_statistics(df, output_file)
        
    elif args.analysis_type == 'scaling':
        # Scaling analysis
        partitions = [25, 50, 75, 100]
        data_sizes = ['1GB', '2GB', '4GB', '6GB', '8GB', '10GB']
        
        df = aggregate_scaling_results(args.base_path, partitions, data_sizes)
        df = calculate_cost_efficiency(df)
        
        output_file = os.path.join(args.output_dir, 'result_stats.csv')
        summary = generate_summary_statistics(df, output_file)
    
    print("Analysis completed successfully!")

if __name__ == "__main__":
    main() 
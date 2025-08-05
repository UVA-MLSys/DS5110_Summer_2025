import os
import json
import argparse
import boto3
from botocore.exceptions import ClientError
import logging

def split_data_into_partitions(data_path, partition_size_mb, output_dir):
    """
    Split large data files into smaller partitions for parallel processing
    
    Args:
        data_path: Path to the input data file
        partition_size_mb: Size of each partition in MB
        output_dir: Directory to save partitioned files
    """
    partition_size_bytes = partition_size_mb * 1024 * 1024
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(data_path, 'rb') as f:
        chunk_num = 0
        while True:
            chunk = f.read(partition_size_bytes)
            if not chunk:
                break
            
            output_file = os.path.join(output_dir, f'partition_{chunk_num:04d}.pt')
            with open(output_file, 'wb') as chunk_file:
                chunk_file.write(chunk)
            
            chunk_num += 1
    
    return chunk_num

def upload_partitions_to_s3(local_dir, bucket_name, s3_prefix):
    """
    Upload partitioned files to S3 bucket
    
    Args:
        local_dir: Local directory containing partitioned files
        bucket_name: S3 bucket name
        s3_prefix: S3 prefix for the files
    """
    s3_client = boto3.client('s3')
    
    for filename in os.listdir(local_dir):
        if filename.startswith('partition_'):
            local_path = os.path.join(local_dir, filename)
            s3_key = f"{s3_prefix}/{filename}"
            
            try:
                s3_client.upload_file(local_path, bucket_name, s3_key)
                print(f"Uploaded {filename} to s3://{bucket_name}/{s3_key}")
            except ClientError as e:
                logging.error(f"Error uploading {filename}: {e}")

def create_partition_config(partition_size_mb, num_partitions, bucket_name, s3_prefix):
    """
    Create configuration for data partitions
    
    Args:
        partition_size_mb: Size of each partition in MB
        num_partitions: Number of partitions created
        bucket_name: S3 bucket name
        s3_prefix: S3 prefix for the files
    
    Returns:
        Dictionary containing partition configuration
    """
    config = {
        'partition_size_mb': partition_size_mb,
        'num_partitions': num_partitions,
        'total_size_mb': partition_size_mb * num_partitions,
        'bucket_name': bucket_name,
        's3_prefix': s3_prefix,
        'partitions': []
    }
    
    for i in range(num_partitions):
        config['partitions'].append({
            'partition_id': i,
            'filename': f'partition_{i:04d}.pt',
            's3_key': f"{s3_prefix}/partition_{i:04d}.pt"
        })
    
    return config

def main():
    parser = argparse.ArgumentParser(description='Split data into partitions for parallel processing')
    parser.add_argument('--data_path', required=True, help='Path to input data file')
    parser.add_argument('--partition_size_mb', type=int, default=25, help='Size of each partition in MB')
    parser.add_argument('--output_dir', required=True, help='Local directory to save partitions')
    parser.add_argument('--bucket_name', required=True, help='S3 bucket name')
    parser.add_argument('--s3_prefix', required=True, help='S3 prefix for uploaded files')
    parser.add_argument('--upload', action='store_true', help='Upload partitions to S3')
    
    args = parser.parse_args()
    
    # Split data into partitions
    num_partitions = split_data_into_partitions(
        args.data_path, 
        args.partition_size_mb, 
        args.output_dir
    )
    
    print(f"Created {num_partitions} partitions of {args.partition_size_mb}MB each")
    
    # Create configuration
    config = create_partition_config(
        args.partition_size_mb,
        num_partitions,
        args.bucket_name,
        args.s3_prefix
    )
    
    # Save configuration
    config_file = os.path.join(args.output_dir, 'partition_config.json')
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Saved partition configuration to {config_file}")
    
    # Upload to S3 if requested
    if args.upload:
        upload_partitions_to_s3(args.output_dir, args.bucket_name, args.s3_prefix)
        print("Uploaded all partitions to S3")

if __name__ == "__main__":
    main() 
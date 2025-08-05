import json
import boto3
import os
import sys
import subprocess
import logging
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """AWS Lambda handler for FMI inference execution"""
    
    # Extract parameters from event
    bucket = event.get('bucket')
    world_size = int(event.get('world_size', 1))
    object_type = event.get('object_type', 'folder')
    s3_object_name = event.get('S3_object_name')
    data_path = event.get('data_path')
    script = event.get('script')
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Download scripts from S3
        s3_client = boto3.client('s3')
        
        # Create directories
        os.makedirs('/tmp/scripts', exist_ok=True)
        os.makedirs('/tmp/results', exist_ok=True)
        
        # Download the entire scripts folder
        if object_type == 'folder':
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket, Prefix=s3_object_name)
            
            for page in pages:
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    local_path = f"/tmp/{key}"
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    
                    s3_client.download_file(bucket, key, local_path)
                    logger.info(f"Downloaded {key} to {local_path}")
        
        # Set up environment variables for FMI
        os.environ['FMI_RENDEZVOUS'] = 'rendezvous.uva-ds5110.com'
        os.environ['FMI_WORLD_SIZE'] = str(world_size)
        os.environ['FMI_RANK'] = '0'  # Will be set by FMI
        
        # Prepare command for inference
        cmd = [
            'python', script,
            '--data_path', data_path,
            '--model_path', '/tmp/scripts/Anomaly Detection/Fine_Tune_Model/Mixed_Inception_z_VITAE_Base_Img_Full_New_Full.pt',
            '--result_path', '/tmp/results/0.json',
            '--batch_size', '512',
            '--device', 'cpu'
        ]
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Execute the inference script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd='/tmp'
        )
        
        # Log output
        if result.stdout:
            logger.info(f"STDOUT: {result.stdout}")
        if result.stderr:
            logger.warning(f"STDERR: {result.stderr}")
        
        # Check if execution was successful
        if result.returncode != 0:
            raise Exception(f"Inference script failed with return code {result.returncode}")
        
        # Upload results back to S3
        if os.path.exists('/tmp/results/0.json'):
            s3_client.upload_file(
                '/tmp/results/0.json',
                bucket,
                'results/0.json'
            )
            logger.info("Results uploaded to S3")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Inference completed successfully',
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 
import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """AWS Lambda handler for FMI initialization"""
    
    # Extract parameters from event
    bucket = event.get('bucket')
    world_size = int(event.get('world_size', 1))
    object_type = event.get('object_type', 'folder')
    s3_object_name = event.get('S3_object_name')
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Create result directory structure in S3
        for i in range(world_size):
            result_key = f"results/{i}.json"
            
            # Create empty result file
            s3_client.put_object(
                Bucket=bucket,
                Key=result_key,
                Body=json.dumps({
                    'status': 'initialized',
                    'rank': i,
                    'world_size': world_size
                })
            )
            logger.info(f"Created result file: {result_key}")
        
        # Prepare the payload for the Map state
        map_payload = {
            'bucket': bucket,
            'world_size': world_size,
            'object_type': object_type,
            'S3_object_name': s3_object_name,
            'data_path': event.get('data_path'),
            'script': event.get('script')
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'FMI initialization completed successfully',
                'world_size': world_size,
                'map_payload': map_payload
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
import json
import boto3
import os
import logging
import numpy as np
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """AWS Lambda handler for summarizing FMI results"""
    
    # Extract parameters from event
    bucket = event.get('bucket')
    world_size = int(event.get('world_size', 1))
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Collect all results
        all_results = []
        performance_metrics = {
            'total_cpu_time': [],
            'total_cpu_memory': [],
            'execution_time': [],
            'throughput_bps': [],
            'sample_persec': [],
            'mae': [],
            'mse': [],
            'r2': []
        }
        
        # Download and process each result file
        for i in range(world_size):
            result_key = f"results/{i}.json"
            
            try:
                # Download result file
                local_path = f"/tmp/result_{i}.json"
                s3_client.download_file(bucket, result_key, local_path)
                
                # Load and process result
                with open(local_path, 'r') as f:
                    result = json.load(f)
                
                all_results.append(result)
                
                # Extract performance metrics
                for metric in performance_metrics.keys():
                    if metric in result:
                        performance_metrics[metric].append(result[metric])
                
                logger.info(f"Processed result {i}")
                
            except Exception as e:
                logger.warning(f"Failed to process result {i}: {str(e)}")
        
        # Calculate summary statistics
        summary = {
            'world_size': world_size,
            'successful_executions': len(all_results),
            'total_samples': sum(r.get('total_samples', 0) for r in all_results),
            'aggregated_metrics': {}
        }
        
        # Calculate aggregated metrics
        for metric, values in performance_metrics.items():
            if values:
                summary['aggregated_metrics'][metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'values': values
                }
        
        # Calculate overall model performance
        all_mae = [r.get('mae', 0) for r in all_results if 'mae' in r]
        all_mse = [r.get('mse', 0) for r in all_results if 'mse' in r]
        all_r2 = [r.get('r2', 0) for r in all_results if 'r2' in r]
        
        if all_mae:
            summary['model_performance'] = {
                'mae': {
                    'mean': np.mean(all_mae),
                    'std': np.std(all_mae)
                },
                'mse': {
                    'mean': np.mean(all_mse),
                    'std': np.std(all_mse)
                },
                'r2': {
                    'mean': np.mean(all_r2),
                    'std': np.std(all_r2)
                }
            }
        
        # Save summary to S3
        summary_key = "results/summary.json"
        summary_path = "/tmp/summary.json"
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        s3_client.upload_file(summary_path, bucket, summary_key)
        logger.info(f"Summary uploaded to s3://{bucket}/{summary_key}")
        
        # Create performance report
        performance_report = {
            'execution_summary': summary,
            'individual_results': all_results,
            'recommendations': generate_recommendations(summary)
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Results summarized successfully',
                'summary': summary,
                'performance_report': performance_report
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

def generate_recommendations(summary):
    """Generate recommendations based on performance analysis"""
    recommendations = []
    
    # Analyze throughput
    if 'sample_persec' in summary['aggregated_metrics']:
        throughput = summary['aggregated_metrics']['sample_persec']
        if throughput['mean'] > 200:
            recommendations.append("High throughput achieved - consider increasing batch size for better efficiency")
        elif throughput['mean'] < 100:
            recommendations.append("Low throughput detected - consider reducing batch size or world_size")
    
    # Analyze memory usage
    if 'total_cpu_memory' in summary['aggregated_metrics']:
        memory = summary['aggregated_metrics']['total_cpu_memory']
        if memory['mean'] > 10000:
            recommendations.append("High memory usage - consider optimizing model or reducing batch size")
    
    # Analyze model performance
    if 'model_performance' in summary:
        mae = summary['model_performance']['mae']['mean']
        r2 = summary['model_performance']['r2']['mean']
        
        if mae < 0.02 and r2 > 0.95:
            recommendations.append("Excellent model performance achieved")
        elif mae > 0.05 or r2 < 0.90:
            recommendations.append("Model performance needs improvement - consider retraining or hyperparameter tuning")
    
    # Analyze scalability
    if summary['successful_executions'] < summary['world_size']:
        recommendations.append("Some executions failed - check Lambda timeout and memory settings")
    
    return recommendations 
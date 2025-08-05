import boto3
import json
import pandas as pd
import argparse
from datetime import datetime, timedelta
import logging

def collect_lambda_logs(log_group_name, start_time=None, end_time=None, filter_pattern=None):
    """
    Collect Lambda execution logs from CloudWatch
    
    Args:
        log_group_name: Name of the CloudWatch log group
        start_time: Start time for log collection (datetime object)
        end_time: End time for log collection (datetime object)
        filter_pattern: Optional filter pattern for logs
    """
    
    # Initialize CloudWatch Logs client
    logs_client = boto3.client('logs')
    
    # Set default time range if not provided
    if not start_time:
        start_time = datetime.now() - timedelta(hours=1)
    if not end_time:
        end_time = datetime.now()
    
    # Convert to milliseconds
    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(end_time.timestamp() * 1000)
    
    logs_data = []
    
    try:
        # Get log streams
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True
        )
        
        for stream in response['logStreams']:
            # Get log events from this stream
            events_response = logs_client.filter_log_events(
                logGroupName=log_group_name,
                logStreamNames=[stream['logStreamName']],
                startTime=start_time_ms,
                endTime=end_time_ms,
                filterPattern=filter_pattern
            )
            
            for event in events_response['events']:
                logs_data.append({
                    'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000),
                    'log_stream': stream['logStreamName'],
                    'message': event['message'],
                    'event_id': event['eventId']
                })
        
        return logs_data
        
    except Exception as e:
        logging.error(f"Error collecting logs: {str(e)}")
        return []

def parse_performance_metrics(logs_data):
    """
    Parse performance metrics from Lambda logs
    
    Args:
        logs_data: List of log entries
    """
    performance_data = []
    
    for log in logs_data:
        message = log['message']
        
        # Look for performance-related log entries
        if 'REPORT' in message:
            # Parse Lambda execution report
            try:
                # Extract duration, billed duration, memory used, etc.
                if 'Duration:' in message:
                    duration_match = message.split('Duration:')[1].split('ms')[0].strip()
                    duration = float(duration_match)
                    
                    billed_match = message.split('Billed Duration:')[1].split('ms')[0].strip()
                    billed_duration = float(billed_match)
                    
                    memory_match = message.split('Memory Size:')[1].split('MB')[0].strip()
                    memory_size = float(memory_match)
                    
                    max_memory_match = message.split('Max Memory Used:')[1].split('MB')[0].strip()
                    max_memory_used = float(max_memory_match)
                    
                    performance_data.append({
                        'timestamp': log['timestamp'],
                        'duration_ms': duration,
                        'billed_duration_ms': billed_duration,
                        'memory_size_mb': memory_size,
                        'max_memory_used_mb': max_memory_used,
                        'log_stream': log['log_stream']
                    })
            except:
                continue
    
    return performance_data

def analyze_performance(performance_data):
    """
    Analyze performance data and generate insights
    
    Args:
        performance_data: List of performance metrics
    """
    if not performance_data:
        return {}
    
    df = pd.DataFrame(performance_data)
    
    analysis = {
        'total_executions': len(df),
        'avg_duration_ms': df['duration_ms'].mean(),
        'avg_billed_duration_ms': df['billed_duration_ms'].mean(),
        'avg_memory_used_mb': df['max_memory_used_mb'].mean(),
        'max_duration_ms': df['duration_ms'].max(),
        'min_duration_ms': df['duration_ms'].min(),
        'std_duration_ms': df['duration_ms'].std(),
        'memory_efficiency': (df['max_memory_used_mb'] / df['memory_size_mb']).mean(),
        'cost_efficiency': (df['billed_duration_ms'] / df['duration_ms']).mean()
    }
    
    return analysis

def main():
    parser = argparse.ArgumentParser(description='Collect and analyze Lambda logs')
    parser.add_argument('--log-group', type=str, required=True, help='CloudWatch log group name')
    parser.add_argument('--start-time', type=str, help='Start time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end-time', type=str, help='End time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--filter', type=str, help='Filter pattern for logs')
    parser.add_argument('--output', type=str, help='Output file for results')
    
    args = parser.parse_args()
    
    # Parse time arguments
    start_time = None
    end_time = None
    
    if args.start_time:
        start_time = datetime.strptime(args.start_time, '%Y-%m-%d %H:%M:%S')
    if args.end_time:
        end_time = datetime.strptime(args.end_time, '%Y-%m-%d %H:%M:%S')
    
    # Collect logs
    print(f"Collecting logs from {args.log_group}...")
    logs_data = collect_lambda_logs(args.log_group, start_time, end_time, args.filter)
    
    print(f"Collected {len(logs_data)} log entries")
    
    # Parse performance metrics
    performance_data = parse_performance_metrics(logs_data)
    print(f"Found {len(performance_data)} performance records")
    
    # Analyze performance
    analysis = analyze_performance(performance_data)
    
    if analysis:
        print("\nPerformance Analysis:")
        print(f"Total Executions: {analysis['total_executions']}")
        print(f"Average Duration: {analysis['avg_duration_ms']:.2f} ms")
        print(f"Average Billed Duration: {analysis['avg_billed_duration_ms']:.2f} ms")
        print(f"Average Memory Used: {analysis['avg_memory_used_mb']:.2f} MB")
        print(f"Memory Efficiency: {analysis['memory_efficiency']:.2%}")
        print(f"Cost Efficiency: {analysis['cost_efficiency']:.2%}")
    
    # Save results
    if args.output:
        results = {
            'logs_data': [log.__dict__ for log in logs_data],
            'performance_data': performance_data,
            'analysis': analysis
        }
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main() 
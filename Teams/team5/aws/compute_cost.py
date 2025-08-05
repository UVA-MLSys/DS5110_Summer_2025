import json
import pandas as pd
import argparse
from datetime import datetime

# AWS Lambda pricing (US East 1, as of 2024)
LAMBDA_PRICE_PER_GB_SEC = 0.0000166667  # $0.0000166667 per GB-second
LAMBDA_PRICE_PER_REQUEST = 0.0000002     # $0.0000002 per request

def calculate_lambda_cost(duration_ms, memory_mb, num_requests=1):
    """
    Calculate AWS Lambda cost based on duration and memory usage
    
    Args:
        duration_ms: Duration in milliseconds
        memory_mb: Memory usage in MB
        num_requests: Number of requests (default 1)
    
    Returns:
        Dictionary with cost breakdown
    """
    # Convert to GB-seconds
    duration_seconds = duration_ms / 1000
    memory_gb = memory_mb / 1024
    gb_seconds = duration_seconds * memory_gb
    
    # Calculate costs
    compute_cost = gb_seconds * LAMBDA_PRICE_PER_GB_SEC
    request_cost = num_requests * LAMBDA_PRICE_PER_REQUEST
    total_cost = compute_cost + request_cost
    
    return {
        'compute_cost': compute_cost,
        'request_cost': request_cost,
        'total_cost': total_cost,
        'gb_seconds': gb_seconds,
        'duration_seconds': duration_seconds,
        'memory_gb': memory_gb
    }

def analyze_cost_efficiency(performance_data):
    """
    Analyze cost efficiency of Lambda executions
    
    Args:
        performance_data: List of performance metrics
    """
    if not performance_data:
        return {}
    
    df = pd.DataFrame(performance_data)
    
    # Calculate costs for each execution
    costs = []
    for _, row in df.iterrows():
        cost = calculate_lambda_cost(
            row['billed_duration_ms'],
            row['max_memory_used_mb']
        )
        costs.append(cost)
    
    # Add cost data to dataframe
    cost_df = pd.DataFrame(costs)
    df = pd.concat([df, cost_df], axis=1)
    
    # Calculate cost statistics
    cost_analysis = {
        'total_executions': len(df),
        'total_cost': df['total_cost'].sum(),
        'avg_cost_per_execution': df['total_cost'].mean(),
        'total_compute_cost': df['compute_cost'].sum(),
        'total_request_cost': df['request_cost'].sum(),
        'cost_efficiency': {
            'avg_gb_seconds': df['gb_seconds'].mean(),
            'avg_memory_utilization': (df['max_memory_used_mb'] / df['memory_size_mb']).mean(),
            'avg_duration_efficiency': (df['duration_ms'] / df['billed_duration_ms']).mean()
        },
        'cost_distribution': {
            'compute_percentage': (df['compute_cost'].sum() / df['total_cost'].sum()) * 100,
            'request_percentage': (df['request_cost'].sum() / df['total_cost'].sum()) * 100
        }
    }
    
    return cost_analysis, df

def generate_cost_recommendations(cost_analysis):
    """
    Generate cost optimization recommendations
    
    Args:
        cost_analysis: Cost analysis results
    """
    recommendations = []
    
    # Memory utilization recommendations
    memory_util = cost_analysis['cost_efficiency']['avg_memory_utilization']
    if memory_util < 0.5:
        recommendations.append("Low memory utilization - consider reducing Lambda memory allocation")
    elif memory_util > 0.9:
        recommendations.append("High memory utilization - consider increasing Lambda memory allocation")
    
    # Duration efficiency recommendations
    duration_efficiency = cost_analysis['cost_efficiency']['avg_duration_efficiency']
    if duration_efficiency < 0.8:
        recommendations.append("Low duration efficiency - consider optimizing code or increasing memory")
    
    # Cost distribution recommendations
    compute_percentage = cost_analysis['cost_distribution']['compute_percentage']
    if compute_percentage > 95:
        recommendations.append("High compute costs - consider optimizing algorithm or reducing execution time")
    
    # Overall cost recommendations
    avg_cost = cost_analysis['avg_cost_per_execution']
    if avg_cost > 0.001:  # $0.001 per execution
        recommendations.append("High per-execution cost - consider batching or optimization")
    
    return recommendations

def main():
    parser = argparse.ArgumentParser(description='Calculate AWS Lambda costs')
    parser.add_argument('--input', type=str, required=True, help='Input JSON file with performance data')
    parser.add_argument('--output', type=str, help='Output file for cost analysis')
    
    args = parser.parse_args()
    
    # Load performance data
    with open(args.input, 'r') as f:
        data = json.load(f)
    
    performance_data = data.get('performance_data', [])
    
    if not performance_data:
        print("No performance data found in input file")
        return
    
    # Analyze costs
    cost_analysis, detailed_df = analyze_cost_efficiency(performance_data)
    
    # Generate recommendations
    recommendations = generate_cost_recommendations(cost_analysis)
    
    # Print results
    print("AWS Lambda Cost Analysis")
    print("=" * 50)
    print(f"Total Executions: {cost_analysis['total_executions']}")
    print(f"Total Cost: ${cost_analysis['total_cost']:.6f}")
    print(f"Average Cost per Execution: ${cost_analysis['avg_cost_per_execution']:.6f}")
    print(f"Compute Cost: ${cost_analysis['total_compute_cost']:.6f}")
    print(f"Request Cost: ${cost_analysis['total_request_cost']:.6f}")
    print(f"Average GB-Seconds: {cost_analysis['cost_efficiency']['avg_gb_seconds']:.4f}")
    print(f"Average Memory Utilization: {cost_analysis['cost_efficiency']['avg_memory_utilization']:.2%}")
    print(f"Average Duration Efficiency: {cost_analysis['cost_efficiency']['avg_duration_efficiency']:.2%}")
    
    print("\nCost Distribution:")
    print(f"Compute Cost: {cost_analysis['cost_distribution']['compute_percentage']:.1f}%")
    print(f"Request Cost: {cost_analysis['cost_distribution']['request_percentage']:.1f}%")
    
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"- {rec}")
    
    # Save detailed results
    if args.output:
        results = {
            'cost_analysis': cost_analysis,
            'recommendations': recommendations,
            'detailed_data': detailed_df.to_dict('records')
        }
        
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to {args.output}")

if __name__ == "__main__":
    main() 
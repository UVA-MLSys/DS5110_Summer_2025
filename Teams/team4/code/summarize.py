import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Determine the list of tasks from the event
        if isinstance(event, list):
            tasks = event
        elif isinstance(event, dict) and "body" in event:
            tasks = event["body"]
        else:
            raise ValueError("Invalid event format. Expecting a list or dict with 'body' key.")

        # Determine the bucket and prefix
        first = tasks[0]
        bucket_name = (
            event.get("bucket")
            or first.get("RESULT_BUCKET")
            or first.get("BUCKET")
            or first.get("S3_BUCKET")
            or "team4-cosmical"
        )
        prefix = first["RESULT_PATH"]

        logger.info(f"Looking for result files in s3://{bucket_name}/{prefix}")

        s3_client = boto3.client("s3")
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if "Contents" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps("No files found in the specified S3 bucket or prefix.")
            }

        output_file_key = f"{prefix}/combined_data.json"
        all_data = []

        for item in response["Contents"]:
            file_key = item["Key"]
            if file_key.endswith(".json") and file_key != output_file_key:
                obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                file_content = obj["Body"].read().decode("utf-8")
                data = json.loads(file_content)
                all_data.extend(data if isinstance(data, list) else [data])

        concatenated_json = json.dumps(all_data)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=output_file_key,
            Body=concatenated_json,
            ContentType="application/json"
        )

        logger.info(f"Combined file saved to s3://{bucket_name}/{output_file_key}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Combined data uploaded successfully",
                "s3_path": f"s3://{bucket_name}/{output_file_key}"
            })
        }
    except Exception as e:
        # Do not call exit(); return a meaningful error response instead
        logger.error(f"Unhandled error in summarize function: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error in summarize function: {str(e)}")
        }

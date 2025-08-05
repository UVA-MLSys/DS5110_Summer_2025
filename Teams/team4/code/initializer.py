import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client("s3")

# ---------- Helper Functions ----------

def get_ith_filename(i):
    return f"{i+1}.pt"

def get_file_list(bucket, prefix):
    logger.info(f"Looking for files in bucket: {bucket}, prefix: {prefix}")
    resp = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if "Contents" not in resp:
        logger.error("No .pt files found under that bucket/prefix.")
        return []

    filenames = [
        obj["Key"] for obj in resp["Contents"] if obj["Key"].endswith(".pt")
    ]

    logger.info(f"Found {len(filenames)} .pt files "
                f"(first 5: {filenames[:5]} …)")
    return filenames

def ceil(a, b):
    return (a + b - 1) // b

# ---------- Lambda Handler ----------

def lambda_handler(event, context):
    logger.info("Received event:\n" + json.dumps(event, indent=2))

    # Extract parameters
    bucket          = event["bucket"]
    object_type     = event["object_type"]
    script          = event["script"]
    s3_obj_name     = event["S3_object_name"]
    result_path     = event["result_path"]
    file_limit      = int(event["file_limit"])
    batch_size      = int(event.get("batch_size", 32))
    world_size      = int(event.get("world_size", file_limit))
    data_bucket     = event["data_bucket"]
    data_prefix     = event["data_prefix"]

    # Get list of .pt files
    filenames = get_file_list(data_bucket, data_prefix)[:file_limit]
    total_files = len(filenames)

    logger.info(f"Partitioning {total_files} files across {world_size} ranks")

    # Partition files across workers (ranks)
    data_map, start = {}, 0
    for rank in range(world_size):
        if rank < total_files:
            step = ceil(total_files - start, world_size - rank)
            data_slice = filenames[start : start + step]
            start += step
            data_map[rank] = data_slice[0] if len(data_slice) == 1 else data_slice
        else:
            data_map[rank] = None

    # Create per-rank job payloads
    all_jobs = []

    logger.info(f"Creating jobs for batch_size={batch_size} → {result_path}")

    for rank in range(world_size):
        payload = {
            "S3_BUCKET":        bucket,
            "BUCKET":           bucket,
            "RESULT_BUCKET":    bucket,
            "S3_OBJECT_NAME":   s3_obj_name,
            "SCRIPT":           script,
            "S3_OBJECT_TYPE":   object_type,
            "WORLD_SIZE":       str(world_size),
            "RANK":             str(rank),
            "DATA_BUCKET":      data_bucket,
            "DATA_PREFIX":      data_prefix,
            "DATA_PATH":        data_map[rank],
            "RESULT_PATH":      result_path,
            "BATCH_SIZE":       batch_size
        }
        all_jobs.append(payload)

    logger.info(f"Created {len(all_jobs)} job payloads")

    # Save full payload.json to S3 (for inspection/debugging)
    master = dict(event)  # shallow copy
    #master["file_limit"] = file_limit
    master["batch_size"] = batch_size
    master["data_map"]   = data_map
    master["body"]       = all_jobs

    s3_client.put_object(
        Bucket=bucket,
        Key="payload.json",
        Body=json.dumps(master, indent=4),
        ContentType="application/json"
    )
    logger.info("payload.json written to S3")

    return {
        "statusCode": 200,
        "body": all_jobs
    }

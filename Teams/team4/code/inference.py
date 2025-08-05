import sys, argparse, json, os, logging, boto3, io, gc
import torch
from torch.utils.data import DataLoader, TensorDataset
from torch.profiler import profile, ProfilerActivity
import platform

s3_client = boto3.client('s3')

# Utility: upload file to S3
def upload_to_s3(bucket, key, content):
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(content),
        ContentType="application/json"
    )

# Load a .pt file from S3 (single or multi-rank)
def load_data(data_path, bucket):
    if isinstance(data_path, list):
        data_list = [load_data(path, bucket) for path in data_path]
        return concatenate_data(data_list)

    buffer = io.BytesIO()
    s3_client.download_fileobj(Bucket=bucket, Key=data_path, Fileobj=buffer)
    buffer.seek(0)
    return torch.load(buffer, weights_only=False)

def concatenate_data(data_list):
    images, mags, reds = [], [], []
    for d in data_list:
        images.append(d[:][0])
        mags.append(d[:][1])
        reds.append(d[:][2])
    return TensorDataset(torch.cat(images), torch.cat(mags), torch.cat(reds))

# Load model
def load_model(path, device):
    model = torch.load(path, map_location=device, weights_only=False)
    return model.module.eval()

# Perform inference
def run_inference(model, dataloader, args):
    rank = args.rank
    device = args.device
    batch_size = args.batch_size
    result_path = args.result_path
    data_path = args.data_path

    total_data_bits = 0
    num_batches = 0
    num_samples = 0

    with profile(activities=[ProfilerActivity.CPU], profile_memory=True) as prof:
        with torch.no_grad():
            for i, batch in enumerate(dataloader):
                image, magnitude = batch[0].to(device), batch[1].to(device)
                _ = model([image, magnitude])

                total_data_bits += (image.element_size() * image.nelement() + magnitude.element_size() * magnitude.nelement()) * 8
                num_batches += 1
                num_samples += len(image)
                gc.collect()

    avg = prof.key_averages().total_average()
    total_cpu_time = avg.cpu_time_total / 1e6
    total_cpu_mem = avg.cpu_memory_usage / 1e6
    avg_time_per_batch = total_cpu_time / (num_samples / batch_size)

    result = {
        "rank": rank,
        "batch_size": batch_size,
        "file_limit": args.file_limit,
        "data_prefix": args.data_prefix,
        "data_bucket": args.data_bucket,
        "result_path": result_path,
        "data_path": data_path,
        "total_samples": num_samples,
        "num_batches": num_batches,
        "execution_time (seconds/batch)": round(avg_time_per_batch, 4),
        "total_cpu_time (seconds)": round(total_cpu_time, 2),
        "total_cpu_memory (MB)": round(total_cpu_mem, 2),
        "throughput_bps": int(total_data_bits / total_cpu_time) if total_cpu_time else 0,
        "sample_persec": round(num_samples / total_cpu_time, 2) if total_cpu_time else 0,
        "device": device
    }

    output_key = f"{result_path}/{rank}.json"
    upload_to_s3(args.result_bucket, output_key, result)
    print(f"✅ Inference complete for rank {rank}, results saved to s3://{args.result_bucket}/{output_key}")

# Entry point
if __name__ == '__main__':
    PRJ_DIR = '/tmp/Anomaly Detection/'

    parser = argparse.ArgumentParser()
    parser.add_argument('--rank', type=int)
    parser.add_argument('--world_size', type=int)
    parser.add_argument('--device', type=str, default='cpu')
    parser.add_argument('--model_path', type=str, default=f'{PRJ_DIR}Fine_Tune_Model/Mixed_Inception_z_VITAE_Base_Img_Full_New_Full.pt')
    args = parser.parse_args()

    # Load from payload.json in S3
    obj = s3_client.get_object(Bucket='team4-cosmical', Key='payload.json')
    payload = json.loads(obj['Body'].read().decode('utf-8'))

    args.batch_size   = int(payload['batch_size'])
    args.file_limit   = int(payload.get('file_limit', -1))
    args.data_prefix  = payload.get('data_prefix', 'unknown')
    args.result_path  = payload['result_path']
    args.data_bucket  = payload['data_bucket']
    args.result_bucket = payload.get('bucket', payload['data_bucket'])
    args.data_path    = payload['data_map'][str(args.rank)]

    if args.data_path is None:
        print(f"❌ Rank {args.rank}: No data path assigned.")
        sys.exit(0)

    data = load_data(args.data_path, args.data_bucket)
    loader = DataLoader(data, batch_size=args.batch_size)

    model = load_model(args.model_path, args.device)
    run_inference(model, loader, args)

# Cloud Provider Reference

Detailed information about supported cloud providers including pricing, server sizes, and regions.

## Hetzner Cloud

European cloud provider with excellent price/performance ratio. Best value for most use cases.

**Authentication:** API token from [Hetzner Cloud Console](https://console.hetzner.cloud/)

### Server Types

| Type | vCPU | RAM | Storage | Price/mo | Architecture | Notes |
|------|------|-----|---------|----------|--------------|-------|
| cx22 | 2 | 4 GB | 40 GB | ~$4 | Intel (shared) | Good for light dev work |
| **cx32** | 4 | 8 GB | 80 GB | ~$8 | Intel (shared) | **Recommended** - balanced |
| cx42 | 8 | 16 GB | 160 GB | ~$16 | Intel (shared) | Heavy workloads |
| cx52 | 16 | 32 GB | 320 GB | ~$32 | Intel (shared) | Large projects |
| cpx21 | 3 | 4 GB | 80 GB | ~$5 | AMD (shared) | AMD alternative |
| cpx31 | 4 | 8 GB | 160 GB | ~$10 | AMD (shared) | AMD alternative |
| cpx41 | 8 | 16 GB | 240 GB | ~$20 | AMD (shared) | AMD alternative |
| cpx51 | 16 | 32 GB | 360 GB | ~$40 | AMD (shared) | AMD alternative |
| cax21 | 4 | 8 GB | 80 GB | ~$6 | ARM64 | EU only, great value |
| cax31 | 8 | 16 GB | 160 GB | ~$11 | ARM64 | EU only |
| cax41 | 16 | 32 GB | 320 GB | ~$22 | ARM64 | EU only |
| ccx23 | 4 | 16 GB | 80 GB | ~$30 | Intel (dedicated) | EU only, dedicated vCPU |
| ccx33 | 8 | 32 GB | 160 GB | ~$60 | Intel (dedicated) | EU only |
| ccx43 | 16 | 64 GB | 240 GB | ~$120 | Intel (dedicated) | EU only |
| ccx53 | 32 | 128 GB | 360 GB | ~$240 | Intel (dedicated) | EU only |
| ccx63 | 48 | 192 GB | 480 GB | ~$360 | Intel (dedicated) | EU only |

### Regions

| Location | Code | Notes |
|----------|------|-------|
| Falkenstein, DE | **fsn1** | Default, all server types |
| Nuremberg, DE | nbg1 | All server types |
| Helsinki, FI | hel1 | All server types |
| Ashburn, US | ash | Intel/AMD shared only |
| Hillsboro, US | hil | Intel/AMD shared only |
| Singapore | sin | Intel/AMD shared only |

**Notes:**
- ARM (cax*) and dedicated (ccx*) types only available in EU locations (fsn1, nbg1, hel1)
- US locations have limited server type availability
- Pricing is approximate and may vary by region

---

## Amazon Web Services (AWS)

Enterprise cloud with global presence. Higher cost but extensive features.

**Authentication:** Access Key + Secret Key from [IAM Console](https://console.aws.amazon.com/iam/)

### Instance Types

| Type | vCPU | RAM | Price/mo* | Notes |
|------|------|-----|-----------|-------|
| t3.micro | 2 | 1 GB | ~$8 | Free tier eligible, minimal resources |
| t3.small | 2 | 2 GB | ~$15 | Light workloads |
| **t3.medium** | 2 | 4 GB | ~$30 | **Recommended** - balanced |
| t3.large | 2 | 8 GB | ~$60 | More memory |
| t3.xlarge | 4 | 16 GB | ~$120 | Heavy workloads |
| t3.2xlarge | 8 | 32 GB | ~$240 | Large projects |
| m6i.large | 2 | 8 GB | ~$70 | Compute optimized |
| m6i.xlarge | 4 | 16 GB | ~$140 | Compute optimized |
| c6i.large | 2 | 4 GB | ~$60 | CPU intensive |
| c6i.xlarge | 4 | 8 GB | ~$120 | CPU intensive |

*Prices are approximate for us-east-1 with on-demand pricing. Actual costs vary by region.

### Regions

| Region | Code | Notes |
|--------|------|-------|
| N. Virginia | **us-east-1** | Default, lowest prices |
| Ohio | us-east-2 | US alternative |
| Oregon | us-west-2 | West coast |
| N. California | us-west-1 | West coast |
| Ireland | eu-west-1 | Europe |
| Frankfurt | eu-central-1 | Europe |
| London | eu-west-2 | Europe |
| Paris | eu-west-3 | Europe |
| Tokyo | ap-northeast-1 | Asia Pacific |
| Singapore | ap-southeast-1 | Asia Pacific |
| Sydney | ap-southeast-2 | Asia Pacific |

**Notes:**
- T3 instances use burstable CPU credits
- Additional costs: EBS storage (~$0.10/GB/mo), data transfer
- Consider Reserved Instances for 30-60% savings on long-term use

---

## DigitalOcean

Simple, developer-friendly cloud. Straightforward pricing.

**Authentication:** API token from [DigitalOcean Control Panel](https://cloud.digitalocean.com/account/api/tokens)

### Droplet Sizes

| Size | vCPU | RAM | Storage | Price/mo | Notes |
|------|------|-----|---------|----------|-------|
| s-1vcpu-1gb | 1 | 1 GB | 25 GB | $6 | Minimal, not recommended |
| s-1vcpu-2gb | 1 | 2 GB | 50 GB | $12 | Light workloads |
| **s-2vcpu-4gb** | 2 | 4 GB | 80 GB | $24 | **Recommended** - balanced |
| s-4vcpu-8gb | 4 | 8 GB | 160 GB | $48 | Heavy workloads |
| s-8vcpu-16gb | 8 | 16 GB | 320 GB | $96 | Large projects |
| g-2vcpu-8gb | 2 | 8 GB | 60 GB | $68 | General purpose |
| g-4vcpu-16gb | 4 | 16 GB | 120 GB | $136 | General purpose |
| c-2 | 2 | 4 GB | 50 GB | $42 | CPU optimized |
| c-4 | 4 | 8 GB | 100 GB | $84 | CPU optimized |
| m-2vcpu-16gb | 2 | 16 GB | 50 GB | $84 | Memory optimized |

### Regions

| Region | Code | Notes |
|--------|------|-------|
| New York 1 | **nyc1** | Default |
| New York 3 | nyc3 | US East alternative |
| San Francisco 3 | sfo3 | US West |
| Toronto 1 | tor1 | Canada |
| Amsterdam 3 | ams3 | Europe |
| London 1 | lon1 | Europe |
| Frankfurt 1 | fra1 | Europe |
| Singapore 1 | sgp1 | Asia Pacific |
| Bangalore 1 | blr1 | India |
| Sydney 1 | syd1 | Australia |

**Notes:**
- Pricing is flat (no variable compute charges)
- 1TB outbound transfer included
- Backups available for +20%

---

## Provider Comparison

| Feature | Hetzner | AWS | DigitalOcean |
|---------|---------|-----|--------------|
| **Best for** | Price/performance | Enterprise/Global | Simplicity |
| **Starting price** | ~$4/mo | ~$8/mo | $6/mo |
| **Recommended** | cx32 (~$8) | t3.medium (~$30) | s-2vcpu-4gb ($24) |
| **Regions** | 6 | 20+ | 10+ |
| **ARM support** | Yes (EU only) | Yes | No |
| **Setup complexity** | Low | Medium | Low |

### Recommendations

- **Best value**: Hetzner cx32 or cax21 (ARM) - $6-8/mo for 4 vCPU, 8GB RAM
- **US-based**: Hetzner ash/hil or DigitalOcean nyc1/sfo3
- **Enterprise needs**: AWS with Reserved Instances
- **Simple billing**: DigitalOcean (flat pricing, no surprises)

---

## Getting API Credentials

### Hetzner Cloud

1. Log in to [Hetzner Cloud Console](https://console.hetzner.cloud/)
2. Select or create a project
3. Go to **Security** > **API tokens**
4. Click **Generate API token**
5. Give it a name and select **Read & Write**
6. Copy the token (shown only once)

### AWS

1. Log in to [AWS Console](https://console.aws.amazon.com/)
2. Go to **IAM** > **Users**
3. Select your user or create a new one
4. Go to **Security credentials** tab
5. Click **Create access key**
6. Select **CLI** use case
7. Copy both Access Key ID and Secret Access Key

**Required IAM permissions:**
- `AmazonEC2FullAccess`
- `AmazonVPCFullAccess`

### DigitalOcean

1. Log in to [DigitalOcean Control Panel](https://cloud.digitalocean.com/)
2. Go to **API** in the left sidebar
3. Click **Generate New Token**
4. Give it a name and select **Read & Write**
5. Copy the token (shown only once)

# KnowledgeCity Educational Platform - Infrastructure

A globally distributed educational platform with multi-regional deployment supporting users in Saudi Arabia and the United States, built using AWS CDK and modern DevOps practices.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GLOBAL LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React) - Deployed to CloudFront CDN             │
│  ├── Static files served from S3                               │
│  ├── Cached at edge locations worldwide                        │
│  └── Single codebase, but region-aware                         │
│                                                                 │
│  Global Content (Courses/Videos)                               │
│  ├── Master content in S3                                      │
│  ├── Replicated to all regions                                 │
│  └── Served via CloudFront CDN                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────┐                    ┌─────────────────────┐
│     US REGION       │                    │    KSA REGION       │
│   (us-east-1)       │                    │   (me-south-1)      │
├─────────────────────┤                    ├─────────────────────┤
│ ┌─────────────────┐ │                    │ ┌─────────────────┐ │
│ │   EKS Cluster   │ │                    │ │   EKS Cluster   │ │
│ │ ┌─────────────┐ │ │                    │ │ ┌─────────────┐ │ │
│ │ │ PHP API     │ │ │                    │ │ │ PHP API     │ │ │
│ │ │ Analytics   │ │ │                    │ │ │ Analytics   │ │ │
│ │ │ Video Proc  │ │ │                    │ │ │ Video Proc  │ │ │
│ │ └─────────────┘ │ │                    │ │ └─────────────┘ │ │
│ └─────────────────┘ │                    │ └─────────────────┘ │
│                     │                    │                     │
│ ┌─────────────────┐ │                    │ ┌─────────────────┐ │
│ │ RDS Database    │ │                    │ │ RDS Database    │ │
│ │ (US Users Data) │ │                    │ │ (KSA Users Data)│ │
│ └─────────────────┘ │                    │ └─────────────────┘ │
└─────────────────────┘                    └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

Before deploying the infrastructure, ensure you have the following tools installed:

- **AWS CLI**
- **AWS CDK** 
- **CDK8s** 
- **kubectl**
- **Docker**
- **Node.js** 
- **Python** 
- **TypeScript**

### Installation

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Install AWS CDK
npm install -g aws-cdk

# Install CDK8s
npm install -g cdk8s-cli

# Install kubectl
brew install kubectl

# Verify installations
aws --version
cdk --version
cdk8s --version
kubectl version --client
```

### AWS Configuration

```bash
# Configure AWS credentials
aws configure

# Set up AWS profiles for multi-region deployment
aws configure set region us-east-1 --profile us-region
aws configure set region me-south-1 --profile ksa-region
```

## 📁 Project Structure

```
├── infrastructure/
│   ├── eks-infra/             # EKS clusters + microservices
│   └── iac-frontend/          # React + CloudFront + S3 (frontend infra)
├── Rds-cluster-instance/      # Multi-AZ RDS clusters
├── kubernetes-iac/            # CDK8s manifests for K8s (Ingress, Services, Deployments, etc.)
├── docs/                      # Documentation
└── README.md                  # Project overview
                
```

## 🔧 Deployment Guide

### 1. Frontend Infrastructure (Global)

```bash
cd infrastructure/iac-frontend

# Install dependencies
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk synth
cdk bootstrap --profile default

# Deploy frontend
cdk synth 
cdk deploy
```

### 2. RDS Database Clusters (Regional)

Configure `settings.py` for each region:

```bash
cd Rds-cluster-instance

# Edit settings.py with your account details
# - AWS Account ID
# - VPC ID
# - Subnet IDs
# - Security Group IDs
# - Region

# Install dependencies
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Deploy US region
cdk synth
cdk deploy --profile us-region

# Deploy KSA region
cdk synth
cdk deploy --profile ksa-region
```

### 3. EKS Clusters (Regional)

```bash
cd infrastructure/eks-infra

# Install dependencies
npm install

# Deploy US region
cdk synth -c stage=prod
cdk deploy -c stage=prod --profile us-region

# Deploy KSA region
cdk synth -c stage=dev
cdk deploy --profile ksa-region
```
### 4. k8s Deployment (Regional)

```bash
# Makr sure your cluster connected

cd kubernetes-iac/ingress

# Edit settings.py with your CR ARN & others variables define like host etc and namespace

# Install dependencies
pipenv install

# Deploy US region
cdk8s synth

# dist folder will be created in yml file

kubectl apply -f dist

# After Ingress Please deploy the other microservcie with the same above k8s Depoyment Guide like ingress.

```


## 🎯 Component Details

### Frontend (React)
- **Technology**: React Single Page Application
- **Hosting**: Amazon S3 with CloudFront CDN
- **Domain**: Route 53 with custom domain
- **Caching**: Global edge locations for minimal latency

### Backend Services
- **PHP Monolith**: Core business logic API
- **Analytics Microservice**: ClickHouse-based data analysis
- **Video Processing**: Automated video conversion and encoding
- **Future Microservices**: Scalable architecture for growth

### Database Strategy
- **Regional Isolation**: US users → US RDS, KSA users → KSA RDS
- **High Availability**: Multi-AZ deployment in each region
- **Backup**: Automated backups with cross-region replication

### Container Orchestration
- **EKS Clusters**: Managed Kubernetes in each region
- **Auto Scaling**: Horizontal pod autoscaling
- **Load Balancing**: Application Load Balancers
- **Service Mesh**: Istio for microservices communication

## 🔒 Security & Compliance

- **Data Residency**: Regional data isolation (US/KSA)
- **Encryption**: At-rest and in-transit encryption
- **Access Control**: IAM roles and RBAC
- **DDoS Protection**: AWS Shield Advanced
- **WAF**: Web Application Firewall rules
- **Secrets Management**: AWS Secrets Manager

## 📊 Monitoring & Observability

- **Metrics**: Prometheus + Grafana
- **Logging**: ELK/EFK stack
- **Tracing**: OpenTelemetry
- **Alerting**: CloudWatch + PagerDuty
- **Health Checks**: Multi-layer health monitoring

## 💰 Cost Optimization

- **Storage Classes**: Intelligent tiering for S3
- **Reserved Instances**: Long-term compute savings
- **Spot Instances**: Cost-effective batch processing
- **CDN Optimization**: CloudFront cost optimization
- **Auto Scaling**: Dynamic resource allocation

## 🌍 Multi-Regional Deployment

### Supported Regions
- **Primary**: US East (us-east-1)
- **Secondary**: Middle East (me-south-1)
- **Future**: Expandable to additional regions

### Data Flow
1. Users access global frontend via CloudFront
2. API requests routed to nearest regional backend
3. User data stored in respective regional databases
4. Global content cached at edge locations

---

**KnowledgeCity DevOps Team**  
Built with  using AWS CDK, Kubernetes, and modern DevOps practices
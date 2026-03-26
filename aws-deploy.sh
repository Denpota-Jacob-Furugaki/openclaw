#!/bin/bash

# OpenClaw AWS Deployment Script for ap-northeast-3 (Osaka)
# This script helps deploy OpenClaw to an EC2 instance

set -e

# Configuration
AWS_REGION="ap-northeast-3"
INSTANCE_TYPE="t3.medium"  # Adjust based on your needs
AMI_ID="ami-0c960bcbab6e0b78b"  # Ubuntu 22.04 LTS in ap-northeast-3
KEY_NAME="openclaw-key"
SECURITY_GROUP_NAME="openclaw-sg"

echo "========================================="
echo "OpenClaw AWS Deployment Script"
echo "Region: ${AWS_REGION}"
echo "========================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install it first."
    echo "Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

echo "Step 1: Creating security group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name ${SECURITY_GROUP_NAME} \
    --description "Security group for OpenClaw" \
    --region ${AWS_REGION} \
    --output text \
    --query 'GroupId' 2>/dev/null || \
    aws ec2 describe-security-groups \
    --group-names ${SECURITY_GROUP_NAME} \
    --region ${AWS_REGION} \
    --output text \
    --query 'SecurityGroups[0].GroupId')

echo "Security Group ID: ${SECURITY_GROUP_ID}"

echo "Step 2: Configuring security group rules..."
# Allow SSH (22)
aws ec2 authorize-security-group-ingress \
    --group-id ${SECURITY_GROUP_ID} \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region ${AWS_REGION} 2>/dev/null || true

# Allow HTTP (80)
aws ec2 authorize-security-group-ingress \
    --group-id ${SECURITY_GROUP_ID} \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region ${AWS_REGION} 2>/dev/null || true

# Allow HTTPS (443)
aws ec2 authorize-security-group-ingress \
    --group-id ${SECURITY_GROUP_ID} \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0 \
    --region ${AWS_REGION} 2>/dev/null || true

# Allow custom port 8080
aws ec2 authorize-security-group-ingress \
    --group-id ${SECURITY_GROUP_ID} \
    --protocol tcp \
    --port 8080 \
    --cidr 0.0.0.0/0 \
    --region ${AWS_REGION} 2>/dev/null || true

echo "Step 3: Creating EC2 key pair (if not exists)..."
if ! aws ec2 describe-key-pairs --key-names ${KEY_NAME} --region ${AWS_REGION} &> /dev/null; then
    aws ec2 create-key-pair \
        --key-name ${KEY_NAME} \
        --region ${AWS_REGION} \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "Key pair created and saved to ${KEY_NAME}.pem"
else
    echo "Key pair ${KEY_NAME} already exists"
fi

echo "Step 4: Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ${AMI_ID} \
    --instance-type ${INSTANCE_TYPE} \
    --key-name ${KEY_NAME} \
    --security-group-ids ${SECURITY_GROUP_ID} \
    --region ${AWS_REGION} \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=OpenClaw-Server}]' \
    --user-data file://user-data.sh \
    --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=30,VolumeType=gp3}' \
    --output text \
    --query 'Instances[0].InstanceId')

echo "Instance ID: ${INSTANCE_ID}"
echo "Waiting for instance to start..."

aws ec2 wait instance-running \
    --instance-ids ${INSTANCE_ID} \
    --region ${AWS_REGION}

PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids ${INSTANCE_ID} \
    --region ${AWS_REGION} \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo "Instance ID: ${INSTANCE_ID}"
echo "Public IP: ${PUBLIC_IP}"
echo "SSH Command: ssh -i ${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo ""
echo "The instance is being configured. Please wait 5-10 minutes for the setup to complete."
echo "You can access OpenClaw at: http://${PUBLIC_IP}"
echo "========================================="

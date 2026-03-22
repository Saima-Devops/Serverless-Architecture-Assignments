# Assignment On Serverless Architecture & CLoud Architecture by using AWS Automation with Boto3 & Lambda

This repository contains Python scripts and AWS Lambda functions to automate various tasks on AWS using **Boto3**. It demonstrates how to manage EC2 instances, handle automated start/stop workflows, and perform other AWS automation tasks.

## Features

- **EC2 Automation**  
  - Start and stop EC2 instances based on tags (`Auto-Start` / `Auto-Stop`)  
  - Automatic logging of affected instances  

- **Lambda Integration**  
  - Run scripts as Lambda functions  
  - Can be triggered manually or scheduled with EventBridge  

- **Boto3 Usage**  
  - Uses Boto3 to interact with AWS services programmatically  
  - Examples of describing, starting, and stopping EC2 instances  
# 🤖 terraform-ai-operations-agent

Managing Terraform operations manually slows down modern infrastructure workflows.

This project introduces an **AI-powered Terraform Operations Agent** built using **Model Context Protocol (MCP)**, enabling LLM agents such as **Claude or GPT** to safely execute Terraform operations locally.

Instead of manually running infrastructure commands, AI agents can understand infrastructure context and assist with provisioning, validation, and planning workflows — while maintaining execution safety.

---

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Terraform](https://img.shields.io/badge/Terraform-Automation-purple)
![Azure](https://img.shields.io/badge/Azure-Cloud-blue)
![MCP](https://img.shields.io/badge/MCP-Agent-green)

---

## 🚀 Project Goal

Build an **AI-assisted Infrastructure Operations Layer** where:

LLM Agent → MCP Server → Terraform CLI → Cloud Infrastructure

This project demonstrates how AI agents can participate in real DevOps workflows while keeping infrastructure execution secure and controlled.

---

## 🏗 Architecture Overview

            Claude Desktop / LLM Agent
                        │
                        ▼
            Terraform MCP Server (Python)
                        │
                        ▼
                Terraform CLI
                        │
                        ▼
            Azure Infrastructure


The MCP server acts as a **secure execution boundary** between AI systems and cloud infrastructure.


---

## 📦 Example Infrastructure

This repository includes a real Azure infrastructure example managed through the MCP Terraform Agent.

📁 Location: examples/azure-terraform-project

### Provisioned Resources

- Azure Resource Group
- Azure Data Factory
- Azure Data Lake Storage Gen2
- Azure SQL Server & Database
- Environment-based Terraform deployments

---

## ⚙️ Prerequisites

Install locally:

- Python **3.11+**
- Terraform
- Azure CLI
- Claude Desktop (MCP enabled)

Verify installation:

```bash
terraform version
az login
python --version

🧩 Setup Instructions

1️⃣ Clone Repository

git clone https://github.com/CloudCraftedRaj/terraform-ai-operations-agent.git
cd terraform-ai-operations-agent

2️⃣ Create Virtual Environment

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

3️⃣ Configure Terraform Variables

Add environment variable file in project(name it as <env>.auto.tfvars)

⚠️ Never commit real credentials or secrets.

🤖 Claude MCP Configuration

Open:

Claude Desktop → Settings → Developer → MCP Servers

Add:

{
  "mcpServers": {
    "terraform": {
      "command": "/Users/<YOUR_USER>/terraform-ai-operations-agent/.venv/bin/python3.11",
      "args": [
        "/Users/<YOUR_USER>/terraform-ai-operations-agent/mcp-server/terraform_mcp.py"
      ],
      "env": {
        "TF_WORKDIR": "/Users/<YOUR_USER>/terraform-ai-operations-agent/examples/azure-terraform-project/terraform",
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}

Replace <YOUR_USER> with your local username.

Restart Claude Desktop after configuration.

ASK Claude to perform any action below:
    Run terraform init
    Run terraform plan with <env>.auto.tfvars
    Run terraform apply with <env>.auto.tfvars


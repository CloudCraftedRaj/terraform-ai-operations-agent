# terraform-ai-operations-agent
Managing Terraform operations manually slows down infrastructure workflows.

This project builds an AI-powered MCP server that allows LLM agents (Claude / GPT) to safely execute Terraform operations locally.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Terraform](https://img.shields.io/badge/Terraform-Automation-purple)
![MCP](https://img.shields.io/badge/MCP-Agent-green)

## Example Infrastructure

This repository includes a real Azure infrastructure example used by the MCP Terraform Agent.

📦 Example Project:
examples/azure-terraform-project

This project provisions:

- Azure Data Factory
- ADLS Gen2
- Azure SQL Database
- Terraform-based environments

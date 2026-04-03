#!/usr/bin/env python3
import sys
import os
import subprocess

PROJECTS_DIR = os.path.expanduser("~/Projects")

GITHUB_WORKFLOW = """name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build
        run: npm run build
      
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
"""

VERCEL_CONFIG = """{
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "framework": "nextjs",
  "outputDirectory": "dist"
}
"""

NETLIFY_CONFIG = """[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""

DOCKERFILE = """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
"""

NGINX_CONFIG = """server {
    listen 80;
    server_name DOMAIN;
    
    root /var/www/html;
    index index.html index.htm;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
}
"""

TERRAFORM_AWS = """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "app" {
  name = "APP_NAME"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecs_cluster" "app" {
  name = "APP_NAME"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "app" {
  family = "APP_NAME"
  network_mode = "awsvpc"
  
  container_definitions = jsonencode([
    {
      name      = "APP_NAME"
      image     = aws_ecr_repository.app.repository_url
      essential = true
      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]
    }
  ])
}

resource "aws_lb" "app" {
  name               = "APP_NAME"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_security_group" "alb" {
  name        = "APP_NAME-alb"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
"""

ANSIBLE_PLAYBOOK = """---
- name: Deploy Application
  hosts: production
  become: yes
  vars:
    app_name: myapp
    app_directory: /var/www/APP_NAME
    node_version: "20"
  
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
      when: ansible_os_family == "Debian"
    
    - name: Install Node.js
      shell: |
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y nodejs
      when: ansible_os_family == "Debian"
    
    - name: Create app directory
      file:
        path: "{{ app_directory }}"
        state: directory
        mode: '0755'
    
    - name: Copy application files
      synchronize:
        src: ./
        dest: "{{ app_directory }}"
        delete: yes
        recursive: yes
    
    - name: Install npm dependencies
      community.general.npm:
        path: "{{ app_directory }}"
        production: yes
    
    - name: Start application with PM2
      community.general.pm2:
        name: "{{ app_name }}"
        script: "npm"
        args: "start"
        state: started
        env:
          NODE_ENV: production
    
    - name: Setup Nginx
      apt:
        name: nginx
        state: present
      when: ansible_os_family == "Debian"
    
    - name: Configure Nginx
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/sites-available/default
      notify: Restart Nginx
  
  handlers:
    - name: Restart Nginx
      service:
        name: nginx
        state: restarted
"""

def init_github_actions(project_name):
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    project_path = os.path.join(PROJECTS_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)
    
    workflow_dir = os.path.join(project_path, ".github", "workflows")
    os.makedirs(workflow_dir, exist_ok=True)
    
    workflow_path = os.path.join(workflow_dir, "ci-cd.yml")
    with open(workflow_path, 'w') as f:
        f.write(GITHUB_WORKFLOW)
    
    return f"GitHub Actions workflow created at: {workflow_path}\n\nTo use:\n  1. Push to GitHub\n  2. Workflow runs on push to main/develop"

def create_dockerfile(project_name, output_path=None):
    if output_path is None:
        output_path = os.path.join(os.getcwd(), "Dockerfile")
    
    with open(output_path, 'w') as f:
        f.write(DOCKERFILE)
    
    return f"Dockerfile created: {output_path}"

def create_nginx_config(domain, output_path=None):
    if output_path is None:
        output_path = "/etc/nginx/sites-available/" + domain
    
    config = NGINX_CONFIG.replace("DOMAIN", domain)
    
    with open(output_path, 'w') as f:
        f.write(config)
    
    return f"Nginx config created: {output_path}\n\nTo enable:\n  sudo ln -s {output_path} /etc/nginx/sites-enabled/\n  sudo systemctl reload nginx"

def init_terraform(project_name):
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    project_path = os.path.join(PROJECTS_DIR, project_name + "-terraform")
    os.makedirs(project_path, exist_ok=True)
    
    config = TERRAFORM_AWS.replace("APP_NAME", project_name)
    
    main_tf = os.path.join(project_path, "main.tf")
    with open(main_tf, 'w') as f:
        f.write(config)
    
    return f"Terraform config created at: {project_path}\n\nTo use:\n  cd {project_path}\n  terraform init\n  terraform plan\n  terraform apply"

def init_ansible(project_name):
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    project_path = os.path.join(PROJECTS_DIR, project_name + "-ansible")
    os.makedirs(project_path, exist_ok=True)
    
    playbook = os.path.join(project_path, "deploy.yml")
    with open(playbook, 'w') as f:
        f.write(ANSIBLE_PLAYBOOK.replace("APP_NAME", project_name))
    
    inventory = os.path.join(project_path, "inventory.ini")
    with open(inventory, 'w') as f:
        f.write("[production]\nYOUR_SERVER_IP ansible_user=root\n")
    
    return f"Ansible playbook created at: {playbook}\n\nTo use:\n  cd {project_path}\n  ansible-playbook -i inventory.ini deploy.yml"

def create_vercel_config(output_path=None):
    if output_path is None:
        output_path = os.path.join(os.getcwd(), "vercel.json")
    
    with open(output_path, 'w') as f:
        f.write(VERCEL_CONFIG)
    
    return f"Vercel config created: {output_path}"

def create_netlify_config(output_path=None):
    if output_path is None:
        output_path = os.path.join(os.getcwd(), "netlify.toml")
    
    with open(output_path, 'w') as f:
        f.write(NETLIFY_CONFIG)
    
    return f"Netlify config created: {output_path}"

def deploy_vercel(project_path):
    try:
        result = subprocess.run(
            ["npx", "vercel", "--prod"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except FileNotFoundError:
        return "Vercel CLI not found. Install: npm i -g vercel"

def main():
    if len(sys.argv) < 2:
        return """Usage: devops-deploy <command> [args]

Commands:
  init-cicd github          - Create GitHub Actions workflow
  init-cicd gitlab          - Create GitLab CI config
  create-dockerfile        - Create Dockerfile
  create-nginx <domain>    - Create Nginx config
  create-vercel            - Create Vercel config
  create-netlify           - Create Netlify config
  init-terraform <name>    - Create Terraform config
  init-ansible <name>      - Create Ansible playbook
  deploy-vercel <path>     - Deploy to Vercel

Examples:
  python handler.py init-cicd github
  python handler.py create-dockerfile
  python handler.py init-terraform myapp"""
    
    command = sys.argv[1]
    
    if command == "init-cicd":
        if len(sys.argv) < 3:
            return "Usage: init-cicd <github|gitlab>"
        platform = sys.argv[2]
        if platform == "github":
            return init_github_actions("myapp")
        elif platform == "gitlab":
            return "GitLab CI coming soon"
        else:
            return f"Unknown platform: {platform}"
    
    elif command == "create-dockerfile":
        return create_dockerfile("myapp")
    
    elif command == "create-nginx":
        if len(sys.argv) < 3:
            return "Usage: create-nginx <domain>"
        return create_nginx_config(sys.argv[2])
    
    elif command == "create-vercel":
        return create_vercel_config()
    
    elif command == "create-netlify":
        return create_netlify_config()
    
    elif command == "init-terraform":
        if len(sys.argv) < 3:
            return "Usage: init-terraform <name>"
        return init_terraform(sys.argv[2])
    
    elif command == "init-ansible":
        if len(sys.argv) < 3:
            return "Usage: init-ansible <name>"
        return init_ansible(sys.argv[2])
    
    elif command == "deploy-vercel":
        if len(sys.argv) < 3:
            return "Usage: deploy-vercel <project-path>"
        return deploy_vercel(sys.argv[2])
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())

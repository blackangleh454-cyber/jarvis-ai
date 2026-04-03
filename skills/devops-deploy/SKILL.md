# DevOps Deploy

**Description:** Deploy applications to cloud platforms, manage CI/CD pipelines, and configure servers.

**Commands:**
- `deploy <platform> <app>` - Deploy to platform
- `init-cicd <platform>` - Initialize CI/CD
- `deploy-nginx <server>` - Deploy Nginx config
- `setup-ssl <domain>` - Setup SSL cert
- `init-ansible` - Generate Ansible playbook
- `deploy-terraform` - Generate Terraform config

**Supported Platforms:**
- Vercel (Next.js)
- Netlify
- Railway
- Render
- DigitalOcean
- AWS
- Custom server

**CI/CD:**
- GitHub Actions
- GitLab CI
- CircleCI

**Usage:**
```bash
python handler.py deploy vercel myapp
python handler.py init-cicd github
python handler.py setup-ssl example.com
python handler.py init-ansible
```

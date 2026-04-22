# Auto-Deployment Setup Guide

This guide sets up automatic deployment from your local machine to your VPS using GitHub Actions.

---

## How It Works

When you push code to GitHub's `main` branch:
1. GitHub Actions triggers automatically
2. SSHs into your VPS
3. Pulls latest code
4. Rebuilds Docker containers
5. Runs migrations
6. Restarts the application

---

## Step 1: Add GitHub Secrets

Go to your GitHub repository: `https://github.com/khdrvss/fikrly/settings/secrets/actions`

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `VPS_HOST` | `38.242.242.133` |
| `VPS_USER` | `maymun` |
| `VPS_SSH_KEY` | Your VPS SSH private key |

---

## Step 2: Generate SSH Key (if you don't have one)

On your local machine:

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -f ~/.ssh/github_deploy -N ""

# Copy public key to VPS
ssh-copy-id -i ~/.ssh/github_deploy.pub maymun@38.242.242.133

# Display private key (copy this to GitHub secret)
cat ~/.ssh/github_deploy
```

Copy the **entire** private key output (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`) to GitHub secret `VPS_SSH_KEY`.

---

## Step 3: Test SSH Connection

From your local machine:

```bash
ssh -i ~/.ssh/github_deploy maymun@38.242.242.133
```

If it logs you in without password, it's working.

---

## Step 4: Push the Deploy Workflow

```bash
git add .github/workflows/deploy.yml
git commit -m "Add auto-deploy workflow"
git push origin main
```

After pushing, check GitHub Actions tab to see the deployment running.

---

## Step 5: Verify Deployment

After the workflow completes, check your site:

```bash
curl https://fikrly.uz/health/
```

Or visit https://fikrly.uz in your browser.

---

## Manual Trigger

You can also trigger deployment manually from GitHub:
1. Go to Actions tab
2. Select "Deploy to VPS"
3. Click "Run workflow"

---

## Troubleshooting

**Workflow fails with "Permission denied"**: Check SSH key is correct in GitHub secrets.

**Docker build fails**: Check logs in GitHub Actions, ensure .env file exists on VPS.

**Migrations fail**: Check database connection in VPS .env file.

**Deployment stuck**: SSH into VPS and check `docker compose ps` and `docker compose logs`.

# CI/CD Setup Plan for Image2Model

**⚠️ DO NOT COMMIT THIS FILE - Contains sensitive information**

## Environment Variable Management Strategy

### My Recommendation for MVP:
**Hybrid Approach** - Keep critical secrets on server, put non-sensitive configs in GitHub

**Why?**
1. **Security**: Database passwords, API keys stay on server only
2. **Flexibility**: Can update configs via GitHub for non-sensitive values
3. **Simplicity**: No complex secret rotation needed for MVP

### Proposed Split:

**Keep on Server Only (.env.production):**
- DATABASE_URL (contains password)
- POSTGRES_PASSWORD
- REDIS_PASSWORD
- SECRET_KEY
- API_KEY / ADMIN_API_KEY
- FAL_API_KEY
- CLOUDFLARE_API_TOKEN
- Any payment/sensitive API keys

**Can go in GitHub Secrets (for CI/CD):**
- DEPLOY_HOST (66.228.60.251)
- DEPLOY_USER (root)
- ENVIRONMENT (production)
- ALLOWED_HOSTS
- BACKEND_CORS_ORIGINS
- Rate limiting values
- Non-sensitive feature flags

**Manual Update Process for Server Secrets:**
1. SSH to server
2. Edit `/opt/image2model/.env.production`
3. Run `./deployment/deploy-mvp.sh` to apply

---

## Phase 1: Information Gathering

### TODO for You:

1. **SSH Private Key**
   ```
   [ ] Copy your SSH private key here:
   -----BEGIN RSA PRIVATE KEY-----
   (paste your key here)
   -----END RSA PRIVATE KEY-----
   ```

2. **Deployment Preferences**
   ```
   [ ] Auto-deploy on push to: main / production / both?
   [ ] Want manual deployment trigger?: yes / no
   [ ] Notification preferences:
       - None
       - Slack (need webhook URL: ____________)
       - Discord (need webhook URL: ____________)
       - Email (to: ____________)
   ```

3. **Environment Variables Decision**
   ```
   [ ] Use hybrid approach (recommended)?: yes / no
   [ ] If no, prefer:
       - All secrets in GitHub
       - All secrets on server only
   ```

---

## Phase 2: GitHub Repository Setup

### TODO for You:

1. **Add GitHub Secrets**
   Go to: Settings → Secrets and variables → Actions
   
   Add these secrets:
   ```
   [ ] SSH_PRIVATE_KEY = (your private key from above)
   [ ] DEPLOY_HOST = 66.228.60.251
   [ ] DEPLOY_USER = root
   ```

2. **Optional Secrets** (if using notifications):
   ```
   [ ] SLACK_WEBHOOK = (if using Slack)
   [ ] DISCORD_WEBHOOK = (if using Discord)
   ```

---

## Phase 3: Implementation Plan

### For Me to Implement:

1. **Clean up old deployment scripts**
   - Delete: deploy.sh, cicd-deploy.sh, fix-dns.sh, configure-access*.py
   - Delete: cloudflare-archive/ directory
   - Keep: deploy-mvp.sh, CLOUDFLARE_MIGRATION_PLAN.md

2. **Create GitHub Actions workflow** (.github/workflows/deploy.yml)
   - Trigger on push to specified branch(es)
   - Optional manual trigger
   - SSH deployment using your key
   - Health checks
   - Notifications (if requested)
   - Rollback on failure

3. **Update deployment README**
   - Document new simplified structure
   - GitHub Actions usage
   - Environment variable management

---

## Phase 4: Testing Plan

### Testing Checklist:

1. **Local Testing**
   ```
   [ ] Test deploy-mvp.sh still works manually
   [ ] Verify health checks pass
   ```

2. **GitHub Actions Testing**
   ```
   [ ] Make small change to trigger workflow
   [ ] Verify deployment succeeds
   [ ] Check logs in Actions tab
   [ ] Verify notifications work (if configured)
   ```

3. **Rollback Testing**
   ```
   [ ] Intentionally break something
   [ ] Verify rollback works
   [ ] Site stays up during failed deployment
   ```

---

## Environment Variable Update Procedures

### Option 1: Manual Update (Recommended for MVP)
```bash
# When you need to update secrets:
ssh root@66.228.60.251
cd /opt/image2model
nano .env.production  # Edit as needed
./deploy-mvp.sh      # Deploy changes
```

### Option 2: Semi-Automated (Future Enhancement)
- Create secure endpoint to update env vars
- Or use configuration management tool
- But this adds complexity for MVP

---

## Questions/Decisions Needed:

1. **Branch Strategy**: 
   - Deploy from `main` only?
   - Or have separate `production` branch?

2. **Deployment Frequency**:
   - Every push to main?
   - Only manual triggers?
   - Scheduled deployments?

3. **Downtime Tolerance**:
   - Current approach has ~60 second downtime
   - OK for MVP?
   - Need zero-downtime deployment?

---

## Next Steps:

1. Fill in the TODOs above
2. I'll implement based on your choices
3. Test deployment pipeline
4. Document for your team

**Please update this file with your information and preferences, then let me know when ready to proceed.**
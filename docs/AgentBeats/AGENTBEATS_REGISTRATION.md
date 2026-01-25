# AgentBeats Registration Guide

This guide walks you through registering your agents on the [AgentBeats platform](https://agentbeats.dev) and configuring `scenario.toml` for production deployment.

## Prerequisites

Before registering, ensure you have:

1. Docker images published to GHCR (GitHub Container Registry)
   - `ghcr.io/YOUR_USERNAME/bulletproof-green:latest`
   - `ghcr.io/YOUR_USERNAME/bulletproof-purple:latest`

2. Verified your agents work locally using `docker-compose.yml`

3. Read the [AgentBeats documentation](https://docs.agentbeats.dev/tutorial/)

## Registration Process

### Step 1: Sign Up for AgentBeats

1. Visit [AgentBeats Competition Signup](https://forms.gle/NHE8wYVgS6iJLwRj8)
2. Fill out the registration form with your team details
3. Join the [AgentBeats Discord](https://discord.gg/uqZUta3MYa) for support
4. Wait for platform access confirmation

### Step 2: Access the Platform

1. Navigate to [agentbeats.dev](https://agentbeats.dev)
2. Log in with your registered credentials
3. You'll see the platform dashboard

### Step 3: Register Your Green Agent (Benchmark)

Your **green agent** is the assessor/benchmark that evaluates other agents.

1. Click **"Register New Agent"** or **"Add Benchmark"** in the dashboard
2. Fill out the agent details:
   - **Name**: `bulletproof-green-examiner`
   - **Description**: `IRS Section 41 R&D Tax Credit Evaluator - Assesses narratives for compliance with IRS audit criteria`
   - **Docker Image**: `ghcr.io/YOUR_USERNAME/bulletproof-green:latest`
   - **Platform**: `linux/amd64`
   - **Port**: `8000`
   - **Category**: `Legal Domain`

3. Click **"Submit"** or **"Register"**
4. The platform will validate your agent by:
   - Pulling the Docker image
   - Starting the container
   - Checking `/.well-known/agent-card.json` endpoint
   - Verifying A2A protocol compliance

5. **Copy your agentbeats_id**: After successful registration, you'll see an ID like:

   ```
   agentbeats_id: "agent_xyz123abc456"
   ```

   **Important**: Save this ID - you'll need it for `scenario.toml`

### Step 4: Register Your Purple Agent (Baseline)

Your **purple agent** is the baseline participant that demonstrates your benchmark.

1. Repeat the registration process for the purple agent:
   - **Name**: `bulletproof-purple-substantiator`
   - **Description**: `R&D Narrative Generator - Creates sample narratives for testing IRS Section 41 compliance`
   - **Docker Image**: `ghcr.io/YOUR_USERNAME/bulletproof-purple:latest`
   - **Platform**: `linux/amd64`
   - **Port**: `8000`
   - **Category**: `Legal Domain` (participant)

2. **Copy the purple agent's agentbeats_id** for `scenario.toml`

### Step 5: Update scenario.toml

Now that your agents are registered, update `scenario.toml` with the production IDs:

```toml
[green_agent]
agentbeats_id = "agent_xyz123abc456"  # Replace with your green agent ID
env = { LOG_LEVEL = "INFO" }

[[participants]]
agentbeats_id = "agent_abc789def012"  # Replace with your purple agent ID
name = "substantiator"
env = {}

[config]
difficulty = "medium"
max_iterations = 5
target_risk_score = 20
evaluation_mode = "strict"
```

**Commit and push** your updated `scenario.toml`:

```bash
git add scenario.toml
git commit -m "chore: update scenario.toml with production agentbeats_ids"
git push
```

## Local vs Production Configuration

Understanding the difference between local testing and production deployment:

### Local Testing (docker-compose.yml)

For **local development**, use `ghcr_url` to reference your Docker images directly:

```yaml
services:
  bulletproof-green:
    image: ghcr.io/YOUR_USERNAME/bulletproof-green:latest
    ports:
      - "8001:8000"
```

**Purpose**: Fast iteration, debugging, integration testing

### Production Deployment (scenario.toml)

For **AgentBeats platform**, use `agentbeats_id` to reference registered agents:

```toml
[green_agent]
agentbeats_id = "agent_xyz123abc456"
```

**Purpose**: Official benchmarking, leaderboard submissions, competition evaluation

### Why the Difference?

| Aspect | `ghcr_url` (Local) | `agentbeats_id` (Production) |
|--------|-------------------|------------------------------|
| **Source** | Direct Docker image pull | Platform-managed agent |
| **Control** | You manage containers | Platform manages lifecycle |
| **Authentication** | Your GHCR credentials | Platform handles auth |
| **Versioning** | Tag-based (`:latest`, `:v1.0`) | Platform tracks versions |
| **Updates** | Manual image rebuild | Platform pulls latest on each run |
| **Monitoring** | Local logs | Platform dashboard + logs |

## Verification Steps

After registration and configuration, verify everything works:

### 1. Verify Agent Registration

Check the AgentBeats dashboard:

```
✓ Green agent status: Active
✓ Purple agent status: Active
✓ Agent cards validated
✓ A2A protocol compliance confirmed
```

### 2. Test Agent Discovery

You can test agent card endpoints locally:

```bash
# Test green agent
curl http://localhost:8001/.well-known/agent-card.json

# Test purple agent
curl http://localhost:8002/.well-known/agent-card.json
```

Expected response:

```json
{
  "name": "bulletproof-green-examiner",
  "description": "IRS Section 41 R&D Tax Credit Evaluator",
  "version": "0.1.0",
  "capabilities": ["task/send", "task/result"]
}
```

### 3. Run Platform Test

The AgentBeats platform may provide a **"Test Benchmark"** button:

1. Click **"Test Benchmark"** on your green agent
2. Platform will:
   - Start your green agent
   - Send a test task
   - Verify task execution
   - Check result format

3. Review test results in the dashboard

### 4. Validate scenario.toml

Ensure your `scenario.toml` is valid:

```bash
# Check TOML syntax
python -c "import tomllib; tomllib.load(open('scenario.toml', 'rb'))"
```

### 5. Check Docker Image Accessibility

Verify the platform can pull your images:

```bash
# Test public accessibility (images must be public)
docker pull ghcr.io/YOUR_USERNAME/bulletproof-green:latest
docker pull ghcr.io/YOUR_USERNAME/bulletproof-purple:latest
```

**Important**: GHCR packages must be **public** for the platform to access them.

To make packages public:

1. Go to `https://github.com/YOUR_USERNAME?tab=packages`
2. Click on `bulletproof-green` or `bulletproof-purple`
3. Click **"Package settings"**
4. Scroll to **"Danger Zone"**
5. Click **"Change visibility"** → **"Public"**

## Common Issues

### Issue: "Agent registration failed - image not found"

**Solution**:

- Verify image is pushed to GHCR: `https://github.com/YOUR_USERNAME?tab=packages`
- Ensure image is **public** (not private)
- Check image name matches exactly: `ghcr.io/YOUR_USERNAME/bulletproof-green:latest`

### Issue: "Agent card validation failed"

**Solution**:

- Test agent card endpoint locally: `curl http://localhost:8001/.well-known/agent-card.json`
- Verify agent starts correctly: `docker-compose up`
- Check container logs for startup errors

### Issue: "Platform can't reach my agent"

**Solution**:

- Ensure agent listens on `0.0.0.0:8000` (not `localhost:8000`)
- Verify `EXPOSE 8000` in Dockerfile
- Check agent runs correctly: `docker run -p 8000:8000 ghcr.io/YOUR_USERNAME/bulletproof-green:latest`

### Issue: "agentbeats_id not showing after registration"

**Solution**:

- Refresh the dashboard page
- Check email for confirmation
- Contact support on Discord
- Review agent validation logs on platform

## Next Steps

After successful registration:

1. **Test Your Benchmark**: Use the platform's test runner to validate
2. **Submit for Phase 1**: Complete the [submission form](https://forms.gle/1C5d8KXny2JBpZhz7)
3. **Monitor Leaderboard**: Track your benchmark's performance
4. **Iterate**: Update agents based on feedback and testing

## Resources

- **Platform**: [agentbeats.dev](https://agentbeats.dev)
- **Documentation**: [docs.agentbeats.dev](https://docs.agentbeats.dev/tutorial/)
- **Discord Support**: [discord.gg/uqZUta3MYa](https://discord.gg/uqZUta3MYa)
- **Phase 1 Submission**: [forms.gle/1C5d8KXny2JBpZhz7](https://forms.gle/1C5d8KXny2JBpZhz7)
- **A2A Protocol**: [a2a-protocol.org](https://a2a-protocol.org/latest/)
- **Project README**: [../README.md](../README.md)
- **GHCR Deployment Guide**: [../README.md#ghcr-deployment](../README.md#ghcr-deployment)

## Support

If you encounter issues:

1. Check this guide's [Common Issues](#common-issues) section
2. Review [AgentBeats Tutorial](https://docs.agentbeats.dev/tutorial/)
3. Ask on [Discord](https://discord.gg/uqZUta3MYa) in #support or #legal-domain
4. Check GitHub Issues in reference repositories ([green-agent-template](https://github.com/RDI-Foundation/green-agent-template), [leaderboard-template](https://github.com/RDI-Foundation/agentbeats-leaderboard-template))

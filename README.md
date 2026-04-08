# AgentCore sample app (Docker / ECR / CodePipeline)

Use this **minimal** project to exercise **`POST /api/deployments/agentcore/deploy`** in the App Management backend. The pipeline zips this folder (or your `module_path`), CodeBuild runs `docker build` and pushes to **ECR**.

## What’s in the box

| File | Purpose |
|------|--------|
| `agentcore.yaml` | Marker file so the backend / path suggestions detect **AgentCore** (see `path_config_service.AGENTCORE_INDICATORS`). |
| `Dockerfile` | Container image; **port 8080** (AgentCore runtime expectation). |
| `main.py` | FastAPI app with **`GET /ping`** and **`POST /invocations`** (minimal contract for custom agents). |
| `requirements.txt` | `fastapi`, `uvicorn`. |

## Architecture note (important)

- **CodeBuild** (standard Linux image) usually builds **`linux/amd64`** images. This Dockerfile uses **`linux/amd64`** for that reason.
- Some AWS docs and samples use **`linux/arm64`**. If your **AgentCore Runtime** only accepts ARM images, change the `FROM --platform=...` line to `linux/arm64` and use a **CodeBuild project** whose environment supports **ARM** (otherwise the build will still produce the wrong architecture).

## Prerequisites in AWS

1. **ECR repository** in the target account/region (URI **without** tag), e.g. `123456789012.dkr.ecr.us-east-1.amazonaws.com/my-agentcore-test`.
2. **CodePipeline** wired to the **S3 source** bucket/key your backend uploads to (same pattern as CDK/Terraform in your setup).
3. **CodeBuild** project used by that pipeline must run **Docker builds** (**privileged** mode) and have IAM to **push to ECR** (and optionally `bedrock-agentcore-control:UpdateAgentRuntime` if you pass runtime update fields).

## Wire this repo in the platform

1. Create a GitHub repo and push this folder (repo root = this sample, or put the sample in a subfolder and set **`module_path`** accordingly).
2. Register the repo on your app and note **`app_id`**, **`environment_id`**, **`repo_id`**.
3. Call **`GET /api/deployments/agentcore/info`** in your API for the full permission list and behavior notes.

## Example deploy request

Adjust IDs and ARNs to your environment.

```http
POST /api/deployments/agentcore/deploy
Content-Type: application/json
Authorization: Bearer <token>
```

```json
{
  "app_id": "<your-app-id>",
  "environment_id": "<your-environment-id>",
  "repo_id": "<your-repo-id>",
  "module_path": "",
  "ecr_repository_uri": "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-agentcore-test",
  "image_tag": "latest",
  "dockerfile_path": "Dockerfile",
  "codepipeline_name": "<your-pipeline-name>",
  "codepipeline_source_bucket": "<your-source-bucket>",
  "codepipeline_source_prefix": "codepipeline-source",
  "codepipeline_source_object_key": "latest.zip"
}
```

Optional: set **`agent_runtime_id`** and **`agent_runtime_execution_role_arn`** together so CodeBuild runs **`aws bedrock-agentcore-control update-agent-runtime`** after the push (requires CLI support on the build image + IAM).

Then poll **`GET /api/deployments/deployment-status/{deployment_id}`** until the pipeline finishes.

## Local smoke test (optional)

```bash
cd samples/agentcore-sample
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

```bash
curl -s http://127.0.0.1:8080/ping
curl -s -X POST http://127.0.0.1:8080/invocations -H "Content-Type: application/json" -d "{\"input\":{\"prompt\":\"hello\"}}"
```

Docker:

```bash
docker build -t agentcore-sample:local .
docker run --rm -p 8080:8080 agentcore-sample:local
```

## Next steps

Replace the stub in **`/invocations`** with your agent (Bedrock, Strands, etc.) and add any env vars your runtime needs in the AgentCore console or runtime configuration.

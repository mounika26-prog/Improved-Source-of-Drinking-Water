"""
ibmcloud_config.py
==================
IBM Cloud watsonx.ai Runtime connection helper.
PS-38: Improved Source of Drinking Water — IBM SkillsBuild Internship

Usage
-----
    from ibmcloud_config import get_watsonx_client, get_credentials, print_plan_info

This module loads credentials from a .env file (or environment variables)
and returns a ready-to-use ibm_watsonx_ai.APIClient.

Requirements
------------
    pip install ibm-watsonx-ai python-dotenv

Free-tier plan limits (Lite plans — no charges):
    watsonx.ai Studio  : 10 CUH/month, 1 user
    watsonx.ai Runtime : 20 CUH/month, 300,000 inference tokens/month
    Cloud Object Storage: 25 GB free for 12 months
"""

from __future__ import annotations

import os
import sys

# ── Load .env if present ────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)          # does not overwrite already-set env vars
except ImportError:
    pass   # python-dotenv is optional; fall back to raw env vars

# ── Required env-var names ──────────────────────────────────────────────────
_REQUIRED = {
    "IBM_CLOUD_API_KEY":   "Your IBM Cloud IAM API key (Manage → Access (IAM) → API keys)",
    "WATSONX_URL":         "watsonx.ai Runtime URL, e.g. https://us-south.ml.cloud.ibm.com",
    "WATSONX_PROJECT_ID":  "Your watsonx.ai Studio Project ID (project → Manage → General)",
}

_OPTIONAL = {
    "WATSONX_INSTANCE_ID": "watsonx.ai Runtime instance GUID (Resource list → instance → Details)",
    "COS_API_KEY":         "Cloud Object Storage API key",
    "COS_INSTANCE_ID":     "Cloud Object Storage resource instance ID",
    "COS_ENDPOINT":        "COS endpoint URL",
    "COS_BUCKET_NAME":     "COS bucket name for this project",
}


def get_credentials() -> dict:
    """
    Read and validate IBM Cloud credentials from environment / .env.

    Returns
    -------
    dict
        Keys: api_key, url, project_id, instance_id (may be None)
    """
    missing = []
    for key, hint in _REQUIRED.items():
        if not os.getenv(key):
            missing.append(f"  {key:30s} → {hint}")

    if missing:
        print("❌  Missing required environment variables:\n")
        print("\n".join(missing))
        print(
            "\n📋  Steps:\n"
            "  1. Copy .env.example → .env\n"
            "  2. Fill in every value (see DEPLOYMENT.md for where to find each)\n"
            "  3. Re-run this script\n"
        )
        sys.exit(1)

    return {
        "api_key":    os.environ["IBM_CLOUD_API_KEY"],
        "url":        os.environ["WATSONX_URL"],
        "project_id": os.environ["WATSONX_PROJECT_ID"],
        "instance_id": os.getenv("WATSONX_INSTANCE_ID"),   # optional
    }


def get_watsonx_client():
    """
    Return an authenticated ibm_watsonx_ai.APIClient.

    Requires
    --------
        pip install ibm-watsonx-ai
    """
    try:
        from ibm_watsonx_ai import APIClient, Credentials
    except ImportError:
        print("❌  ibm-watsonx-ai not installed.\n   Run:  pip install ibm-watsonx-ai")
        sys.exit(1)

    creds_dict = get_credentials()

    credentials = Credentials(
        url=creds_dict["url"],
        api_key=creds_dict["api_key"],
    )

    client = APIClient(credentials)
    client.set.default_project(creds_dict["project_id"])

    print(f"✅  Connected to watsonx.ai Runtime")
    print(f"    URL        : {creds_dict['url']}")
    print(f"    Project ID : {creds_dict['project_id']}")
    return client


def print_plan_info() -> None:
    """Print a reminder of free-tier Lite plan limits."""
    print(
        "\n📊  IBM Cloud Lite Plan Limits (free — no charges):\n"
        "    ┌──────────────────────────────────┬──────────────────────────────┐\n"
        "    │ Service                          │ Free Limit                   │\n"
        "    ├──────────────────────────────────┼──────────────────────────────┤\n"
        "    │ watsonx.ai Studio                │ 10 CUH / month, 1 user       │\n"
        "    │ watsonx.ai Runtime               │ 20 CUH / month               │\n"
        "    │ watsonx.ai Runtime (tokens)      │ 300,000 tokens / month       │\n"
        "    │ Cloud Object Storage             │ 25 GB free (12 months)       │\n"
        "    └──────────────────────────────────┴──────────────────────────────┘\n"
        "    ⚠️  This project runs EDA only — it does NOT use foundation model\n"
        "        inferencing, so token limits are irrelevant here.\n"
        "        The 20 CUH Runtime limit is more than enough to run the notebook.\n"
    )


if __name__ == "__main__":
    print_plan_info()
    client = get_watsonx_client()
    print("\n✅  Connection test passed. You are ready to upload and run the notebook.")

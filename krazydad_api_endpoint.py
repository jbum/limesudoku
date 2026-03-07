"""Shared API endpoint for local uploader/testing scripts."""

import os

KD_API_V3_ENDPOINT = os.environ.get(
    "KD_API_V3_URL",
    "https://5wgjf22qdcsqb2qbssca36j2q40ewfxa.lambda-url.us-west-2.on.aws",
).rstrip("/")

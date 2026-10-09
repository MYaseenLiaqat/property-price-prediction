"""Download and verify the existing model artifact before application startup."""

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen


BASE = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE / "models" / "lahore_house_sale_model.joblib"
MANIFEST_PATH = BASE / "models" / "model_artifact_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    print(f"Model provisioning failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not MANIFEST_PATH.exists():
        fail(f"missing manifest: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected_hash = os.environ.get("MODEL_ARTIFACT_SHA256", manifest.get("sha256"))
    source_url = os.environ.get("MODEL_ARTIFACT_URL")
    if not expected_hash:
        fail("set MODEL_ARTIFACT_SHA256 or provide it in the manifest")

    if MODEL_PATH.exists() and sha256_file(MODEL_PATH) == expected_hash.lower():
        print(f"Verified existing model: {MODEL_PATH}")
        return

    if not source_url:
        fail("model is missing or has the wrong checksum; set MODEL_ARTIFACT_URL")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=MODEL_PATH.parent, prefix=".model-", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        try:
            with urlopen(source_url, timeout=120) as response:
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    temporary.write(chunk)
            actual_hash = sha256_file(temporary_path)
            if actual_hash != expected_hash.lower():
                fail(
                    f"checksum mismatch: expected {expected_hash.lower()}, "
                    f"got {actual_hash}"
                )
            temporary_path.replace(MODEL_PATH)
        finally:
            temporary_path.unlink(missing_ok=True)
    print(f"Downloaded and verified model: {MODEL_PATH}")


if __name__ == "__main__":
    main()

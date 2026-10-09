import json
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
PORT = "8765"
BASE_URL = f"http://127.0.0.1:{PORT}"


class BackendIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        environment = os.environ.copy()
        environment["PORT"] = PORT
        cls.process = subprocess.Popen(
            [PYTHON, "-m", "backend.main"],
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                if cls.get("/health")["status"] == "ok":
                    return
            except (ConnectionError, OSError):
                time.sleep(0.25)
        output = cls.process.stdout.read() if cls.process.stdout else ""
        cls.process.kill()
        raise RuntimeError(f"backend did not start:\n{output}")

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=10)

    @staticmethod
    def get(path):
        with urlopen(BASE_URL + path, timeout=10) as response:
            return json.loads(response.read())

    @staticmethod
    def post(path, payload):
        request = Request(
            BASE_URL + path,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read())

    def test_static_assets(self):
        for path, expected in (
            ("/", b"EstateIQ"),
            ("/app.js", b"API_BASE"),
            ("/styles.css", b"--ivory"),
        ):
            with urlopen(BASE_URL + path, timeout=10) as response:
                self.assertEqual(response.status, 200)
                self.assertIn(expected, response.read())

    def test_health_and_metadata(self):
        self.assertTrue(self.get("/health")["model_loaded"])
        self.assertEqual(self.get("/metadata")["status"], "ok")

    def test_prediction_and_sensitivity_requests(self):
        request = {
            "location": "DHA Defence, DHA Phase 6",
            "area_sqft": 2722,
            "bedrooms": 5,
            "bathrooms": 6,
        }
        prediction = self.post("/predict", request)
        self.assertIsInstance(prediction["estimated_price_pkr"], int)
        values = [
            self.post("/predict", {**request, "area_sqft": area})[
                "estimated_price_pkr"
            ]
            for area in (2042, 2382, 2722, 3062, 3403)
        ]
        self.assertEqual(len(values), 5)
        self.assertGreater(len(set(values)), 1)

    def test_invalid_prediction(self):
        with self.assertRaises(HTTPError) as error:
            self.post(
                "/predict",
                {
                    "location": "",
                    "area_sqft": 50,
                    "bedrooms": 5,
                    "bathrooms": 6,
                },
            )
        self.assertEqual(error.exception.code, 422)


if __name__ == "__main__":
    unittest.main()

from flask import Flask, request, jsonify
import subprocess
import json
import os
import time
import logging
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("gto_service.log"), logging.StreamHandler()],
)

app = Flask(__name__)

# Configuration
GTO_PLUS_API_HOST = "localhost"
GTO_PLUS_API_PORT = 8082
GTO_PLUS_API_URL = f"http://{GTO_PLUS_API_HOST}:{GTO_PLUS_API_PORT}"


@app.route("/health")
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "timestamp": time.time(),
            "server": "Windows VM GTO+ Service",
        }
    )


@app.route("/gto/health")
def gto_health_check():
    """Check if GTO+ API is responding"""
    try:
        response = requests.get(f"{GTO_PLUS_API_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify(
                {
                    "gto_status": "healthy",
                    "gto_response": response.json() if response.content else "OK",
                    "timestamp": time.time(),
                }
            )
        else:
            return (
                jsonify(
                    {
                        "gto_status": "unhealthy",
                        "status_code": response.status_code,
                        "timestamp": time.time(),
                    }
                ),
                503,
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"GTO+ API health check failed: {str(e)}")
        return (
            jsonify(
                {"gto_status": "unreachable", "error": str(e), "timestamp": time.time()}
            ),
            503,
        )


@app.route("/gto/solve", methods=["POST"])
def gto_solve():
    """Forward solve requests to GTO+ API"""
    try:
        # Forward the request to GTO+ API
        response = requests.post(
            f"{GTO_PLUS_API_URL}/solve",
            json=request.json,
            headers={"Content-Type": "application/json"},
            timeout=300,  # 5 minute timeout for solve
        )

        logging.info(f"GTO+ solve request completed with status {response.status_code}")

        # Return the response from GTO+
        return jsonify(response.json()), response.status_code

    except requests.exceptions.Timeout:
        logging.error("GTO+ solve request timed out")
        return (
            jsonify({"error": "GTO+ solve request timed out", "status": "timeout"}),
            504,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"GTO+ solve request failed: {str(e)}")
        return (
            jsonify(
                {"error": f"Failed to connect to GTO+: {str(e)}", "status": "error"}
            ),
            502,
        )
    except Exception as e:
        logging.error(f"Unexpected error in solve request: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/gto/info")
def gto_info():
    """Get GTO+ solver information"""
    try:
        response = requests.get(f"{GTO_PLUS_API_URL}/info", timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"GTO+ info request failed: {str(e)}")
        return (
            jsonify({"error": f"Failed to get GTO+ info: {str(e)}", "status": "error"}),
            502,
        )


@app.route("/api/analyze", methods=["POST"])
def analyze_hand():
    """Legacy mock analysis endpoint"""
    try:
        data = request.json
        hand_id = data.get("hand_id", "unknown")
        hand_history = data.get("hand_history", "")

        logging.info(f"Received legacy analysis request for hand {hand_id}")

        # Save hand to temp file
        temp_dir = "C:\\temp\\gto"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, f"hand_{hand_id}.txt")

        with open(temp_file, "w") as f:
            f.write(hand_history)

        # Mock GTO+ analysis (replace with actual GTO+ command)
        start_time = time.time()

        # Simulate processing time
        time.sleep(2)

        # Mock solver output (replace with actual GTO+ results)
        mock_output = {
            "solver_output": f"Mock GTO+ analysis for hand {hand_id}\\n\\nPreflop Analysis:\\n- Position: Analysis based on hand history\\n- Range recommendations: Dynamically generated\\n- Frequency suggestions: Based on GTO principles",
            "ranges": {
                "CO": "77+, AJs+, AQo+, KQs",
                "BB": "99+, AKo, AQs+, some KQs",
                "BTN": "22+, A2+, K2+, Q2+, J2+",
            },
            "frequencies": {
                "KK_5bet": 1.0,
                "QQ_5bet": 0.52,
                "QQ_call": 0.48,
                "AKs_5bet": 0.41,
                "AKs_call": 0.59,
            },
            "ev_analysis": {
                "KK_flat_loss": -0.18,
                "QQ_fold_loss": -0.22,
                "AKs_5bet_fold_loss": -0.03,
            },
        }

        processing_time = time.time() - start_time

        # Cleanup
        try:
            os.remove(temp_file)
        except:
            pass

        logging.info(f"Completed analysis for hand {hand_id} in {processing_time:.2f}s")

        return jsonify(
            {
                **mock_output,
                "processing_time": processing_time,
                "status": "success",
                "hand_id": hand_id,
            }
        )

    except Exception as e:
        logging.error(f"Error processing hand: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500


if __name__ == "__main__":
    # This will be replaced by Ansible template variables
    service_port = 8080  # Default port, will be templated
    logging.info(f"Starting GTO+ Service on port {service_port}")
    logging.info(f"GTO+ API URL: {GTO_PLUS_API_URL}")
    app.run(host="0.0.0.0", port=service_port, debug=False)

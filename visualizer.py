#!/usr/bin/env python3
"""
GTO Analysis Visualizer

A web-based visualization tool for poker hand analysis results.
Displays analysis in a ChatGPT-like interface with clean formatting.
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from markupsafe import Markup
import markdown

app = Flask(__name__)

# Configuration
OUTPUT_FOLDER = "exports"
STATIC_FOLDER = "static"
TEMPLATES_FOLDER = "templates"

# Create required directories
Path(STATIC_FOLDER).mkdir(exist_ok=True)
Path(TEMPLATES_FOLDER).mkdir(exist_ok=True)


def load_analysis_files():
    """Load all analysis files from exports folder"""
    analysis_files = glob.glob(os.path.join(OUTPUT_FOLDER, "analysis_*.json"))
    analyses = []

    for filepath in sorted(analysis_files, reverse=True):  # Most recent first
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract metadata
            filename = os.path.basename(filepath)
            hand_id = data.get("hand_data", {}).get("hand_id", "unknown")
            stakes = data.get("hand_data", {}).get("stakes", "unknown")
            processed_at = data.get("processed_at", "")

            # Parse timestamp for display
            try:
                dt = datetime.fromisoformat(processed_at.replace("Z", "+00:00"))
                display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                display_time = processed_at

            analyses.append(
                {
                    "filename": filename,
                    "filepath": filepath,
                    "hand_id": hand_id,
                    "stakes": stakes,
                    "processed_at": display_time,
                    "data": data,
                }
            )

        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            continue

    return analyses


def extract_hole_cards(raw_history):
    """Extract hole cards from raw hand history"""
    import re

    # Look for pattern like "Dealt to Roughneck7 [8s 9s]"
    dealt_match = re.search(r"Dealt to \w+ \[([^\]]+)\]", raw_history)
    if dealt_match:
        cards = dealt_match.group(1).strip()
        # Format cards nicely (e.g., "8s 9s" -> "8♠9♠")
        return format_cards(cards)
    return "??"


def extract_position(raw_history):
    """Extract position from raw hand history"""
    import re

    # Extract seat info and button position
    lines = raw_history.split("\n")

    # Find button position
    button_match = re.search(r"Seat #(\d+) is the button", raw_history)
    if not button_match:
        return "??"

    button_seat = int(button_match.group(1))

    # Find hero's seat (player being dealt to)
    hero_match = re.search(r"Dealt to (\w+)", raw_history)
    if not hero_match:
        return "??"

    hero_name = hero_match.group(1)

    # Find hero's seat number
    hero_seat_match = re.search(rf"Seat (\d+): {hero_name}", raw_history)
    if not hero_seat_match:
        return "??"

    hero_seat = int(hero_seat_match.group(1))

    # Count total seats
    seat_matches = re.findall(r"Seat \d+:", raw_history)
    num_seats = len(seat_matches)

    # Calculate position relative to button
    if num_seats == 6:  # 6-max
        positions = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
    elif num_seats == 9:  # Full ring
        positions = ["BTN", "SB", "BB", "UTG", "UTG1", "MP", "MP1", "CO", "HJ"]
    else:
        return "??"

    # Calculate seats from button
    seats_from_button = (hero_seat - button_seat) % num_seats

    if seats_from_button < len(positions):
        return positions[seats_from_button]

    return "??"


def format_cards(cards_str):
    """Format card string with suit symbols"""
    # Replace suit letters with symbols
    cards_str = (
        cards_str.replace("s", "♠")
        .replace("h", "♥")
        .replace("d", "♦")
        .replace("c", "♣")
    )
    # Remove spaces between cards for more compact display
    return cards_str.replace(" ", "")


def load_gto_files():
    """Load all GTO analysis files from exports folder"""
    gto_files = glob.glob(os.path.join(OUTPUT_FOLDER, "gto_analysis_*.json"))
    complete_files = glob.glob(os.path.join(OUTPUT_FOLDER, "analysis_*.json"))

    gto_analyses = []
    complete_hand_ids = set()

    # First, collect hand IDs that have complete analysis
    for filepath in complete_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            hand_id = data.get("hand_data", {}).get("hand_id", "unknown")
            complete_hand_ids.add(hand_id)
        except:
            continue

    # Load GTO files and mark which have complete analysis
    for filepath in sorted(gto_files, reverse=True):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract metadata
            filename = os.path.basename(filepath)
            hand_id = data.get("hand_data", {}).get("hand_id", "unknown")
            stakes = data.get("hand_data", {}).get("stakes", "unknown")
            game_type = data.get("hand_data", {}).get("game_type", "unknown")
            processed_at = data.get("processed_at", "")
            deviation_score = data.get("deviation_score", 0.0)

            # Extract solver metrics
            solver_result = data.get("solver_result", {})
            processing_time = solver_result.get("processing_time", 0.0)
            ev_analysis = solver_result.get("ev_analysis", {})
            frequencies = solver_result.get("frequencies", {})

            # Extract hole cards and position from raw_history
            raw_history = data.get("hand_data", {}).get("raw_history", "")
            hole_cards = extract_hole_cards(raw_history)
            position = extract_position(raw_history)

            # Calculate key metrics
            total_ev = sum(
                v for v in ev_analysis.values() if isinstance(v, (int, float))
            )
            max_freq = max(
                (v for v in frequencies.values() if isinstance(v, (int, float))),
                default=0.0,
            )

            # Parse timestamp for display
            try:
                dt = datetime.fromisoformat(processed_at.replace("Z", "+00:00"))
                display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                display_time = processed_at

            gto_analyses.append(
                {
                    "filename": filename,
                    "filepath": filepath,
                    "hand_id": hand_id,
                    "stakes": stakes,
                    "game_type": game_type,
                    "processed_at": display_time,
                    "deviation_score": deviation_score,
                    "processing_time": processing_time,
                    "total_ev": total_ev,
                    "max_frequency": max_freq,
                    "hole_cards": hole_cards,
                    "position": position,
                    "has_ai_analysis": hand_id in complete_hand_ids,
                    "data": data,
                }
            )

        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            continue

    return gto_analyses


def format_hand_history(raw_history):
    """Format hand history for display"""
    lines = raw_history.strip().split("\n")
    formatted = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Highlight different types of actions
        if line.startswith("Hand #"):
            formatted.append(f'<div class="hand-header">{line}</div>')
        elif "Dealt to" in line:
            formatted.append(f'<div class="dealt-cards">{line}</div>')
        elif any(action in line for action in ["raises", "calls", "folds", "wins"]):
            formatted.append(f'<div class="action-line">{line}</div>')
        else:
            formatted.append(f'<div class="info-line">{line}</div>')

    return Markup("\n".join(formatted))


def format_ranges(ranges):
    """Format range data for display"""
    if not ranges:
        return "No range data available"

    formatted = []
    for position, range_str in ranges.items():
        formatted.append(f'<div class="range-item">')
        formatted.append(f'  <span class="position">{position}:</span>')
        formatted.append(f'  <span class="range">{range_str}</span>')
        formatted.append(f"</div>")

    return Markup("\n".join(formatted))


def format_frequencies(frequencies):
    """Format frequency data for display"""
    if not frequencies:
        return "No frequency data available"

    formatted = []
    for action, freq in frequencies.items():
        percentage = (
            f"{freq * 100:.1f}%" if isinstance(freq, (int, float)) else str(freq)
        )
        formatted.append(f'<div class="freq-item">')
        formatted.append(f'  <span class="action">{action}:</span>')
        formatted.append(f'  <span class="frequency">{percentage}</span>')
        formatted.append(f"</div>")

    return Markup("\n".join(formatted))


def format_ev_analysis(ev_analysis):
    """Format EV analysis for display"""
    if not ev_analysis:
        return "No EV analysis available"

    formatted = []
    for metric, value in ev_analysis.items():
        if isinstance(value, (int, float)):
            display_value = f"{value:+.3f}" if value != 0 else "0.000"
            color_class = (
                "positive" if value > 0 else "negative" if value < 0 else "neutral"
            )
        else:
            display_value = str(value)
            color_class = "neutral"

        formatted.append(f'<div class="ev-item">')
        formatted.append(f'  <span class="metric">{metric}:</span>')
        formatted.append(f'  <span class="value {color_class}">{display_value}</span>')
        formatted.append(f"</div>")

    return Markup("\n".join(formatted))


@app.route("/")
def index():
    """Main page showing table of GTO analyses"""
    gto_analyses = load_gto_files()
    return render_template("index.html", gto_analyses=gto_analyses)


@app.route("/complete")
def complete_analyses():
    """Page showing complete analyses only"""
    analyses = load_analysis_files()
    return render_template("complete.html", analyses=analyses)


@app.route("/analysis/<filename>")
def view_analysis(filename):
    """View specific analysis"""
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.exists(filepath):
        return "Analysis not found", 404

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Format the AI analysis as markdown
        ai_analysis = data.get("ai_analysis", "")
        ai_analysis_html = Markup(markdown.markdown(ai_analysis))

        # Format other data
        hand_data = data.get("hand_data", {})
        solver_result = data.get("solver_result", {})

        formatted_hand = format_hand_history(hand_data.get("raw_history", ""))
        formatted_ranges = format_ranges(solver_result.get("ranges", {}))
        formatted_frequencies = format_frequencies(solver_result.get("frequencies", {}))
        formatted_ev = format_ev_analysis(solver_result.get("ev_analysis", {}))

        return render_template(
            "analysis.html",
            filename=filename,
            hand_data=hand_data,
            solver_result=solver_result,
            ai_analysis=ai_analysis_html,
            formatted_hand=formatted_hand,
            formatted_ranges=formatted_ranges,
            formatted_frequencies=formatted_frequencies,
            formatted_ev=formatted_ev,
            processed_at=data.get("processed_at", ""),
        )

    except Exception as e:
        return f"Error loading analysis: {e}", 500


@app.route("/gto/<filename>")
def view_gto_analysis(filename):
    """View GTO-only analysis"""
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.exists(filepath):
        return "Analysis not found", 404

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Format data
        hand_data = data.get("hand_data", {})
        solver_result = data.get("solver_result", {})

        formatted_hand = format_hand_history(hand_data.get("raw_history", ""))
        formatted_ranges = format_ranges(solver_result.get("ranges", {}))
        formatted_frequencies = format_frequencies(solver_result.get("frequencies", {}))
        formatted_ev = format_ev_analysis(solver_result.get("ev_analysis", {}))

        return render_template(
            "gto_analysis.html",
            filename=filename,
            hand_data=hand_data,
            solver_result=solver_result,
            formatted_hand=formatted_hand,
            formatted_ranges=formatted_ranges,
            formatted_frequencies=formatted_frequencies,
            formatted_ev=formatted_ev,
            processed_at=data.get("processed_at", ""),
            deviation_score=data.get("deviation_score", 0.0),
        )

    except Exception as e:
        return f"Error loading GTO analysis: {e}", 500


@app.route("/api/trigger_ai/<hand_id>", methods=["POST"])
def trigger_ai_analysis(hand_id):
    """Trigger AI analysis for a specific hand"""
    try:
        # Import here to avoid circular imports
        import subprocess
        import sys

        # Find the GTO analysis file for this hand
        gto_files = glob.glob(
            os.path.join(OUTPUT_FOLDER, f"gto_analysis_{hand_id}_*.json")
        )
        if not gto_files:
            return jsonify({"error": f"No GTO analysis found for hand {hand_id}"}), 404

        # Use the CLI to trigger AI analysis
        cmd = [sys.executable, "gto_cli.py", "ai", "--hands", hand_id]

        # Run in background
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Don't wait for completion, return immediately
        return jsonify(
            {
                "status": "started",
                "message": f"AI analysis started for hand {hand_id}",
                "hand_id": hand_id,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/find_analysis/<hand_id>")
def find_analysis_file(hand_id):
    """Find the analysis file for a specific hand ID"""
    try:
        # Look for complete analysis files for this hand
        analysis_files = glob.glob(
            os.path.join(OUTPUT_FOLDER, f"analysis_{hand_id}_*.json")
        )

        if analysis_files:
            # Return the most recent one
            latest_file = max(analysis_files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            return jsonify(
                {"found": True, "filename": filename, "url": f"/analysis/{filename}"}
            )
        else:
            return jsonify({"found": False})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/check_ai_status/<hand_id>")
def check_ai_status(hand_id):
    """Check if AI analysis is complete for a hand"""
    try:
        # Check if complete analysis file exists
        analysis_files = glob.glob(
            os.path.join(OUTPUT_FOLDER, f"analysis_{hand_id}_*.json")
        )

        if analysis_files:
            # Find the most recent one
            latest_file = max(analysis_files, key=os.path.getctime)
            filename = os.path.basename(latest_file)
            return jsonify(
                {
                    "status": "complete",
                    "filename": filename,
                    "url": f"/analysis/{filename}",
                }
            )
        else:
            return jsonify({"status": "pending"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/analyses")
def api_analyses():
    """API endpoint for analysis list"""
    analyses = load_analysis_files()
    return jsonify(
        [
            {
                "filename": a["filename"],
                "hand_id": a["hand_id"],
                "stakes": a["stakes"],
                "processed_at": a["processed_at"],
            }
            for a in analyses
        ]
    )


@app.route("/api/gto_analyses")
def api_gto_analyses():
    """API endpoint for GTO analysis list"""
    gto_analyses = load_gto_files()
    return jsonify(
        [
            {
                "hand_id": a["hand_id"],
                "stakes": a["stakes"],
                "game_type": a["game_type"],
                "hole_cards": a["hole_cards"],
                "position": a["position"],
                "deviation_score": a["deviation_score"],
                "processing_time": a["processing_time"],
                "total_ev": a["total_ev"],
                "max_frequency": a["max_frequency"],
                "has_ai_analysis": a["has_ai_analysis"],
                "processed_at": a["processed_at"],
                "filename": a["filename"],
            }
            for a in gto_analyses
        ]
    )


@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(STATIC_FOLDER, filename)


# Templates are now stored as external files in templates/ folder


# Static files are now stored as external files in static/ folder


def main():
    """Run the visualizer"""
    print("🎨 GTO Analysis Visualizer")
    print("=" * 40)

    # Check for analysis files
    analyses = load_analysis_files()
    print(f"📊 Found {len(analyses)} analysis files")

    if not analyses:
        print("⚠️  No analysis files found in exports/ folder")
        print("   Run the GTO Assistant first to generate some analyses:")
        print("   python gto_assistant_preloaded.py")
        print()

    print("🌐 Starting web server...")
    print("📱 Open your browser to: http://localhost:8081")
    print("🛑 Press Ctrl+C to stop")
    print()

    try:
        app.run(host="0.0.0.0", port=8081, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Visualizer stopped")


if __name__ == "__main__":
    main()

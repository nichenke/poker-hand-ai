"""
GTO Assistant: Automated Poker Hand Analysis

Processes poker hands through remote GTO+ solver and analyzes results using ChatGPT.

Features:
- Load hand histories from files
- Submit to remote GTO+ solver on Windows
- Analyze solver output with AI
- Export results and analysis

Required:
- OPENAI_API_KEY set in environment
- Remote GTO+ solver access
- Input hand files
"""

import os
import json
import glob
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
MODEL = "gpt-4o"
TEMPERATURE = 0.3
GTO_SOLVER_URL = os.getenv("GTO_SOLVER_URL", "http://your-windows-node:8080")
INPUT_FOLDER = "hands"
OUTPUT_FOLDER = "exports"


@dataclass
class HandData:
    """Structure for poker hand data"""

    hand_id: str
    timestamp: str
    stakes: str
    game_type: str
    positions: Dict[str, str]
    actions: List[str]
    raw_history: str


@dataclass
class SolverResult:
    """Structure for GTO solver results"""

    hand_id: str
    solver_output: str
    ranges: Dict[str, str]
    frequencies: Dict[str, float]
    ev_analysis: Dict[str, float]
    processing_time: float


class HandParser:
    """Parse poker hand histories from various formats"""

    @staticmethod
    def parse_hand_file(filepath: str) -> HandData:
        """Parse a single hand file"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract basic info (customize based on your hand format)
        lines = content.strip().split("\n")
        header = lines[0] if lines else ""

        # Basic parsing - adapt to your hand history format
        hand_id = HandParser._extract_hand_id(header)
        timestamp = HandParser._extract_timestamp(header)
        stakes = HandParser._extract_stakes(header)
        game_type = HandParser._extract_game_type(header)

        return HandData(
            hand_id=hand_id,
            timestamp=timestamp,
            stakes=stakes,
            game_type=game_type,
            positions={},  # TODO: Parse positions
            actions=[],  # TODO: Parse actions
            raw_history=content,
        )

    @staticmethod
    def _extract_hand_id(header: str) -> str:
        """Extract hand ID from header"""
        # Example: "Hand #2517850956 - ..."
        try:
            return header.split("#")[1].split(" ")[0]
        except:
            return "unknown"

    @staticmethod
    def _extract_timestamp(header: str) -> str:
        """Extract timestamp from header"""
        # Customize based on your format
        return datetime.now().isoformat()

    @staticmethod
    def _extract_stakes(header: str) -> str:
        """Extract stakes from header"""
        # Example: "$0.05/$0.10"
        try:
            parts = header.split("$")
            if len(parts) >= 3:
                return f"${parts[1]}/{parts[2].split(' ')[0]}"
        except:
            pass
        return "unknown"

    @staticmethod
    def _extract_game_type(header: str) -> str:
        """Extract game type from header"""
        if "Holdem" in header:
            return "Texas Hold'em"
        elif "Omaha" in header:
            return "Omaha"
        return "unknown"


class GTOSolverClient:
    """Client for remote GTO+ solver on Windows"""

    def __init__(self, solver_url: str):
        self.solver_url = solver_url
        self.session = requests.Session()

    def submit_hand(self, hand_data: HandData) -> Optional[SolverResult]:
        """Submit hand to remote GTO+ solver"""
        try:
            payload = {
                "hand_id": hand_data.hand_id,
                "hand_history": hand_data.raw_history,
                "solver_type": "gto_plus",
                "analysis_depth": "full",
            }

            response = self.session.post(
                f"{self.solver_url}/api/analyze",
                json=payload,
                timeout=300,  # 5 minutes timeout
            )

            if response.status_code == 200:
                result = response.json()
                return SolverResult(
                    hand_id=hand_data.hand_id,
                    solver_output=result.get("solver_output", ""),
                    ranges=result.get("ranges", {}),
                    frequencies=result.get("frequencies", {}),
                    ev_analysis=result.get("ev_analysis", {}),
                    processing_time=result.get("processing_time", 0.0),
                )
            else:
                print(f"❌ Solver error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return None

    def health_check(self) -> bool:
        """Check if remote solver is available"""
        try:
            response = self.session.get(f"{self.solver_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False


class AIAnalyzer:
    """AI-powered analysis of solver results"""

    def __init__(self, client: OpenAI):
        self.client = client

    def analyze_hand(self, hand_data: HandData, solver_result: SolverResult) -> str:
        """Analyze hand using AI"""
        prompt = self._build_analysis_prompt(hand_data, solver_result)

        response = self.client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=[
                {
                    "role": "system",
                    "content": "You're a world-class poker GTO expert. Analyze solver output and provide strategic insights in clear, actionable terms.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content

    def _build_analysis_prompt(
        self, hand_data: HandData, solver_result: SolverResult
    ) -> str:
        """Build analysis prompt for AI"""
        return f"""
Analyze this poker hand using GTO solver output:

HAND DETAILS:
- Hand ID: {hand_data.hand_id}
- Stakes: {hand_data.stakes}
- Game: {hand_data.game_type}

HAND HISTORY:
{hand_data.raw_history}

SOLVER ANALYSIS:
{solver_result.solver_output}

RANGES:
{json.dumps(solver_result.ranges, indent=2)}

FREQUENCIES:
{json.dumps(solver_result.frequencies, indent=2)}

EV ANALYSIS:
{json.dumps(solver_result.ev_analysis, indent=2)}

Please provide:
1. Strategic assessment of the played line
2. Key deviations from GTO recommendations
3. EV impact of any mistakes
4. Specific improvement suggestions
5. Learning points for similar spots

Format your response with clear sections and actionable insights.
"""


class GTOAssistant:
    """Main application class"""

    def __init__(self):
        self.parser = HandParser()
        self.solver = GTOSolverClient(GTO_SOLVER_URL)
        self.analyzer = AIAnalyzer(client)

        # Create required directories
        Path(INPUT_FOLDER).mkdir(exist_ok=True)
        Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

    def process_hand_files(self, pattern: str = "*.txt") -> List[Dict]:
        """Process all hand files matching pattern"""
        hand_files = glob.glob(os.path.join(INPUT_FOLDER, pattern))
        results = []

        if not hand_files:
            print(f"❌ No hand files found in {INPUT_FOLDER}/")
            return results

        print(f"🔍 Found {len(hand_files)} hand files to process")

        # Check solver availability
        if not self.solver.health_check():
            print(f"❌ Remote GTO+ solver not available at {GTO_SOLVER_URL}")
            print("   Please check your Windows node connection")
            return results

        for i, filepath in enumerate(hand_files, 1):
            print(
                f"\n📊 Processing hand {i}/{len(hand_files)}: {os.path.basename(filepath)}"
            )

            try:
                # Parse hand
                hand_data = self.parser.parse_hand_file(filepath)
                print(f"   Hand ID: {hand_data.hand_id}")

                # Submit to solver
                print("   🔄 Submitting to GTO+ solver...")
                solver_result = self.solver.submit_hand(hand_data)

                if not solver_result:
                    print("   ❌ Solver analysis failed")
                    continue

                print(f"   ✅ Solver completed in {solver_result.processing_time:.1f}s")

                # AI analysis
                print("   🤖 Running AI analysis...")
                ai_analysis = self.analyzer.analyze_hand(hand_data, solver_result)

                # Save results
                result = self._save_analysis(hand_data, solver_result, ai_analysis)
                results.append(result)

                print(f"   ✅ Analysis saved to {result['output_file']}")

            except Exception as e:
                print(f"   ❌ Error processing {filepath}: {e}")
                continue

        print(f"\n🎉 Completed processing {len(results)} hands")
        return results

    def _save_analysis(
        self, hand_data: HandData, solver_result: SolverResult, ai_analysis: str
    ) -> Dict:
        """Save complete analysis to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{hand_data.hand_id}_{timestamp}.json"
        filepath = os.path.join(OUTPUT_FOLDER, filename)

        analysis_data = {
            "hand_data": {
                "hand_id": hand_data.hand_id,
                "timestamp": hand_data.timestamp,
                "stakes": hand_data.stakes,
                "game_type": hand_data.game_type,
                "raw_history": hand_data.raw_history,
            },
            "solver_result": {
                "solver_output": solver_result.solver_output,
                "ranges": solver_result.ranges,
                "frequencies": solver_result.frequencies,
                "ev_analysis": solver_result.ev_analysis,
                "processing_time": solver_result.processing_time,
            },
            "ai_analysis": ai_analysis,
            "processed_at": datetime.now().isoformat(),
            "solver_url": GTO_SOLVER_URL,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2)

        return {
            "hand_id": hand_data.hand_id,
            "output_file": filepath,
            "status": "success",
        }


def main():
    """Main entry point"""
    print("🚀 GTO Assistant - Automated Hand Analysis")
    print("=" * 50)

    # Initialize assistant
    assistant = GTOAssistant()

    # Process all hand files
    results = assistant.process_hand_files()

    if results:
        print(f"\n📈 Summary:")
        print(f"   Processed: {len(results)} hands")
        print(f"   Output folder: {OUTPUT_FOLDER}/")
        print(f"   Latest results available for review")
    else:
        print(f"\n📋 Next steps:")
        print(f"   1. Add hand history files to {INPUT_FOLDER}/")
        print(f"   2. Ensure remote GTO+ solver is running")
        print(f"   3. Set GTO_SOLVER_URL environment variable")


def export_hand_history():
    """Legacy function - now handled by main processing pipeline"""
    print("⚠️  export_hand_history() is deprecated")
    print("   Use main() for full processing pipeline")


if __name__ == "__main__":
    main()

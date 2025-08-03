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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
MODEL = "gpt-4o"
TEMPERATURE = 0.3
GTO_SOLVER_URL = os.getenv("GTO_SOLVER_URL", "http://your-windows-node:8080")
INPUT_FOLDER = "hands"
OUTPUT_FOLDER = "exports"
DEBUG_FOLDER = "debug"


class DebugLogger:
    """Debug logging utility for GTO+ output and ChatGPT commands"""

    def __init__(self, debug_folder: str = DEBUG_FOLDER):
        self.debug_folder = Path(debug_folder)
        self.debug_folder.mkdir(exist_ok=True)

        # Create subfolders for different types of logs
        self.gto_logs = self.debug_folder / "gto_outputs"
        self.chatgpt_logs = self.debug_folder / "chatgpt_commands"
        self.raw_requests = self.debug_folder / "raw_requests"

        for folder in [self.gto_logs, self.chatgpt_logs, self.raw_requests]:
            folder.mkdir(exist_ok=True)

    def log_gto_output(self, hand_id: str, raw_request: dict, raw_response: dict):
        """Log GTO+ solver request and response"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Log the raw request
        request_file = self.raw_requests / f"gto_request_{hand_id}_{timestamp}.json"
        with open(request_file, "w", encoding="utf-8") as f:
            json.dump(raw_request, f, indent=2)

        # Log the raw response
        response_file = self.gto_logs / f"gto_response_{hand_id}_{timestamp}.json"
        with open(response_file, "w", encoding="utf-8") as f:
            json.dump(raw_response, f, indent=2)

        # Log just the solver output text for easy reading
        solver_output = raw_response.get("solver_output", "")
        if solver_output:
            text_file = self.gto_logs / f"gto_solver_output_{hand_id}_{timestamp}.txt"
            with open(text_file, "w", encoding="utf-8") as f:
                f.write(f"Hand ID: {hand_id}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write("=" * 60 + "\n")
                f.write(solver_output)

        print(f"   📝 GTO+ logs saved to {self.gto_logs}/")

    def log_chatgpt_interaction(self, hand_id: str, messages: list, response: str):
        """Log ChatGPT API request and response"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Log the full interaction
        interaction_data = {
            "hand_id": hand_id,
            "timestamp": timestamp,
            "model": MODEL,
            "temperature": TEMPERATURE,
            "messages": messages,
            "response": response,
            "response_length": len(response),
            "prompt_tokens_estimate": sum(
                len(msg.get("content", "")) for msg in messages
            )
            // 4,
        }

        interaction_file = (
            self.chatgpt_logs / f"chatgpt_interaction_{hand_id}_{timestamp}.json"
        )
        with open(interaction_file, "w", encoding="utf-8") as f:
            json.dump(interaction_data, f, indent=2)

        # Log just the prompt for easy reading
        prompt_file = self.chatgpt_logs / f"chatgpt_prompt_{hand_id}_{timestamp}.txt"
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(f"Hand ID: {hand_id}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Model: {MODEL}\n")
            f.write("=" * 60 + "\n\n")

            for i, message in enumerate(messages):
                role = message.get("role", "unknown")
                content = message.get("content", "")
                f.write(f"MESSAGE {i+1} ({role.upper()}):\n")
                f.write("-" * 40 + "\n")
                f.write(content)
                f.write("\n\n")

        # Log just the response for easy reading
        response_file = (
            self.chatgpt_logs / f"chatgpt_response_{hand_id}_{timestamp}.txt"
        )
        with open(response_file, "w", encoding="utf-8") as f:
            f.write(f"Hand ID: {hand_id}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("=" * 60 + "\n")
            f.write(response)

        print(f"   📝 ChatGPT logs saved to {self.chatgpt_logs}/")

    def log_error(
        self, component: str, hand_id: str, error: Exception, context: dict = None
    ):
        """Log errors with context"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = self.debug_folder / f"error_{component}_{hand_id}_{timestamp}.json"

        error_data = {
            "hand_id": hand_id,
            "timestamp": timestamp,
            "component": component,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        }

        with open(error_file, "w", encoding="utf-8") as f:
            json.dump(error_data, f, indent=2)

        print(f"   📝 Error logged to {error_file}")

    def create_session_summary(self, session_results: list):
        """Create a summary of the entire processing session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.debug_folder / f"session_summary_{timestamp}.json"

        summary_data = {
            "session_timestamp": timestamp,
            "total_hands_processed": len(session_results),
            "successful_hands": len(
                [r for r in session_results if r.get("status") == "success"]
            ),
            "failed_hands": len(
                [r for r in session_results if r.get("status") != "success"]
            ),
            "gto_solver_url": GTO_SOLVER_URL,
            "model_used": MODEL,
            "results": session_results,
        }

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        print(f"📝 Session summary saved to {summary_file}")


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

    def __init__(self, solver_url: str, debug_logger: DebugLogger = None):
        self.solver_url = solver_url
        self.session = requests.Session()
        self.debug_logger = debug_logger

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

                # Log GTO+ output if debug logger is available
                if self.debug_logger:
                    self.debug_logger.log_gto_output(hand_data.hand_id, payload, result)

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
            if self.debug_logger:
                self.debug_logger.log_error(
                    "gto_solver", hand_data.hand_id, e, {"payload": payload}
                )
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

    def __init__(self, client: OpenAI, debug_logger: DebugLogger = None):
        self.client = client
        self.debug_logger = debug_logger

    def analyze_hand(self, hand_data: HandData, solver_result: SolverResult) -> str:
        """Analyze hand using AI"""
        messages = [
            {
                "role": "system",
                "content": "You're a world-class poker GTO expert and coach. Focus exclusively on analyzing the hero's (Roughneck7's) play. Provide strategic insights with visual formatting using suit symbols (♠ ♥ ♦ ♣) and emojis (✅ ⚠️ ❌ 💡 🎯 💰 🔍 ⏰) to make the analysis engaging and easy to scan. Use emojis consistently to indicate move quality, learning opportunities, and key insights. Make every analysis visually appealing and educational.",
            },
            {
                "role": "user",
                "content": self._build_analysis_prompt(hand_data, solver_result),
            },
        ]

        response = self.client.chat.completions.create(
            model=MODEL,
            temperature=TEMPERATURE,
            messages=messages,
        )

        response_text = response.choices[0].message.content

        # Log ChatGPT interaction if debug logger is available
        if self.debug_logger:
            self.debug_logger.log_chatgpt_interaction(
                hand_data.hand_id, messages, response_text
            )

        return response_text

    def _build_analysis_prompt(
        self, hand_data: HandData, solver_result: SolverResult
    ) -> str:
        """Build analysis prompt for AI"""
        return f"""
Analyze this poker hand from Roughneck7's perspective as the hero. Focus exclusively on Roughneck7's decisions and strategy.

HAND DETAILS:
- Hand ID: {hand_data.hand_id}
- Stakes: {hand_data.stakes}
- Game: {hand_data.game_type}
- Hero: Roughneck7

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

Please provide analysis focused ONLY on Roughneck7's play using these formatting guidelines:

**CARD SUITS**: Use ♠ ♥ ♦ ♣ symbols when referencing specific cards or suits
**MOVE INDICATORS**:
- ✅ Excellent/Optimal GTO play
- ⚠️ Suboptimal but acceptable
- ❌ Clear mistake/poor decision
- 💡 Learning opportunity/interesting spot
- 🎯 Key strategic insight
- 💰 EV impact (positive/negative)
- 🔍 Hand reading point
- ⏰ Timing tell or bet sizing note

**ANALYSIS SECTIONS**:

## ♠ Roughneck7's Strategic Assessment
Evaluate each of Roughneck7's decisions with move indicators and suit symbols where applicable.

## ♥ GTO Alignment Analysis
How well did Roughneck7's actions align with GTO recommendations? Use ✅/⚠️/❌ for each decision.

## ♦ EV Impact Breakdown
What was the EV impact of Roughneck7's specific decisions? Use 💰 for each EV calculation.

## ♣ Alternative Lines & Options
What other options did Roughneck7 have at each decision point? Use 💡 for interesting alternatives.

## 🎯 Key Learning Points
Critical takeaways for Roughneck7 to improve in similar spots. Use 💡 for each learning point.

**FORMATTING REQUIREMENTS**:
- Always use suit symbols (♠ ♥ ♦ ♣) when mentioning specific cards
- Mark every decision with ✅/⚠️/❌ based on GTO alignment
- Use 💰 before every EV calculation or monetary impact
- Use 💡 for learning opportunities and insights
- Use 🔍 for hand reading analysis
- Use ⏰ for timing or bet sizing observations
- Use 🎯 for strategic insights

IMPORTANT: 
- Ignore opponent play analysis unless it directly impacts Roughneck7's decisions
- Focus on actionable insights for Roughneck7's improvement
- Provide specific hand reading and range analysis from Roughneck7's perspective
- Include bet sizing analysis and timing tells if relevant to Roughneck7's decisions
- Make the analysis visually engaging with consistent emoji usage

Format your response with clear sections, suit symbols, and emojis for easy scanning and learning.
"""


class GTOAssistant:
    """Main application class"""

    def __init__(self):
        # Initialize OpenAI client with API key validation
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")

        self.openai_client = OpenAI(api_key=api_key)
        self.debug_logger = DebugLogger()
        self.parser = HandParser()
        self.solver = GTOSolverClient(GTO_SOLVER_URL, self.debug_logger)
        self.analyzer = AIAnalyzer(self.openai_client, self.debug_logger)

        # Create required directories
        Path(INPUT_FOLDER).mkdir(exist_ok=True)
        Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

    def process_gto_analysis(self, pattern: str = "*.txt") -> List[Dict]:
        """Step 1: Run GTO+ analysis only, save solver results"""
        hand_files = glob.glob(os.path.join(INPUT_FOLDER, pattern))
        results = []

        if not hand_files:
            print(f"❌ No hand files found in {INPUT_FOLDER}/")
            return results

        print(f"🔍 Found {len(hand_files)} hand files to process with GTO+ solver")

        # Check solver availability
        if not self.solver.health_check():
            print(f"❌ Remote GTO+ solver not available at {GTO_SOLVER_URL}")
            print("   Please check your Windows node connection")
            return results

        for i, filepath in enumerate(hand_files, 1):
            print(
                f"\n📊 Processing GTO analysis {i}/{len(hand_files)}: {os.path.basename(filepath)}"
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
                    results.append(
                        {
                            "hand_id": hand_data.hand_id,
                            "status": "solver_failed",
                            "error": "GTO+ solver returned no result",
                        }
                    )
                    continue

                print(f"   ✅ Solver completed in {solver_result.processing_time:.1f}s")

                # Save GTO-only results
                result = self._save_gto_analysis(hand_data, solver_result)
                results.append(result)

                print(f"   ✅ GTO analysis saved to {result['output_file']}")

                # Calculate deviation score for prioritization
                deviation_score = self._calculate_deviation_score(solver_result)
                result["deviation_score"] = deviation_score
                print(f"   📈 Deviation score: {deviation_score:.2f}")

            except Exception as e:
                print(f"   ❌ Error processing {filepath}: {e}")
                self.debug_logger.log_error(
                    "gto_processing",
                    hand_data.hand_id if "hand_data" in locals() else "unknown",
                    e,
                    {"filepath": filepath},
                )
                results.append(
                    {
                        "hand_id": (
                            hand_data.hand_id if "hand_data" in locals() else "unknown"
                        ),
                        "status": "error",
                        "error": str(e),
                    }
                )
                continue

        # Create session summary
        self.debug_logger.create_session_summary(results)

        print(
            f"\n🎉 Completed GTO analysis for {len([r for r in results if r.get('status') == 'success'])} hands"
        )

        # Sort by deviation score and show recommendations
        successful_results = [r for r in results if r.get("status") == "success"]
        if successful_results:
            successful_results.sort(
                key=lambda x: x.get("deviation_score", 0), reverse=True
            )
            print(
                f"\n🎯 Hands with highest deviations (recommended for ChatGPT analysis):"
            )
            for i, result in enumerate(successful_results[:5]):
                print(
                    f"   {i+1}. Hand #{result['hand_id']} - Deviation: {result['deviation_score']:.2f}"
                )

        return results

    def process_ai_analysis(
        self, hand_ids: List[str] = None, min_deviation: float = 0.0
    ) -> List[Dict]:
        """Step 2: Run AI analysis on selected hands or hands above deviation threshold"""
        if hand_ids:
            print(f"🤖 Running AI analysis on {len(hand_ids)} selected hands...")
        else:
            print(
                f"🤖 Running AI analysis on hands with deviation ≥ {min_deviation}..."
            )

        # Find GTO analysis files
        gto_files = glob.glob(os.path.join(OUTPUT_FOLDER, "gto_analysis_*.json"))
        results = []

        processed_count = 0
        for filepath in gto_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                hand_id = data["hand_data"]["hand_id"]
                deviation_score = data.get("deviation_score", 0.0)

                # Skip if not in selected hands or below threshold
                if hand_ids and hand_id not in hand_ids:
                    continue
                if not hand_ids and deviation_score < min_deviation:
                    continue

                print(
                    f"\n🤖 Processing AI analysis for Hand #{hand_id} (deviation: {deviation_score:.2f})"
                )

                # Reconstruct objects for AI analysis
                hand_data = HandData(
                    hand_id=data["hand_data"]["hand_id"],
                    timestamp=data["hand_data"]["timestamp"],
                    stakes=data["hand_data"]["stakes"],
                    game_type=data["hand_data"]["game_type"],
                    positions={},
                    actions=[],
                    raw_history=data["hand_data"]["raw_history"],
                )

                solver_result = SolverResult(
                    hand_id=data["solver_result"]["hand_id"],
                    solver_output=data["solver_result"]["solver_output"],
                    ranges=data["solver_result"]["ranges"],
                    frequencies=data["solver_result"]["frequencies"],
                    ev_analysis=data["solver_result"]["ev_analysis"],
                    processing_time=data["solver_result"]["processing_time"],
                )

                # Run AI analysis
                print("   🔄 Running ChatGPT analysis...")
                ai_analysis = self.analyzer.analyze_hand(hand_data, solver_result)

                # Save complete analysis
                result = self._save_complete_analysis(
                    hand_data, solver_result, ai_analysis, deviation_score
                )
                results.append(result)

                processed_count += 1
                print(f"   ✅ Complete analysis saved to {result['output_file']}")

            except Exception as e:
                print(f"   ❌ Error processing AI analysis for {filepath}: {e}")
                self.debug_logger.log_error(
                    "ai_processing",
                    hand_id if "hand_id" in locals() else "unknown",
                    e,
                    {"filepath": filepath},
                )
                continue

        print(f"\n🎉 Completed AI analysis for {processed_count} hands")
        return results

    def list_gto_results(self, min_deviation: float = 0.0) -> List[Dict]:
        """List available GTO analysis results with deviation scores"""
        gto_files = glob.glob(os.path.join(OUTPUT_FOLDER, "gto_analysis_*.json"))
        results = []

        for filepath in gto_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                deviation_score = data.get("deviation_score", 0.0)
                if deviation_score >= min_deviation:
                    results.append(
                        {
                            "hand_id": data["hand_data"]["hand_id"],
                            "stakes": data["hand_data"]["stakes"],
                            "deviation_score": deviation_score,
                            "processed_at": data["processed_at"],
                            "filepath": filepath,
                        }
                    )
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
                continue

        # Sort by deviation score
        results.sort(key=lambda x: x["deviation_score"], reverse=True)
        return results

    def _calculate_deviation_score(self, solver_result: SolverResult) -> float:
        """Calculate a deviation score based on EV analysis and frequencies"""
        deviation_score = 0.0

        # Check EV analysis for significant losses
        for metric, value in solver_result.ev_analysis.items():
            if isinstance(value, (int, float)):
                # Negative EV indicates suboptimal play
                if value < 0:
                    deviation_score += abs(value) * 10  # Scale the impact

        # Check frequency deviations (simplified)
        for action, freq in solver_result.frequencies.items():
            if isinstance(freq, (int, float)):
                # Look for extreme frequencies that might indicate interesting spots
                if freq == 1.0 or freq == 0.0:
                    deviation_score += 0.5  # Add points for pure strategies
                elif 0.3 <= freq <= 0.7:
                    deviation_score += 0.2  # Mixed strategies are interesting

        return round(deviation_score, 2)

    def _save_gto_analysis(
        self, hand_data: HandData, solver_result: SolverResult
    ) -> Dict:
        """Save GTO-only analysis to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gto_analysis_{hand_data.hand_id}_{timestamp}.json"
        filepath = os.path.join(OUTPUT_FOLDER, filename)

        # Calculate deviation score before saving
        deviation_score = self._calculate_deviation_score(solver_result)

        analysis_data = {
            "hand_data": {
                "hand_id": hand_data.hand_id,
                "timestamp": hand_data.timestamp,
                "stakes": hand_data.stakes,
                "game_type": hand_data.game_type,
                "raw_history": hand_data.raw_history,
            },
            "solver_result": {
                "hand_id": solver_result.hand_id,
                "solver_output": solver_result.solver_output,
                "ranges": solver_result.ranges,
                "frequencies": solver_result.frequencies,
                "ev_analysis": solver_result.ev_analysis,
                "processing_time": solver_result.processing_time,
            },
            "deviation_score": deviation_score,
            "processed_at": datetime.now().isoformat(),
            "solver_url": GTO_SOLVER_URL,
            "analysis_type": "gto_only",
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2)

        return {
            "hand_id": hand_data.hand_id,
            "output_file": filepath,
            "status": "success",
            "deviation_score": deviation_score,  # Include in return value
        }

    def _save_complete_analysis(
        self,
        hand_data: HandData,
        solver_result: SolverResult,
        ai_analysis: str,
        deviation_score: float,
    ) -> Dict:
        """Save complete analysis with both GTO and AI results"""
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
                "hand_id": solver_result.hand_id,
                "solver_output": solver_result.solver_output,
                "ranges": solver_result.ranges,
                "frequencies": solver_result.frequencies,
                "ev_analysis": solver_result.ev_analysis,
                "processing_time": solver_result.processing_time,
            },
            "ai_analysis": ai_analysis,
            "deviation_score": deviation_score,
            "processed_at": datetime.now().isoformat(),
            "solver_url": GTO_SOLVER_URL,
            "analysis_type": "complete",
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2)

        return {
            "hand_id": hand_data.hand_id,
            "output_file": filepath,
            "status": "success",
        }


def main():
    """Main entry point with support for step-by-step analysis"""
    print("🚀 GTO Assistant - Automated Hand Analysis")
    print("=" * 50)

    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("   Please add your OpenAI API key to the .env file:")
        print("   OPENAI_API_KEY=your-api-key-here")
        return

    gto_url = os.getenv("GTO_SOLVER_URL")
    if not gto_url or gto_url == "http://your-windows-node:8080":
        print("❌ Error: GTO_SOLVER_URL not configured")
        print("   Please add your Windows VM URL to the .env file:")
        print("   GTO_SOLVER_URL=http://192.168.15.234:8080")
        return

    print(f"✅ Environment configured:")
    print(f"   GTO Solver: {gto_url}")
    print(f"   OpenAI API: {'***' + os.getenv('OPENAI_API_KEY', '')[-4:]}")
    print(f"   Debug logging: enabled ({DEBUG_FOLDER}/)")

    # Initialize assistant
    try:
        assistant = GTOAssistant()
    except ValueError as e:
        print(f"❌ Initialization error: {e}")
        return

    # Interactive workflow
    print(f"\n📋 Choose analysis workflow:")
    print(f"   1. Run GTO+ analysis only (Step 1)")
    print(f"   2. Run AI analysis on selected hands (Step 2)")
    print(f"   3. List GTO results and deviation scores")
    print(f"   4. Run full pipeline (legacy mode)")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        # Step 1: GTO analysis only
        results = assistant.process_gto_analysis()
        if results:
            print(f"\n📈 GTO Analysis Complete:")
            print(f"   Output folder: {OUTPUT_FOLDER}/")
            print(f"   Debug logs: {DEBUG_FOLDER}/")
            print(f"   Use option 2 to run AI analysis on selected hands")

    elif choice == "2":
        # Step 2: AI analysis on selected hands
        gto_results = assistant.list_gto_results()
        if not gto_results:
            print("❌ No GTO analysis results found. Run option 1 first.")
            return

        print(f"\n📊 Available hands for AI analysis:")
        for i, result in enumerate(gto_results[:10]):  # Show top 10
            print(
                f"   {i+1}. Hand #{result['hand_id']} - Stakes: {result['stakes']} - Deviation: {result['deviation_score']:.2f}"
            )

        print(f"\n🎯 Analysis options:")
        print(f"   1. Analyze top 3 hands by deviation")
        print(f"   2. Analyze hands with deviation ≥ threshold")
        print(f"   3. Select specific hands")

        ai_choice = input("Enter choice (1-3): ").strip()

        if ai_choice == "1":
            # Top 3 hands
            top_hands = [r["hand_id"] for r in gto_results[:3]]
            assistant.process_ai_analysis(hand_ids=top_hands)

        elif ai_choice == "2":
            # Threshold-based
            threshold = float(input("Enter minimum deviation score (e.g., 1.0): "))
            assistant.process_ai_analysis(min_deviation=threshold)

        elif ai_choice == "3":
            # Manual selection
            hand_input = input("Enter hand IDs separated by commas: ")
            hand_ids = [h.strip() for h in hand_input.split(",")]
            assistant.process_ai_analysis(hand_ids=hand_ids)

    elif choice == "3":
        # List results
        min_dev = input("Enter minimum deviation score to show (default 0.0): ").strip()
        min_deviation = float(min_dev) if min_dev else 0.0

        results = assistant.list_gto_results(min_deviation=min_deviation)
        if results:
            print(f"\n📊 GTO Analysis Results (deviation ≥ {min_deviation}):")
            print(
                f"{'Hand ID':<12} {'Stakes':<10} {'Deviation':<10} {'Processed At':<20}"
            )
            print("-" * 60)
            for result in results:
                processed_time = result["processed_at"][:16].replace("T", " ")
                print(
                    f"{result['hand_id']:<12} {result['stakes']:<10} {result['deviation_score']:<10.2f} {processed_time:<20}"
                )

            print(
                f"\n💡 Hands with higher deviation scores are better candidates for AI analysis"
            )
        else:
            print(f"❌ No GTO results found with deviation ≥ {min_deviation}")

    elif choice == "4":
        # Legacy full pipeline
        print("⚠️  Running legacy full pipeline mode (processes all hands with AI)")
        results = assistant.process_hand_files()
        if results:
            print(f"\n📈 Summary:")
            print(f"   Processed: {len(results)} hands")
            print(f"   Output folder: {OUTPUT_FOLDER}/")
            print(f"   Debug logs: {DEBUG_FOLDER}/")
    else:
        print("❌ Invalid choice")
        return

    print(f"\n🎉 Analysis complete! Check {OUTPUT_FOLDER}/ for results")


def run_gto_only():
    """Helper function to run GTO analysis only"""
    assistant = GTOAssistant()
    return assistant.process_gto_analysis()


def run_ai_analysis(hand_ids: List[str] = None, min_deviation: float = 0.0):
    """Helper function to run AI analysis on selected hands"""
    assistant = GTOAssistant()
    return assistant.process_ai_analysis(hand_ids=hand_ids, min_deviation=min_deviation)


def list_gto_results(min_deviation: float = 0.0):
    """Helper function to list GTO results"""
    assistant = GTOAssistant()
    return assistant.list_gto_results(min_deviation=min_deviation)


def export_hand_history():
    """Legacy function - now handled by main processing pipeline"""
    print("⚠️  export_hand_history() is deprecated")
    print("   Use main() for full processing pipeline")


if __name__ == "__main__":
    main()

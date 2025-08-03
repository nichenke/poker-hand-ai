#!/usr/bin/env python3
"""
GTO Assistant CLI - Cost-optimized poker analysis workflow

Usage:
    python gto_cli.py gto          # Run GTO+ analysis only
    python gto_cli.py list [min]   # List GTO results with deviation scores
    python gto_cli.py ai --top 3   # Run AI on top 3 hands by deviation
    python gto_cli.py ai --min 1.5 # Run AI on hands with deviation ≥ 1.5
    python gto_cli.py ai --hands "123,456" # Run AI on specific hands
"""

import argparse
import sys
from gto_assistant_preloaded import GTOAssistant


def main():
    parser = argparse.ArgumentParser(
        description="GTO Assistant - Cost-optimized poker analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # GTO analysis only
    subparsers.add_parser("gto", help="Run GTO+ analysis only")

    # List GTO results
    list_parser = subparsers.add_parser(
        "list", help="List GTO results with deviation scores"
    )
    list_parser.add_argument(
        "min_deviation",
        nargs="?",
        default=0.0,
        type=float,
        help="Minimum deviation score to show (default: 0.0)",
    )

    # AI analysis
    ai_parser = subparsers.add_parser("ai", help="Run AI analysis on selected hands")
    ai_group = ai_parser.add_mutually_exclusive_group(required=True)
    ai_group.add_argument(
        "--top", type=int, metavar="N", help="Analyze top N hands by deviation score"
    )
    ai_group.add_argument(
        "--min",
        type=float,
        metavar="SCORE",
        help="Analyze hands with deviation ≥ SCORE",
    )
    ai_group.add_argument(
        "--hands", type=str, metavar="IDS", help="Comma-separated hand IDs to analyze"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        assistant = GTOAssistant()

        if args.command == "gto":
            print("🔧 Running GTO+ analysis only...")
            results = assistant.process_gto_analysis()

            if results:
                successful = [r for r in results if r.get("status") == "success"]
                if successful:
                    # Show top deviations
                    successful.sort(
                        key=lambda x: x.get("deviation_score", 0), reverse=True
                    )
                    print("\n🎯 Top hands by deviation (candidates for AI analysis):")
                    for i, result in enumerate(successful[:5]):
                        print(
                            f"   {i+1}. Hand #{result['hand_id']} - Deviation: {result['deviation_score']:.2f}"
                        )

                    print("\n💡 Next steps:")
                    print("   python gto_cli.py ai --top 3")
                    print("   python gto_cli.py ai --min 1.0")
                    print("   python gto_cli.py list")

        elif args.command == "list":
            print(f"📊 Listing GTO results with deviation ≥ {args.min_deviation}...")
            results = assistant.list_gto_results(min_deviation=args.min_deviation)

            if results:
                print(
                    f"\n{'Hand ID':<12} {'Stakes':<10} {'Deviation':<10} {'Processed At':<20}"
                )
                print("-" * 60)
                for result in results:
                    processed_time = result["processed_at"][:16].replace("T", " ")
                    print(
                        f"{result['hand_id']:<12} {result['stakes']:<10} {result['deviation_score']:<10.2f} {processed_time:<20}"
                    )

                print("\n💡 Run AI analysis:")
                print(
                    f"   python gto_cli.py ai --hands \"{','.join([r['hand_id'] for r in results[:3]])}\""
                )
            else:
                print(f"❌ No results found with deviation ≥ {args.min_deviation}")

        elif args.command == "ai":
            if args.top:
                print(f"🤖 Running AI analysis on top {args.top} hands by deviation...")
                gto_results = assistant.list_gto_results()
                if len(gto_results) < args.top:
                    print(f"⚠️  Only {len(gto_results)} hands available")
                top_hands = [r["hand_id"] for r in gto_results[: args.top]]
                if top_hands:
                    assistant.process_ai_analysis(hand_ids=top_hands)
                else:
                    print("❌ No GTO results found. Run 'python gto_cli.py gto' first.")

            elif args.min:
                print(f"🤖 Running AI analysis on hands with deviation ≥ {args.min}...")
                assistant.process_ai_analysis(min_deviation=args.min)

            elif args.hands:
                hand_ids = [h.strip() for h in args.hands.split(",")]
                print(f"🤖 Running AI analysis on hands: {hand_ids}")
                assistant.process_ai_analysis(hand_ids=hand_ids)

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

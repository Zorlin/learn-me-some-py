#!/usr/bin/env python
"""
Demo: Claude Player Integration

Shows how to use ClaudePlayer to have Claude AI play LMSP challenges.

Usage:
    export ANTHROPIC_API_KEY="your-key-here"
    python examples/claude_player_demo.py

This demonstrates self-playtesting capabilities for LMSP development.
"""

import asyncio
import os
from lmsp.multiplayer import ClaudePlayer, TeachingStyle, _multiplayer_available
from lmsp.adaptive.engine import LearnerProfile


async def demo_simple_claude_player():
    """Demo: Simple Claude player."""

    if not _multiplayer_available:
        print("⚠️  Multiplayer not available!")
        print("   Install with: pip install -e '.[multiplayer]'")
        print("   And set: export ANTHROPIC_API_KEY=your-key-here")
        return

    print("🎮 Creating Claude AI Player...")

    # Create a Claude player
    player = ClaudePlayer(
        name="ClaudeBot",
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        teaching_style=TeachingStyle.SOCRATIC,
        skill_level=0.7,  # Intermediate skill
    )

    print(f"✓ Created player: {player.name}")
    print(f"  Teaching Style: {player.teaching_style.value}")
    print(f"  Model: {player.model}")
    print(f"  Skill Level: {player.skill_level}")

    # Example: Set up a challenge
    player.current_challenge = "hello_world"
    player.code_buffer = "# Write hello world\n"

    # Build context
    context = player.build_context()
    print("\n📝 Context built:")
    print(context[:200] + "..." if len(context) > 200 else context)

    # Query Claude (this makes an API call)
    print("\n🤖 Querying Claude API...")
    try:
        response = await player.query_claude(context)
        print(f"✓ Response received: {len(response)} chars")
        print(f"\nResponse preview:\n{response[:300]}...")

        # Parse response to events
        events = player.parse_response_to_events(response)
        print(f"\n📡 Parsed {len(events)} events:")
        for event in events[:3]:  # Show first 3
            print(f"  - {event.get('type')}: {event.get('content', event.get('char', ''))[:50]}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure ANTHROPIC_API_KEY is set correctly")


async def demo_teaching_styles():
    """Demo: Different teaching styles."""

    if not _multiplayer_available:
        print("Multiplayer not available")
        return

    print("\n🎯 Teaching Style Comparison")
    print("=" * 50)

    styles = [
        TeachingStyle.SOCRATIC,
        TeachingStyle.DEMONSTRATIVE,
        TeachingStyle.ENCOURAGING,
    ]

    for style in styles:
        player = ClaudePlayer(
            name=f"Claude_{style.value}",
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            teaching_style=style,
        )

        system_prompt = player.get_teaching_style_instructions()
        print(f"\n{style.value.upper()}:")
        print(system_prompt[:150] + "...")


def main():
    """Run the demo."""
    print("=" * 50)
    print("LMSP Claude Player Demo")
    print("=" * 50)
    print()

    # Check if API key is set
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set!")
        print("   Set it with: export ANTHROPIC_API_KEY=your-key-here")
        print()
        print("   Or create a .env file:")
        print("   echo 'ANTHROPIC_API_KEY=your-key-here' > .env")
        return

    # Run async demos
    asyncio.run(demo_simple_claude_player())
    asyncio.run(demo_teaching_styles())

    print("\n" + "=" * 50)
    print("Demo complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()


# Self-teaching note:
#
# This file demonstrates:
# - Async/await for API calls (Level 6: async programming)
# - Environment variables for API keys (Level 4: os module)
# - Error handling and user feedback (Level 3: exceptions)
# - CLI scripts with __name__ == "__main__" (Level 2: modules)
# - Type hints and documentation (Level 5+)
#
# Prerequisites:
# - Level 2: Modules and imports
# - Level 3: Error handling
# - Level 4: Environment and OS interaction
# - Level 5: Async programming basics
# - Level 6: External API integration
#
# This demonstrates how professional Python projects:
# 1. Handle optional dependencies gracefully
# 2. Provide example/demo scripts
# 3. Use async for I/O operations
# 4. Document API usage clearly

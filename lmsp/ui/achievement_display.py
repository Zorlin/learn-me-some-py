"""
Rich visualization for achievements with animated celebrations and progress.

Makes unlocking achievements FEEL rewarding through visual polish,
sparkles, color gradients, and celebration moments.
"""

from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, ProgressColumn, Text
from rich.align import Align
from rich.text import Text as RichText
from rich import box
import time

from .achievements import Achievement, AchievementProgress, AchievementTier


class AchievementDisplayRenderer:
    """Renders achievements with gorgeous Rich visualizations."""

    # Sparkle characters for celebration
    SPARKLES = ["✨", "⭐", "🌟", "💫", "✨"]
    CONFETTI = ["🎉", "🎊", "🎈", "🎁", "🏆"]

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def _get_tier_color(self, tier: AchievementTier) -> str:
        """Get hex color for achievement tier."""
        return tier.color

    def _get_tier_emoji(self, tier: AchievementTier) -> str:
        """Get emoji for achievement tier."""
        tier_emojis = {
            AchievementTier.BRONZE: "🥉",
            AchievementTier.SILVER: "🥈",
            AchievementTier.GOLD: "🥇",
            AchievementTier.PLATINUM: "💎",
            AchievementTier.DIAMOND: "💠",
        }
        return tier_emojis.get(tier, "🏆")

    def render_progress_bar(
        self,
        progress: AchievementProgress,
        achievement: Achievement,
        width: int = 40,
    ) -> str:
        """
        Render a gorgeous progress bar for an achievement.

        Uses color gradients and smooth animation.
        """
        percent = progress.progress_percent(achievement.required_value)
        color = self._get_tier_color(achievement.tier)

        # Build the bar
        filled = int((percent / 100) * width)
        empty = width - filled

        # Create gradient effect by varying brightness
        if percent >= 100:
            bar_text = f"[{color}]{'█' * width}[/]"
            label = f"{achievement.icon} Complete!"
        else:
            bar_text = f"[{color}]{'█' * filled}[/][dim]{'░' * empty}[/]"
            label = f"{percent:.0f}%"

        return f"{bar_text} {label}"

    def render_achievement_card(
        self,
        achievement: Achievement,
        progress: AchievementProgress,
        show_progress: bool = True,
    ) -> Panel:
        """
        Render a complete achievement card with all details.

        Includes icon, name, description, progress, and tier badge.
        """
        content_lines = []

        # Header with icon and tier
        tier_emoji = self._get_tier_emoji(achievement.tier)
        header = f"{achievement.icon} {achievement.name} {tier_emoji}"
        content_lines.append(Align.center(RichText(header, style="bold")))
        content_lines.append("")

        # Description
        content_lines.append(achievement.description)

        # Progress bar if requested
        if show_progress:
            content_lines.append("")
            progress_bar = self.render_progress_bar(progress, achievement)
            content_lines.append(progress_bar)

            # Progress text
            content_lines.append("")
            progress_text = f"Progress: {progress.current_value}/{achievement.required_value}"
            content_lines.append(Align.center(progress_text))

        # Rewards
        if achievement.xp_reward > 0 or achievement.unlocks_concept or achievement.unlocks_theme:
            content_lines.append("")
            content_lines.append("[dim]═══════════════════════════[/]")
            content_lines.append("[bold yellow]Rewards:[/]")

            if achievement.xp_reward > 0:
                content_lines.append(f"  ⭐ {achievement.xp_reward} XP")

            if achievement.unlocks_concept:
                content_lines.append(f"  🔓 Unlocks: {achievement.unlocks_concept}")

            if achievement.unlocks_theme:
                content_lines.append(f"  🎨 Theme: {achievement.unlocks_theme}")

        # Status
        if progress.unlocked:
            content_lines.append("")
            unlock_date_str = progress.unlock_date.strftime("%Y-%m-%d %H:%M") if progress.unlock_date else "Unknown"
            content_lines.append(f"[green]✓ Unlocked on {unlock_date_str}[/]")

        content = "\n".join(str(line) for line in content_lines)

        # Create panel with tier-colored border
        tier_color = self._get_tier_color(achievement.tier)
        return Panel(
            content,
            title=f"[{tier_color}]Achievement[/]",
            border_style=tier_color,
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def render_celebration(
        self,
        achievement: Achievement,
        progress: AchievementProgress,
        duration: float = 2.0,
    ) -> None:
        """
        Render a celebration animation when achievement is unlocked.

        Creates a gorgeous visual celebration with sparkles and confetti.
        """
        console = self.console
        tier_emoji = self._get_tier_emoji(achievement.tier)
        tier_color = self._get_tier_color(achievement.tier)

        # Clear screen for celebration
        console.clear()

        # Animated sparkle frame
        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < duration:
            frame_count += 1

            # Calculate pulse animation
            pulse = (frame_count % 20) / 20.0
            sparkle_count = int(pulse * 6)

            # Build celebration text with varying sparkles
            sparkles = " ".join(self.SPARKLES[i % len(self.SPARKLES)] for i in range(sparkle_count))
            confetti = " ".join(self.CONFETTI[i % len(self.CONFETTI)] for i in range(sparkle_count // 2))

            # Celebration message
            title = RichText(f"\n{tier_emoji} ACHIEVEMENT UNLOCKED! {tier_emoji}\n", style=f"bold {tier_color}")
            name_text = RichText(f"\n{achievement.icon} {achievement.name}\n", style="bold white on blue")
            desc_text = RichText(f"\n{achievement.description}\n", style="white")

            # XP reward
            if achievement.xp_reward > 0:
                xp_text = RichText(f"\n+{achievement.xp_reward} XP\n", style="bold yellow")
            else:
                xp_text = RichText("")

            # Build the celebration display
            lines = [
                "",
                sparkles,
                str(title),
                str(name_text),
                str(desc_text),
                str(xp_text),
                confetti,
                "",
            ]

            # Display in a glowing panel
            content = "\n".join(lines)
            panel = Panel(
                content,
                border_style=tier_color,
                box=box.DOUBLE,
                padding=(2, 4),
            )

            # Render with clear
            console.clear()
            console.print(Align.center(panel))

            # Frame delay for animation
            time.sleep(0.1)

        # Final celebration view (no animation)
        console.clear()
        final_panel = self.render_achievement_card(achievement, progress, show_progress=False)
        console.print(Align.center(final_panel))
        console.print()

    def render_achievement_list(
        self,
        achievements: list[tuple[Achievement, AchievementProgress]],
        title: str = "Achievements",
        max_items: Optional[int] = None,
    ) -> None:
        """
        Render a list of achievements in a table-like format.

        Useful for showing progress toward multiple achievements.
        """
        if max_items:
            achievements = achievements[:max_items]

        console = self.console
        console.print(f"\n[bold cyan]{title}[/]\n")

        for achievement, progress in achievements:
            tier_emoji = self._get_tier_emoji(achievement.tier)
            status = "✓" if progress.unlocked else "○"

            # Progress percentage
            percent = progress.progress_percent(achievement.required_value)

            # Build line
            line = f"{status} {achievement.icon} {achievement.name:25} {tier_emoji} {percent:3.0f}%"
            console.print(line)

            # Progress bar
            progress_bar = self.render_progress_bar(progress, achievement, width=30)
            console.print(f"  {progress_bar}")
            console.print()

    def render_tier_stats(
        self,
        stats: dict,
    ) -> Panel:
        """
        Render tier-by-tier achievement statistics.

        Shows progress across bronze, silver, gold, etc.
        """
        content_lines = []

        content_lines.append("[bold]Achievement Progress by Tier[/]\n")

        for tier_name, tier_stats in stats.get("by_tier", {}).items():
            total = tier_stats["total"]
            unlocked = tier_stats["unlocked"]
            percent = tier_stats["percent"]

            # Color based on tier
            tier_colors = {
                "bronze": "#CD7F32",
                "silver": "#C0C0C0",
                "gold": "#FFD700",
                "platinum": "#E5E4E2",
                "diamond": "#B9F2FF",
            }
            color = tier_colors.get(tier_name, "white")

            # Tier line
            tier_text = f"[{color}]{tier_name.capitalize():12}[/]"
            progress_text = f"{unlocked:2}/{total:2}"
            percent_text = f"{percent:5.1f}%"

            # Progress bar
            bar_width = 20
            filled = int((percent / 100) * bar_width)
            bar = f"[{color}]{'█' * filled}[/][dim]{'░' * (bar_width - filled)}[/]"

            line = f"{tier_text} {progress_text} {bar} {percent_text}"
            content_lines.append(line)

        # Total stats
        total = stats.get("total", 0)
        unlocked = stats.get("unlocked", 0)
        percent = stats.get("percent", 0)
        xp = stats.get("total_xp", 0)

        content_lines.append("")
        content_lines.append("[bold cyan]Total[/]")
        content_lines.append(f"  Unlocked: {unlocked}/{total} ({percent:.1f}%)")
        content_lines.append(f"  Total XP: {xp}")

        content = "\n".join(content_lines)
        return Panel(
            content,
            title="[bold]Statistics[/]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )

    def render_next_milestone(
        self,
        achievements_in_progress: list[tuple[Achievement, AchievementProgress]],
    ) -> Optional[Panel]:
        """
        Render the next achievement milestone (closest to completion).

        Great for motivational display showing what's coming next.
        """
        if not achievements_in_progress:
            return None

        # Get closest to completion
        achievement, progress = achievements_in_progress[0]
        percent = progress.progress_percent(achievement.required_value)

        content_lines = []
        content_lines.append("[bold cyan]Next Milestone[/]\n")
        content_lines.append(f"{achievement.icon} {achievement.name}")
        content_lines.append(achievement.description)
        content_lines.append("")

        # Progress bar
        progress_bar = self.render_progress_bar(progress, achievement, width=35)
        content_lines.append(progress_bar)

        # How many more needed
        remaining = achievement.required_value - progress.current_value
        if remaining > 0:
            content_lines.append("")
            content_lines.append(f"[dim]{remaining} more to unlock[/]")

        content = "\n".join(content_lines)
        return Panel(
            content,
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2),
        )


# Self-teaching note:
#
# This file demonstrates:
# - Rich library integration for beautiful terminal UI (Level 5+)
# - Time-based animation loops (Level 4: loops and timing)
# - Type hints with Optional and Tuple (Level 5: type hints)
# - String formatting and color codes (Level 3+)
# - Methods that return Rich objects for composable UI (Level 6: design patterns)
#
# Prerequisites:
# - Level 2: Collections and strings
# - Level 3: Functions and classes
# - Level 4: Loops and time module
# - Level 5: Type hints and dataclasses
# - Level 6: Design patterns and UI frameworks
#
# The Rich library is used by professional tools:
# - Apache Airflow
# - Poetry
# - Typer
# - Many CLI tools and TUIs
#
# This demonstrates professional Python for terminal-based applications.

"""The Life Vision workbook: evidence-based exercises that turn a written vision into energy and action.

A picture of the future is not enough on its own. Research by Kappes and Oettingen found that only
daydreaming about an ideal future lowers the energy people bring to it, so every vision in this workbook is
paired with an obstacle, an if-then plan, a visible record of progress and a regular review.

All wording here is original. Each method carries the study it rests on and an honest note on its limits,
so the app, the PDF workbook, the MCP server and the coach agent can all show the same sources.
"""
from __future__ import annotations

METHODS = [
    {
        "key": "best_self",
        "title": "Write your best possible future",
        "do": "For about ten minutes, describe your life a few years from now after you have worked hard and things have gone as well as they realistically could. Write in the present tense and include how it feels.",
        "why": "Across 29 studies, this short writing exercise raised positive feelings, optimism and wellbeing compared with control groups.",
        "limit": "The lift is small to moderate and fades, which is why this workbook asks you to revisit it rather than write it once.",
        "source": "Carrillo et al. (2019), PLOS ONE 14(9): e0222386",
        "url": "https://doi.org/10.1371/journal.pone.0222386",
    },
    {
        "key": "contrast",
        "title": "Name what stands in the way",
        "do": "For each vision, write the best result you hope for, then the main obstacle inside you that could stop it (a habit, a feeling, an excuse).",
        "why": "In four experiments, people who only pictured an ideal future had less energy for it than people who also questioned it. Putting the obstacle next to the dream is what turns a wish into commitment.",
        "limit": "This works for goals you believe you can reach. If a goal feels out of reach, shrink it first.",
        "source": "Kappes & Oettingen (2011), Journal of Experimental Social Psychology 47(4), 719-729",
        "url": "https://doi.org/10.1016/j.jesp.2011.02.003",
    },
    {
        "key": "if_then",
        "title": "Make an if-then plan",
        "do": "Finish this sentence for your obstacle: If (the obstacle or the moment) happens, then I will (one specific action).",
        "why": "A review of 94 tests found that people who made if-then plans reached their goals more often than people who only set the goal. Combined with naming the obstacle, a review of 21 studies found a small to medium gain.",
        "limit": "Later, larger reviews suggest the true benefit is smaller than first reported, and plans help most when you already care about the goal.",
        "source": "Gollwitzer & Sheeran (2006), Advances in Experimental Social Psychology 38, 69-119; Wang, Wang & Gai (2021), Frontiers in Psychology 12:565202",
        "url": "https://doi.org/10.3389/fpsyg.2021.565202",
    },
    {
        "key": "track",
        "title": "Record your progress where you can see it",
        "do": "Tick the tracker on each area page every week you act on it, and share your progress with one person.",
        "why": "A review of 138 studies with about 20,000 people found that checking progress more often helps people reach goals, and it helps more when progress is written down or shared.",
        "limit": "Most of those studies were about health goals, so treat it as a strong hint for other areas rather than proof.",
        "source": "Harkin et al. (2016), Psychological Bulletin 142(2), 198-229",
        "url": "https://doi.org/10.1037/bul0000025",
    },
    {
        "key": "patience",
        "title": "Give habits time, and forgive a missed day",
        "do": "Tie each new action to a daily cue and expect it to take a couple of months to feel automatic. If you miss a day, carry on the next day.",
        "why": "In a 12-week study of new daily habits, the typical time to feel automatic was about 66 days, ranging from 18 to 254, and missing one day made no lasting difference.",
        "limit": "That figure comes from the people whose habits did form in a small study, so it is a guide and not a deadline.",
        "source": "Lally et al. (2010), European Journal of Social Psychology 40(6), 998-1009",
        "url": "https://doi.org/10.1002/ejsp.674",
    },
]

ENERGIZE = [
    {"key": "en_out", "label": "Best result", "hint": "If this vision comes true, what is the best thing about it?"},
    {"key": "en_obs", "label": "My obstacle", "hint": "What inside me is most likely to get in the way?"},
    {"key": "en_plan", "label": "If-then plan", "hint": "If (obstacle or moment), then I will (one specific action)."},
]

BEST_SELF_PROMPT = METHODS[0]["do"]


def export_for_web() -> dict:
    return {"methods": METHODS, "energize": ENERGIZE, "best_self": BEST_SELF_PROMPT}

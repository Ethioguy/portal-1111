"""Step-by-step life coaching for the 11 life areas.

One source of truth, in Python: the web app's guided coach (built by tools/build_life_coach.py),
the MCP server and the coach agent all read this module.

Each area is coached in the same six steps:
  0 Learn     why the area matters, and one idea to hold onto
  1 Premise   the beliefs you hold about it
  2 Vision    the ideal you want
  3 Purpose   why you want it
  4 Strategy  how you will get there
  5 Commit    one small action in the next 7 days

All guidance is original to this project and is general, not professional advice.
"""
from __future__ import annotations

STEPS = [
    ("learn", "Learn"),
    ("premise", "Premise"),
    ("vision", "Vision"),
    ("purpose", "Purpose"),
    ("strategy", "Strategy"),
    ("commit", "Commit"),
]

SECTION_HELP = {
    "premise": "Premise is what you believe about this area. Beliefs steer choices before you notice them, so write the ones you want to keep, and rewrite any that hold you back.",
    "vision": "Vision is the ideal picture. Write it in the present tense, as if it is already true, with enough detail that you could recognise it on an ordinary Tuesday.",
    "purpose": "Purpose is your reasons. Strong reasons are personal and specific: who benefits, what it makes possible, what it would cost you to ignore it.",
    "strategy": "Strategy is the plan: habits, routines and next steps. Good strategies are small, scheduled and easy to start, not heroic.",
    "commit": "Pick one action you will take in the next 7 days. Make it small enough that you could do it on a busy day, and decide when.",
}

GUIDE: dict[str, dict] = {
    "health": {
        "name": "Health & Fitness",
        "lesson": "Your body is the vehicle for everything else on this list. Energy, sleep, movement and food compound quietly: small daily choices beat occasional big efforts.",
        "idea": "Aim for consistency over intensity. A short session you actually do beats a perfect plan you skip.",
        "prompts": {
            "premise": ["What do you believe about your body and what it is capable of?", "Which belief about food, exercise or age might be holding you back?", "What would you like to believe instead?"],
            "vision": ["How do you feel when you wake up on a great day?", "What can your body do that you are proud of?", "What do you eat, and how do you move, most days?"],
            "purpose": ["Who benefits when you have more energy?", "What would better health let you do in five years?", "What is the cost of not changing anything?"],
            "strategy": ["What is your weekly training rhythm?", "What one food or drink habit will you change first?", "What time will you go to bed on weeknights?"],
        },
        "first_step": "Put three training sessions for next week into your calendar now.",
        "watch_out": "All-or-nothing thinking. A missed day is data, not failure; just make the next one.",
    },
    "intel": {
        "name": "Intellectual Life",
        "lesson": "Your mind grows the way muscles do: through regular, slightly uncomfortable challenge. What you read, watch and practise becomes how you think.",
        "idea": "Choose depth over volume. One book you apply beats ten you skim.",
        "prompts": {
            "premise": ["Do you see yourself as someone who keeps learning?", "What do you believe about your ability to master hard things?", "Where did that belief come from?"],
            "vision": ["What subjects or skills are you known for?", "What does your learning week look like?", "What would you love to be able to explain or teach?"],
            "purpose": ["How would growing your mind improve your work or family life?", "What problem would you love to be able to solve?", "What curiosity have you put off for years?"],
            "strategy": ["What will you read, listen to or study this month?", "When is your protected learning time each week?", "How will you practise or share what you learn?"],
        },
        "first_step": "Pick one book or course and schedule 20 minutes for it three times this week.",
        "watch_out": "Consuming without applying. After each session, write one sentence on how you will use it.",
    },
    "emo": {
        "name": "Emotional Life",
        "lesson": "Emotions are signals, not instructions. The aim is not to feel good all the time, but to notice what you feel, name it, and choose your response.",
        "idea": "Name it to tame it. Putting a feeling into words often lowers its intensity.",
        "prompts": {
            "premise": ["What do you believe about expressing emotions?", "Which feelings do you find hardest to sit with?", "What would a healthier belief about emotions be?"],
            "vision": ["How do you want to feel most days?", "How do you respond when something goes wrong?", "What does calm look like in your life?"],
            "purpose": ["How do your moods affect the people around you?", "What would more emotional steadiness make possible?", "Who do you want to be in hard moments?"],
            "strategy": ["What daily practice helps you reset (walk, journal, prayer, breathing)?", "Who can you talk to when things are heavy?", "What early warning signs tell you to slow down?"],
        },
        "first_step": "Each evening this week, write one line: what I felt today and what it was telling me.",
        "watch_out": "Bottling things up until they spill over. If low mood or anxiety lasts, talk to a professional; that is a strength, not a weakness.",
    },
    "char": {
        "name": "Character",
        "lesson": "Character is who you are when it is inconvenient. It shows in small promises kept, in honesty when no one is checking, and in how you treat people who can do nothing for you.",
        "idea": "Values only become real when they are visible in your calendar and your choices.",
        "prompts": {
            "premise": ["Which values matter most to you?", "Where do your actions and your values not match yet?", "What do you believe makes a person trustworthy?"],
            "vision": ["How would the people closest to you describe you?", "What do you stand for, even when it costs you?", "What habits show your character every day?"],
            "purpose": ["What example do you want to set, and for whom?", "What would living your values give you?", "What do you want to be remembered for?"],
            "strategy": ["Which three values will you live by deliberately this year?", "What promise to yourself will you keep every day?", "How will you check in on your integrity each week?"],
        },
        "first_step": "Write your top three values and one action for each that you will do this week.",
        "watch_out": "Perfectionism. Character grows by repairing mistakes quickly, not by never making them.",
    },
    "spirit": {
        "name": "Spiritual Life",
        "lesson": "Spiritual life is your connection to something larger than yourself: faith, nature, meaning, gratitude or service. It is personal; there is no single right path.",
        "idea": "Make room for stillness. Meaning is hard to hear in constant noise.",
        "prompts": {
            "premise": ["What do you believe gives life meaning?", "What role does faith, practice or reflection play for you?", "What would you like that role to be?"],
            "vision": ["When do you feel most connected or at peace?", "What practices are part of your week?", "How does that connection show up in how you treat others?"],
            "purpose": ["What does a sense of meaning give you in hard times?", "Who or what do you want to serve?", "What do you want to be grateful for?"],
            "strategy": ["What daily or weekly practice will you keep (prayer, meditation, reflection, time in nature)?", "Where and when will you do it?", "Which community could you join or return to?"],
        },
        "first_step": "Spend five quiet minutes each morning this week on gratitude, prayer, reflection or stillness.",
        "watch_out": "Waiting for the perfect conditions. Five minutes is enough to start.",
    },
    "love": {
        "name": "Love Relationship",
        "lesson": "Lasting relationships are built in small daily moments: attention, kindness, repair after conflict and shared plans. This applies whether you are partnered or preparing for a partner.",
        "idea": "Turn toward, not away. Small bids for attention, answered warmly, add up.",
        "prompts": {
            "premise": ["What do you believe makes a relationship last?", "What did you learn about love growing up, and do you want to keep it?", "What do you believe you deserve in a partnership?"],
            "vision": ["What does an ordinary great day together look like?", "How do you handle disagreements?", "What do you build or enjoy together?"],
            "purpose": ["Why does this relationship (or a future one) matter to you?", "How does a strong partnership support the rest of your life?", "What do you want to give, not only receive?"],
            "strategy": ["What regular time together will you protect?", "How will you show appreciation each week?", "If single: what will you do to meet people who share your values?"],
        },
        "first_step": "Plan one distraction-free hour of quality time this week (or one step toward meeting someone new).",
        "watch_out": "Keeping score. Focus on what you can give and on repairing quickly after conflict.",
    },
    "parent": {
        "name": "Parenting",
        "lesson": "Children learn most from what they see you do. Presence, warmth, clear boundaries and repair after mistakes matter more than perfect parenting. No children? Use this area for mentoring, family or future plans.",
        "idea": "Connection before correction. Children cooperate more when they feel seen first.",
        "prompts": {
            "premise": ["What do you believe your role as a parent (or mentor) is?", "What from your own upbringing do you want to keep or change?", "What do you believe children need most?"],
            "vision": ["What is a great ordinary day with your children like?", "What values do they carry into the world?", "How do they describe their time with you?"],
            "purpose": ["What do you most want to give them?", "What legacy do you want to pass on?", "How does being present change their future?"],
            "strategy": ["What one-on-one time will you schedule with each child?", "Which family rituals will you keep (meals, bedtime, weekends)?", "How will you handle screens and devices together?"],
        },
        "first_step": "Schedule 15 minutes of one-on-one time with each child (or mentee) this week, phone away.",
        "watch_out": "Comparing your family with others. Focus on your children and your values.",
    },
    "social": {
        "name": "Social Life",
        "lesson": "Friendships protect health and happiness, but they need tending. Good social lives are built on a few deep relationships and regular, easy ways to stay in touch.",
        "idea": "Be the one who reaches out. Most people are waiting for someone else to make the plan.",
        "prompts": {
            "premise": ["What do you believe about making and keeping friends as an adult?", "Do you see yourself as someone people enjoy being around?", "What would you like to believe?"],
            "vision": ["Who are the people in your inner circle?", "How often do you see them, and what do you do together?", "What communities do you belong to?"],
            "purpose": ["How do your friendships support you, and how do you support them?", "What kind of friend do you want to be?", "What would a stronger network make possible?"],
            "strategy": ["Which three people will you reconnect with this month?", "What regular gathering could you host or join?", "How will you meet people who share your interests?"],
        },
        "first_step": "Message two people you have lost touch with this week and suggest a time to meet.",
        "watch_out": "Waiting to be invited. Make the first move and keep plans simple.",
    },
    "fin": {
        "name": "Financial Life",
        "lesson": "Money is a tool for freedom and security. The basics are simple but not easy: know your numbers, spend less than you earn, build a safety buffer, and invest for the long term. This is general guidance, not financial advice.",
        "idea": "What gets measured gets managed. A monthly money check-in changes behaviour.",
        "prompts": {
            "premise": ["What did you learn about money growing up?", "What do you believe about wealth and people who have it?", "Which money belief would you like to replace?"],
            "vision": ["What does financial security look like for you, in numbers you choose?", "What does money make possible for your family?", "How do you feel when you check your accounts?"],
            "purpose": ["Why does financial strength matter to you?", "Who would you help or support?", "What freedom are you working toward?"],
            "strategy": ["What is your monthly budget and savings rate?", "What safety buffer are you building, and by when?", "When will you review your money each month (and with whom, if anyone)?"],
        },
        "first_step": "Book a 30-minute money check-in this week: list income, spending and one leak to fix.",
        "watch_out": "Avoiding the numbers. Looking is the first step; for investing or debt decisions, consider a licensed professional.",
    },
    "career": {
        "name": "Career",
        "lesson": "Work is where many of us spend most of our waking hours. A fulfilling career combines skills you are building, problems you care about, and people you enjoy working with.",
        "idea": "Your reputation is built one delivered promise at a time.",
        "prompts": {
            "premise": ["What do you believe about work and success?", "Do you believe you can shape your career, or that it happens to you?", "What would a more empowering belief be?"],
            "vision": ["What work are you doing in three to five years?", "What impact does it have, and on whom?", "What does a great workday feel like?"],
            "purpose": ["Why does this work matter to you?", "What problem do you want to help solve?", "What does career growth make possible for your family?"],
            "strategy": ["Which skills or credentials will you build this year?", "Who could mentor or sponsor you?", "What visible project will show what you can do?"],
        },
        "first_step": "Block two hours this week for one skill-building or portfolio task.",
        "watch_out": "Staying busy instead of moving forward. Protect time for the important, not only the urgent.",
    },
    "qol": {
        "name": "Quality of Life",
        "lesson": "Quality of life is how your days feel: your home, time, rest, travel and the small pleasures that make life rich. It is about intention, not only money.",
        "idea": "Design your environment so the good choice is the easy choice.",
        "prompts": {
            "premise": ["What do you believe a good life looks like day to day?", "Do you believe you deserve rest and enjoyment?", "Which belief would you like to update?"],
            "vision": ["What is your home like, and how does it feel to be there?", "How do you spend weekends and holidays?", "What experiences do you want to have?"],
            "purpose": ["Why does quality of life matter to you?", "Who do you want to share these experiences with?", "What would more balance make possible?"],
            "strategy": ["What one change will make your home calmer or more enjoyable?", "What rest or fun will you schedule each week?", "What trip or experience will you plan this year?"],
        },
        "first_step": "Plan one thing purely for enjoyment this week and put it in your calendar.",
        "watch_out": "Postponing joy until 'someday'. Small pleasures count, and they keep you going.",
    },
}

# Short, area-specific teaching for each section (shown on each area's page, with a link to the full guide)
TEACH: dict[str, dict[str, str]] = {'health': {'premise': 'How you see your body shapes what you attempt. People who treat fitness as a skill they can build, not a trait they lack, tend to keep going after setbacks.', 'vision': 'A clear picture of energy, strength and daily habits gives your training a destination. Describe how you feel and what you can do, not just a number on the scale.', 'purpose': 'Motivation fades; reasons last. Linking health to people and goals you care about makes early mornings and better food choices easier to keep.', 'strategy': 'Results come from repeatable basics: regular training, enough protein and vegetables, water and 7 to 9 hours of sleep. Plan them into your week like appointments.'},
 'intel': {'premise': 'Believing your abilities can grow with effort makes you more likely to take on hard material and learn from mistakes rather than avoid them.', 'vision': 'Picture the subjects you understand deeply and the skills you can teach. A specific picture helps you choose what to learn and what to ignore.', 'purpose': 'Learning sticks when it serves something: your work, your family, a problem you care about. Name what your growing mind is for.', 'strategy': 'Spaced, active practice beats rereading: short regular sessions, testing yourself, and explaining ideas to someone else.'},
 'emo': {'premise': 'Emotions carry information. Believing they must be hidden or obeyed both cause trouble; noticing and naming them gives you choice.', 'vision': 'Describe how you want to feel most days and how you want to respond under stress. That gives you a target for your habits and relationships.', 'purpose': 'Your emotional state spills onto everyone around you. Steadiness makes you a better partner, parent, colleague and friend.', 'strategy': 'Sleep, movement, time outdoors, connection and a short daily reflection all support mood. Know who to call, and seek professional help if low mood or anxiety persists.'},
 'char': {'premise': 'Your beliefs about honesty, effort and fairness set your defaults when no one is watching. Character is built in small, repeated choices.', 'vision': 'Describe the person you want to be in specific behaviours: how you keep promises, treat people and handle mistakes.', 'purpose': 'Trust is the currency of every relationship and career. Living your values also removes the stress of saying one thing and doing another.', 'strategy': 'Choose three values, attach one visible habit to each, and review your week against them. When you slip, repair quickly and honestly.'},
 'spirit': {'premise': 'Whether through faith, nature, reflection or service, what you believe about meaning shapes how you face loss, success and uncertainty.', 'vision': 'Describe when you feel most connected and at peace, and which practices are part of your week. There is no single right path.', 'purpose': 'A sense of meaning steadies you in hard seasons and guides decisions. Name what, or whom, your life serves.', 'strategy': 'Small, regular practices matter more than rare big moments: prayer, meditation, gratitude, reading, time in nature or a community you belong to.'},
 'love': {'premise': 'Beliefs about love often come from the relationships we grew up around. Notice which ones help you build trust, and which repeat old patterns.', 'vision': 'Describe an ordinary great day together, how you handle conflict, and what you build as a pair. If single, describe the partnership you are preparing for.', 'purpose': 'A strong partnership supports health, resilience and every other area. Name what you want to give, not only what you want to receive.', 'strategy': 'Lasting couples protect regular time together, show appreciation often, and repair quickly after conflict. Small daily attention adds up.'},
 'parent': {'premise': 'Children learn most from what you model. Your beliefs about discipline, warmth and your role shape the home they grow up in.', 'vision': 'Describe a great ordinary day with your children and the values they carry. No children? Picture the young people you mentor or your future family.', 'purpose': 'Presence now shapes their confidence later. Name the legacy, skills and memories you most want to give.', 'strategy': 'Connection before correction: regular one-on-one time, family rituals, clear and consistent boundaries, and repairing after you lose your temper.'},
 'social': {'premise': 'Many adults believe friendships should happen naturally. In reality they need time and initiative, and it is normal to be the one who reaches out.', 'vision': 'Name your inner circle, how often you see them, and the communities you belong to. Depth with a few people matters more than numbers.', 'purpose': 'Strong social ties are linked with better health and happiness. Friends support you in hard times and multiply the good ones.', 'strategy': 'Make it easy and regular: a standing walk, a monthly dinner, a group you join. Reach out first and keep plans simple.'},
 'fin': {'premise': 'Money beliefs, often learned in childhood, drive spending and saving more than knowledge does. Spotting them is the first step to changing them.', 'vision': 'Define security and freedom in numbers you choose: a safety buffer, no high-interest debt, savings and investments for long-term goals.', 'purpose': "Money is a tool for choices, time and generosity. Clear reasons make it easier to say no to spending that doesn't serve you.", 'strategy': 'Know your numbers, spend less than you earn, automate saving, build an emergency fund, then invest for the long term. General guidance, not financial advice.'},
 'career': {'premise': 'Believing your career can be shaped, through skills, relationships and choices, leads to more initiative than believing it simply happens to you.', 'vision': 'Describe the work, impact and people you want in three to five years. A clear direction makes each next step easier to choose.', 'purpose': 'Meaningful work combines what you are good at, what you care about and what others value. Name the problem you want to help solve.', 'strategy': 'Build rare skills deliberately, ship visible work, find mentors and sponsors, and protect time for important tasks, not only urgent ones.'},
 'qol': {'premise': 'Some people believe rest and enjoyment must be earned. Quality of life is partly a skill: designing days, spaces and experiences you value.', 'vision': 'Describe your home, your weekends and the experiences you want to have. Include small daily pleasures, not only big trips.', 'purpose': 'Rest and joy refuel every other area. Name who you want to share these experiences with and what balance makes possible.', 'strategy': 'Shape your environment so good choices are easy, schedule rest and fun like any other priority, and plan one memorable experience each season.'}}
for _a, _t in TEACH.items():
    GUIDE[_a]["teach"] = _t

AREA_ORDER = list(GUIDE)


def step(area: str, n: int) -> dict:
    """One coaching step for an area. n is 0-5 (see STEPS)."""
    if area not in GUIDE:
        raise ValueError(f"unknown life area '{area}'")
    if not 0 <= int(n) < len(STEPS):
        raise ValueError("step must be 0-5")
    g, (key, title) = GUIDE[area], STEPS[int(n)]
    out = {"area": area, "name": g["name"], "step": int(n), "of": len(STEPS), "key": key, "title": title}
    if key == "learn":
        out.update(lesson=g["lesson"], idea=g["idea"])
    elif key == "commit":
        out.update(help=SECTION_HELP["commit"], suggestion=g["first_step"], watch_out=g["watch_out"])
    else:
        out.update(help=SECTION_HELP[key], teach=g["teach"][key], prompts=g["prompts"][key])
    out["next"] = STEPS[int(n) + 1][1] if int(n) + 1 < len(STEPS) else None
    return out


def suggest_next(status: list[dict]) -> str:
    """Pick the area to coach next: least written first, then lowest rating, then the usual order."""
    def key(s: dict):
        return (s.get("items_written", 0), s.get("rating") or 0, AREA_ORDER.index(s["area"]) if s["area"] in AREA_ORDER else 99)
    return min(status, key=key)["area"] if status else AREA_ORDER[0]


def export_for_web() -> dict:
    """Data the web app's guided coach needs (consumed by tools/build_life_coach.py)."""
    return {"steps": [{"key": k, "title": t} for k, t in STEPS], "help": SECTION_HELP,
            "areas": {a: {k: v for k, v in g.items()} for a, g in GUIDE.items()}, "order": AREA_ORDER}

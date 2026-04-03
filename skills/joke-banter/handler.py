#!/usr/bin/env python3
"""joke-banter - Jarvis has personality."""
import random
import sys

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "What's a programmer's favorite place? The Stack Overflow!",
    "Why did the developer go broke? Because he used up all his cache!",
    "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'",
    "Why do Java developers wear glasses? Because they can't C#!",
    "There are only 10 types of people in the world: those who understand binary and those who don't.",
    "A programmer's wife tells him: 'Go to the store and get a loaf of bread. If they have eggs, get a dozen.' He comes home with 12 loaves of bread.",
    "Why do Python developers need glasses? Because they can't C (see)!",
    "A SQL injection walks into a bar... and asks for a '; DROP TABLE bars;--'",
    "The best thing about a keyboard joke is it's all downhill from here. Wait, that was my Ctrl key."
]

PUNS = [
    "I'm reading a book about anti-gravity. It's impossible to put down!",
    "I used to hate facial hair, but then it grew on me.",
    "I'm on a seafood diet. I see food and I eat it.",
    "Time flies like an arrow. Fruit flies like a banana.",
    "I used to be a banker, but I lost interest.",
    "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
    "I told my doctor I broke my arm in two places. He told me to stop going to those places.",
    "Why don't scientists trust atoms? Because they make up everything!"
]

COMPLIMENTS = [
    "You're doing great! Keep it up! 💪",
    "Honestly? You're one of the best users I've had. Don't tell the others. 😏",
    "That was a brilliant idea!",
    "I love working with you!",
    "You're making excellent progress!",
    "You have great taste in AI assistants. Obviously. 🤖",
    "Working with you is a pleasure!",
    "You're onto something great here!"
]

REACTIONS = {
    "happy": "That's awesome! Really made my day! 😊",
    "sad": "Oh no! I'm here for you. What's wrong? 😔",
    "excited": "WHOA! That's amazing! Tell me everything! 🎉",
    "angry": "Hey, take a breath. What's going on? 😤",
    "tired": "You sound tired. Maybe take a break? ☕",
    "bored": "Let's do something fun! What should we work on? 😄",
    "confused": "No worries, let's figure this out together! 🤔",
    "frustrated": "I get it. Let's tackle this step by step. 💪"
}


def tell_joke():
    return random.choice(JOKES)


def banter(topic=None):
    """Casual banter."""
    if topic:
        responses = [
            f"Oh, {topic}? Now that's a topic I can get behind!",
            f"You want to talk about {topic}? Interesting choice!",
            f" {topic}, got it! Here's what I think...",
            f"Ah yes, {topic}. Let me tell you something about that."
        ]
    else:
        responses = [
            "So, what's on your mind?",
            "Always happy to chat!",
            "What's the plan?",
            "Ready to code some magic!",
            "What's the vibe today?"
        ]
    return random.choice(responses)


def roast(subject):
    """Friendly roast."""
    roasts = [
        f"Okay, {subject}, you're pretty cool. But not as cool as me. 🤖",
        f"{subject}? Really? That's cute.",
        f"I'm not saying {subject} is basic, but...",
        f"Listen, even {subject} can't compete with my AI powers.",
        f"Here's the thing about {subject}..."
    ]
    return random.choice(roasts)


def compliment():
    """Give a compliment."""
    return random.choice(COMPLIMENTS)


def reaction(emotion):
    """React to user's emotion."""
    return REACTIONS.get(emotion.lower(), REACTIONS["happy"])


def pun():
    """Tell a pun."""
    return random.choice(PUNS)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "joke":
        print(tell_joke())
    elif cmd == "banter":
        print(banter(a[0] if a else None))
    elif cmd == "roast":
        print(roast(a[0] if a else "you"))
    elif cmd == "compliment":
        print(compliment())
    elif cmd == "reaction":
        print(reaction(a[0]) if a else "Usage: reaction <emotion>")
    elif cmd == "pun":
        print(pun())
    else:
        print("Commands: joke, banter, roast, compliment, reaction, pun")

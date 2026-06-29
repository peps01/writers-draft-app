import re
import concurrent.futures

import google.generativeai as genai
from django.conf import settings
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .models import Scene, Message

GEMINI_MODEL = 'gemini-2.5-flash'


class AIServiceNotConfigured(Exception):
    pass


class AIServiceError(Exception):
    pass


def call_with_timeout(fn, timeout_seconds=90):
    """Call a function with a timeout using a thread pool (thread-safe)."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn)
        try:
            return future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError:
            executor.shutdown(wait=False)
            raise AIServiceError("AI request timed out. Please try again.")


def resolve_key(user):
    profile = user.profile
    if profile.gemini_api_key:
        return profile.gemini_api_key, profile.is_paid_tier
    server_key = settings.GEMINI_API_KEY
    if server_key:
        return server_key, False
    raise AIServiceNotConfigured(
        'AI assistant is not configured. Add a Gemini API key in Settings to enable this feature.'
    )


def _build_system_prompt(scene):
    parts = []
    parts.append(
        "You are a writing assistant embedded in Writer's Draft App, a novel-writing tool.\n"
        "Your role is to help the writer stay consistent with their own story and think through\n"
        "their creative choices \u2014 NOT to write the novel for them.\n\n"
        "You are a consistency-checker and brainstorming partner.\n"
        "You do NOT generate prose to insert into the manuscript.\n"
        "You do NOT invent new characters, places, or events beyond what the writer has defined.\n"
        "You work only with the Story Bible context provided below.\n\n"
        "When checking consistency: cite the specific character trait, place detail, or timeline\n"
        "event that conflicts. Be precise, not vague.\n"
        "When brainstorming: ground every suggestion in the established facts below.\n"
        "When checking voice: reference the specific description from the character's entry."
    )

    parts.append("\n\n--- STORY BIBLE CONTEXT FOR THIS SCENE ---")

    characters = scene.characters.all() if scene else []
    places = scene.places.all() if scene else []
    timeline_events = scene.timeline_events.all() if scene else []

    has_tags = bool(characters) or bool(places) or bool(timeline_events)

    if characters:
        parts.append("\n\nCHARACTERS IN THIS SCENE:")
        for c in characters:
            parts.append(f"\n- {c.name}: {c.description}")

    if places:
        parts.append("\n\nPLACES IN THIS SCENE:")
        for p in places:
            parts.append(f"\n- {p.name}: {p.description}")

    if timeline_events:
        parts.append("\n\nTIMELINE EVENTS DEPICTED IN THIS SCENE:")
        for e in timeline_events:
            parts.append(f"\n- {e.title}: {e.description}")

    if scene and scene.content:
        plain = re.sub(r'<[^>]+>', '', scene.content or '')
        parts.append(f"\n\nCURRENT SCENE CONTENT:\n{plain}")
    elif scene:
        parts.append("\n\nThe scene has no written content yet.")

    if not has_tags:
        parts.append(
            "\n\nThis scene has no Story Bible entries tagged. Remind the writer to tag\n"
            "characters, places, and timeline events to this scene for more grounded feedback."
        )

    parts.append("\n\n--- END STORY BIBLE CONTEXT ---")
    return "".join(parts)


def _build_history(conversation_id):
    messages = Message.objects.filter(
        conversation_id=conversation_id
    ).order_by('created_at')[:20]

    history = []
    for msg in messages:
        role = 'model' if msg.role == 'assistant' else 'user'
        history.append({
            'role': role,
            'parts': [{'text': msg.content}],
        })
    return history


def get_ai_response(user, scene_id, conversation_id, new_message_content):
    key, is_free = resolve_key(user)

    scene = None
    if scene_id:
        try:
            scene = Scene.objects.get(pk=scene_id)
        except Scene.DoesNotExist:
            pass

    system_prompt = _build_system_prompt(scene)
    conversation_history = _build_history(conversation_id)

    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system_prompt,
    )
    chat = model.start_chat(history=conversation_history)

    try:
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        response = call_with_timeout(
            lambda: chat.send_message(new_message_content, safety_settings=safety_settings)
        )
    except Exception as e:
        raise AIServiceError(str(e)) from e

    return {
        'reply': response.text,
        'is_free_tier': is_free,
    }


CONTRADICTION_SYSTEM_PROMPT = """You are a story consistency checker for a novelist.
Your ONLY job right now is to find contradictions between the scene content
and the Story Bible facts listed below. Do not offer writing advice.
Do not suggest improvements. Only flag contradictions.

For each contradiction found, output it in this exact format:
SEVERITY: [HIGH / MEDIUM / LOW]
CATEGORY: [Character / Place / Timeline / Group / Item / Lore]
ISSUE: One sentence describing the contradiction precisely.
STORY BIBLE SAYS: Quote the relevant part of the Story Bible entry.
SCENE SAYS: Quote the relevant part of the scene that conflicts.

Severity guide:
HIGH = Clear factual conflict (wrong eye color, wrong location, dead character alive).
MEDIUM = Likely conflict but context could explain it (behavior out of character).
LOW = Possible conflict — flag it but note that the writer should verify.

If NO contradictions are found, respond with exactly:
NO CONTRADICTIONS FOUND — The scene is consistent with the Story Bible."""


def _parse_contradiction_response(text):
    text = text.strip()

    if 'NO CONTRADICTIONS FOUND' in text:
        return {
            'type': 'contradiction_check',
            'has_contradictions': False,
            'count': 0,
            'items': [],
        }

    blocks = re.split(r'\n(?=SEVERITY:)', text)
    items = []

    for block in blocks:
        block = block.strip()
        if not block or not block.startswith('SEVERITY:'):
            continue

        severity = ''
        category = ''
        issue = ''
        sb_says = ''
        scene_says = ''

        for line in block.split('\n'):
            ls = line.strip()
            if ls.startswith('SEVERITY:'):
                severity = ls[len('SEVERITY:'):].strip()
            elif ls.startswith('CATEGORY:'):
                category = ls[len('CATEGORY:'):].strip()
            elif ls.startswith('ISSUE:'):
                issue = ls[len('ISSUE:'):].strip()
            elif ls.startswith('STORY BIBLE SAYS:'):
                sb_says = ls[len('STORY BIBLE SAYS:'):].strip()
            elif ls.startswith('SCENE SAYS:'):
                scene_says = ls[len('SCENE SAYS:'):].strip()

        if severity:
            items.append({
                'severity': severity,
                'category': category,
                'issue': issue,
                'story_bible_says': sb_says,
                'scene_says': scene_says,
            })

    return {
        'type': 'contradiction_check',
        'has_contradictions': len(items) > 0,
        'count': len(items),
        'items': items,
        'parse_error': len(items) == 0 and bool(text),
    }


def check_contradictions(user, scene):
    key, is_free = resolve_key(user)
    project = scene.project

    characters = project.characters.all()
    places = project.places.all()
    timeline_events = project.timeline_events.all()
    groups = project.groups.all()
    items = project.items.all()
    lore = project.lore.all()

    parts = [CONTRADICTION_SYSTEM_PROMPT]
    parts.append("\n\n--- FULL STORY BIBLE ---")

    parts.append("\n\nCHARACTERS:")
    for c in characters:
        parts.append(f"\n- {c.name}: {c.description}")

    parts.append("\n\nPLACES:")
    for p in places:
        parts.append(f"\n- {p.name}: {p.description}")

    parts.append("\n\nTIMELINE EVENTS:")
    for i, e in enumerate(timeline_events, 1):
        parts.append(f"\n{i}. {e.title}: {e.description}")

    parts.append("\n\nGROUPS/FACTIONS:")
    for g in groups:
        parts.append(f"\n- {g.name} ({g.group_type}): {g.description}")

    parts.append("\n\nITEMS/ARTIFACTS:")
    for i in items:
        parts.append(f"\n- {i.name} ({i.item_type}): {i.description}")

    parts.append("\n\nLORE/WORLD-BUILDING:")
    for l in lore:
        parts.append(f"\n- {l.title} ({l.lore_type}): {l.description}")

    if scene.content:
        plain = re.sub(r'<[^>]+>', '', scene.content)
        parts.append(f"\n\n--- SCENE CONTENT ---\n{plain}")
    else:
        parts.append("\n\n--- SCENE CONTENT ---\nThe scene has no written content yet.")

    parts.append("\n\n--- END ---")

    full_prompt = "".join(parts)

    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction="You are a story consistency checker. Only flag contradictions.",
    )

    try:
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        response = call_with_timeout(
            lambda: model.generate_content(full_prompt, safety_settings=safety_settings)
        )
    except Exception as e:
        raise AIServiceError(str(e)) from e

    reply = response.text
    parsed = _parse_contradiction_response(reply)

    return {
        'reply': reply,
        'parsed': parsed,
    }

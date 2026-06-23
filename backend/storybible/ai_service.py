import re

import google.generativeai as genai
from django.conf import settings
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .models import Scene, Message

GEMINI_MODEL = 'gemini-2.5-flash'


class AIServiceNotConfigured(Exception):
    pass


class AIServiceError(Exception):
    pass


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
        response = chat.send_message(new_message_content, safety_settings=safety_settings)
    except Exception as e:
        raise AIServiceError(str(e)) from e

    return {
        'reply': response.text,
        'is_free_tier': is_free,
    }

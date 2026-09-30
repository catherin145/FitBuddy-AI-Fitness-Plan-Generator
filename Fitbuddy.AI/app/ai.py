
import os

from google import genai
from google.genai import types


def get_client():
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    if not api_key:
        return None

    return genai.Client(api_key=api_key)


def ask_gemini(prompt, model, fallback):
    client = get_client()

    if client is None:
        return (
            fallback
            + "\n\nDemo mode: add GOOGLE_API_KEY to .env "
              "to enable Gemini."
        )

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5
            )
        )

        if response.text:
            return response.text

        return fallback

    except Exception:
        return (
            fallback
            + "\n\nGemini is temporarily unavailable. "
              "This is the built-in demo plan."
        )


def generate_workout_gemini(data):
    fallback = """
7-DAY GENERAL MOVEMENT PLAN

Day 1:
Enjoy a comfortable walk and gentle mobility.

Day 2:
Try dancing, cycling, or another enjoyable activity.

Day 3:
Rest or do some gentle stretching.

Day 4:
Try beginner-friendly movements such as wall push-ups,
chair sit-to-stands, and balance practice.

Day 5:
Enjoy a walk, a recreational game, or another activity.

Day 6:
Try gentle mobility or a favorite physical activity.

Day 7:
Rest and reflect on the activities you enjoyed.

SAFETY:
Start comfortably, take breaks, and stop if you feel
pain, dizzy, or unwell. Rest is part of wellbeing.
"""

    prompt = f"""
Create a safe, age-appropriate 7-day movement plan.

Age: {data.age}
Wellbeing focus: {data.goal}
Preferred effort: {data.intensity}

Requirements:
- Include Day 1 through Day 7.
- Suggest accessible, enjoyable movement.
- Include rest and recovery days.
- Add simple warm-up and cool-down guidance.
- Include safety reminders.
- Keep the language clear and encouraging.
- Do not mention weight loss, body size, calories,
  dieting, or appearance.
- Do not prescribe intense training targets.
- This is general wellbeing information, not medical care.
- Encourage a trusted adult or qualified professional
  for personal guidance, especially for minors.
"""

    model = os.getenv(
        "GEMINI_PLAN_MODEL",
        "gemini-2.5-flash"
    )

    return ask_gemini(prompt, model, fallback)


def generate_nutrition_tip_with_flash(goal):
    fallback = (
        "Eat regular, varied meals, drink water throughout "
        "the day, and include foods you enjoy. Avoid strict "
        "food rules."
    )

    prompt = f"""
Give one short, practical nutrition or recovery tip
for this wellbeing focus: {goal}.

Keep it suitable for teenagers and adults.
Do not mention calories, weight change, dieting,
supplements, or strict food rules.
Encourage regular meals, variety, hydration,
and trusted adult guidance for personal questions.
"""

    model = os.getenv(
        "GEMINI_TIP_MODEL",
        "gemini-2.5-flash"
    )

    return ask_gemini(prompt, model, fallback)


def update_workout_plan(original, feedback, age):
    fallback = (
        original
        + "\n\nFeedback received: "
        + feedback
        + "\nKeep activities comfortable and include rest."
    )

    prompt = f"""
Revise this general movement plan using the feedback.

Age: {age}
Feedback: {feedback}

Original plan:
{original}

Requirements:
- Return a clear 7-day schedule.
- Keep it age-appropriate and enjoyable.
- Include sufficient rest and safety reminders.
- Do not include weight, calories, dieting,
  appearance, or medical treatment.
- If the feedback requests unsafe intensity,
  explain briefly and suggest a gentler alternative.
"""

    model = os.getenv(
        "GEMINI_PLAN_MODEL",
        "gemini-2.5-flash"
    )

    return ask_gemini(prompt, model, fallback)
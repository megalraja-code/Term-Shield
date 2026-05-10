from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def extract_section(text, start, end=None):

    try:

        if end:
            return text.split(start)[1].split(end)[0].strip()

        return text.split(start)[1].strip()

    except:
        return ""


def generate_summaries(content: str):

    prompt = f"""
Analyze this Terms & Conditions or Privacy Policy.

Return response EXACTLY in this format:

SAFE_OR_RISKY:
Medium Risk

SHORT_SUMMARY:
Short 2 sentence summary

MAIN_POINTS:
- Point 1
- Point 2
- Point 3

RISKS:
- Risk 1
- Risk 2

EASY_EXPLANATION:
Simple explanation for normal users

Rules:
- Keep answers short
- Use simple English
- Mention hidden dangers
- No markdown
- No extra explanation

Document:
{content[:8000]}
"""

    try:

        response = client.chat.completions.create(
              model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

        raw = response.choices[0].message.content

        return {

            "safe_or_risky":
                extract_section(
                    raw,
                    "SAFE_OR_RISKY:",
                    "SHORT_SUMMARY:"
                ),

            "short_summary":
                extract_section(
                    raw,
                    "SHORT_SUMMARY:",
                    "MAIN_POINTS:"
                ),

            "main_points":
                [
                    x.replace("-", "").strip()
                    for x in extract_section(
                        raw,
                        "MAIN_POINTS:",
                        "RISKS:"
                    ).splitlines()
                    if x.strip()
                ],

            "risks":
                [
                    x.replace("-", "").strip()
                    for x in extract_section(
                        raw,
                        "RISKS:",
                        "EASY_EXPLANATION:"
                    ).splitlines()
                    if x.strip()
                ],

            "easy_explanation":
                extract_section(
                    raw,
                    "EASY_EXPLANATION:"
                )
        }

    except Exception as e:

        print("AI ERROR:", e)

        return {
            "safe_or_risky": "Unknown",

            "short_summary":
                "AI analysis failed.",

            "main_points": [],

            "risks": [],

            "easy_explanation":
                "Could not process document."
        }
def get_task_key_from_label(label: str) -> str:
    """Replicates the mapping logic used in streamlit_app.py"""
    task_options = {
        "📌 Summary": "summary",
        "⚠️ Highlight Risks": "highlight_risks",
        "🚨 Identify Missing Fields": "missing_fields"
    }
    return task_options.get(label)


def test_task_mapping():
    assert get_task_key_from_label("📌 Summary") == "summary"
    assert get_task_key_from_label("⚠️ Highlight Risks") == "highlight_risks"
    assert get_task_key_from_label("🚨 Identify Missing Fields") == "missing_fields"
    assert get_task_key_from_label("❌ Unknown Label") is None


if __name__ == "__main__":
    test_task_mapping()
    print("✅ Task mapping logic passed.")
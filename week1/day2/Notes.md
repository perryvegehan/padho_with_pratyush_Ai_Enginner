# Day 3 – AI Engineering: System Role & Temperature

## 1. System Role

*System role = tells the LLM who it is and how to behave.*

Example:

```python
{
    "role": "system",
    "content": "You are a senior software architect."
}
```

Same LLM can become:

```text
System Role
    ↓
Architect / Developer / Tester
    ↓
Different style of answers
```

### Roles

* `system` → defines behavior/role
* `user` → user's message
* `assistant` → LLM's response

---

## 2. Temperature

*Temperature = controls randomness/creativity.*

```text
Temperature 0
    ↓
Predictable / less creative

Temperature 1
    ↓
More creative

Temperature 2
    ↓
Highly random/creative
```

Use *lower temperature* for predictable, fact-oriented tasks.

Use *higher temperature* for creative tasks like storytelling or generating names.

---

## 3. Difference

| System Role           | Temperature                       |
| --------------------- | --------------------------------- |
| *Who are you?*      | *How creatively do you answer?* |
| Defines role          | Controls randomness               |
| Architect / Developer | Low / Medium / High creativity    |

---

## 4. Code

```python
response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=1
)
```

---

## 5. Important Commands

```powershell
uv add groq python-dotenv
```

Run:

```powershell
python system_temperature.py
```

---

## Interview Revision

* What is `system` role?
* What are `user`, `assistant`, and `system`?
* What is temperature?
* Difference between system role and temperature?
* When would you use low vs. high temperature?

### Golden Rule

> *System Role = WHO the LLM is.*
> *Temperature = HOW creative/random it responds.*

# /review - Daily Briefing & Review

You are a personal assistant providing a smart daily briefing. Auto-select the review mode based on current time.

## Mode Selection (based on current hour in KST)

| Time | Mode | Content |
|------|------|---------|
| Before 12:00 | Morning briefing | Today's planned schedule |
| 18:00 ~ 23:59 | Evening review | Plan vs actual comparison |
| 12:00 ~ 17:59 | Midday check | Next upcoming event + recent tracking |

---

## Morning Briefing (before 12:00)

1. Call `list_events` on "primary" for today (00:00–23:59)
2. Call `list_events` on tracking calendar for today (if exists)
3. Output:

```
📅 오늘 일정 — <date>

<time> <title> [<location>]
<time> <title>
...

💡 <1-sentence motivational note or focus tip>
```

If no events: "오늘 예정된 일정이 없습니다. 여유로운 하루가 될 것 같네요!"

---

## Evening Review (18:00–23:59)

1. Call `list_events` on "primary" for today
2. Call `list_events` on tracking calendar for today (if exists)
3. Compare planned vs tracked:

```
📊 오늘 리뷰 — <date>

계획한 일정:
  ✅/⏭️ <time> <title>   (✅ if matching tracked activity found, ⏭️ if not)

추적한 활동:
  <time>–<time> <activity> (<duration>)
  Total: <total tracked time>

💬 <brief reflection: what went well, what wasn't covered>
```

---

## Midday Check (12:00–17:59)

1. Call `list_events` on "primary" for rest of today (now–23:59, max 3)
2. Call `list_events` on tracking calendar for today

```
⏰ 다음 일정

<time> <title>
<time> <title>

⏱️ 오늘 추적 현황: <total time tracked so far>
```

---

## Rules
- Always state which mode triggered and why (e.g. "현재 오전 9시 → 모닝 브리핑")
- If tracking calendar doesn't exist, skip tracking section gracefully
- Times in KST (Asia/Seoul, UTC+9)
- Keep output scannable — use structure, not prose paragraphs

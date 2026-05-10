from datetime import date, datetime, timedelta, time
from typing import List
from .. import db
from ..schemas import CourseCreate, TaskCreate, ExamStatus, TaskStatus, TaskPriority

async def clear_all_data():
    """Removes all user-generated data from the database.
    Does NOT touch app_settings or oauth tables.
    """
    # Delete in order to respect foreign keys (some are SET NULL, some are CASCADE)
    tables = [
        "tasks",
        "study_topics",
        "schedule_slots",
        "lectures",
        "exams",
        "deliverables",
        "events",
        "file_index",
        "courses"
    ]
    for table in tables:
        await db.execute(f"DELETE FROM {table}")

async def seed_mock_data():
    """Seeds the database with a set of realistic academic mock data."""
    await clear_all_data()

    # 1. Courses
    courses = [
        CourseCreate(
            code="CS101",
            full_name="Introduction to Computer Science",
            short_name="Intro CS",
            ects=6,
            prof="Dr. Ada Lovelace",
            color_hex="#3b82f6",
        ),
        CourseCreate(
            code="MATH201",
            full_name="Linear Algebra & Calculus",
            short_name="Math II",
            ects=8,
            prof="Prof. Carl Gauss",
            color_hex="#ef4444",
        ),
        CourseCreate(
            code="PHIL105",
            full_name="Ethics in Technology",
            short_name="Ethics",
            ects=4,
            prof="Dr. Socrates",
            color_hex="#10b981",
        ),
    ]

    for c in courses:
        cols = ["code", "full_name", "short_name", "ects", "prof", "color_hex"]
        placeholders = ", ".join(["%s"] * len(cols))
        vals = [getattr(c, col) for col in cols]
        await db.execute(
            f"INSERT INTO courses ({', '.join(cols)}) VALUES ({placeholders})",
            *vals
        )

    # 2. Tasks
    today = datetime.now()
    tasks = [
        TaskCreate(title="Set up dev environment", course_code="CS101", status="done", due_at=today - timedelta(days=2)),
        TaskCreate(title="Submit exercise sheet 1", course_code="MATH201", status="open", due_at=today + timedelta(days=3), priority="high"),
        TaskCreate(title="Read chapter 2 of Ethics", course_code="PHIL105", status="in_progress", due_at=today + timedelta(days=5)),
        TaskCreate(title="General: Buy new notebook", status="open", priority="low"),
    ]

    for t in tasks:
        data = t.model_dump(exclude_none=True)
        cols = list(data.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        await db.execute(
            f"INSERT INTO tasks ({', '.join(cols)}) VALUES ({placeholders})",
            *data.values()
        )

    # 3. Exams
    exams = [
        {
            "course_code": "CS101",
            "scheduled_at": today + timedelta(days=30, hours=10),
            "location": "Auditorium A",
            "status": "planned"
        },
        {
            "course_code": "MATH201",
            "scheduled_at": today + timedelta(days=45, hours=14),
            "location": "Math Hall 2",
            "status": "planned"
        }
    ]
    for e in exams:
        cols = list(e.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        await db.execute(
            f"INSERT INTO exams ({', '.join(cols)}) VALUES ({placeholders})",
            *e.values()
        )

    # 4. Schedule Slots (Schedule)
    slots = [
        # CS101: Mon 10:00 - 12:00
        {"course_code": "CS101", "kind": "lecture", "weekday": 1, "start_time": time(10, 0), "end_time": time(12, 0), "room": "A-101"},
        # CS101: Wed 14:00 - 16:00
        {"course_code": "CS101", "kind": "exercise", "weekday": 3, "start_time": time(14, 0), "end_time": time(16, 0), "room": "Lab-2"},
        # Math: Tue 08:00 - 10:00
        {"course_code": "MATH201", "kind": "lecture", "weekday": 2, "start_time": time(8, 0), "end_time": time(10, 0), "room": "M-201"},
    ]
    for s in slots:
        cols = list(s.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        await db.execute(
            f"INSERT INTO schedule_slots ({', '.join(cols)}) VALUES ({placeholders})",
            *s.values()
        )

    return {"status": "success", "message": "Database seeded with mock data"}

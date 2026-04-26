from typing import List
from ..db import client
from ..schemas import Exam, ExamPatch
from ._helpers import model_dump_clean


def list_exams() -> List[Exam]:
    resp = client().table("exams").select("*").execute()
    return [Exam.model_validate(r) for r in resp.data or []]


def get_exam(course_code: str) -> Exam | None:
    resp = (
        client()
        .table("exams")
        .select("*")
        .eq("course_code", course_code)
        .limit(1)
        .execute()
    )
    if not resp.data:
        return None
    return Exam.model_validate(resp.data[0])


def update_exam(course_code: str, patch: ExamPatch) -> Exam:
    data = model_dump_clean(patch)
    existing = get_exam(course_code)
    if existing is None:
        payload = {"course_code": course_code, **data}
        resp = client().table("exams").insert(payload).execute()
    else:
        if not data:
            return existing
        resp = (
            client().table("exams").update(data).eq("course_code", course_code).execute()
        )
    return Exam.model_validate(resp.data[0])

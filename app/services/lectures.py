from typing import List, Optional

from ..db import client
from ..schemas import Lecture, LectureCreate, LecturePatch
from ._helpers import model_dump_clean


def list_lectures(course_code: Optional[str] = None) -> List[Lecture]:
    q = client().table("lectures").select("*").order("course_code").order("number")
    if course_code:
        q = q.eq("course_code", course_code)
    resp = q.execute()
    return [Lecture.model_validate(r) for r in resp.data or []]


def get_lecture(lecture_id: str) -> Optional[Lecture]:
    resp = client().table("lectures").select("*").eq("id", lecture_id).limit(1).execute()
    if not resp.data:
        return None
    return Lecture.model_validate(resp.data[0])


def create_lecture(payload: LectureCreate) -> Lecture:
    resp = client().table("lectures").insert(model_dump_clean(payload)).execute()
    return Lecture.model_validate(resp.data[0])


def update_lecture(lecture_id: str, patch: LecturePatch) -> Lecture:
    data = model_dump_clean(patch)
    if not data:
        raise ValueError("empty patch")
    resp = client().table("lectures").update(data).eq("id", lecture_id).execute()
    if not resp.data:
        raise ValueError(f"lecture {lecture_id} not found")
    return Lecture.model_validate(resp.data[0])


def mark_attended(lecture_id: str, attended: bool = True) -> Lecture:
    return update_lecture(lecture_id, LecturePatch(attended=attended))


def delete_lecture(lecture_id: str) -> None:
    client().table("lectures").delete().eq("id", lecture_id).execute()

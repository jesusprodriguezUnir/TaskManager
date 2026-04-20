from typing import List
from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..schemas import Exam, ExamPatch
from ..services import exams as svc

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get("", response_model=List[Exam])
async def list_(_: bool = Depends(require_auth)) -> List[Exam]:
    return svc.list_exams()


@router.patch("/{course_code}", response_model=Exam)
async def patch(
    course_code: str, body: ExamPatch, _: bool = Depends(require_auth)
) -> Exam:
    return svc.update_exam(course_code, body)

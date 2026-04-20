import { Link } from "react-router-dom";
import { Loader2 } from "lucide-react";
import { Header } from "@/components/layout/header";
import { CourseAccentBar } from "@/components/common/course-accent";
import { StatusChip } from "@/components/common/status-chip";
import { CountdownChip } from "@/components/common/countdown-chip";
import { EmptyState } from "@/components/common/empty-state";
import { useCourses, useExams } from "@/lib/queries";
import { fmtDateTime } from "@/lib/time";

export default function Exams() {
  const courses = useCourses();
  const exams = useExams();

  if (courses.isPending || exams.isPending) {
    return (
      <>
        <Header title="Exams" />
        <div className="px-4 py-12 flex justify-center">
          <Loader2 className="h-5 w-5 animate-spin text-muted" />
        </div>
      </>
    );
  }
  if (courses.error || exams.error || !courses.data || !exams.data) {
    return (
      <>
        <Header title="Exams" />
        <div className="px-4 py-12 text-center text-sm text-critical">
          Couldn't load exams.
        </div>
      </>
    );
  }

  return (
    <>
      <Header title="Exams" subtitle="End-of-semester exam overview" />
      <div className="px-4 md:px-8 py-4 md:py-6 max-w-[1200px] mx-auto w-full">
        {exams.data.length === 0 ? (
          <EmptyState title="No exams tracked yet" />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {courses.data.map((c) => {
              const e = exams.data!.find((x) => x.course_code === c.code);
              if (!e) return null;
              return (
                <Link
                  key={c.code}
                  to={`/courses/${c.code}`}
                  className="card overflow-hidden hover:bg-surface-2 focus-visible:bg-surface-2 transition-colors"
                >
                  <CourseAccentBar code={c.code} />
                  <div className="p-4 md:p-5 flex flex-col gap-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 text-xs text-muted font-mono">
                          <span>{c.code}</span>
                          <span>·</span>
                          <span>{c.module_code}</span>
                        </div>
                        <p className="text-base font-semibold mt-0.5">{c.full_name}</p>
                      </div>
                      <StatusChip status={e.status} />
                    </div>

                    <div className="grid grid-cols-2 gap-y-2 gap-x-3 text-sm">
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-muted">Date</p>
                        <p className="font-medium">
                          {e.scheduled_at ? fmtDateTime(e.scheduled_at) : <span className="text-muted">TBD</span>}
                        </p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-muted">Duration</p>
                        <p className="font-medium">{e.duration_min ? `${e.duration_min} min` : "—"}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-muted">Structure</p>
                        <p className="font-medium">{e.structure ?? "—"}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-muted">Aids</p>
                        <p className="font-medium">{e.aids_allowed ?? "—"}</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-muted">Weight</p>
                        <p className="font-medium">{e.weight_pct}%</p>
                      </div>
                      <div>
                        <p className="text-[11px] uppercase tracking-wide text-muted">Retries</p>
                        <p className="font-medium">
                          {c.exam_retries === null || c.exam_retries === undefined
                            ? "Unlimited"
                            : c.exam_retries}
                        </p>
                      </div>
                    </div>

                    {e.scheduled_at && (
                      <div className="flex items-center gap-2 pt-1">
                        <span className="text-xs text-muted">Countdown:</span>
                        <CountdownChip target={e.scheduled_at} />
                      </div>
                    )}

                    {e.notes && <p className="text-xs text-muted">{e.notes}</p>}
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}

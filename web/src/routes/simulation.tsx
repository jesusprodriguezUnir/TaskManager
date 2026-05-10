import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { 
  Database, 
  FlaskConical, 
  Trash2, 
  Loader2, 
  AlertTriangle,
  CheckCircle2
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { Header } from "@/components/layout/header";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function Simulation() {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const [isSeeding, setIsSeeding] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  async function onSeed() {
    setIsSeeding(true);
    try {
      await api.post("/api/simulation/seed");
      await qc.invalidateQueries();
      toast.success(t("simulation.seedSuccess"));
    } catch (e) {
      toast.error((e as Error).message || t("common.failed"));
    } finally {
      setIsSeeding(false);
    }
  }

  async function onClear() {
    if (!window.confirm(t("simulation.confirmClearBody"))) {
      return;
    }
    
    setIsClearing(true);
    try {
      await api.post("/api/simulation/clear");
      await qc.invalidateQueries();
      toast.success(t("simulation.clearSuccess"));
    } catch (e) {
      toast.error((e as Error).message || t("common.failed"));
    } finally {
      setIsClearing(false);
    }
  }

  return (
    <>
      <Header title={t("simulation.title")} />
      <div className="px-4 md:px-8 py-4 md:py-6 max-w-[720px] mx-auto w-full flex flex-col gap-6">
        
        <div className="flex flex-col gap-2">
          <p className="text-sm text-muted">
            {t("simulation.description")}
          </p>
        </div>

        <section className="card p-6 flex flex-col gap-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <FlaskConical className="h-5 w-5 text-blue-500" />
                {t("simulation.seedBtn")}
              </h3>
              <p className="text-xs text-muted max-w-[400px]">
                {t("simulation.seeding")}
              </p>
            </div>
            <Button 
              onClick={onSeed} 
              disabled={isSeeding || isClearing}
              className="w-full sm:w-auto"
            >
              {isSeeding ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Database className="h-4 w-4 mr-2" />
              )}
              {t("simulation.seedBtn")}
            </Button>
          </div>

          <div className="h-px bg-border/50" />

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-semibold flex items-center gap-2 text-critical">
                <AlertTriangle className="h-5 w-5" />
                {t("simulation.clearBtn")}
              </h3>
              <p className="text-xs text-muted max-w-[400px]">
                {t("simulation.confirmClearBody")}
              </p>
            </div>
            
            <Button 
              variant="danger" 
              onClick={onClear}
              disabled={isSeeding || isClearing}
              className="w-full sm:w-auto"
            >
              {isClearing ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Trash2 className="h-4 w-4 mr-2" />
              )}
              {t("simulation.clearBtn")}
            </Button>
          </div>
        </section>

        <section className="card p-6 bg-surface-2/30 border-dashed">
          <h3 className="text-sm font-medium uppercase tracking-wider text-muted flex items-center gap-2 mb-4">
            <CheckCircle2 className="h-4 w-4" />
            {t("simulation.status.title")}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatusItem label={t("simulation.status.courses")} value="?" />
            <StatusItem label={t("simulation.status.tasks")} value="?" />
            <StatusItem label={t("simulation.status.exams")} value="?" />
          </div>
        </section>
      </div>
    </>
  );
}

function StatusItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 p-3 rounded-lg bg-surface border border-border/50">
      <span className="text-[10px] uppercase tracking-widest text-muted font-bold">{label}</span>
      <span className="text-xl font-serif">{value}</span>
    </div>
  );
}

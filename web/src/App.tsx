import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom";
import { AppShell } from "@/components/layout/app-shell";
import { QueryProvider } from "@/components/layout/query-provider";
import { Toaster } from "@/components/ui/toaster";
import Landing from "@/routes/landing";
import Dashboard from "@/routes/dashboard";
import Courses from "@/routes/courses";
import CourseDetail from "@/routes/course-detail";
import Tasks from "@/routes/tasks";
import Deliverables from "@/routes/deliverables";
import Exams from "@/routes/exams";
import Files from "@/routes/files";
import Activity from "@/routes/activity";
import Settings from "@/routes/settings";
import Login from "@/routes/login";

// Marketing landing is only for the hosted openstudy.dev deploy. Self-hosters
// leave VITE_SHOW_LANDING unset/false so `/` jumps straight to the app, same
// pattern Cal.com / n8n / Plausible / Ghost / Sentry use.
const SHOW_LANDING = import.meta.env.VITE_SHOW_LANDING === "true";

const router = createBrowserRouter([
  {
    path: "/",
    element: SHOW_LANDING ? <Landing /> : <Navigate to="/app" replace />,
  },
  { path: "/login", element: <Login /> },
  {
    path: "/app",
    element: <AppShell />,
    children: [
      { index: true, element: <Dashboard /> },
      { path: "courses", element: <Courses /> },
      { path: "courses/:code", element: <CourseDetail /> },
      { path: "tasks", element: <Tasks /> },
      { path: "deliverables", element: <Deliverables /> },
      { path: "exams", element: <Exams /> },
      { path: "files", element: <Files /> },
      { path: "activity", element: <Activity /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);

export default function App() {
  return (
    <QueryProvider>
      <RouterProvider router={router} />
      <Toaster />
    </QueryProvider>
  );
}

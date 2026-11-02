"use client";

import { useSyncExternalStore } from "react";
import {
  CalendarIcon,
  ChartIcon,
  EditIcon,
  SearchIcon,
  UserPlusIcon,
  UsersIcon,
} from "./icons";

export type QuickAction = {
  title: string;
  description: string;
  prompt: string;
  /** "send" asks right away; "fill" puts a template in the box for you to finish. */
  mode: "send" | "fill";
  icon: React.ReactNode;
};

export const QUICK_ACTIONS: QuickAction[] = [
  {
    title: "Workforce overview",
    description: "Headcount, payroll and teams at a glance",
    prompt: "Give me a quick overview of the workforce: total headcount, payroll and headcount per department.",
    mode: "send",
    icon: <ChartIcon />,
  },
  {
    title: "Recent joiners",
    description: "Who started in the last 90 days",
    prompt: "Who joined the company in the last 90 days?",
    mode: "send",
    icon: <CalendarIcon />,
  },
  {
    title: "View a team",
    description: "List everyone in a department",
    prompt: "Show me everyone in the Engineering department.",
    mode: "fill",
    icon: <UsersIcon />,
  },
  {
    title: "Find an employee",
    description: "Look someone up by name or email",
    prompt: "Find the employee named ",
    mode: "fill",
    icon: <SearchIcon />,
  },
  {
    title: "Add a new hire",
    description: "Create an employee record",
    prompt:
      "Add a new employee: name …, email …, job …, department …, salary …, start date ….",
    mode: "fill",
    icon: <UserPlusIcon />,
  },
  {
    title: "Update a record",
    description: "Change salary, role or department",
    prompt: "Change the salary of employee # to ",
    mode: "fill",
    icon: <EditIcon />,
  },
];

function greetingFor(hour: number) {
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

/** Updates once a minute (not every second) so the rest of the page doesn't re-render. */
let minuteSnapshot: Date | null = null;

function subscribeMinute(onChange: () => void) {
  const id = setInterval(() => {
    minuteSnapshot = new Date();
    onChange();
  }, 60_000);
  return () => clearInterval(id);
}

function getMinuteSnapshot() {
  const now = new Date();
  if (!minuteSnapshot || now.getMinutes() !== minuteSnapshot.getMinutes()) minuteSnapshot = now;
  return minuteSnapshot;
}

function useMinuteClock(): Date | null {
  // The server renders without a time (null) so the HTML matches on load.
  return useSyncExternalStore(subscribeMinute, getMinuteSnapshot, () => null);
}

export default function Welcome({ onAction }: { onAction: (action: QuickAction) => void }) {
  const now = useMinuteClock();

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-10 pt-10 sm:pt-16">
      <p className="text-sm font-medium text-indigo-600">
        {now
          ? now.toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" })
          : " "}
      </p>
      <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
        {now ? greetingFor(now.getHours()) : "Hello"}, HR Manager.
      </h1>
      <p className="mt-2 text-base text-slate-500">
        Ask about your people in plain English. I can look up teams, find employees, and add or
        update records — I&apos;ll always ask before changing anything.
      </p>

      <div className="mt-8 grid grid-cols-2 gap-3 lg:grid-cols-3">
        {QUICK_ACTIONS.map((action) => (
          <button
            key={action.title}
            onClick={() => onAction(action)}
            className="group flex flex-col items-start rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-md"
          >
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white">
              {action.icon}
            </span>
            <span className="mt-3 text-sm font-semibold text-slate-900">{action.title}</span>
            <span className="mt-0.5 text-xs text-slate-500">{action.description}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

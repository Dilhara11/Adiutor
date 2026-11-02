"use client";

import { formatDate, formatMoney, type WorkforceSummary } from "../lib/api";
import {
  BuildingIcon,
  CloseIcon,
  PlusIcon,
  RefreshIcon,
  UsersIcon,
  WalletIcon,
} from "./icons";

type SidebarProps = {
  summary: WorkforceSummary | null;
  summaryError: string | null;
  isRefreshing: boolean;
  onRefresh: () => void;
  onNewChat: () => void;
  onAsk: (prompt: string) => void;
  open: boolean;
  onClose: () => void;
};

function Stat({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2.5">
      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
        {icon}
      </span>
      <div className="min-w-0">
        <p className="text-xs text-slate-500">{label}</p>
        <p className="truncate text-base font-semibold text-slate-900">{value}</p>
      </div>
    </div>
  );
}

export default function Sidebar({
  summary,
  summaryError,
  isRefreshing,
  onRefresh,
  onNewChat,
  onAsk,
  open,
  onClose,
}: SidebarProps) {
  const maxHeadcount = Math.max(1, ...(summary?.departments.map((d) => d.headcount) ?? [1]));

  return (
    <>
      {open ? (
        <button
          className="fixed inset-0 z-30 bg-slate-900/30 lg:hidden"
          aria-label="Close sidebar"
          onClick={onClose}
        />
      ) : null}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-80 flex-col border-r border-slate-200 bg-slate-50 transition-transform lg:static lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-5 pb-4 pt-5">
          <div className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 text-sm font-bold text-white">
              A
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-900">Adiutor</p>
              <p className="text-xs text-slate-500">HR Assistant</p>
            </div>
          </div>
          <button
            className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-200 lg:hidden"
            onClick={onClose}
            aria-label="Close sidebar"
          >
            <CloseIcon />
          </button>
        </div>

        <div className="px-5">
          <button
            onClick={onNewChat}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-indigo-700"
          >
            <PlusIcon /> New conversation
          </button>
        </div>

        <div className="mt-6 flex-1 space-y-6 overflow-y-auto px-5 pb-6">
          <section>
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Workforce overview
              </h2>
              <button
                onClick={onRefresh}
                className="rounded-md p-1 text-slate-400 hover:bg-slate-200 hover:text-slate-600"
                aria-label="Refresh overview"
                title="Refresh"
              >
                <RefreshIcon className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              </button>
            </div>

            {summaryError ? (
              <p className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5 text-xs text-amber-800">
                {summaryError}
              </p>
            ) : (
              <div className="space-y-2">
                <Stat
                  icon={<UsersIcon />}
                  label="Employees"
                  value={summary ? String(summary.total_employees) : "…"}
                />
                <Stat
                  icon={<BuildingIcon />}
                  label="Departments"
                  value={summary ? String(summary.department_count) : "…"}
                />
                <Stat
                  icon={<WalletIcon />}
                  label="Average salary"
                  value={summary ? formatMoney(summary.average_salary) : "…"}
                />
              </div>
            )}
          </section>

          {summary && summary.departments.length > 0 ? (
            <section>
              <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Headcount by department
              </h2>
              <ul className="space-y-1">
                {summary.departments.map((dept) => (
                  <li key={dept.department_id}>
                    <button
                      onClick={() =>
                        onAsk(`Show me everyone in the ${dept.department_name} department.`)
                      }
                      className="group w-full rounded-lg px-2 py-1.5 text-left hover:bg-white"
                      title={`Ask about ${dept.department_name}`}
                    >
                      <div className="flex items-center justify-between text-sm">
                        <span className="truncate text-slate-700 group-hover:text-indigo-700">
                          {dept.department_name}
                        </span>
                        <span className="ml-2 font-medium tabular-nums text-slate-900">
                          {dept.headcount}
                        </span>
                      </div>
                      <div className="mt-1 h-1.5 rounded-full bg-slate-200">
                        <div
                          className="h-1.5 rounded-full bg-indigo-500"
                          style={{ width: `${(dept.headcount / maxHeadcount) * 100}%` }}
                        />
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          {summary && summary.recent_hires.length > 0 ? (
            <section>
              <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Recent hires
              </h2>
              <ul className="space-y-1">
                {summary.recent_hires.map((person) => {
                  const name = [person.first_name, person.last_name].filter(Boolean).join(" ");
                  const initials = name
                    .split(" ")
                    .map((part) => part[0])
                    .join("")
                    .slice(0, 2)
                    .toUpperCase();
                  return (
                    <li key={person.employee_id}>
                      <button
                        onClick={() =>
                          onAsk(`Show me the full details for ${name} (employee #${person.employee_id}).`)
                        }
                        className="flex w-full items-center gap-3 rounded-lg px-2 py-1.5 text-left hover:bg-white"
                      >
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-xs font-semibold text-slate-700">
                          {initials || "?"}
                        </span>
                        <span className="min-w-0">
                          <span className="block truncate text-sm text-slate-800">{name || "Unnamed"}</span>
                          <span className="block truncate text-xs text-slate-500">
                            {person.job_title ?? person.job_id} · {formatDate(person.hire_date)}
                          </span>
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          ) : null}
        </div>
      </aside>
    </>
  );
}

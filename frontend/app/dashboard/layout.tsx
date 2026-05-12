import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Events" },
  { href: "/dashboard/hotels", label: "Hotels" },
  { href: "/dashboard/reports", label: "Reports" },
  { href: "/dashboard/upload", label: "Upload" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#0a0a0a] flex">
      {/* Sidebar */}
      <aside className="w-56 border-r border-[#1a1a1a] flex flex-col py-6 px-4 shrink-0">
        <div className="mb-8 px-2">
          <div className="text-lg font-bold text-[#f5f5f5] tracking-tight">3atef</div>
          <div className="text-xs text-[#555] mt-0.5">Event Intelligence</div>
        </div>
        <nav className="space-y-1 flex-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block px-3 py-2 rounded-md text-sm text-[#888] hover:text-[#f5f5f5] hover:bg-[#111] transition-colors"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="px-2 text-xs text-[#333] border-t border-[#1a1a1a] pt-4">
          v1.0.0
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}

interface ApprovalStatusProps {
  status: "approved" | "rejected" | "pending";
  size?: "sm" | "md" | "lg";
}

const config = {
  approved: { label: "Approved", bg: "bg-green-500/10", text: "text-green-400", dot: "bg-green-400" },
  rejected: { label: "Rejected", bg: "bg-red-500/10", text: "text-red-400", dot: "bg-red-400" },
  pending:  { label: "Pending",  bg: "bg-yellow-500/10", text: "text-yellow-400", dot: "bg-yellow-400" },
};

const sizeClass = { sm: "text-xs px-2 py-0.5", md: "text-sm px-3 py-1", lg: "text-base px-4 py-1.5" };

export default function ApprovalStatus({ status, size = "md" }: ApprovalStatusProps) {
  const c = config[status] ?? config.pending;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${c.bg} ${c.text} ${sizeClass[size]}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {c.label}
    </span>
  );
}

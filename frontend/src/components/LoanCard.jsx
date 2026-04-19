import ResultCard from "./ResultCard";

function formatINR(value = 0) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function LoanCard({ loan }) {
  if (!loan) {
    return null;
  }

  const decisionMap = {
    approve: "bg-emerald-100 text-emerald-700",
    approve_with_limit: "bg-amber-100 text-amber-700",
    manual_review: "bg-red-100 text-red-700",
  };

  return (
    <ResultCard title="Loan Recommendation" className="border-blue-100">
      <div className="space-y-4">
        <div>
          <span className="text-xs font-medium uppercase text-gray-500">Decision</span>
          <div className="mt-2">
            <span className={`rounded-full px-3 py-1 text-sm font-semibold ${decisionMap[loan.decision] || "bg-gray-100 text-gray-700"}`}>
              {loan.decision?.replaceAll("_", " ")}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="rounded-xl bg-gray-50 p-3">
            <p className="text-xs uppercase text-gray-500">Recommended loan</p>
            <p className="mt-1 text-lg font-bold text-gray-900">{formatINR(loan.recommended_loan_amount)}</p>
          </div>
          <div className="rounded-xl bg-gray-50 p-3">
            <p className="text-xs uppercase text-gray-500">Max EMI</p>
            <p className="mt-1 text-lg font-bold text-gray-900">{formatINR(loan.max_emi)}</p>
          </div>
        </div>
      </div>
    </ResultCard>
  );
}

export default LoanCard;

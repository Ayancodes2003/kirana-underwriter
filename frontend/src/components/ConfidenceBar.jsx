function ConfidenceBar({ confidence = 0 }) {
  const percentage = Math.max(0, Math.min(100, Math.round(confidence * 100)));

  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-sm text-gray-600">
        <span>Model confidence</span>
        <span className="font-semibold text-gray-800">{percentage}%</span>
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-100">
        <div
          className="h-full rounded-full bg-blue-600 transition-all duration-700"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default ConfidenceBar;

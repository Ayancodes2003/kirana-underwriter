import ResultCard from "./ResultCard";

function BenchmarkCard({ benchmark }) {
  if (!benchmark) {
    return null;
  }

  const peerPercentile = Math.max(0, Math.min(100, benchmark.peer_percentile || 0));

  return (
    <ResultCard title="Peer Benchmark">
      <div className="space-y-3">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-xs uppercase text-gray-500">Peer bucket</p>
            <p className="text-lg font-semibold text-gray-900">{benchmark.peer_bucket}</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">{peerPercentile}%</p>
        </div>
        <div className="h-3 w-full overflow-hidden rounded-full bg-gray-100">
          <div className="h-full rounded-full bg-gray-900 transition-all duration-700" style={{ width: `${peerPercentile}%` }} />
        </div>
      </div>
    </ResultCard>
  );
}

export default BenchmarkCard;

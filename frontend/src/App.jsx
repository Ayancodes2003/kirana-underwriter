import { motion } from "framer-motion";
import axios from "axios";
import { useMemo, useState } from "react";
import BenchmarkCard from "./components/BenchmarkCard";
import ConfidenceBar from "./components/ConfidenceBar";
import LoanCard from "./components/LoanCard";
import ResultCard from "./components/ResultCard";
import UploadForm from "./components/UploadForm";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

function formatINR(value = 0) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const riskTagClass = useMemo(
    () => ({
      low_visibility: "bg-amber-100 text-amber-700",
      inventory_footfall_mismatch: "bg-red-100 text-red-700",
      inventory_competition_mismatch: "bg-red-100 text-red-700",
      over_optimized_shelf: "bg-red-100 text-red-700",
    }),
    []
  );

  const handleSubmit = async ({ images, latitude, longitude }) => {
    setLoading(true);
    setError("");

    const formData = new FormData();
    images.forEach((file) => formData.append("images", file));
    formData.append("latitude", latitude);
    formData.append("longitude", longitude);

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze-store`, formData);
      setResult(response.data);
    } catch (requestError) {
      const apiMessage = requestError?.response?.data?.detail;
      setError(apiMessage || "Unable to analyze this store right now. Please try again.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const listItemVariants = {
    hidden: { opacity: 0, y: 8 },
    visible: (index) => ({
      opacity: 1,
      y: 0,
      transition: { delay: 0.06 * index, duration: 0.35 },
    }),
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="min-h-screen bg-white"
    >
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Kirana Underwriting Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">AI-powered underwriting for unorganized retail</p>
        </header>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <section className="fintech-panel p-6 lg:col-span-4">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Store Input</h2>
            <UploadForm onSubmit={handleSubmit} loading={loading} />
            {error ? <p className="mt-4 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
          </section>

          <section className="space-y-4 lg:col-span-8">
            <div className="fintech-panel p-6">
              <h2 className="text-lg font-semibold text-gray-900">Analysis Results</h2>
              <p className="mt-1 text-sm text-gray-600">Risk-aware underwriting output with benchmark and loan recommendation.</p>
            </div>

            {loading ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="fintech-panel flex min-h-64 flex-col items-center justify-center gap-4 p-10"
              >
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
                <p className="text-sm text-gray-600">Running underwriting pipeline...</p>
              </motion.div>
            ) : null}

            {!loading && result ? (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35 }}
                className="space-y-4"
              >
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  <ResultCard title="Sales Estimation">
                    <div className="space-y-3">
                      <div>
                        <p className="text-xs uppercase text-gray-500">Daily sales range</p>
                        <p className="mt-1 text-lg font-bold text-gray-900">
                          {formatINR(result.daily_sales_range?.[0])} - {formatINR(result.daily_sales_range?.[1])}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs uppercase text-gray-500">Monthly revenue range</p>
                        <p className="mt-1 text-lg font-bold text-gray-900">
                          {formatINR(result.monthly_revenue_range?.[0])} - {formatINR(result.monthly_revenue_range?.[1])}
                        </p>
                      </div>
                    </div>
                  </ResultCard>

                  <ResultCard title="Confidence">
                    <ConfidenceBar confidence={result.confidence_score} />
                  </ResultCard>

                  <ResultCard title="Risk Flags">
                    <div className="flex flex-wrap gap-2">
                      {(result.risk_flags || []).length === 0 ? (
                        <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">No major flags</span>
                      ) : (
                        result.risk_flags.map((flag) => (
                          <span
                            key={flag}
                            className={`rounded-full px-3 py-1 text-sm font-medium ${riskTagClass[flag] || "bg-gray-100 text-gray-700"}`}
                          >
                            {flag.replaceAll("_", " ")}
                          </span>
                        ))
                      )}
                    </div>
                  </ResultCard>

                  <ResultCard title="Geo + Feature Insights">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="rounded-xl bg-gray-50 p-3">
                        <p className="text-xs uppercase text-gray-500">Shelf density</p>
                        <p className="mt-1 font-semibold text-gray-900">{result.features?.shelf_density}</p>
                      </div>
                      <div className="rounded-xl bg-gray-50 p-3">
                        <p className="text-xs uppercase text-gray-500">SKU diversity</p>
                        <p className="mt-1 font-semibold text-gray-900">{result.features?.sku_diversity}</p>
                      </div>
                      <div className="rounded-xl bg-gray-50 p-3">
                        <p className="text-xs uppercase text-gray-500">POI density</p>
                        <p className="mt-1 font-semibold text-gray-900">{result.geo_features?.poi_density}</p>
                      </div>
                      <div className="rounded-xl bg-gray-50 p-3">
                        <p className="text-xs uppercase text-gray-500">Competition density</p>
                        <p className="mt-1 font-semibold text-gray-900">{result.geo_features?.competition_density}</p>
                      </div>
                      <div className="rounded-xl bg-gray-50 p-3 col-span-2">
                        <p className="text-xs uppercase text-gray-500">Footfall score</p>
                        <p className="mt-1 font-semibold text-gray-900">{result.geo_features?.footfall_score}</p>
                      </div>
                    </div>
                  </ResultCard>

                  <BenchmarkCard benchmark={result.benchmark} />
                  <LoanCard loan={result.loan_recommendation} />
                </div>

                <ResultCard title="Explanation">
                  <ul className="space-y-2 text-sm text-gray-700">
                    {(result.explanation || []).map((item, index) => (
                      <motion.li
                        key={`${item}-${index}`}
                        custom={index}
                        variants={listItemVariants}
                        initial="hidden"
                        animate="visible"
                        className="rounded-xl bg-gray-50 px-3 py-2"
                      >
                        • {item}
                      </motion.li>
                    ))}
                  </ul>
                </ResultCard>
              </motion.div>
            ) : null}
          </section>
        </div>
      </div>
    </motion.div>
  );
}

export default App;

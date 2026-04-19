import { motion } from "framer-motion";

function ResultCard({ title, children, className = "" }) {
  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 280, damping: 22 }}
      className={`fintech-panel p-5 ${className}`}
    >
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">{title}</h3>
      {children}
    </motion.div>
  );
}

export default ResultCard;

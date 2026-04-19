import { motion } from "framer-motion";
import { useState } from "react";

function UploadForm({ onSubmit, loading }) {
  const [images, setImages] = useState([]);
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);

  const validateAndSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (images.length < 3 || images.length > 5) {
      setError("Please upload between 3 and 5 images.");
      return;
    }

    if (latitude.trim() === "" || longitude.trim() === "") {
      setError("Latitude and longitude are required.");
      return;
    }

    await onSubmit({
      images,
      latitude,
      longitude,
    });
  };

  const handleFiles = (fileList) => {
    const selected = Array.from(fileList || []).filter((file) => file.type.startsWith("image/"));
    setImages(selected.slice(0, 5));
  };

  return (
    <form className="space-y-4" onSubmit={validateAndSubmit}>
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          handleFiles(event.dataTransfer.files);
        }}
        className={`rounded-2xl border-2 border-dashed p-6 text-center transition ${
          isDragging ? "border-blue-400 bg-blue-50" : "border-gray-300 bg-gray-50"
        }`}
      >
        <p className="text-sm font-medium text-gray-700">Drag and drop store images here</p>
        <p className="mt-1 text-xs text-gray-500">Upload 3-5 photos: shelf, counter, storefront</p>
        <input
          type="file"
          accept="image/*"
          multiple
          className="mt-3 block w-full cursor-pointer text-sm text-gray-600 file:mr-4 file:rounded-full file:border-0 file:bg-blue-600 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-blue-700"
          onChange={(event) => handleFiles(event.target.files)}
        />
        {images.length > 0 && (
          <p className="mt-2 text-xs font-medium text-gray-600">{images.length} image(s) selected</p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-xs font-semibold uppercase text-gray-500">Latitude</label>
          <input
            type="number"
            step="any"
            value={latitude}
            onChange={(event) => setLatitude(event.target.value)}
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-500"
            placeholder="19.0760"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-semibold uppercase text-gray-500">Longitude</label>
          <input
            type="number"
            step="any"
            value={longitude}
            onChange={(event) => setLongitude(event.target.value)}
            className="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none transition focus:border-blue-500"
            placeholder="72.8777"
          />
        </div>
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <motion.button
        type="submit"
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.98 }}
        disabled={loading}
        className="w-full rounded-2xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-black disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? "Analyzing..." : "Analyze Store"}
      </motion.button>
    </form>
  );
}

export default UploadForm;

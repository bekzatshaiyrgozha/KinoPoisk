import React, { useState } from 'react';
import { movieService } from '@/services';

type Props = {
  movieId: number;
  onUploaded?: () => void;
  isAdminHint?: boolean;
};

export const VideoUploadForm: React.FC<Props> = ({
  movieId,
  onUploaded,
  isAdminHint = true,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      await movieService.uploadVideo(movieId, file);
      if (onUploaded) {
        onUploaded();
      }
      setFile(null);
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.video?.[0] ||
        'Не удалось загрузить видео';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="space-y-2">
        <input
          type="file"
          accept="video/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm"
        />
        {isAdminHint && (
          <p className="text-xs text-gray-500">
            Только админ/стфф может загрузить видео — сервер проверит права.
          </p>
        )}
      </div>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button
        type="submit"
        disabled={loading || !file}
        className="px-4 py-2 bg-indigo-600 text-white rounded disabled:opacity-50"
      >
        {loading ? 'Загрузка...' : 'Загрузить видео'}
      </button>
    </form>
  );
};

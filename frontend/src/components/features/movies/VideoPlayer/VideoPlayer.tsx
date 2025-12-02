import React from 'react';

type Props = {
  src?: string | null;
  title: string;
};

export const VideoPlayer: React.FC<Props> = ({ src, title }) => {
  if (!src) {
    return (
      <div className="w-full bg-gray-100 rounded-lg p-6 text-center text-gray-500">
        Видео пока не загружено
      </div>
    );
  }

  return (
    <div className="w-full">
      <video
        key={src}
        controls
        className="w-full rounded-lg border border-gray-200"
      >
        <source src={src} />
        Ваш браузер не поддерживает видео.
      </video>
      <p className="mt-2 text-sm text-gray-600">{title}</p>
    </div>
  );
};

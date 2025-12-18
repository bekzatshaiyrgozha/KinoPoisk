import React from 'react';
import VideoPlayerComponent from '@/components/ui/video-player';

type Props = {
  src?: string | null;
  title: string;
  cover?: string;
};

export const VideoPlayer: React.FC<Props> = ({ src, title, cover }) => {
  return <VideoPlayerComponent src={src} title={title} cover={cover} />;
};

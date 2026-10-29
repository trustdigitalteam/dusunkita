import React from 'react';
import {Composition} from 'remotion';
import {EpisodeFromBrief} from './EpisodeFromBrief';
import {EP001} from './episodes';

const FPS = 30;
const SHOT_SEC = 5; // 15 detik = 3 shot × 5s

export const RemotionRoot: React.FC = () => (
  <Composition
    id="EP-001"
    component={EpisodeFromBrief}
    durationInFrames={EP001.shots.length * SHOT_SEC * FPS}
    fps={FPS}
    width={1080}
    height={1920}
    defaultProps={{...EP001, shotSec: SHOT_SEC}}
  />
);

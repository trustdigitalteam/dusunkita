import React, {useMemo} from 'react';
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  Img,
  staticFile,
  Audio,
  interpolate,
  Easing,
} from 'remotion';

// ============ SCHEMA ============
export type Shot = {
  title: string;
  lines: string[];
  zoom: boolean;      // zoom-in pelan
  fade: boolean;      // fade in/out di boundary
  bg: string;         // path screenshot (static file name)
};

export type EpisodeProps = {
  episode: number;
  shots: Shot[];
  bgm?: string;        // staticFile name for BGM
  palet: {
    bg: string;        // background (if no screenshot)
    text: string;
    accent: string;
    shadow: string;
  };
};

// schema sederhana (tanpa zod untuk hindari import tambahan)
export const dusunkitaSchema = undefined as any;

// ============ SHOT RENDERER ============
const SHOT_SEC = 6;

const Shot: React.FC<{shot: Shot; index: number; palet: EpisodeProps['palet']}> = ({shot, index, palet}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const shotFrames = SHOT_SEC * fps;
  const localFrame = frame - index * shotFrames;
  const progress = Math.min(localFrame / shotFrames, 1);

  // zoom-in (1.0 -> 1.12)
  const zoom = shot.zoom ? interpolate(progress, [0, 1], [1.0, 1.12], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  }) : 1.0;

  // fade in/out (0.4s = 12 frames @30fps)
  const fadeFrames = Math.round(0.4 * fps);
  let opacity = 1;
  if (shot.fade) {
    opacity = interpolate(localFrame,
      [0, fadeFrames, shotFrames - fadeFrames, shotFrames],
      [0, 1, 1, 0],
      {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  }

  // spring title
  const titleScale = interpolate(localFrame, [0, 12], [0.8, 1.0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.ease)});

  // line stagger: tiap line masuk 8 frame setelah line sebelumnya
  const lines = shot.lines.map((ln, i) => {
    const lineStart = 8 + i * 8;
    const lineOp = interpolate(localFrame, [lineStart, lineStart + 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const lineY = interpolate(localFrame, [lineStart, lineStart + 10], [10, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return {ln, op: lineOp, y: lineY, i};
  });

  return (
    <AbsoluteFill style={{opacity}}>
      {/* background: screenshot atau warna */}
      {shot.bg ? (
        <Img
          src={staticFile(shot.bg)}
          style={{
            width: `${zoom * 100}%`,
            height: `${zoom * 100}%`,
            objectFit: 'cover',
            objectPosition: 'center',
            position: 'absolute',
            left: '50%',
            top: '50%',
            transform: `translate(-50%,-50%)`,
          }}
        />
      ) : (
        <AbsoluteFill style={{background: palet.bg}} />
      )}

      {/* overlay text dengan drop shadow */}
      <AbsoluteFill
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 18,
        }}
      >
        {/* title shot */}
        <div style={{
          fontSize: 52,
          fontWeight: 900,
          color: palet.accent,
          textShadow: '0 4px 12px rgba(0,0,0,0.7)',
          transform: `scale(${titleScale})`,
          letterSpacing: 1,
        }}>
          {shot.title}
        </div>
        {/* body lines */}
        {lines.map(({ln, op, y, i}) => (
          <div key={i} style={{
            fontSize: i === 0 ? 40 : 36,
            fontWeight: 800,
            color: palet.text,
            textShadow: '0 3px 10px rgba(0,0,0,0.8)',
            opacity: op,
            transform: `translateY(${y}px)`,
          }}>
            {ln}
          </div>
        ))}
      </AbsoluteFill>

      {/* audio (BGM per shot) */}
      {shot.index === 0 ? null : null}
    </AbsoluteFill>
  );
};

// ============ MAIN COMPOSITION ============
export const DusunKita: React.FC<EpisodeProps> = (props) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const shotFrames = SHOT_SEC * fps;

  // hitung shot aktif
  const shotIdx = Math.min(Math.floor(frame / shotFrames), props.shots.length - 1);
  const activeShot = props.shots[shotIdx];

  // BGM (1 track penuh, fade out 1.5s)
  const bgmSrc = props.bgm ? staticFile(props.bgm) : null;

  const fadeIn = interpolate(frame, [0, 0.4 * fps], [0, 1], {extrapolateRight: 'clamp', extrapolateLeft: 'clamp'});

  return (
    <AbsoluteFill style={{background: props.palet.bg}}>
      {activeShot && <Shot shot={activeShot} index={shotIdx} palet={props.palet} />}

      {/* BGM */}
      {bgmSrc && <Audio src={bgmSrc} volume={0.6} />}
    </AbsoluteFill>
  );
};

import {EP001} from './episodes';
export {EP001};
export const EPISODES = [EP001];

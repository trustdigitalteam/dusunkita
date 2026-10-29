// src/EpisodeFromBrief.tsx — generic untuk semua episode. SHOT_SEC + voiceovers dari props.
import React from 'react';
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

type Shot = {
  title: string;
  lines: string[];
  zoom?: boolean;
  fade?: boolean;
  bg?: string;
  pan?: 'center' | 'top' | 'bottom' | 'left' | 'right';
};
type Palet = { bg: string; text: string; accent: string };
type Props = {
  shots: Shot[];
  bgm?: string;
  voiceovers?: string[]; // staticFile path per shot (MP3)
  palet: Palet;
  shotSec?: number; // default 5
};

const PAN: Record<Shot['pan'] | 'center', string> = {
  center: '50% 50%',
  top: '50% 25%',
  bottom: '50% 70%',
  left: '35% 50%',
  right: '65% 50%',
};

const ShotView: React.FC<{shot: Shot; index: number; palet: Palet; shotFrames: number}> = ({shot, index, palet, shotFrames}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const localFrame = frame - index * shotFrames;
  const progress = Math.min(localFrame / shotFrames, 1);

  const pan = shot.pan || 'center';
  const panPos = PAN[pan];
  const zStart = pan === 'center' ? 1.0 : 1.08;
  const zEnd = pan === 'center' ? 1.12 : 1.2;
  const zoom = shot.zoom ? interpolate(progress, [0, 1], [zStart, zEnd], {extrapolateRight: 'clamp', easing: Easing.out(Easing.quad)}) : 1.0;

  const fadeFrames = Math.round(0.4 * fps);
  let opacity = 1;
  if (shot.fade) {
    opacity = interpolate(localFrame,
      [0, fadeFrames, shotFrames - fadeFrames, shotFrames],
      [0, 1, 1, 0],
      {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  }

  const titleScale = interpolate(localFrame, [0, 14], [0.85, 1.0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.ease)});

  const lines = shot.lines.map((ln, i) => {
    const s = 8 + i * 7;
    const op = interpolate(localFrame, [s, s + 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    const y = interpolate(localFrame, [s, s + 10], [12, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    return {ln, op, y, i};
  });

  return (
    <AbsoluteFill style={{opacity}}>
      {shot.bg ? (
        <Img src={staticFile(shot.bg)} style={{
          position: 'absolute',
          left: '50%', top: '50%',
          width: `${zoom * 100}%`, height: `${zoom * 100}%`,
          transform: 'translate(-50%,-50%)',
          objectFit: 'cover',
          objectPosition: panPos,
        }} />
      ) : (
        <AbsoluteFill style={{background: palet.bg}} />
      )}

      {/* scrim gelap bawah biar text readable di atas peta */}
      <AbsoluteFill style={{
        background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.55) 18%, rgba(0,0,0,0.15) 40%, rgba(0,0,0,0) 55%)',
      }} />

      {/* text di lower third (aman reel) */}
      <AbsoluteFill style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end',
        gap: 14, paddingBottom: 340, padding: '0 60px 340px',
      }}>
        <div style={{
          fontSize: 76, fontWeight: 900, color: palet.accent,
          textShadow: '0 4px 18px rgba(0,0,0,0.9)',
          transform: `scale(${titleScale})`, letterSpacing: 1, textAlign: 'center',
          lineHeight: 1.05,
        }}>
          {shot.title}
        </div>
        {lines.map(({ln, op, y, i}) => (
          <div key={i} style={{
            fontSize: i === 0 ? 52 : 46, fontWeight: 800, color: palet.text,
            textShadow: '0 3px 12px rgba(0,0,0,0.95)', opacity: op,
            transform: `translateY(${y}px)`, textAlign: 'center', lineHeight: 1.35,
          }}>{ln}</div>
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const EpisodeFromBrief: React.FC<Props> = (props) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const shotSec = props.shotSec || 5;
  const shotFrames = shotSec * fps;
  const shotIdx = Math.min(Math.floor(frame / shotFrames), props.shots.length - 1);
  const active = props.shots[shotIdx];
  const bgmSrc = props.bgm ? staticFile(props.bgm) : null;
  const voSrc = props.voiceovers?.[shotIdx] ? staticFile(props.voiceovers![shotIdx]) : null;

  return (
    <AbsoluteFill style={{background: props.palet.bg}}>
      {active && <ShotView shot={active} index={shotIdx} palet={props.palet} shotFrames={shotFrames} />}
      {bgmSrc && (
        <Audio
          src={bgmSrc}
          volume={(f: number) =>
            f < 0.5 * fps ? f / (0.5 * fps) * 0.25 :
            f > durationInFrames - 1 * fps ? Math.max(0, (durationInFrames - 1 - f) / (1 * fps) * 0.25) :
            0.25
          }
        />
      )}
      {voSrc && (
        <Audio
          src={voSrc}
          volume={(f: number) => {
            const start = shotIdx * shotFrames;
            const end = (shotIdx + 1) * shotFrames;
            if (f < start || f >= end) return 0;
            const fadeIn = Math.round(0.3 * fps);
            const fadeOut = Math.round(0.3 * fps);
            if (f - start < fadeIn) return (f - start) / fadeIn;
            if (end - f < fadeOut) return (end - f) / fadeOut;
            return 1.0;
          }}
        />
      )}
    </AbsoluteFill>
  );
};

import {EpisodeProps} from './DusunKita';

// ============ EP-001 (15s = 3 shot × 5s) ============
export const EP001: EpisodeProps = {
  episode: 1,
  shots: [
    {
      title: 'DUSUN KITA DIBUKA 🏘️',
      lines: ['Hari ke-1 · 0 warga'],
      zoom: true,
      fade: true,
      pan: 'center',
      bg: 'screenshots/peta-hari1.png',
    },
    {
      title: 'Komen jadi warga:',
      lines: ['NAMA, BATA <warna>, TEMBOK <warna>', 'Gratis!'],
      zoom: true,
      fade: true,
      pan: 'left',
      bg: 'screenshots/peta-hari1.png',
    },
    {
      title: 'GOAL: BANGUN BALAI DUSUN',
      lines: ['Target: 100 Bata', '@DusunKita.id'],
      zoom: true,
      fade: true,
      pan: 'right',
      bg: 'screenshots/peta-hari1.png',
    },
  ],
  bgm: 'ambience.mp3',
  // voiceover per shot (opsional, di-mix di ffmpeg setelah Remotion)
  voiceovers: [
    'vo-EP-001-shot1.wav',
    'vo-EP-001-shot2.wav',
    'vo-EP-001-shot3.wav',
  ],
  palet: {
    bg: '#7A4A2C',
    text: '#FFFFFF',
    accent: '#F2C230',
    shadow: 'rgba(0,0,0,0.8)',
  },
};

// Template untuk episode baru (copy-paste, ubah episode num + shots)
export const EP_TEMPLATE: EpisodeProps = {
  episode: 1,
  shots: [
    {title: 'HOOK', lines: [], zoom: true, fade: true, pan: 'center', bg: ''},
    {title: 'ISI', lines: [], zoom: true, fade: true, pan: 'left', bg: ''},
    {title: 'CTA', lines: [], zoom: true, fade: true, pan: 'right', bg: ''},
  ],
  bgm: 'ambience.mp3',
  voiceovers: [],
  palet: {bg: '#7A4A2C', text: '#FFFFFF', accent: '#F2C230', shadow: 'rgba(0,0,0,0.8)'},
};

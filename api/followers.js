// Jumlah follower @dusunkita.id via Facebook Graph API.
// Token = page access token (EAARL...) dari app TrustD Automation.
// Disimpan aman di Vercel (Environment Variable IG_TOKEN).
const FB = 'https://graph.facebook.com/v21.0/';
const IG_PAGE_ID = '1446452998543954'; // FB Page "Dusun Kita Virtual"

export default async function handler(req, res) {
  const token = String(process.env.IG_TOKEN || '').trim().replace(/^["']|["']$/g, '');
  if (!token) return res.status(500).json({ error: 'IG_TOKEN belum diatur' });
  try {
    // cari IG business account dari page
    const pr = await fetch(FB + IG_PAGE_ID + '?fields=instagram_business_account{id,username,followers_count}&access_token=' + encodeURIComponent(token));
    const pj = await pr.json();
    if (!pr.ok || pj.error) return res.status(502).json({ error: (pj.error && pj.error.message) || 'Gagal' });
    const ig = pj.instagram_business_account;
    if (!ig) return res.status(404).json({ error: 'IG business account tidak ditemukan' });
    res.setHeader('Cache-Control', 's-maxage=600, stale-while-revalidate=3600');
    return res.status(200).json({
      followers: ig.followers_count,
      username: ig.username,
      at: new Date().toISOString(),
    });
  } catch (e) {
    return res.status(502).json({ error: 'Graph API tidak bisa dihubungi' });
  }
}

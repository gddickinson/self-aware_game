// Subtle falling-code background (a nod to the game's Matrix mode); off under prefers-reduced-motion.
export function rain(cv) {
  if (!cv || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const ctx = cv.getContext('2d'), chars = '01ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  let cols = [];
  const size = () => {
    cv.width = innerWidth; cv.height = innerHeight;
    cols = Array.from({ length: Math.ceil(cv.width / 28) }, () => Math.random() * cv.height);
  };
  size(); addEventListener('resize', size);
  let last = 0;
  const tick = t => {
    if (t - last > 90) {
      last = t;
      ctx.fillStyle = 'rgba(5,6,12,.18)'; ctx.fillRect(0, 0, cv.width, cv.height);
      ctx.fillStyle = 'rgba(80,255,140,.3)'; ctx.font = '14px monospace';
      cols.forEach((y, i) => {
        ctx.fillText(chars[(Math.random() * chars.length) | 0], i * 28, y);
        cols[i] = y > cv.height + Math.random() * 4000 ? 0 : y + 18;
      });
    }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

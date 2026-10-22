/* ============================================================
   Procedural, endlessly-looping "flow" background.
   White field, single-color floating effect (CFAC66), with only
   opacity/shade variation for depth — no other hues in the motion.
   ============================================================ */

const canvas = document.getElementById('bgCanvas');
const ctx = canvas.getContext('2d');

let W, H, DPR;

function resize() {
  DPR = Math.min(window.devicePixelRatio || 1, 2);

  W = canvas.clientWidth;
  H = canvas.clientHeight;

  canvas.width = W * DPR;
  canvas.height = H * DPR;

  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}

window.addEventListener('resize', resize);
resize();

const COLORS = {
  base: '#FFFFFF',
  baseDeep: '#FBF9F5',
  primary: '#CFAC66',
  primaryLight: '#E3C983',
  primaryDeep: '#B08F4E'
};

function hexA(hex, a) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);

  return `rgba(${r},${g},${b},${a})`;
}

/* ---- flowing ribbon strands ---------------------------------- */

class Strand {
  constructor(seed) {
    this.seed = seed;
    this.yBase = 0.35 + seed * 0.13 + Math.random() * 0.06;
    this.amp = 0.05 + Math.random() * 0.06;
    this.freq = 0.8 + Math.random() * 0.7;
    this.speed = 0.06 + Math.random() * 0.05;
    this.phase = Math.random() * Math.PI * 2;
    this.width = 1.4 + Math.random() * 2.2;

    this.colorSet = [
      COLORS.primaryDeep,
      COLORS.primary,
      COLORS.primaryLight
    ][seed % 3];

    this.opacity = 0.22 + Math.random() * 0.28;
  }

  draw(t) {
    const points = [];
    const steps = 60;

    for (let i = 0; i <= steps; i++) {
      const nx = i / steps;
      const x = nx * W * 1.15 - W * 0.075;

      const wobble =
        Math.sin(
          nx * Math.PI * this.freq +
          t * this.speed +
          this.phase
        ) *
        this.amp +
        Math.sin(
          nx * Math.PI * this.freq * 2.3 +
          t * this.speed * 1.6 +
          this.phase
        ) *
        this.amp *
        0.35;

      const y = (this.yBase + wobble) * H;

      points.push([x, y]);
    }

    ctx.beginPath();

    ctx.moveTo(
      points[0][0],
      points[0][1]
    );

    for (let i = 1; i < points.length - 2; i++) {
      const xc =
        (points[i][0] + points[i + 1][0]) / 2;

      const yc =
        (points[i][1] + points[i + 1][1]) / 2;

      ctx.quadraticCurveTo(
        points[i][0],
        points[i][1],
        xc,
        yc
      );
    }

    const grad = ctx.createLinearGradient(
      0,
      0,
      W,
      0
    );

    grad.addColorStop(
      0,
      hexA(this.colorSet, 0)
    );

    grad.addColorStop(
      0.25,
      hexA(this.colorSet, this.opacity)
    );

    grad.addColorStop(
      0.65,
      hexA(
        COLORS.primaryLight,
        this.opacity * 1.1
      )
    );

    grad.addColorStop(
      1,
      hexA(this.colorSet, 0)
    );

    ctx.strokeStyle = grad;
    ctx.lineWidth = this.width;

    ctx.shadowColor =
      hexA(this.colorSet, 0.55);

    ctx.shadowBlur = 8;

    ctx.stroke();

    ctx.shadowBlur = 0;

    return points;
  }
}

const strands = [];

for (let i = 0; i < 9; i++) {
  strands.push(new Strand(i));
}

/* ---- drifting particles along the flow field ------------------ */

class Particle {
  constructor() {
    this.reset(true);
  }

  reset(initial) {
    this.x = initial
      ? Math.random() * W
      : -20;

    this.yBase =
      0.3 + Math.random() * 0.5;

    this.speed =
      12 + Math.random() * 22;

    this.r =
      0.6 + Math.random() * 1.8;

    this.amp =
      20 + Math.random() * 40;

    this.freq =
      0.6 + Math.random() * 1.2;

    this.phase =
      Math.random() * Math.PI * 2;

    this.color =
      Math.random() < 0.5
        ? COLORS.primary
        : (
            Math.random() < 0.5
              ? COLORS.primaryLight
              : COLORS.primaryDeep
          );

    this.opacity =
      0.3 + Math.random() * 0.45;
  }

  update(dt, t) {
    this.x += this.speed * dt;

    if (this.x > W + 20) {
      this.reset(false);
    }

    this.y =
      this.yBase * H +
      Math.sin(
        t * this.freq + this.phase
      ) *
      this.amp;
  }

  draw() {
    ctx.beginPath();

    ctx.fillStyle =
      hexA(this.color, this.opacity);

    ctx.shadowColor =
      hexA(this.color, 0.8);

    ctx.shadowBlur = 6;

    ctx.arc(
      this.x,
      this.y,
      this.r,
      0,
      Math.PI * 2
    );

    ctx.fill();

    ctx.shadowBlur = 0;
  }
}

const particles = [];

for (let i = 0; i < 70; i++) {
  particles.push(new Particle());
}

/* ---- render loop --------------------------------------------- */

let last = performance.now();

function frame(now) {
  const dt = Math.min(
    (now - last) / 1000,
    0.05
  );

  last = now;

  const t = now / 1000;

  ctx.fillStyle = COLORS.base;
  ctx.fillRect(0, 0, W, H);

  strands.forEach((s) => {
    s.draw(t);
  });

  particles.forEach((p) => {
    p.update(dt, t);
    p.draw();
  });

  const floor = ctx.createLinearGradient(
    0,
    H * 0.72,
    0,
    H
  );

  floor.addColorStop(
    0,
    hexA(COLORS.primaryDeep, 0)
  );

  floor.addColorStop(
    1,
    hexA(COLORS.primaryDeep, 0.045)
  );

  ctx.fillStyle = floor;

  ctx.fillRect(
    0,
    H * 0.72,
    W,
    H * 0.28
  );

  requestAnimationFrame(frame);
}

requestAnimationFrame(frame);

/* ============================================================
   Mobile drawer / hamburger menu
   ============================================================ */

(function () {

  const toggle =
    document.querySelector('.menu_toggle');

  const drawer =
    document.getElementById('mobileDrawer');

  const overlay =
    document.getElementById('drawerOverlay');

  const closeBtn =
    document.getElementById('drawerClose');

  if (
    !toggle ||
    !drawer ||
    !overlay ||
    !closeBtn
  ) {
    return;
  }

  const drawerLinks =
    drawer.querySelectorAll('a');

  let isOpen = false;

  function open() {

    if (isOpen) return;

    isOpen = true;

    drawer.classList.add('is_open');

    overlay.classList.add('is_open');

    toggle.classList.add('is_active');

    toggle.setAttribute(
      'aria-expanded',
      'true'
    );

    toggle.setAttribute(
      'aria-label',
      'Close menu'
    );

    document.body.classList.add(
      'no_scroll'
    );
  }

  function close() {

    if (!isOpen) return;

    isOpen = false;

    drawer.classList.remove(
      'is_open'
    );

    overlay.classList.remove(
      'is_open'
    );

    toggle.classList.remove(
      'is_active'
    );

    toggle.setAttribute(
      'aria-expanded',
      'false'
    );

    toggle.setAttribute(
      'aria-label',
      'Open menu'
    );

    document.body.classList.remove(
      'no_scroll'
    );
  }

  toggle.addEventListener(
    'click',
    () => {
      isOpen ? close() : open();
    }
  );

  overlay.addEventListener(
    'click',
    close
  );

  closeBtn.addEventListener(
    'click',
    close
  );

  // close drawer when any link inside it is clicked
  drawerLinks.forEach((a) => {
    a.addEventListener(
      'click',
      close
    );
  });

  // ESC closes the drawer
  document.addEventListener(
    'keydown',
    (e) => {

      if (
        e.key === 'Escape' &&
        isOpen
      ) {
        close();
      }

    }
  );

  // close drawer automatically if user resizes back to desktop
  window.addEventListener(
    'resize',
    () => {

      if (
        window.innerWidth > 980 &&
        isOpen
      ) {
        close();
      }

    }
  );

})();
/* Stage 4A — Editor's Choice carousel */

document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('[data-choice-carousel]').forEach(function (carousel) {

        const slides = Array.from(
            carousel.querySelectorAll('[data-choice-slide]')
        );

        if (!slides.length) {
            return;
        }

        const section = carousel.closest('.choice');

        const prev = section.querySelector('[data-choice-prev]');
        const next = section.querySelector('[data-choice-next]');
        const position = section.querySelector('[data-choice-position]');

        let index = 0;

        function showSlide(newIndex) {

            index = (newIndex + slides.length) % slides.length;

            slides.forEach(function (slide, i) {

                const active = i === index;

                slide.classList.toggle('is_active', active);

                slide.setAttribute(
                    'aria-hidden',
                    active ? 'false' : 'true'
                );

                slide.style.display = active
                    ? 'block'
                    : 'none';
            });

            if (position) {
                position.textContent =
                    (index + 1) + ' / ' + slides.length;
            }
        }

        if (prev) {
            prev.addEventListener('click', function () {
                showSlide(index - 1);
            });
        }

        if (next) {
            next.addEventListener('click', function () {
                showSlide(index + 1);
            });
        }

        showSlide(0);
    });

});

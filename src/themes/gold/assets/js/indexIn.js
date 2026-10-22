document.addEventListener("DOMContentLoaded", function () {

  const marquee = document.querySelector(".marquee");
  const track = marquee?.querySelector(".mq-track");

  if (!marquee || !track) return;

  /* =========================================
     DUPLICATE ITEMS
  ========================================= */

  const originalItems = Array.from(track.children);

  // فقط یک بار آیتم‌ها را کپی می‌کنیم
  originalItems.forEach(function (item) {
    const clone = item.cloneNode(true);
    clone.setAttribute("aria-hidden", "true");
    track.appendChild(clone);
  });

  /* =========================================
     VARIABLES
  ========================================= */

  let position = 0;
  let cycleWidth = 0;
  let paused = false;

  // سرعت حرکت - پیکسل در ثانیه
  const speed = 45;

  /* =========================================
     CALCULATE REAL WIDTH
  ========================================= */

  function calculateCycleWidth() {

    if (!originalItems.length) return;

    let width = 0;

    originalItems.forEach(function (item) {
      width += item.getBoundingClientRect().width;
    });

    // مقدار gap بین آیتم‌ها
    const styles = window.getComputedStyle(track);
    const gap =
      parseFloat(styles.columnGap) ||
      parseFloat(styles.gap) ||
      0;

    width += gap * originalItems.length;

    cycleWidth = width;
  }

  /* =========================================
     WAIT FOR IMAGES
  ========================================= */

  const images = track.querySelectorAll("img");

  let loaded = 0;

  function startWhenReady() {

    calculateCycleWidth();

    if (cycleWidth <= 0) {
      setTimeout(startWhenReady, 50);
      return;
    }

    requestAnimationFrame(animate);
  }

  if (images.length === 0) {

    startWhenReady();

  } else {

    images.forEach(function (img) {

      if (img.complete) {

        loaded++;

        if (loaded === images.length) {
          startWhenReady();
        }

      } else {

        img.addEventListener("load", function () {

          loaded++;

          if (loaded === images.length) {
            startWhenReady();
          }

        }, { once: true });

        img.addEventListener("error", function () {

          loaded++;

          if (loaded === images.length) {
            startWhenReady();
          }

        }, { once: true });

      }

    });

  }

  /* =========================================
     RESIZE
  ========================================= */

  let resizeTimer;

  window.addEventListener("resize", function () {

    clearTimeout(resizeTimer);

    resizeTimer = setTimeout(function () {

      calculateCycleWidth();

      // جلوگیری از به‌هم‌ریختن موقعیت
      if (cycleWidth > 0) {
        position = position % cycleWidth;
      }

    }, 100);

  });

  /* =========================================
     HOVER PAUSE
  ========================================= */

  marquee.addEventListener("mouseenter", function () {
    paused = true;
  });

  marquee.addEventListener("mouseleave", function () {
    paused = false;
  });

  /* =========================================
     ANIMATION
  ========================================= */

  let lastTime = performance.now();

  function animate(currentTime) {

    const deltaTime = currentTime - lastTime;
    lastTime = currentTime;

    if (!paused && cycleWidth > 0) {

      // حرکت بر اساس زمان واقعی
      position -= speed * (deltaTime / 1000);

      // حلقه بی‌نهایت
      if (Math.abs(position) >= cycleWidth) {
        position += cycleWidth;
      }

      track.style.transform =
        `translate3d(${position}px, 0, 0)`;
    }

    requestAnimationFrame(animate);
  }

});

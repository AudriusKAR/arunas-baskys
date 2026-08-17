/* ============================================================
   Bendri puslapio skriptai: mobilus meniu, galerijos lightbox
   ============================================================ */
(function () {
  /* --- mobilus meniu --- */
  var toggle = document.querySelector('.nav-toggle');
  var panel = document.querySelector('.nav-mobile');
  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      var open = panel.classList.toggle('open');
      toggle.querySelector('.ms').textContent = open ? 'close' : 'menu';
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* --- sutraukti atsiliepimų paveikslai (telefone) --- */
  [].forEach.call(document.querySelectorAll('.clip-btn'), function (btn) {
    btn.addEventListener('click', function () {
      var open = btn.closest('.clip').classList.toggle('open');
      btn.innerHTML = open
        ? 'Suskleisti <span class="ms ms-sm">expand_less</span>'
        : 'Rodyti visą atsiliepimą <span class="ms ms-sm">expand_more</span>';
    });
  });

  /* --- galerijų lightbox (bendras visoms .gal) --- */
  var gals = [].slice.call(document.querySelectorAll('.gal'));
  var lb = document.getElementById('lb');
  if (!gals.length || !lb) return;

  var lbImg = lb.querySelector('img');
  var imgs = [].slice.call(document.querySelectorAll('.gal img'));
  var idx = 0;

  function show(i) {
    idx = (i + imgs.length) % imgs.length;
    lbImg.src = imgs[idx].src;
    lbImg.alt = imgs[idx].alt;
    lb.classList.add('on');
  }
  function close() { lb.classList.remove('on'); }

  gals.forEach(function (gal) {
    gal.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (b) show(imgs.indexOf(b.querySelector('img')));
    });
  });
  lb.querySelector('.lb-close').addEventListener('click', close);
  lb.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(idx - 1); });
  lb.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(idx + 1); });
  lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('on')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(idx - 1);
    if (e.key === 'ArrowRight') show(idx + 1);
  });

  /* braukimas pirštu telefone: kairėn – kita, dešinėn – ankstesnė */
  var touchX = null;
  lb.addEventListener('touchstart', function (e) {
    touchX = e.touches[0].clientX;
  }, { passive: true });
  lb.addEventListener('touchend', function (e) {
    if (touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX;
    touchX = null;
    if (Math.abs(dx) > 40) show(idx + (dx < 0 ? 1 : -1));
  }, { passive: true });
})();

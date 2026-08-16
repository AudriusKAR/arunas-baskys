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

  /* --- galerijos lightbox --- */
  var gal = document.getElementById('gal');
  var lb = document.getElementById('lb');
  if (!gal || !lb) return;

  var lbImg = lb.querySelector('img');
  var imgs = [].slice.call(gal.querySelectorAll('img'));
  var idx = 0;

  function show(i) {
    idx = (i + imgs.length) % imgs.length;
    lbImg.src = imgs[idx].src;
    lbImg.alt = imgs[idx].alt;
    lb.classList.add('on');
  }
  function close() { lb.classList.remove('on'); }

  gal.addEventListener('click', function (e) {
    var b = e.target.closest('button');
    if (b) show(imgs.indexOf(b.querySelector('img')));
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
})();

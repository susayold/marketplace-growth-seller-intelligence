(() => {
  const menuBtn = document.getElementById('menuBtn');
  const mainNav = document.getElementById('mainNav');
  if (menuBtn && mainNav) {
    menuBtn.addEventListener('click', () => mainNav.classList.toggle('open'));
    mainNav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => mainNav.classList.remove('open')));
  }

  const backTop = document.getElementById('backTop');
  window.addEventListener('scroll', () => {
    if (!backTop) return;
    backTop.classList.toggle('show', window.scrollY > 650);
  });
  if (backTop) backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  const pageMeta = {
    1: ['Executive Overview','A high-level view of marketplace performance, seller concentration and key metrics.'],
    2: ['Seller Acquisition','Lead volume, observed conversion, channel mix and downstream seller value.'],
    3: ['Seller Activation & Retention','Time-to-first-sale, observable activation windows and retention guardrails.'],
    4: ['Commercial Performance','Seller value distribution, concentration and commercial resilience.'],
    5: ['Customer Experience & Operations','Delivery performance and its association with customer review outcomes.'],
    6: ['Root Cause & Diagnostic','Structured evidence review across six cases and twenty hypotheses.'],
    7: ['Decision Center','Prioritized actions with KPIs, guardrails, owners and review cadence.']
  };

  const pdfUrl = './assets/final-market-dashboard.pdf';
  let pdfDoc = null;
  let currentPage = 1;
  let renderToken = 0;

  if (window.pdfjsLib) {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  }

  async function renderPdfPage(canvas, pageNum, maxCssWidth) {
    if (!pdfDoc || !canvas) return;
    const token = ++renderToken;
    const page = await pdfDoc.getPage(pageNum);
    const base = page.getViewport({ scale: 1 });
    const cssWidth = maxCssWidth || base.width;
    const cssScale = cssWidth / base.width;
    // Render substantially above CSS resolution so dashboard typography stays crisp
    // on desktop and high-DPI displays.
    const density = Math.min(Math.max(window.devicePixelRatio || 1, 2.5), 3);
    const viewport = page.getViewport({ scale: cssScale * density });

    canvas.width = Math.floor(viewport.width);
    canvas.height = Math.floor(viewport.height);
    canvas.style.width = Math.floor(cssWidth) + 'px';
    canvas.style.height = Math.floor(base.height * cssScale) + 'px';

    const ctx = canvas.getContext('2d', { alpha: false });
    if (token !== renderToken && canvas.id === 'dashboardCanvas') return;
    await page.render({ canvasContext: ctx, viewport }).promise;
  }

  async function renderHero() {
    const canvas = document.getElementById('heroPdfCanvas');
    if (!canvas || !pdfDoc) return;
    const width = Math.max(320, Math.min(760, canvas.parentElement.clientWidth));
    const page = await pdfDoc.getPage(1);
    const base = page.getViewport({ scale: 1 });
    const cssScale = width / base.width;
    const density = Math.min(Math.max(window.devicePixelRatio || 1, 2.25), 3);
    const viewport = page.getViewport({ scale: cssScale * density });
    canvas.width = Math.floor(viewport.width);
    canvas.height = Math.floor(viewport.height);
    canvas.style.width = width + 'px';
    canvas.style.height = Math.floor(base.height * cssScale) + 'px';
    const ctx = canvas.getContext('2d', { alpha: false });
    await page.render({ canvasContext: ctx, viewport }).promise;
  }

  async function showPage(pageNum) {
    if (!pdfDoc) return;
    currentPage = Math.max(1, Math.min(7, pageNum));
    const loading = document.getElementById('pdfLoading');
    const canvas = document.getElementById('dashboardCanvas');
    if (loading) loading.classList.add('show');

    const wrap = canvas?.parentElement;
    const targetWidth = wrap ? Math.max(320, wrap.clientWidth - 28) : 1120;
    await renderPdfPage(canvas, currentPage, targetWidth);

    const meta = pageMeta[currentPage];
    const title = document.getElementById('dashTitle');
    const subtitle = document.getElementById('dashSubtitle');
    const counter = document.getElementById('pageCurrent');
    if (title) title.textContent = meta[0];
    if (subtitle) subtitle.textContent = meta[1];
    if (counter) counter.textContent = currentPage;

    document.querySelectorAll('#dashboardTabs button').forEach(btn => {
      btn.classList.toggle('active', Number(btn.dataset.page) === currentPage);
    });

    if (loading) loading.classList.remove('show');
  }

  async function initPdf() {
    const loading = document.getElementById('pdfLoading');
    try {
      if (!window.pdfjsLib) throw new Error('PDF.js unavailable');
      if (loading) loading.classList.add('show');
      pdfDoc = await pdfjsLib.getDocument(pdfUrl).promise;
      await Promise.all([renderHero(), showPage(1)]);
    } catch (err) {
      console.error(err);
      if (loading) {
        loading.classList.add('show');
        loading.innerHTML = 'Preview could not render in this browser. <a href="./assets/final-market-dashboard.pdf" target="_blank" rel="noopener">Open the full PDF →</a>';
      }
      const hero = document.querySelector('.laptop-screen');
      if (hero) hero.innerHTML = '<div class="hero-fallback">Power BI<br><strong>7-page Executive Report</strong></div>';
    }
  }

  document.getElementById('prevPage')?.addEventListener('click', () => showPage(currentPage === 1 ? 7 : currentPage - 1));
  document.getElementById('nextPage')?.addEventListener('click', () => showPage(currentPage === 7 ? 1 : currentPage + 1));
  document.querySelectorAll('#dashboardTabs button').forEach(btn => btn.addEventListener('click', () => showPage(Number(btn.dataset.page))));

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (!pdfDoc) return;
      renderHero();
      showPage(currentPage);
    }, 220);
  });

  initPdf();
})();
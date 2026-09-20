(() => {
  const menuBtn = document.getElementById('menuBtn');
  const nav = document.getElementById('mainNav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', () => nav.classList.toggle('open'));
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));
  }

  const pages = [
    {title:'Executive Overview', desc:'A high-level view of marketplace scale, seller concentration and management risk signals.'},
    {title:'Seller Acquisition', desc:'Channel volume, conversion quality and downstream seller value.'},
    {title:'Seller Activation & Retention', desc:'Time-to-first-sale, observable activation windows and retention guardrails.'},
    {title:'Commercial Performance', desc:'Seller value distribution, concentration and commercial resilience.'},
    {title:'Customer Experience & Operations', desc:'Delivery reliability, review outcomes and operational risk.'},
    {title:'Root Cause & Diagnostic', desc:'Evidence-led hypotheses across measurement, growth and operational drivers.'},
    {title:'Decision Center', desc:'Prioritized actions with KPIs, guardrails, owners and review cadence.'}
  ];

  let current = 0;
  let pdfDoc = null;
  let renderToken = 0;
  const pdfUrl = './assets/final-market-dashboard.pdf';
  const dashboardCanvas = document.getElementById('dashboardCanvas');
  const heroCanvas = document.getElementById('heroCanvas');
  const loading = document.getElementById('dashboardLoading');
  const title = document.getElementById('dashboardTitle');
  const desc = document.getElementById('dashboardDesc');
  const counter = document.getElementById('dashboardCounter');
  const pdfPageLink = document.getElementById('pdfPageLink');

  if (window.pdfjsLib) {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
      'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  }

  async function renderPdfPage(pageNumber, canvas, quality = 1.45) {
    if (!pdfDoc || !canvas) return;
    const myToken = ++renderToken;
    const page = await pdfDoc.getPage(pageNumber);
    const base = page.getViewport({ scale: 1 });
    const wrap = canvas.parentElement;
    const cssWidth = Math.max(320, wrap.clientWidth);
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const scale = (cssWidth * dpr * quality) / base.width;
    const viewport = page.getViewport({ scale });

    canvas.width = Math.floor(viewport.width);
    canvas.height = Math.floor(viewport.height);
    canvas.style.width = cssWidth + 'px';
    canvas.style.height = Math.round(cssWidth * base.height / base.width) + 'px';

    const ctx = canvas.getContext('2d', { alpha: false });
    ctx.save();
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.restore();

    await page.render({ canvasContext: ctx, viewport }).promise;
    if (myToken && loading && canvas === dashboardCanvas) loading.hidden = true;
  }

  async function loadPdf() {
    if (!window.pdfjsLib) {
      if (loading) loading.textContent = 'Preview unavailable — open the PDF report.';
      return;
    }
    try {
      pdfDoc = await window.pdfjsLib.getDocument(pdfUrl).promise;
      await Promise.all([
        renderPdfPage(1, dashboardCanvas, 1.35),
        renderPdfPage(1, heroCanvas, .8)
      ]);
    } catch (err) {
      console.error(err);
      if (loading) loading.innerHTML = '<a href="' + pdfUrl + '" target="_blank" rel="noopener">Open the Power BI PDF ↗</a>';
    }
  }

  async function renderPage() {
    if (title) title.textContent = pages[current].title;
    if (desc) desc.textContent = pages[current].desc;
    if (counter) counter.textContent = (current + 1) + ' / ' + pages.length;
    if (pdfPageLink) pdfPageLink.href = pdfUrl + '#page=' + (current + 1);
    if (loading) loading.hidden = false;
    if (pdfDoc) await renderPdfPage(current + 1, dashboardCanvas, 1.35);
  }

  document.getElementById('prevPage')?.addEventListener('click', async () => {
    current = (current - 1 + pages.length) % pages.length;
    await renderPage();
  });
  document.getElementById('nextPage')?.addEventListener('click', async () => {
    current = (current + 1) % pages.length;
    await renderPage();
  });
  document.querySelectorAll('[data-page-jump]').forEach(btn => btn.addEventListener('click', async () => {
    current = Math.max(0, Math.min(pages.length - 1, Number(btn.dataset.pageJump) - 1));
    await renderPage();
  }));

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (!pdfDoc) return;
      renderPdfPage(current + 1, dashboardCanvas, 1.2);
      renderPdfPage(1, heroCanvas, .75);
    }, 220);
  });

  const back = document.getElementById('backTop');
  window.addEventListener('scroll', () => back?.classList.toggle('show', window.scrollY > 700));
  back?.addEventListener('click', () => window.scrollTo({top:0, behavior:'smooth'}));

  loadPdf();
})();
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
  const image = document.getElementById('dashboardImage');
  const title = document.getElementById('dashboardTitle');
  const desc = document.getElementById('dashboardDesc');
  const counter = document.getElementById('dashboardCounter');
  const pdfPageLink = document.getElementById('pdfPageLink');

  function renderPage() {
    const pct = pages.length === 1 ? 0 : current / (pages.length - 1) * 100;
    if (image) image.style.backgroundPosition = 'center ' + pct + '%';
    if (title) title.textContent = pages[current].title;
    if (desc) desc.textContent = pages[current].desc;
    if (counter) counter.textContent = (current + 1) + ' / ' + pages.length;
    if (pdfPageLink) pdfPageLink.href = './assets/final-market-dashboard.pdf#page=' + (current + 1);
  }

  document.getElementById('prevPage')?.addEventListener('click', () => {
    current = (current - 1 + pages.length) % pages.length; renderPage();
  });
  document.getElementById('nextPage')?.addEventListener('click', () => {
    current = (current + 1) % pages.length; renderPage();
  });
  document.querySelectorAll('[data-page-jump]').forEach(btn => btn.addEventListener('click', () => {
    current = Math.max(0, Math.min(pages.length - 1, Number(btn.dataset.pageJump) - 1));
    renderPage();
    document.getElementById('dashboard')?.scrollIntoView({behavior:'smooth'});
  }));
  renderPage();

  const back = document.getElementById('backTop');
  window.addEventListener('scroll', () => back?.classList.toggle('show', window.scrollY > 700));
  back?.addEventListener('click', () => window.scrollTo({top:0, behavior:'smooth'}));
})();
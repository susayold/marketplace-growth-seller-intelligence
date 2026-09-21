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

  let currentPage = 1;
  const imageFor = page => './assets/dashboard/page-' + page + '.png?v=7acad6c';

  function preload(page) {
    const img = new Image();
    img.src = imageFor(page);
  }

  function showPage(pageNum) {
    currentPage = Math.max(1, Math.min(7, pageNum));
    const image = document.getElementById('dashboardImage');
    const loading = document.getElementById('pdfLoading');
    const fullResLink = document.getElementById('dashboardFullRes');
    const fullResButton = document.getElementById('dashboardFullResButton');
    const meta = pageMeta[currentPage];
    const pageImage = imageFor(currentPage);

    if (fullResLink) {
      fullResLink.href = pageImage;
      fullResLink.setAttribute('aria-label', 'Open dashboard page ' + currentPage + ' in full resolution');
    }
    if (fullResButton) fullResButton.href = pageImage;

    if (loading) {
      loading.innerHTML = 'Loading ultra-high-resolution Power BI page…';
      loading.classList.add('show');
    }

    if (image) {
      image.classList.add('is-loading');
      image.onload = () => {
        image.classList.remove('is-loading');
        if (loading) loading.classList.remove('show');
      };
      image.onerror = () => {
        image.classList.remove('is-loading');
        if (loading) {
          loading.innerHTML = 'Preview unavailable. <a href="./assets/final-market-dashboard.pdf" target="_blank" rel="noopener">Open the full PDF →</a>';
          loading.classList.add('show');
        }
      };
      image.src = pageImage;
      image.alt = 'Power BI dashboard page ' + currentPage + ' — ' + meta[0];
    }

    const title = document.getElementById('dashTitle');
    const subtitle = document.getElementById('dashSubtitle');
    const counter = document.getElementById('pageCurrent');
    if (title) title.textContent = meta[0];
    if (subtitle) subtitle.textContent = meta[1];
    if (counter) counter.textContent = currentPage;

    document.querySelectorAll('#dashboardTabs button').forEach(btn => {
      btn.classList.toggle('active', Number(btn.dataset.page) === currentPage);
    });

    preload(currentPage === 7 ? 1 : currentPage + 1);
    preload(currentPage === 1 ? 7 : currentPage - 1);
  }

  document.getElementById('prevPage')?.addEventListener('click', () => showPage(currentPage === 1 ? 7 : currentPage - 1));
  document.getElementById('nextPage')?.addEventListener('click', () => showPage(currentPage === 7 ? 1 : currentPage + 1));
  document.querySelectorAll('#dashboardTabs button').forEach(btn => btn.addEventListener('click', () => showPage(Number(btn.dataset.page))));

  const heroImg = document.getElementById('heroDashboardImage');
  if (heroImg) {
    heroImg.onerror = () => {
      const screen = heroImg.closest('.laptop-screen');
      if (screen) screen.innerHTML = '<div class="hero-fallback">Power BI<br><strong>7-page Executive Report</strong></div>';
    };
  }

  preload(1);
  preload(2);
  showPage(1);
})();
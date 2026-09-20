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
    backTop.classList.toggle('show', window.scrollY > 700);
  });
  if (backTop) backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  const pages = {
    1: {
      title: 'Power BI Executive Overview',
      eyebrow: 'PAGE 01 · EXECUTIVE OVERVIEW',
      headline: 'Use the overview to orient management, then move quickly to the risk drivers.',
      body: 'Headline scale is meaningful, but the strongest management signals are concentration, activation delay, and operational quality. The website uses the analytical release—not decorative dashboard copy—as the interpretation layer.',
      bullets: ['GMV proxy: R$13.59M','Orders: 98,666','Sellers: 3,095','Top 20% seller share: 82.7%']
    },
    2: {
      title: 'Power BI Seller Acquisition',
      eyebrow: 'PAGE 02 · SELLER ACQUISITION',
      headline: 'Channel quality must be governed across the funnel, not ranked from one conversion rate.',
      body: 'The canonical acquisition evidence contains 8,000 MQLs. Origin is associated with conversion, but downstream value and retention remain separate governance dimensions. Unknown stays in the denominator for context and is not an actionable channel winner.',
      bullets: ['Paid Search conversion: 12.3%','Organic Search: 11.8%','Social: 5.6%','Cramér’s V: 0.131']
    },
    3: {
      title: 'Power BI Seller Activation and Retention',
      eyebrow: 'PAGE 03 · ACTIVATION & RETENTION',
      headline: 'Activation is a time-to-event problem with right-censoring, not a simple conversion percentage.',
      body: 'Canonical v3 rates use only sellers observable for each fixed window. Retention by acquisition origin is not precise enough to support a channel winner, so it remains a guardrail.',
      bullets: ['30D: 15.8%','60D: 30.8%','90D: 42.1%','Observed activator median: 44.3 days']
    },
    4: {
      title: 'Power BI Commercial Performance',
      eyebrow: 'PAGE 04 · COMMERCIAL PERFORMANCE',
      headline: 'The key commercial issue is concentration, not simply seller count.',
      body: 'Marketplace GMV is highly concentrated among positive-GMV sellers. Concentration should trigger monitoring and category-level investigation, not an automatic diversification program.',
      bullets: ['Gini: 0.792','Top 1%: 26.1%','Top 5%: 53.3%','Top 20%: 82.7%']
    },
    5: {
      title: 'Power BI Customer Experience and Operations',
      eyebrow: 'PAGE 05 · CUSTOMER EXPERIENCE & OPERATIONS',
      headline: 'Late delivery is a high-priority diagnostic signal because the review gap is both large and persistent.',
      body: 'Late orders show materially weaker review outcomes. The association survives observed controls, but causal language is avoided because category, route, carrier, selection, and other factors can still confound the relationship.',
      bullets: ['Review gap: −1.73 points','Low-review gap: +44.8pp','Observed RR: 5.87×','Adjusted delay-day OR: 1.080']
    },
    6: {
      title: 'Power BI Root Cause and Diagnostic',
      eyebrow: 'PAGE 06 · ROOT CAUSE & DIAGNOSTIC',
      headline: 'Root-cause work separates what is supported from what remains plausible or rejected.',
      body: 'The release contains six cases and twenty hypotheses covering reporting completeness, acquisition quality, onboarding, seller concentration, delivery/CX, and category underperformance.',
      bullets: ['RC1 measurement issue confirmed','RC3 onboarding signal supported','RC5 delivery/CX mechanism supported','RC2/RC4/RC6 retain decision boundaries']
    },
    7: {
      title: 'Power BI Decision Center',
      eyebrow: 'PAGE 07 · DECISION CENTER',
      headline: 'The final page converts evidence into KPI ownership, cadence, guardrails, and stop conditions.',
      body: 'Five governed decisions connect the analysis to operating routines. Four are P1 because measurement completeness, acquisition governance, onboarding, and delivery investigation can be acted on without pretending the data is causal.',
      bullets: ['D01 Data / BI','D02 Seller Acquisition','D03 Seller Operations','D04 Commercial Analytics','D05 Customer Experience']
    }
  };

  const frame = document.getElementById('dashFrame');
  const commentary = document.getElementById('dashCommentary');
  document.querySelectorAll('.dash-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const page = btn.dataset.page;
      const p = pages[page];
      document.querySelectorAll('.dash-tab').forEach(x => x.classList.remove('active'));
      btn.classList.add('active');
      if (frame) {
        frame.src = './assets/final-market-dashboard.pdf#page=' + page + '&view=FitH';
        frame.title = p.title;
      }
      if (commentary) {
        commentary.innerHTML = '<span>' + p.eyebrow + '</span><h3>' + p.headline + '</h3><p>' + p.body + '</p><ul>' + p.bullets.map(x => '<li>' + x + '</li>').join('') + '</ul>';
      }
    });
  });
})();
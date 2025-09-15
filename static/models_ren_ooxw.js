  
  (function () {
    const qs = new URLSearchParams(location.search);

    if (qs.has('bypass_pref')) {
      sessionStorage.setItem('sv_pref_bypass', '1');
      return;
    }
    if (sessionStorage.getItem('sv_pref_bypass') === '1') return;

    const pref = localStorage.getItem('landing_pref');
    const already = sessionStorage.getItem('sv_pref_redirected');

    if (pref && location.pathname === '/' && !already) {
      sessionStorage.setItem('sv_pref_redirected', '1');
      location.replace(pref); 
    }
  })();

  document.addEventListener('DOMContentLoaded', function () {
    const btn      = document.getElementById('sv-landing-btn');
    const modal    = document.getElementById('sv-landing-modal');
    const save     = document.getElementById('sv-save');
    const closeBtn = document.getElementById('sv-close');
    const applyNow = document.getElementById('sv-apply-now');

    const open = () => {
      const v = localStorage.getItem('landing_pref') || '/';
      modal.querySelectorAll('input[name="sv-landing"]')
           .forEach(r => r.checked = (r.value === v));
      modal.classList.remove('hidden'); modal.classList.add('flex');
    };
    const hide = () => { modal.classList.add('hidden'); modal.classList.remove('flex'); };

    btn.addEventListener('click', open);
    closeBtn.addEventListener('click', hide);
    modal.addEventListener('click', e => { if (e.target === modal) hide(); });

    save.addEventListener('click', () => {
      const v = modal.querySelector('input[name="sv-landing"]:checked')?.value || '/';
      localStorage.setItem('landing_pref', v);
      hide();
      if (applyNow.checked) location.href = v;
    });
  });
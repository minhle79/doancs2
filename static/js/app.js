// Dropdown categories
document.querySelectorAll('.dropdown').forEach(dd => {
  dd.addEventListener('mouseenter', () => dd.classList.add('open'));
  dd.addEventListener('mouseleave', () => dd.classList.remove('open'));
});

// Search suggestion
const searchInput = document.getElementById('search-input');
const suggestBox = document.getElementById('search-suggest');
if (searchInput && suggestBox) {
  let last = 0;
  searchInput.addEventListener('input', async () => {
    const q = searchInput.value.trim();
    const now = Date.now();
    last = now;
    if (!q) { suggestBox.innerHTML=''; suggestBox.classList.remove('show'); return; }
    try {
      const res = await fetch(`/api/suggest/?q=${encodeURIComponent(q)}`);
      if (last !== now) return; // prevent race
      const data = await res.json();
      suggestBox.innerHTML = data.results.map(r => `
        <a class="suggest-item" href="/product/${r.slug}/">${r.name}</a>
      `).join('');
      suggestBox.classList.toggle('show', data.results.length > 0);
    } catch(e){ /* ignore */ }
  });
  document.addEventListener('click', (e)=>{
    if (!suggestBox.contains(e.target) && e.target !== searchInput) {
      suggestBox.classList.remove('show');
    }
  });
}

// Cart modal
const openCartBtn = document.getElementById('openCart');
const cartModal = document.getElementById('cartModal');
async function openCart(){
  if (!cartModal) return;
  const res = await fetch('/cart/?fragment=1');
  cartModal.innerHTML = await res.text();
  cartModal.classList.remove('hidden');
  const closeBtn = cartModal.querySelector('#closeCart');
  closeBtn && closeBtn.addEventListener('click', () => cartModal.classList.add('hidden'));
  // close when clicking outside content
  cartModal.addEventListener('click', (e)=>{
    if (e.target === cartModal) cartModal.classList.add('hidden');
  }, { once:true });
  // close with ESC
  const esc = (e)=>{ if(e.key==='Escape'){ cartModal.classList.add('hidden'); document.removeEventListener('keydown', esc);} };
  document.addEventListener('keydown', esc);
}
openCartBtn && openCartBtn.addEventListener('click', openCart);

// Back to top
const backBtn = document.getElementById('backToTop');
function onScroll(){
  if (!backBtn) return;
  backBtn.classList.toggle('show', window.scrollY > 400);
}
window.addEventListener('scroll', onScroll);
backBtn && backBtn.addEventListener('click', () => window.scrollTo({top:0, behavior:'smooth'}));

// Toast notification
function showToast(message, type='success'){
  let t = document.getElementById('toast');
  if(!t){
    t = document.createElement('div');
    t.id = 'toast';
    document.body.appendChild(t);
  }
  t.className = `toast ${type} show`;
  t.textContent = message;
  setTimeout(()=>{ t.classList.remove('show'); }, 2500);
}

// Update cart badge count
function setCartCount(n){
  const badge = document.querySelector('#openCart .badge');
  if (badge) badge.textContent = n;
}

// Intercept add/remove cart forms
document.addEventListener('submit', async (e) => {
  const form = e.target;
  if (!(form instanceof HTMLFormElement)) return;
  const action = form.getAttribute('action') || '';
  if (action.includes('/cart/add/')) {
    e.preventDefault();
    const res = await fetch(action, { method:'POST', headers:{'X-Requested-With':'XMLHttpRequest'}, body: new FormData(form) });
    const data = await res.json();
    if (data.ok){
      showToast(data.message, 'success');
      setCartCount(data.cart_count);
    }
  }
  if (action.includes('/cart/remove/')) {
    e.preventDefault();
    const ok = confirm('Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?');
    if (!ok) return;
    const res = await fetch(action, { method:'POST', headers:{'X-Requested-With':'XMLHttpRequest'}, body: new FormData(form) });
    const data = await res.json();
    if (data.ok){
      showToast(data.message, 'success');
      setCartCount(data.cart_count);
      if (cartModal && !cartModal.classList.contains('hidden')) {
        cartModal.innerHTML = data.modal;
        const closeBtn = cartModal.querySelector('#closeCart');
        closeBtn && closeBtn.addEventListener('click', () => cartModal.classList.add('hidden'));
      }
    }
  }
});



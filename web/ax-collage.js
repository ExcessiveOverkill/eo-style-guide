// eo-style image collage: a tilted photo wall that leans toward the mouse.
// Hovering a tile lifts it out of the wall and brings back full color; clicking
// opens it full size with its caption. Esc or click closes.
//
//   axCollage(el, [
//     { src: 'assets/gimbus-render.jpg', caption: 'Gimbus, render', span: [2, 2] },  // [cols, rows]
//     { src: 'assets/mini-pcb.jpg', caption: 'Mini, controller PCB' },
//   ], { columns: 6, tilt: 14 })

(function () {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  window.axCollage = function (root, items, { columns = 6, rowHeight = 120, tilt = 14 } = {}) {
    root.classList.add('ax-collage');
    root.innerHTML = '';
    const wall = document.createElement('div');
    wall.className = 'ax-collage-wall';
    wall.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
    wall.style.gridAutoRows = rowHeight + 'px';
    root.appendChild(wall);

    const base = { x: tilt * 0.8, y: -tilt * 0.35, z: tilt * 0.15 };
    const lean = (x, y) => (wall.style.transform = `rotateX(${base.x - y * 6}deg) rotateY(${base.y + x * 8}deg) rotateZ(${base.z}deg)`);
    lean(0, 0);

    items.forEach((it, i) => {
      const t = document.createElement('figure');
      t.className = 'ax-collage-tile';
      const [c, r] = it.span || [1, 1];
      t.style.gridColumn = `span ${c}`; t.style.gridRow = `span ${r}`;
      t.style.animationDelay = reduced ? '0s' : `${i * 60}ms`;
      t.innerHTML = `<img src="${it.src}" alt="${it.caption || ''}" loading="lazy"><figcaption><span>${String(i + 1).padStart(2, '0')}</span>${it.caption || ''}</figcaption>`;
      t.addEventListener('click', () => open(it, i));
      wall.appendChild(t);
    });

    if (!reduced) {
      root.addEventListener('pointermove', e => {
        const r = root.getBoundingClientRect();
        lean((e.clientX - r.left) / r.width - 0.5, (e.clientY - r.top) / r.height - 0.5);
      });
      root.addEventListener('pointerleave', () => lean(0, 0));
    }

    function open(it, i) {
      const box = document.createElement('div');
      box.className = 'ax-lightbox';
      box.innerHTML = `<figure><img src="${it.src}" alt=""><figcaption><b>Fig. ${i + 1}.</b> ${it.caption || ''}</figcaption></figure>`;
      const close = () => { box.classList.add('closing'); setTimeout(() => box.remove(), 180); removeEventListener('keydown', esc); };
      const esc = e => e.key === 'Escape' && close();
      box.addEventListener('click', close);
      addEventListener('keydown', esc);
      document.body.appendChild(box);
    }
  };
})();

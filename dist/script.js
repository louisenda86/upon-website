document.documentElement.classList.add('js');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
const header = document.querySelector('.site-header');
const menuToggle = document.querySelector('.menu-toggle');
const mobileNav = document.querySelector('#mobile-nav');

function closeMenu() {
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.textContent = 'Menu';
  mobileNav.hidden = true;
}
menuToggle.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.textContent = open ? 'Close' : 'Menu';
  mobileNav.hidden = !open;
});
mobileNav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !mobileNav.hidden) {
    closeMenu(); menuToggle.focus();
  }
});
window.addEventListener('scroll', () => header.classList.toggle('scrolled', scrollY > 40), { passive: true });

const reveals = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !reduceMotion.matches) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: .08 });
  reveals.forEach(item => observer.observe(item));
} else reveals.forEach(item => item.classList.add('visible'));

const tabs = [...document.querySelectorAll('[role="tab"]')];
const panels = [...document.querySelectorAll('[role="tabpanel"]')];
function selectTab(next) {
  tabs.forEach(tab => {
    const selected = tab === next;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
  });
  panels.forEach(panel => panel.hidden = panel.dataset.panelContent !== next.dataset.panel);
}
tabs.forEach((tab, index) => {
  tab.tabIndex = tab.getAttribute('aria-selected') === 'true' ? 0 : -1;
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = tabs[(index + 1) % tabs.length];
    if (event.key === 'ArrowLeft') next = tabs[(index - 1 + tabs.length) % tabs.length];
    if (event.key === 'Home') next = tabs[0];
    if (event.key === 'End') next = tabs.at(-1);
    if (next) { event.preventDefault(); selectTab(next); next.focus(); }
  });
});

const video = document.querySelector('#upon-film');
const playButton = document.querySelector('#film-play');
const soundButton = document.querySelector('#film-sound');
const chapters = [...document.querySelectorAll('[data-time]')];
let userPaused = false;
let automaticPause = false;
const filmSource = video.querySelector('source').src;
let seekableSource;
let filmBlobURL;
let seekableMetadata;
async function ensureFilmCanSeek(time) {
  if (video.seekable.length && video.seekable.end(video.seekable.length - 1) >= time) return;
  // A few static hosts omit byte-range support. A cached, same-origin Blob
  // makes this small film seekable without changing ordinary streaming.
  if (!seekableSource) {
    seekableSource = fetch(filmSource, { cache: 'force-cache', signal: AbortSignal.timeout(15000) })
      .then(response => {
        if (!response.ok) throw new Error('Film unavailable');
        return response.blob();
      }).then(blob => {
        if (!blob.size || blob.size > 10000000) throw new Error('Unexpected film size');
        return blob;
      }).catch(error => { seekableSource = undefined; throw error; });
  }
  const blob = await seekableSource;
  if (filmBlobURL) return seekableMetadata;
  filmBlobURL = URL.createObjectURL(blob);
  seekableMetadata = new Promise((resolve, reject) => {
    const finish = error => {
      clearTimeout(timer);
      video.removeEventListener('loadedmetadata', loaded);
      video.removeEventListener('error', failed);
      error ? reject(error) : resolve();
    };
    const loaded = () => finish();
    const failed = () => finish(new Error('Film could not load'));
    const timer = setTimeout(failed, 8000);
    video.addEventListener('loadedmetadata', loaded, { once: true });
    video.addEventListener('error', failed, { once: true });
  });
  automaticPause = !video.paused;
  video.src = filmBlobURL;
  video.load();
  try { await seekableMetadata; }
  catch (error) {
    URL.revokeObjectURL(filmBlobURL); filmBlobURL = undefined;
    video.src = filmSource; video.load();
    throw error;
  }
}
window.addEventListener('pagehide', event => { if (filmBlobURL && !event.persisted) URL.revokeObjectURL(filmBlobURL); });
function syncFilmControls() {
  playButton.textContent = video.paused ? 'Play' : 'Pause';
  playButton.setAttribute('aria-label', video.paused ? 'Play the film' : 'Pause the film');
  soundButton.textContent = video.muted ? 'Sound off' : 'Sound on';
  soundButton.setAttribute('aria-pressed', String(!video.muted));
}
playButton.addEventListener('click', () => {
  if (video.paused) { userPaused = false; video.play().catch(() => {}); }
  else { userPaused = true; video.pause(); }
});
soundButton.addEventListener('click', () => {
  video.muted = !video.muted;
  if (!video.muted && video.paused) { userPaused = false; video.play().catch(() => {}); }
});
video.addEventListener('play', () => { userPaused = false; syncFilmControls(); });
video.addEventListener('pause', () => {
  if (!automaticPause && !video.ended) userPaused = true;
  automaticPause = false; syncFilmControls();
});
video.addEventListener('volumechange', syncFilmControls);
video.addEventListener('timeupdate', () => {
  const active = [...chapters].reverse().find(chapter => video.currentTime >= Number(chapter.dataset.time));
  chapters.forEach(chapter => {
    chapter.classList.toggle('active', chapter === active);
    if (chapter === active) chapter.setAttribute('aria-current', 'true');
    else chapter.removeAttribute('aria-current');
  });
});
chapters.forEach(chapter => chapter.addEventListener('click', async () => {
  chapters.forEach(button => button.disabled = true);
  try {
    const time = Number(chapter.dataset.time);
    await ensureFilmCanSeek(time);
    video.currentTime = time; userPaused = false;
    video.play().catch(() => {});
  } catch {
    announce('The film could not jump. Please try again or download it.');
  } finally { chapters.forEach(button => button.disabled = false); }
}));
if ('IntersectionObserver' in window) {
  let filmVisible = false;
  const filmObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      filmVisible = entry.isIntersecting;
      if (entry.isIntersecting) {
        const resume = () => {
          if (filmVisible && !reduceMotion.matches && !userPaused) video.play().catch(() => {});
        };
        ensureFilmCanSeek(1).then(resume, resume);
      }
      else if (!entry.isIntersecting && !video.paused) {
        automaticPause = true; video.pause();
      }
    });
  }, { threshold: .35 });
  filmObserver.observe(video);
}
reduceMotion.addEventListener('change', () => {
  if (reduceMotion.matches && !video.paused) { automaticPause = true; video.pause(); }
});
syncFilmControls();

const copyButton = document.querySelector('#copy-checksum');
const toast = document.querySelector('.toast');
let toastTimer;
function announce(message) {
  toast.textContent = message;
  toast.classList.add('visible'); clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('visible'), 3200);
}
copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(document.querySelector('#checksum-value').textContent.trim());
    announce('Checksum copied');
  } catch { announce('Select the checksum to copy it'); }
});

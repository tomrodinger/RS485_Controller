import { STORAGE_KEY, emptyFeedback, validateFeedback, mergeFeedback, normalizeCandidates, filterCandidates } from './feedback.js';

const $ = id => document.getElementById(id);
const state = { candidates: [], selected: null, compare: [], mode: 'single', filter: 'all', query: '', data: emptyFeedback(), saveTimer: null, storageOK: true };
const viewers = [];
const ratingNames = ['Not rated yet', '1 star · Needs a rethink', '2 stars · Needs work', '3 stars · Promising direction', '4 stars · Strong direction', '5 stars · Excellent'];

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function notice(message, error = false) {
  $('notice').textContent = message;
  $('notice').classList.toggle('error', error);
  $('notice').hidden = false;
}
function getRecord(id = state.selected) {
  return state.data.feedback[id] || { rating: 0, comment: '', revision: '', updatedAt: '' };
}
function getCandidate(id = state.selected) { return state.candidates.find(candidate => candidate.id === id); }
function saveStatus(message, warning = false) {
  $('save-status').textContent = message;
  $('save-status').classList.toggle('warning', warning);
}
function persist() {
  clearTimeout(state.saveTimer);
  state.saveTimer = null;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state.data));
    state.storageOK = true;
    saveStatus('Saved in this browser');
  } catch {
    state.storageOK = false;
    saveStatus('Browser save unavailable · export to keep', true);
    notice('Your browser could not save this feedback. Keep this page open and use Export feedback to download your notes.', true);
  }
}
function updateFeedback(patch) {
  const candidate = getCandidate();
  if (!candidate) return;
  state.data.feedback[candidate.id] = { ...getRecord(), ...patch, updatedAt: new Date().toISOString(), revision: candidate.revision };
  saveStatus('Saving…');
  clearTimeout(state.saveTimer);
  state.saveTimer = setTimeout(persist, 300);
  updateProgress();
  updateCardReview(candidate.id);
  updateRating();
  $('revision-warning').hidden = true;
}
function restore() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) state.data = validateFeedback(JSON.parse(stored));
    saveStatus('Saved in this browser');
  } catch {
    state.storageOK = false;
    saveStatus('Check browser storage', true);
    notice('Existing browser feedback could not be read. You can import a previous JSON export, or start a new review and export your notes.', true);
  }
}

class ImageViewer {
  constructor(container, candidate, label) {
    this.container = container;
    this.candidate = candidate;
    this.scale = 1;
    this.x = 0;
    this.y = 0;
    this.isFit = true;
    this.loaded = false;
    this.pointer = null;
    this.abort = new AbortController();
    const eventOptions = { signal: this.abort.signal };
    container.replaceChildren();
    const stage = this.stage = element('div', 'viewer-stage');
    stage.tabIndex = 0;
    stage.setAttribute('role', 'region');
    stage.setAttribute('aria-label', `${label}: ${candidate.title}. Arrow keys pan. Plus or minus zoom. Zero fits the image. One shows full resolution.`);
    const image = this.image = element('img', 'viewer-image');
    image.alt = candidate.description ? `${candidate.title}. ${candidate.description}` : candidate.title;
    image.draggable = false;
    image.hidden = true;
    const loading = this.loading = element('div', 'viewer-loading', 'Loading full-resolution diagram…');
    loading.setAttribute('role', 'status');
    stage.append(image, loading);
    const toolbar = element('div', 'viewer-toolbar');
    const controls = element('div', 'zoom-controls');
    const button = (text, accessible, action) => {
      const node = element('button', '', text);
      node.type = 'button';
      node.setAttribute('aria-label', `${accessible}: ${candidate.title}`);
      node.title = accessible;
      node.addEventListener('click', action, eventOptions);
      controls.append(node);
      return node;
    };
    button('−', 'Zoom out', () => this.zoom(this.scale / 1.3));
    this.output = element('span', 'zoom-output', '—');
    this.output.setAttribute('aria-label', 'Image zoom');
    this.output.setAttribute('aria-live', 'polite');
    controls.append(this.output);
    button('+', 'Zoom in', () => this.zoom(this.scale * 1.3));
    button('Fit', 'Fit image (0)', () => this.fit());
    button('100%', 'Full resolution (1)', () => this.zoom(1, undefined, true));
    const original = element('a', 'original-link', 'Open PNG ↗');
    original.href = candidate.image;
    original.target = '_blank';
    original.rel = 'noopener';
    original.setAttribute('aria-label', `Open full-resolution PNG for ${candidate.title} in a new tab`);
    toolbar.append(controls, original);
    const hint = element('p', 'viewer-hint', 'Drag to pan · Ctrl/⌘ + scroll to zoom · Arrow keys to pan');
    container.append(stage, toolbar);
    container.after(hint);
    this.hint = hint;
    image.addEventListener('load', () => {
      this.loaded = true;
      image.hidden = false;
      loading.hidden = true;
      this.fit();
    }, eventOptions);
    image.addEventListener('error', () => {
      loading.textContent = 'This PNG could not be loaded. Check the candidate image path or try opening the original.';
      loading.classList.add('error');
    }, eventOptions);
    image.src = candidate.image;
    stage.addEventListener('pointerdown', event => {
      if (!this.loaded || event.button !== 0) return;
      if (this.pointer !== null) return;
      this.pointer = event.pointerId;
      this.lastPoint = { x: event.clientX, y: event.clientY };
      stage.setPointerCapture(event.pointerId);
      stage.classList.add('dragging');
      stage.focus({ preventScroll: true });
    }, eventOptions);
    stage.addEventListener('pointermove', event => {
      if (this.pointer !== event.pointerId) return;
      this.x += event.clientX - this.lastPoint.x;
      this.y += event.clientY - this.lastPoint.y;
      this.lastPoint = { x: event.clientX, y: event.clientY };
      this.isFit = false;
      this.draw();
    }, eventOptions);
    const stopDrag = event => {
      if (this.pointer !== event.pointerId) return;
      this.pointer = null;
      stage.classList.remove('dragging');
    };
    stage.addEventListener('pointerup', stopDrag, eventOptions);
    stage.addEventListener('pointercancel', stopDrag, eventOptions);
    stage.addEventListener('lostpointercapture', stopDrag, eventOptions);
    stage.addEventListener('wheel', event => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault();
      const bounds = stage.getBoundingClientRect();
      this.zoom(this.scale * Math.exp(-event.deltaY * .008), {
        x: event.clientX - bounds.left - bounds.width / 2,
        y: event.clientY - bounds.top - bounds.height / 2,
      });
    }, { ...eventOptions, passive: false });
    stage.addEventListener('keydown', event => {
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      const step = event.shiftKey ? 120 : 40;
      const moves = { ArrowLeft: [step, 0], ArrowRight: [-step, 0], ArrowUp: [0, step], ArrowDown: [0, -step] };
      if (moves[event.key]) {
        event.preventDefault();
        this.x += moves[event.key][0]; this.y += moves[event.key][1];
        this.isFit = false;
        this.draw();
      } else if (['+', '=', '-', '_', '0', '1'].includes(event.key)) {
        event.preventDefault();
        if (event.key === '0') this.fit();
        else if (event.key === '1') this.zoom(1, undefined, true);
        else this.zoom(this.scale * (['+', '='].includes(event.key) ? 1.3 : 1 / 1.3));
      }
    }, eventOptions);
    this.resize = new ResizeObserver(() => { if (this.isFit && this.loaded) this.fit(); });
    this.resize.observe(stage);
  }
  fit() {
    if (!this.loaded || !this.stage.clientWidth || !this.stage.clientHeight) return;
    this.scale = Math.min((this.stage.clientWidth - 32) / this.image.naturalWidth, (this.stage.clientHeight - 32) / this.image.naturalHeight, 1);
    this.x = 0; this.y = 0; this.isFit = true; this.draw();
  }
  zoom(scale, point = { x: 0, y: 0 }, reset = false) {
    if (!this.loaded) return;
    const next = Math.max(.005, Math.min(8, scale));
    if (reset) { this.x = 0; this.y = 0; }
    else {
      this.x = point.x - (point.x - this.x) * next / this.scale;
      this.y = point.y - (point.y - this.y) * next / this.scale;
    }
    this.scale = next; this.isFit = false; this.draw();
  }
  draw() {
    this.image.style.width = `${this.image.naturalWidth}px`;
    this.image.style.height = `${this.image.naturalHeight}px`;
    this.image.style.transform = `translate(-50%, -50%) translate(${this.x}px, ${this.y}px) scale(${this.scale})`;
    this.output.textContent = `${Math.round(this.scale * 100)}%`;
  }
  destroy() { this.abort.abort(); this.resize.disconnect(); this.hint.remove(); }
}

function destroyViewers() { viewers.splice(0).forEach(viewer => viewer.destroy()); }
function updateProgress() {
  const reviewed = state.candidates.filter(candidate => {
    const record = getRecord(candidate.id);
    return record.rating > 0 || Boolean(record.comment.trim());
  }).length;
  const total = state.candidates.length;
  $('review-count').textContent = reviewed;
  $('total-count').textContent = total;
  $('progress-fill').style.width = `${total ? reviewed / total * 100 : 0}%`;
  const progress = document.querySelector('.progress-track');
  progress.setAttribute('aria-valuemax', total);
  progress.setAttribute('aria-valuenow', reviewed);
  progress.setAttribute('aria-valuetext', `${reviewed} of ${total} candidates reviewed`);
}
function updateRating() {
  const rating = getRecord().rating;
  document.querySelectorAll('#rating-stars .star-option').forEach((option, index) => {
    option.classList.toggle('active', index < rating);
    option.querySelector('input').checked = index + 1 === rating;
  });
  $('rating-label').textContent = ratingNames[rating];
  $('clear-rating').disabled = rating === 0;
}
function buildStars() {
  for (let value = 1; value <= 5; value++) {
    const option = element('span', 'star-option');
    const input = element('input');
    input.type = 'radio'; input.name = 'candidate-rating'; input.value = value; input.id = `rating-${value}`;
    input.setAttribute('aria-label', `${value} ${value === 1 ? 'star' : 'stars'}`);
    const label = element('label', '', '★'); label.htmlFor = input.id; label.setAttribute('aria-hidden', 'true');
    input.addEventListener('change', () => {
      updateFeedback({ rating: value });
      if (state.filter !== 'all') renderGallery();
    });
    option.append(input, label); $('rating-stars').append(option);
  }
}
function selectCandidate(id, focus = false) {
  if (state.saveTimer) persist();
  state.selected = id;
  state.mode = 'single';
  renderWorkspace();
  renderGallery();
  if (focus) {
    $('single-panel').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    $('selected-title').tabIndex = -1;
    $('selected-title').focus({ preventScroll: true });
  }
}
function renderWorkspace() {
  destroyViewers();
  const candidate = getCandidate();
  $('empty-state').hidden = Boolean(state.candidates.length);
  $('single-panel').hidden = state.mode !== 'single' || !candidate;
  $('compare-panel').hidden = state.mode !== 'compare' || !state.candidates.length;
  $('single-view').classList.toggle('active', state.mode === 'single');
  $('single-view').setAttribute('aria-pressed', state.mode === 'single');
  $('compare-view').classList.toggle('active', state.mode === 'compare');
  $('compare-view').setAttribute('aria-pressed', state.mode === 'compare');
  $('compare-count').textContent = `${state.compare.length} / 2`;
  if (state.mode === 'compare') { renderCompare(); return; }
  if (!candidate) return;
  $('selected-title').textContent = candidate.title;
  $('selected-style').textContent = candidate.style;
  $('selected-status').textContent = candidate.reviewStatus;
  $('selected-description').textContent = candidate.description;
  $('detail-style').textContent = candidate.style;
  $('detail-revision').textContent = candidate.revision || '—';
  $('detail-resolution').textContent = candidate.width && candidate.height ? `${candidate.width.toLocaleString()} × ${candidate.height.toLocaleString()} px` : 'Original PNG';
  $('position').textContent = `${state.candidates.indexOf(candidate) + 1} / ${state.candidates.length}`;
  $('previous').disabled = state.candidates.length < 2;
  $('next').disabled = state.candidates.length < 2;
  $('comment').value = getRecord().comment;
  const priorRevision = getRecord().revision;
  $('revision-warning').hidden = !priorRevision || priorRevision === candidate.revision;
  $('revision-warning').textContent = `Your saved review refers to revision ${priorRevision}. This candidate is now ${candidate.revision || 'a new revision'}. Editing the review applies it to this version.`;
  updateRating();
  updateCompareButton();
  viewers.push(new ImageViewer($('main-viewer'), candidate, 'Diagram inspection'));
}
function updateCompareButton() {
  const added = state.compare.includes(state.selected);
  $('add-compare').textContent = added ? 'Remove from comparison −' : 'Add to comparison +';
  $('add-compare').setAttribute('aria-pressed', added);
}
function toggleCompare(id) {
  if (state.compare.includes(id)) state.compare = state.compare.filter(item => item !== id);
  else if (state.compare.length < 2) state.compare.push(id);
  else {
    notice('Your comparison already has two candidates. Uncheck one to choose another.');
    renderGallery();
    return;
  }
  $('compare-count').textContent = `${state.compare.length} / 2`;
  updateCompareButton();
  renderGallery();
  if (state.mode === 'compare') { destroyViewers(); renderCompare(); }
}
function renderCompare() {
  const grid = $('compare-grid'); grid.replaceChildren();
  for (let slot = 0; slot < 2; slot++) {
    const candidate = state.compare[slot] ? getCandidate(state.compare[slot]) : null;
    if (!candidate) {
      const empty = element('div', 'compare-empty');
      empty.append(element('strong', '', `Choose candidate ${slot + 1}`), element('span', '', 'Use the Compare checkboxes in the gallery below.'));
      grid.append(empty); continue;
    }
    const card = element('article', 'compare-card');
    const heading = element('div', 'compare-card-heading');
    const title = element('div'); title.append(element('p', 'eyebrow', candidate.style), element('h3', '', candidate.title));
    const remove = element('button', 'icon-button', '×');
    remove.setAttribute('aria-label', `Remove ${candidate.title} from comparison`);
    remove.addEventListener('click', () => toggleCompare(candidate.id));
    heading.append(title, remove);
    const viewer = element('div', 'viewer');
    const review = element('div', 'compare-review');
    const rating = getRecord(candidate.id).rating;
    const inspect = element('button', 'text-button', 'Rate & leave notes →');
    inspect.addEventListener('click', () => { selectCandidate(candidate.id); $('comment').focus({ preventScroll: true }); });
    review.append(element('span', 'compare-rating', rating ? `${'★'.repeat(rating)}${'☆'.repeat(5 - rating)} · ${rating} / 5` : 'Not rated yet'), inspect);
    card.append(heading, viewer, review); grid.append(card);
    viewers.push(new ImageViewer(viewer, candidate, `Comparison ${slot + 1}`));
  }
}
function cardRating(id) {
  const record = getRecord(id);
  const stars = element('span', `card-stars${record.rating ? '' : ' unrated'}`, '★'.repeat(record.rating) + '☆'.repeat(5 - record.rating));
  stars.setAttribute('role', 'img');
  stars.setAttribute('aria-label', record.rating ? `${record.rating} out of 5 stars` : 'Not rated');
  if (record.comment.trim()) {
    const note = element('span', 'card-reviewed', 'Notes');
    note.setAttribute('aria-label', 'Has review notes'); stars.append(note);
  }
  return stars;
}
function updateCardReview(id) {
  for (const card of $('gallery').children) {
    if (card.dataset.id === id) card.querySelector('.card-stars').replaceWith(cardRating(id));
  }
}
function renderGallery() {
  const focusId = document.activeElement?.dataset.compareId;
  const candidates = filterCandidates(state.candidates, state.data.feedback, state.filter, state.query);
  $('gallery-count').textContent = candidates.length;
  $('no-results').hidden = candidates.length > 0 || !state.candidates.length;
  const fragment = document.createDocumentFragment();
  for (const candidate of candidates) {
    const selected = candidate.id === state.selected;
    const index = state.candidates.indexOf(candidate) + 1;
    const card = element('article', `candidate-card${selected ? ' selected' : ''}`); card.dataset.id = candidate.id;
    const open = element('button', 'candidate-open');
    open.setAttribute('aria-label', `Inspect ${candidate.title}${selected ? ', currently selected' : ''}`);
    open.setAttribute('aria-pressed', selected);
    const wrap = element('div', 'thumbnail-wrap');
    const img = element('img'); img.src = candidate.thumbnail; img.alt = ''; img.loading = 'lazy'; img.decoding = 'async';
    img.addEventListener('error', () => { img.hidden = true; wrap.append(element('span', 'muted', 'Preview unavailable')); }, { once: true });
    wrap.append(img);
    const body = element('div', 'card-body');
    body.append(element('span', 'card-index', `DIRECTION ${String(index).padStart(2, '0')}${candidate.revision ? ` / ${candidate.revision}` : ''}`), element('h3', 'card-title', candidate.title), element('p', 'card-style', candidate.style));
    open.append(wrap, body); open.addEventListener('click', () => selectCandidate(candidate.id, true));
    const bottom = element('div', 'card-bottom');
    const label = element('label', 'compare-check');
    const check = element('input'); check.type = 'checkbox'; check.checked = state.compare.includes(candidate.id);
    check.dataset.compareId = candidate.id;
    check.setAttribute('aria-label', `Compare ${candidate.title}`);
    check.addEventListener('change', () => toggleCompare(candidate.id));
    label.append(check, document.createTextNode('Compare'));
    bottom.append(cardRating(candidate.id), label); card.append(open, bottom);
    if (selected) card.append(element('span', 'selected-badge', 'VIEWING'));
    fragment.append(card);
  }
  $('gallery').replaceChildren(fragment);
  if (focusId) {
    const input = [...$('gallery').querySelectorAll('input')].find(node => node.dataset.compareId === focusId);
    input?.focus({ preventScroll: true });
  }
}

function exportFeedback() {
  if (state.saveTimer) persist();
  const payload = { ...state.data, exportedAt: new Date().toISOString(), gallery: 'Gearotons RS485 wiring diagram review', candidates: state.candidates.map(({ id, title, revision, image }) => ({ id, title, revision, image })) };
  const blob = new Blob([JSON.stringify(payload, null, 2) + '\n'], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url; anchor.download = `gearotons-wiring-feedback-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
  document.body.append(anchor); anchor.click(); anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
  notice(`Feedback export downloaded. Send the JSON file back with your review.${state.storageOK ? ' Browser feedback remains saved here.' : ' Keep the exported file; browser storage is unavailable.'}`);
}
async function importFeedback(file) {
  if (!file) return;
  try {
    if (file.size > 5 * 1024 * 1024) throw new Error('Choose a feedback JSON file smaller than 5 MB.');
    const incoming = validateFeedback(JSON.parse(await file.text()));
    if (state.saveTimer) persist();
    const merged = mergeFeedback(state.data, incoming);
    state.data = merged.data;
    persist(); renderWorkspace(); renderGallery(); updateProgress();
    const message = `Imported ${merged.imported} newer feedback ${merged.imported === 1 ? 'record' : 'records'}. For matching IDs, the newest review is kept.`;
    notice(state.storageOK ? message : `${message} Browser storage is unavailable; export the merged review to keep it.`, !state.storageOK);
  } catch (error) {
    notice(error instanceof SyntaxError ? 'This file is not valid JSON. No feedback was imported.' : error.message, true);
  }
  $('import-file').value = '';
}

buildStars(); restore();
$('export').addEventListener('click', exportFeedback);
$('import').addEventListener('click', () => $('import-file').click());
$('import-file').addEventListener('change', event => importFeedback(event.target.files[0]));
$('comment').addEventListener('input', event => updateFeedback({ comment: event.target.value }));
$('comment').addEventListener('change', () => { if (state.filter !== 'all') renderGallery(); });
$('comment').addEventListener('blur', () => { if (state.saveTimer) persist(); });
$('clear-rating').addEventListener('click', () => { updateFeedback({ rating: 0 }); if (state.filter !== 'all') renderGallery(); });
$('rating-filter').addEventListener('change', event => { state.filter = event.target.value; renderGallery(); });
$('search').addEventListener('input', event => { state.query = event.target.value; renderGallery(); });
$('add-compare').addEventListener('click', () => toggleCompare(state.selected));
$('single-view').addEventListener('click', () => { state.mode = 'single'; renderWorkspace(); });
$('compare-view').addEventListener('click', () => { state.mode = 'compare'; renderWorkspace(); });
$('clear-compare').addEventListener('click', () => { state.compare = []; renderWorkspace(); renderGallery(); });
for (const [button, direction] of [['previous', -1], ['next', 1]]) {
  $(button).addEventListener('click', () => {
    const index = state.candidates.findIndex(candidate => candidate.id === state.selected);
    const next = (index + direction + state.candidates.length) % state.candidates.length;
    if (state.candidates[next]) selectCandidate(state.candidates[next].id);
  });
}
window.addEventListener('pagehide', () => { if (state.saveTimer) persist(); });
document.addEventListener('visibilitychange', () => { if (document.hidden && state.saveTimer) persist(); });

try {
  const response = await fetch('candidates.json', { cache: 'no-cache' });
  if (!response.ok) throw new Error(`Candidate manifest returned HTTP ${response.status}.`);
  state.candidates = normalizeCandidates(await response.json());
  state.selected = state.candidates[0]?.id || null;
} catch (error) {
  notice(`Could not load candidates. ${error.message} Serve this folder over HTTP and check candidates.json.`, true);
  $('empty-state').querySelector('h2').textContent = 'The diagram gallery could not be loaded.';
  $('empty-state').querySelector('p').textContent = 'Check the manifest and image paths, then reload this page.';
}
renderWorkspace(); renderGallery(); updateProgress();

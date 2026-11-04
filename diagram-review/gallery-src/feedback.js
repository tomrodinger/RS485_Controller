export const STORAGE_KEY = 'gearotons.wiring-review.feedback.v1';
export const SCHEMA_VERSION = 1;

export function emptyFeedback() {
  return { schemaVersion: SCHEMA_VERSION, feedback: Object.create(null) };
}

export function validateFeedback(input) {
  if (!input || input.schemaVersion !== SCHEMA_VERSION || !input.feedback ||
      typeof input.feedback !== 'object' || Array.isArray(input.feedback)) {
    throw new Error('Choose a feedback JSON export from this gallery (schema version 1).');
  }
  const result = emptyFeedback();
  const entries = Object.entries(input.feedback);
  if (entries.length > 10000) throw new Error('This file contains too many feedback records.');
  for (const [id, record] of entries) {
    if (!id || id.length > 300 || ['__proto__', 'prototype', 'constructor'].includes(id) ||
        !record || typeof record !== 'object' ||
        !Number.isInteger(record.rating) || record.rating < 0 || record.rating > 5 ||
        typeof record.comment !== 'string' || record.comment.length > 100000 ||
        typeof record.updatedAt !== 'string' || !Number.isFinite(Date.parse(record.updatedAt))) {
      throw new Error(`Invalid feedback record: ${id.slice(0, 80) || '(missing ID)'}. No records were imported.`);
    }
    result.feedback[id] = {
      rating: record.rating,
      comment: record.comment,
      updatedAt: new Date(record.updatedAt).toISOString(),
      revision: String(record.revision ?? '').slice(0, 300),
    };
  }
  return result;
}

// Keep the most recent record for each ID; preserve feedback for candidates absent
// from the current manifest so reviewers can move between gallery revisions.
export function mergeFeedback(current, incoming) {
  const result = emptyFeedback();
  let imported = 0;
  for (const [id, record] of Object.entries(current.feedback)) result.feedback[id] = { ...record };
  for (const [id, record] of Object.entries(incoming.feedback)) {
    if (!result.feedback[id] || Date.parse(record.updatedAt) > Date.parse(result.feedback[id].updatedAt)) {
      result.feedback[id] = { ...record };
      imported++;
    }
  }
  return { data: result, imported };
}

export function normalizeCandidates(input) {
  const entries = Array.isArray(input) ? input : input?.candidates;
  if (!Array.isArray(entries)) throw new Error('candidates.json must contain an array of candidates.');
  const ids = new Set();
  return entries.map((item, index) => {
    const id = typeof item?.id === 'string' ? item.id.trim() : '';
    if (!id || ids.has(id) || ['__proto__', 'prototype', 'constructor'].includes(id)) {
      throw new Error(`Candidate ${index + 1} needs a unique, nonempty ID.`);
    }
    ids.add(id);
    const safeAsset = value => {
      if (typeof value !== 'string' || !/^assets\/[\w./%() +@-]+$/u.test(value) ||
          value.split('/').some(part => part === '..') || /%2e|%2f|%5c/i.test(value)) {
        throw new Error(`Candidate ${id} must use a relative assets/ image path.`);
      }
      return value;
    };
    return {
      id, title: String(item.title || id), style: String(item.style || 'Wiring diagram'),
      description: String(item.description || ''), image: safeAsset(item.image),
      thumbnail: item.thumbnail ? safeAsset(item.thumbnail) : safeAsset(item.image),
      width: Number(item.width) || 0, height: Number(item.height) || 0,
      revision: String(item.revision || ''), reviewStatus: String(item.reviewStatus || 'Ready for review'),
    };
  });
}

export function filterCandidates(candidates, feedback, filter, query = '') {
  const search = query.trim().toLocaleLowerCase();
  return candidates.filter(candidate => {
    const record = feedback[candidate.id];
    const rating = record?.rating || 0;
    const reviewed = rating > 0 || Boolean(record?.comment.trim());
    const matchesRating = filter === 'all' ||
      (filter === 'unreviewed' && !reviewed) ||
      (filter === 'reviewed' && reviewed) ||
      (filter === 'favorites' && rating >= 4) ||
      (/^[1-5]$/.test(filter) && rating === Number(filter));
    return matchesRating && (!search ||
      `${candidate.title} ${candidate.style} ${candidate.description}`.toLocaleLowerCase().includes(search));
  });
}

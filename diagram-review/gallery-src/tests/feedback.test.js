import test from 'node:test';
import assert from 'node:assert/strict';
import { emptyFeedback, validateFeedback, mergeFeedback, normalizeCandidates, filterCandidates } from '../feedback.js';

const record = (rating, comment, updatedAt = '2026-10-26T08:00:00.000Z') => ({ rating, comment, updatedAt, revision: 'r1' });
const candidate = (id, overrides = {}) => ({ id, title: `Direction ${id}`, style: 'Technical', image: `assets/${id}.png`, ...overrides });

test('feedback exports round-trip Unicode comments and cleared ratings', () => {
  const source = emptyFeedback();
  source.feedback.a = record(5, 'Clear labels. 更清楚的连接。 <script>literal text</script>');
  source.feedback.b = record(0, 'Keep this note after clearing my rating.');
  const restored = validateFeedback(JSON.parse(JSON.stringify(source)));
  assert.deepEqual(restored.feedback.a, source.feedback.a);
  assert.deepEqual(restored.feedback.b, source.feedback.b);
  assert.equal(Object.getPrototypeOf(restored.feedback), null);
});

test('import rejects malformed records before returning a partial import', () => {
  const source = { schemaVersion: 1, feedback: { valid: record(4, 'Keep'), invalid: record(6, 'Invalid') } };
  assert.throws(() => validateFeedback(source), /Invalid feedback record: invalid/);
  for (const invalid of [record(1.5, ''), record(-1, ''), record(0, 42), record(3, '', 'not-a-date')]) {
    assert.throws(() => validateFeedback({ schemaVersion: 1, feedback: { a: invalid } }), /Invalid/);
  }
  assert.throws(() => validateFeedback({ schemaVersion: 2, feedback: {} }), /schema version 1/);
});

test('import rejects prototype-related keys', () => {
  const malicious = JSON.parse('{"schemaVersion":1,"feedback":{"__proto__":{"rating":5,"comment":"x","updatedAt":"2026-10-26"}}}');
  assert.throws(() => validateFeedback(malicious), /Invalid feedback record/);
  assert.equal({}.rating, undefined);
});

test('merging imports preserves newer local feedback and unknown candidate IDs', () => {
  const current = emptyFeedback();
  current.feedback.a = record(5, 'New local review', '2026-10-26T09:00:00Z');
  current.feedback.b = record(2, 'Earlier local review');
  const incoming = emptyFeedback();
  incoming.feedback.a = record(1, 'Stale review', '2026-10-25T08:00:00Z');
  incoming.feedback.b = record(4, 'New imported review', '2026-10-26T10:00:00Z');
  incoming.feedback.future = record(3, 'Candidate in a future gallery');
  const { data, imported } = mergeFeedback(current, incoming);
  assert.equal(imported, 2);
  assert.equal(data.feedback.a.comment, 'New local review');
  assert.equal(data.feedback.b.rating, 4);
  assert.equal(data.feedback.future.rating, 3);
  assert.equal(current.feedback.b.rating, 2, 'merge must not mutate existing feedback');
});

test('equal timestamps keep local record and import is idempotent', () => {
  const source = emptyFeedback(); source.feedback.a = record(4, 'Reviewed');
  const first = mergeFeedback(emptyFeedback(), source);
  assert.equal(first.imported, 1);
  assert.equal(mergeFeedback(first.data, source).imported, 0);
});

test('manifest validates IDs and keeps all assets relative to this gallery', () => {
  const values = normalizeCandidates({ candidates: [candidate('a', { thumbnail: 'assets/thumbs/a preview.png', width: 4000, height: 3000 })] });
  assert.equal(values[0].thumbnail, 'assets/thumbs/a preview.png');
  assert.equal(values[0].width, 4000);
  assert.throws(() => normalizeCandidates([candidate('a'), candidate('a')]), /unique/);
  for (const image of ['https://example.com/a.png', '/assets/a.png', 'assets/../secret.png', 'assets/%2e%2e/secret.png', 'assets/a.png?credential=abc', 'javascript:alert(1)']) {
    assert.throws(() => normalizeCandidates([candidate('a', { image })]), /relative assets/);
  }
});

test('rating filters treat meaningful comments as reviewed and combine with search', () => {
  const candidates = normalizeCandidates([candidate('a', { title: 'Minimal green' }), candidate('b'), candidate('c'), candidate('d')]);
  const feedback = { a: record(5, ''), b: record(0, 'Add the pin labels'), c: record(0, '   '), d: record(2, '') };
  const ids = (filter, query) => filterCandidates(candidates, feedback, filter, query).map(item => item.id);
  assert.deepEqual(ids('unreviewed'), ['c']);
  assert.deepEqual(ids('reviewed'), ['a', 'b', 'd']);
  assert.deepEqual(ids('favorites'), ['a']);
  assert.deepEqual(ids('2'), ['d']);
  assert.deepEqual(ids('all', ' GREEN '), ['a']);
  assert.deepEqual(ids('favorites', 'Direction'), []);
});

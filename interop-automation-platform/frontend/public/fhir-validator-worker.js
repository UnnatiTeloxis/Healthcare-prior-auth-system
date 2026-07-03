/* eslint-disable no-restricted-globals */
/**
 * Background worker for JSON parsing and lightweight FHIR resource type extraction.
 * Keeps the main UI thread responsive for large files.
 */
self.onmessage = function onMessage(event) {
  const { id, type, payload } = event.data || {};

  try {
    if (type === 'parseJson') {
      const parsed = JSON.parse(payload);
      self.postMessage({ id, ok: true, parsed });
      return;
    }

    if (type === 'resourceType') {
      const parsed = JSON.parse(payload);
      const resourceType = parsed && typeof parsed === 'object' ? parsed.resourceType || null : null;
      self.postMessage({ id, ok: true, resourceType });
      return;
    }

    self.postMessage({ id, ok: false, error: 'Unknown worker task' });
  } catch (error) {
    self.postMessage({ id, ok: false, error: error && error.message ? error.message : 'Parse failed' });
  }
};

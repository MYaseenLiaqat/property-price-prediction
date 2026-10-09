const API_BASE = window.ESTATEIQ_API_BASE
  || (window.location.hostname === '127.0.0.1' && window.location.port === '5500'
    ? 'http://127.0.0.1:8000'
    : '');
const $ = (id) => document.getElementById(id);
let selectedIntent = 'sell';

const formatPKR = (value) => new Intl.NumberFormat('en-PK', {
  style: 'currency', currency: 'PKR', maximumFractionDigits: 0,
}).format(value);

const formatCrore = (value) => `PKR ${(value / 10000000).toFixed(2)} Crore`;

function clearResult() {
  $('result-content').hidden = true;
  $('result-empty').hidden = false;
}

function clearSensitivity(
  message = 'The model will estimate values for nearby property sizes using the same selected inputs.',
  title = 'Calculate a valuation to see size sensitivity.',
) {
  const state = $('sensitivity-state');
  const chart = $('sensitivity-chart');
  chart.hidden = true;
  chart.replaceChildren();
  state.hidden = false;
  $('sensitivity-title').textContent = title;
  $('sensitivity-message').textContent = message;
}

function renderSensitivity(estimates) {
  const chart = $('sensitivity-chart');
  const maximum = Math.max(...estimates.map((item) => item.value));
  chart.replaceChildren(...estimates.map((item) => {
    const bar = document.createElement('div');
    bar.className = 'sensitivity-item';
    const value = document.createElement('strong');
    value.textContent = formatCrore(item.value);
    const fill = document.createElement('span');
    fill.className = 'sensitivity-bar';
    fill.style.height = `${Math.max(8, (item.value / maximum) * 100)}%`;
    fill.setAttribute('aria-hidden', 'true');
    const label = document.createElement('small');
    label.textContent = `${item.area.toLocaleString('en-PK')} sq ft`;
    bar.append(value, fill, label);
    return bar;
  }));
  $('sensitivity-state').hidden = true;
  chart.hidden = false;
}

async function loadSensitivity(request) {
  const state = $('sensitivity-state');
  const chart = $('sensitivity-chart');
  chart.hidden = true;
  chart.replaceChildren();
  state.hidden = false;
  $('sensitivity-title').textContent = 'Calculating size sensitivity…';
  $('sensitivity-message').textContent = 'Requesting model estimates for nearby property sizes.';
  const areas = [...new Set([0.75, 0.875, 1, 1.125, 1.25]
    .map((factor) => Math.min(100000, Math.max(101, Math.round(request.area_sqft * factor)))))]
    .sort((a, b) => a - b);
  const responses = await Promise.all(areas.map(async (area) => {
    const response = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...request, area_sqft: area }),
    });
    if (!response.ok) throw new Error('sensitivity');
    const result = await response.json();
    if (result.status === 'model_not_ready' || typeof result.estimated_price_pkr !== 'number') {
      throw new Error('sensitivity');
    }
    return { area, value: result.estimated_price_pkr };
  }));
  renderSensitivity(responses);
}

document.querySelectorAll('[data-intent]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-intent]').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    selectedIntent = button.dataset.intent;
    clearResult();
    clearSensitivity();
    const messages = {
      sell: 'Indicative asking-price estimate for a property you may sell.',
      buy: 'Reference estimate only; this is not a buyer-specific valuation.',
      rent: 'A Lahore rent model is not yet available.',
    };
    $('intent-message').textContent = messages[selectedIntent];
  });
});

async function loadMetadata() {
  try {
    const response = await fetch(`${API_BASE}/metadata`);
    if (!response.ok) throw new Error('metadata');
    const metadata = await response.json();
    if (metadata.status !== 'ok') throw new Error('metadata');
    $('dataset-year').textContent = String(metadata.dataset.date).slice(0, 4);
  } catch {
    // The form remains usable; the visible default is the documented source baseline.
  }
}

$('valuation-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const button = $('submit-button');
  const message = $('form-message');
  if (!$('valuation-form').reportValidity()) {
    clearResult();
    clearSensitivity('Please check the property details before requesting model estimates.');
    message.textContent = 'Please check the property details and try again.';
    return;
  }
  if (selectedIntent === 'rent') {
    clearSensitivity('A Lahore rent model is not yet available, so size sensitivity is unavailable.');
    message.textContent = 'A Lahore rent model is not yet available. No prediction was generated.';
    return;
  }
  button.disabled = true;
  button.textContent = 'Calculating…';
  message.textContent = 'Analyzing Lahore property data…';
  clearSensitivity('Requesting model estimates for nearby property sizes.');
  const request = {
    location: $('location').value.trim(),
    area_sqft: Number($('area_sqft').value),
    bedrooms: Number($('bedrooms').value),
    bathrooms: Number($('bathrooms').value),
  };
  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      if (response.status === 422) throw new Error('invalid');
      throw new Error(response.status === 503 ? 'model' : 'service');
    }
    const result = await response.json();
    if (result.status === 'model_not_ready') throw new Error('model');
    $('result-empty').hidden = true;
    $('result-content').hidden = false;
    $('result-title').textContent = `${request.location} · Lahore`;
    $('result-summary').textContent = `House · ${request.bedrooms} bedrooms · ${request.bathrooms} bathrooms · ${request.area_sqft.toLocaleString('en-PK')} sq ft`;
    $('estimate-crore').textContent = formatCrore(result.estimated_price_pkr);
    $('estimate-pkr').textContent = formatPKR(result.estimated_price_pkr);
    $('confidence').textContent = result.prediction_interval_status === 'not_calibrated' ? 'Limited' : 'See details';
    $('interval-note').textContent = result.prediction_interval_status === 'not_calibrated'
      ? 'Prediction range is not currently calibrated.'
      : 'Prediction interval status available in the result details.';
    message.textContent = selectedIntent === 'buy'
      ? 'Reference estimate ready. It is not a buyer-specific valuation.'
      : 'Property value calculated.';
    try {
      await loadSensitivity(request);
    } catch {
      clearSensitivity(
        'Size sensitivity is unavailable because one or more model estimates could not be retrieved.',
        'Size sensitivity unavailable.',
      );
    }
    $('result-content').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  } catch (error) {
    clearResult();
    clearSensitivity('Size sensitivity is unavailable until the valuation service responds.');
    message.textContent = error.message === 'model'
      ? 'Valuation model unavailable.'
      : error.message === 'invalid'
        ? 'Please check the property details and try again.'
      : 'Valuation service unavailable.';
  } finally {
    button.disabled = false;
    button.innerHTML = 'Calculate Property Value <span aria-hidden="true">→</span>';
  }
});

loadMetadata();

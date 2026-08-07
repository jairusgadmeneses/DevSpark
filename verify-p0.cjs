/**
 * P0 frontend verification:
 *  1. Parse index.html with jsdom and execute the inline script.
 *  2. Simulate form submission by calling renderCritiques with canonical response data.
 *  3. Verify optimized solution is NOT in DOM before reflection.
 *  4. Verify short/gibberish reflection does not enable reveal button.
 *  5. Verify valid reflection enables reveal and unlock injects optimized code.
 *  6. Verify Learning Report renders canonical backend values.
 */

const fs = require('fs');
const { JSDOM, VirtualConsole } = require('jsdom');

const html = fs.readFileSync('./index.html', 'utf8');

// Collect script errors during initial load.
let loadError = null;
const virtualConsole = new VirtualConsole();
virtualConsole.on('error', (err) => {
  loadError = err;
  console.error('JSDOM script error:', err.message || err);
});
virtualConsole.on('jsdomError', (err) => {
  loadError = err;
  console.error('JSDOM error:', err.message || err);
});

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  resources: 'usable',
  url: 'http://localhost:5173/',
  virtualConsole,
});

const { document, window } = dom.window;

// Expose minimal fetch so the inline script can be defined without throwing.
if (typeof window.fetch !== 'function') {
  window.fetch = () => Promise.reject(new Error('fetch not implemented in test'));
}

// Polyfill scrollIntoView which jsdom does not implement.
if (typeof window.Element.prototype.scrollIntoView !== 'function') {
  window.Element.prototype.scrollIntoView = function () {};
}

// Polyfill requestAnimationFrame.
if (typeof window.requestAnimationFrame !== 'function') {
  window.requestAnimationFrame = (cb) => setTimeout(cb, 0);
}

// Wait a tick for inline script to execute.
function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function runChecks() {
  await wait(100);

  if (loadError) {
    throw new Error('Inline script failed to load: ' + (loadError.message || loadError));
  }
  if (typeof window.renderCritiques !== 'function') {
    const globals = Object.keys(window).filter((k) => k.includes('render') || k.includes('Critique'));
    throw new Error('renderCritiques not available. Relevant globals: ' + globals.join(', '));
  }

  const codeEditor = document.getElementById('code-editor');
  codeEditor.value = 'x = 0';
  codeEditor.dispatchEvent(new window.Event('input'));

  // Simulate a backend response using the canonical schema.
  const mockResponse = {
    critiques: [
      {
        line: 1,
        severity: 'warning',
        explanation: 'The variable name is unclear.',
        why_it_matters: 'Naming affects maintainability.',
        suggested_improvement: 'Use a descriptive name.',
        engineering_principle: 'Readability',
      },
    ],
    learning_report: {
      code_quality_score: 82,
      strengths: ['Clear structure'],
      improvement_areas: ['Naming', 'Error handling'],
      engineering_concepts: ['Readability', 'Defensive Programming'],
      personalized_recommendation: 'Refactor variable names next.',
    },
    optimized_solution: '# Optimized code\nuser_count = 0\n',
  };

  // Trigger the same success path the app uses.
  window.renderCritiques(
    mockResponse.critiques,
    mockResponse.optimized_solution,
    mockResponse.learning_report
  );

  await wait(50);

  const optimizedCodeContent = document.getElementById('optimized-code-content');
  const reflection1 = document.getElementById('reflection-step1');
  const reflection2 = document.getElementById('reflection-step2');
  const revealBtn = document.getElementById('reveal-btn');

  // 1. Optimized solution must NOT be in DOM before reflection.
  const textBefore = optimizedCodeContent.textContent;
  if (textBefore.includes('user_count')) {
    throw new Error('FAIL: optimized solution leaked into DOM before reflection');
  }
  if (!textBefore.includes('Optimized solution is locked')) {
    throw new Error('FAIL: placeholder not shown in locked code block');
  }
  console.log('PASS: optimized solution is absent from DOM before reflection');

  // 2. Short reflection must keep button disabled.
  reflection1.value = 'too short';
  reflection2.value = 'also short';
  reflection1.dispatchEvent(new window.Event('input'));
  reflection2.dispatchEvent(new window.Event('input'));
  await wait(10);
  if (!revealBtn.disabled) {
    throw new Error('FAIL: reveal button enabled for short reflection');
  }
  console.log('PASS: short reflection does not unlock');

  // 3. Gibberish repeated-character reflection must keep button disabled.
  reflection1.value = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
  reflection2.value = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb';
  reflection1.dispatchEvent(new window.Event('input'));
  reflection2.dispatchEvent(new window.Event('input'));
  await wait(10);
  if (!revealBtn.disabled) {
    throw new Error('FAIL: reveal button enabled for gibberish reflection');
  }
  console.log('PASS: gibberish reflection does not unlock');

  // 4. Meaningful reflection must enable the button.
  reflection1.value =
    'The variable naming is the most impactful issue because unclear names make the code hard to understand and maintain.';
  reflection2.value =
    'I would rename variables to be descriptive and add error handling around edge cases before viewing the solution.';
  reflection1.dispatchEvent(new window.Event('input'));
  reflection2.dispatchEvent(new window.Event('input'));
  await wait(10);
  if (revealBtn.disabled) {
    throw new Error('FAIL: reveal button disabled for valid reflection');
  }
  console.log('PASS: valid reflection enables reveal button');

  // 5. Clicking reveal injects the optimized solution.
  revealBtn.dispatchEvent(new window.Event('click'));
  await wait(100);
  const textAfter = optimizedCodeContent.textContent;
  if (!textAfter.includes('user_count')) {
    throw new Error('FAIL: optimized solution was not injected after reveal');
  }
  console.log('PASS: optimized solution injected after reflection');

  // 6. Learning Report renders canonical values.
  const scoreValue = document.getElementById('report-score-value').textContent;
  if (scoreValue !== '82') {
    throw new Error('FAIL: expected score 82, got ' + scoreValue);
  }

  const improvementsList = document.getElementById('report-improvements');
  if (!improvementsList.textContent.includes('Naming') || !improvementsList.textContent.includes('Error handling')) {
    throw new Error('FAIL: improvement areas not rendered');
  }

  const conceptsContainer = document.getElementById('report-concepts');
  if (!conceptsContainer.textContent.includes('Readability') || !conceptsContainer.textContent.includes('Defensive Programming')) {
    throw new Error('FAIL: engineering concepts not rendered');
  }

  const nextConcept = document.getElementById('report-next-concept').textContent;
  if (!nextConcept.includes('Readability')) {
    throw new Error('FAIL: next concept from engineering_concepts not rendered');
  }

  console.log('PASS: learning report renders canonical backend values');

  // Verify fallback to personalized_recommendation when no concepts exist.
  // We call renderLearningReport directly because reflectionLearningReport is
  // a local script variable, not a window property.
  window.renderLearningReport({
    code_quality_score: 55,
    strengths: [],
    improvement_areas: ['Missing error handling'],
    engineering_concepts: [],
    personalized_recommendation: 'Study defensive programming patterns first.',
  });
  await wait(100);
  const recOnly = document.getElementById('report-next-concept').textContent;
  if (!recOnly.includes('Study defensive programming patterns first')) {
    throw new Error(
      'FAIL: personalized_recommendation fallback not rendered. Got: ' +
        recOnly.slice(0, 200)
    );
  }
  console.log('PASS: personalized_recommendation fallback renders');
  console.log('\nAll frontend P0 verification checks passed.');
}

runChecks().catch((err) => {
  console.error(err.message);
  process.exit(1);
});

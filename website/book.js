// Booking form: validates, optionally posts to a form service (data-endpoint),
// then shows a summary with a pre-filled WhatsApp message as a backup channel.
(function () {
  var WHATSAPP = '447504548304';
  var form = document.getElementById('booking');
  if (!form) return;

  // Pre-select "who" from ?who=… links on other pages.
  var match = /[?&]who=([a-z]+)/.exec(location.search);
  if (match) {
    var preset = document.getElementById('who-' + (match[1] === 'homeowner' ? 'home' : match[1]));
    if (preset) preset.checked = true;
  }

  var errorEl = document.getElementById('form-error');

  function value(id) { return (document.getElementById(id).value || '').trim(); }

  function collect() {
    var who = form.querySelector('input[name=who]:checked');
    var services = Array.prototype.map.call(form.querySelectorAll('input[name=service]:checked'), function (c) { return c.value; });
    return {
      who: who ? who.value : '',
      services: services.join(', ') || 'Not specified',
      frequency: value('frequency'),
      start: value('when'),
      postcode: value('postcode').toUpperCase(),
      size: value('size'),
      details: value('details'),
      name: value('name'),
      phone: value('phone'),
      email: value('email'),
      contact: value('contact'),
      heard: value('heard')
    };
  }

  function summaryText(d) {
    return [
      'New Bloom Gardens quote request',
      'Name: ' + d.name,
      'Phone: ' + d.phone + (d.email ? '\nEmail: ' + d.email : ''),
      'Booking for: ' + d.who,
      'Services: ' + d.services,
      'How often: ' + d.frequency + ' | Start: ' + d.start,
      'Postcode: ' + d.postcode + ' | Size: ' + d.size,
      d.details ? 'Details: ' + d.details : '',
      'Contact by: ' + d.contact + (d.heard ? ' | Heard via: ' + d.heard : '')
    ].filter(Boolean).join('\n');
  }

  function validate(d) {
    if (!d.name) return ['name', 'Please add your name so we know who to ask for.'];
    if (!/^[0-9+()\s-]{10,}$/.test(d.phone)) return ['phone', 'Please add a phone number we can reach you on.'];
    if (!/^[A-Z]{1,2}[0-9][A-Z0-9]?\s*[0-9][A-Z]{2}$/.test(d.postcode)) return ['postcode', 'Please add a full UK postcode, for example CM1 1AA.'];
    if (d.email && !/^\S+@\S+\.\S+$/.test(d.email)) return ['email', 'That email address doesn\'t look right. Leave it blank if you prefer.'];
    return null;
  }

  function showDone(d, sent) {
    var text = summaryText(d);
    document.getElementById('summary').textContent = text;
    document.getElementById('wa-send').href = 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(text);
    if (!sent) {
      document.getElementById('done-title').textContent = 'One last step: send it to us';
      document.getElementById('done-text').textContent = 'Tap the button to send your request on WhatsApp. Add a few photos of the garden and we can usually price it straight away.';
    }
    document.getElementById('form-body').hidden = true;
    var done = document.getElementById('form-done');
    done.hidden = false;
    done.focus();
    window.scrollTo({ top: form.getBoundingClientRect().top + window.pageYOffset - 90 });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = collect();
    var problem = validate(d);
    if (problem) {
      errorEl.textContent = problem[1];
      errorEl.hidden = false;
      document.getElementById(problem[0]).focus();
      return;
    }
    errorEl.hidden = true;

    var endpoint = form.getAttribute('data-endpoint');
    if (!endpoint) { showDone(d, false); return; }

    var btn = document.getElementById('submit');
    btn.disabled = true;
    btn.textContent = 'Sending…';
    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(Object.assign({ _subject: 'Quote request: ' + d.name + ', ' + d.postcode }, d))
    }).then(function (res) {
      if (!res.ok) throw new Error('status ' + res.status);
      showDone(d, true);
    }).catch(function () {
      // Never lose a lead: fall back to WhatsApp if the form service fails.
      showDone(d, false);
    });
  });
})();

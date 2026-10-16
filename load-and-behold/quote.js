// Quote form: validates, posts to Netlify Forms, then shows a summary with a
// pre-filled WhatsApp message (so photos can be added). If the post fails
// (e.g. viewing the page off Netlify), WhatsApp becomes the main way to send.
(function () {
  var WHATSAPP = '447504548304';
  var form = document.getElementById('quote-form');
  if (!form) return;
  var errorEl = document.getElementById('form-error');

  function value(id) { return (document.getElementById(id).value || '').trim(); }

  function collect() {
    var jobs = Array.prototype.map.call(form.querySelectorAll('input[name=job]:checked'), function (c) { return c.value; });
    return {
      job: jobs.join(', ') || 'Not specified',
      details: value('details'),
      from: value('from').toUpperCase(),
      to: value('to').toUpperCase(),
      when: value('when'),
      name: value('name'),
      phone: value('phone'),
      email: value('email')
    };
  }

  function summaryText(d) {
    return [
      'Load & Behold quote request',
      'Name: ' + d.name,
      'Phone: ' + d.phone + (d.email ? '\nEmail: ' + d.email : ''),
      'Job: ' + d.job,
      d.details ? 'Details: ' + d.details : '',
      'From: ' + (d.from || 'not given') + (d.to ? ' | To: ' + d.to : ''),
      'When: ' + d.when
    ].filter(Boolean).join('\n');
  }

  function validate(d) {
    if (!d.name) return ['name', 'Please add your name.'];
    if (!/^[0-9+()\s-]{10,}$/.test(d.phone)) return ['phone', 'Please add a phone number we can reach you on.'];
    if (d.email && !/^\S+@\S+\.\S+$/.test(d.email)) return ['email', 'That email doesn\'t look right. Leave it blank if you prefer.'];
    if (!d.details && d.job === 'Not specified') return ['details', 'Tell us a little about the job so we can price it.'];
    return null;
  }

  function showDone(d, sent) {
    var text = summaryText(d);
    document.getElementById('summary').textContent = text;
    document.getElementById('wa-send').href = 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(text);
    if (!sent) {
      document.getElementById('done-title').textContent = 'One last step: send it to us';
      document.getElementById('done-text').textContent = 'Tap the button to send your request on WhatsApp, and add a few photos so we can price it straight away.';
    }
    document.getElementById('form-body').hidden = true;
    var done = document.getElementById('form-done');
    done.hidden = false;
    done.focus();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = collect();
    var problem = validate(d);
    if (problem) {
      errorEl.textContent = problem[1];
      document.getElementById(problem[0]).focus();
      return;
    }
    errorEl.textContent = '';
    var body = new URLSearchParams(new FormData(form)).toString();
    fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body })
      .then(function (r) { showDone(d, r.ok); })
      .catch(function () { showDone(d, false); });
  });
})();

/* GeoIdentify : questionnaire pas à pas (amélioration facultative).
   Sans JavaScript, toutes les questions restent visibles et le formulaire fonctionne quand même. */
(function () {
    'use strict';

    var form = document.querySelector('[data-wizard]');
    if (!form) { return; }

    var steps = Array.prototype.slice.call(form.querySelectorAll('.step'));
    var segs = Array.prototype.slice.call(form.querySelectorAll('.seg'));
    var recap = form.querySelector('[data-recap]');
    var recapList = form.querySelector('[data-recap-list]');
    var back = form.querySelector('[data-back]');
    var label = form.querySelector('[data-progress-label]');
    var current = form.querySelector('[data-current]');
    var total = steps.length;
    var index = 0;
    var timer = null;

    function answered(i) {
        return !!steps[i].querySelector('input:checked');
    }

    function firstUnanswered() {
        for (var i = 0; i < total; i++) {
            if (!answered(i)) { return i; }
        }
        return total;
    }

    function buildRecap() {
        recapList.innerHTML = '';
        steps.forEach(function (step, i) {
            var checked = step.querySelector('input:checked');
            var li = document.createElement('li');

            var q = document.createElement('span');
            q.className = 'recap-q';
            q.textContent = step.querySelector('legend').textContent;

            var a = document.createElement('span');
            a.className = 'recap-a';
            var text = step.querySelector('input:checked + .opt .opt-label');
            a.textContent = text ? text.textContent : '';
            if (checked && checked.value === 'unknown') { a.className += ' is-skipped'; }

            var edit = document.createElement('button');
            edit.type = 'button';
            edit.className = 'recap-edit';
            edit.textContent = 'Modifier';
            edit.setAttribute('aria-label', 'Modifier : ' + q.textContent);
            edit.addEventListener('click', function () { show(i, true); });

            var left = document.createElement('div');
            left.appendChild(q);
            left.appendChild(document.createElement('br'));
            left.appendChild(a);
            li.appendChild(left);
            li.appendChild(edit);
            recapList.appendChild(li);
        });
    }

    function show(i, focus) {
        index = Math.max(0, Math.min(i, total));
        var reach = firstUnanswered();

        steps.forEach(function (step, n) { step.hidden = n !== index; });
        recap.hidden = index !== total;
        back.hidden = index === 0;
        label.hidden = index === total;
        if (index < total) { current.textContent = String(index + 1); }
        if (index === total) { buildRecap(); }

        segs.forEach(function (seg, n) {
            seg.classList.toggle('is-done', answered(n));
            seg.classList.toggle('is-current', n === index);
            seg.classList.toggle('is-reachable', n <= reach);
        });

        if (focus) {
            var target = index < total ? steps[index].querySelector('legend') : recap.querySelector('h2');
            if (target) {
                target.setAttribute('tabindex', '-1');
                target.focus({ preventScroll: false });
            }
        }
    }

    form.addEventListener('change', function (event) {
        if (!event.target.matches('.opt-input')) { return; }
        var stepIndex = steps.indexOf(event.target.closest('.step'));
        if (stepIndex !== index) { return; }
        window.clearTimeout(timer);
        var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        timer = window.setTimeout(function () { show(index + 1, true); }, reduced ? 0 : 220);
    });

    form.addEventListener('submit', function () {
        // An unanswered step is equivalent to the explicit "Je ne sais pas" option.
        steps.forEach(function (step) {
            if (!answered(steps.indexOf(step))) {
                var unknown = step.querySelector('input[value=\"unknown\"]');
                if (unknown) { unknown.checked = true; }
            }
        });
    });

    back.addEventListener('click', function () {
        window.clearTimeout(timer);
        show(index - 1, true);
    });

    segs.forEach(function (seg, n) {
        seg.addEventListener('click', function () {
            if (n <= firstUnanswered()) {
                window.clearTimeout(timer);
                show(n, true);
            }
        });
    });

    show(firstUnanswered(), false);
}());

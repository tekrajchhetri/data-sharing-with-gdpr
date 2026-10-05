// Guide pages: filter entries by keyword and highlight the current section in the contents.
(function () {
  var input = document.getElementById('guide-search');
  var sections = Array.prototype.slice.call(document.querySelectorAll('.g-section'));
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  var empty = document.getElementById('no-results');
  var count = document.getElementById('search-count');

  if (input) {
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      sections.forEach(function (section) {
        var titleMatch = section.querySelector('h2').textContent.toLowerCase().indexOf(q) !== -1;
        var visible = 0;
        section.querySelectorAll('.g-item').forEach(function (item) {
          var match = !q || titleMatch || item.textContent.toLowerCase().indexOf(q) !== -1;
          item.hidden = !match;
          if (match) visible++;
        });
        section.hidden = visible === 0;
        shown += visible;
        var link = document.querySelector('.toc a[href="#' + section.id + '"]');
        if (link) link.parentElement.hidden = section.hidden;
      });
      if (empty) empty.hidden = shown !== 0;
      if (count) count.textContent = q ? shown + (shown === 1 ? ' entry' : ' entries') + ' found' : '';
    });
  }

  if ('IntersectionObserver' in window && tocLinks.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        tocLinks.forEach(function (a) {
          a.classList.toggle('active', a.getAttribute('href') === '#' + entry.target.id);
        });
      });
    }, { rootMargin: '-20% 0px -70% 0px' });
    sections.forEach(function (s) { observer.observe(s); });
  }
})();

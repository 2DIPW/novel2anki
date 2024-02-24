var chunkElements = document.querySelectorAll('span[class*="chunk"]');
chunkElements.forEach(span => {
	console.log(span.textContent);
	span.addEventListener('click', () => {
		var word = span.textContent;
		var expElements = document.getElementsByClassName('exp');
		for (var i = 0; i < expElements.length; i++) {
			expElements[i].classList.remove('active');
		}
		var targetElement = document.getElementById(word);
		if (targetElement) {
			targetElement.classList.add('active');
		};
	});
});
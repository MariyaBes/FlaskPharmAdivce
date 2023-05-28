document.addEventListener('DOMContentLoaded', () => {
	const productsBtn = document.querySelectorAll('.product__btn');
	const cartProductsList = document.querySelector('.cart-content__list');
	const cart = document.querySelector('.cart');
	const cartQuantity = cart.querySelector('.count');
	const fullPrice = document.querySelector('.fullprice');
	let idProduct = document.getElementById(['data-id']);
	
	const count = document.querySelector('.items_current');
	let price = 0;

	const priceWithoutSpaces = (str) => {
		return str.replace(/\s/g, '');
	};

	const normalPrice = (str) => {
		return String(str).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
	};

	const plusFullPrice = (totalCount) => {
		return price += totalCount;
	};

	const totalPriceCount = (counter, currentPrice) => {
		totalCount = counter * currentPrice;
		return plusFullPrice (totalCount);
	}

	const minusFullPrice = (currentPrice) => {
		return price -= currentPrice;
	};

	const printFullPrice = () => {
		fullPrice.textContent = `${normalPrice(price)} ₽`;
	};

	productsBtn.forEach(el => {

		el.addEventListener('click', (e) => {
			let self = e.currentTarget;
			let parent = self.closest('.product');
			let id = parent.dataset.id;

			let img = parent.querySelector('.image-switch__img img').getAttribute('src');
			let title = parent.querySelector('.showcase-title').textContent;
			let counter = parent.querySelector('[data-counter]').textContent;

			let priceString = priceWithoutSpaces(parent.querySelector('.price-box .price').textContent);
			let priceNumber = parseInt(priceWithoutSpaces(parent.querySelector('.price-box .price').textContent));

			totalPriceCount(counter, priceNumber);
			printFullPrice();
			let fullPrice = totalPriceCount(counter, priceNumber)

			printQuantity();
			
			self.disabled = true;

			$.ajax({
				url: '/basket',
				method: 'post',
				dataType: 'json',
				data: {
					id: id,
					img: img,
					title: title,
					price: priceNumber,
					count: counter
				},
				success: function (response) {
					console.log(response);
				},
				error: function (error) {
					console.log(error);
				}
			});

		});
	});

	// Добавляем прослушку на всем окне
	window.addEventListener('click', function (event) {

		let counter;

		if (event.target.dataset.action === 'plus' || event.target.dataset.action === 'minus') {

			const counterWrapper = event.target.closest('.counter-wrapper');
			counter = counterWrapper.querySelector('[data-counter]');
		}

		if (event.target.dataset.action === 'plus') {
			if (counter.innerText < 10){
				counter.innerText = ++counter.innerText;
			}
		}

		if (event.target.dataset.action === 'minus') {

			if (parseInt(counter.innerText) > 1) {
				counter.innerText = --counter.innerText;
			} 
		}
	});
	
});



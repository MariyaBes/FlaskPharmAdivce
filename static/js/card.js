let ProductImg = document.getElementsByClassName('small-img');

let activeImages = document.getElementsByClassName('active');

for(var i=0; i < ProductImg.length; i++){

    ProductImg[i].addEventListener('click', function(){
        console.log(activeImages);

        if(activeImages.length > 0){
            activeImages[0].classList.remove('active')
        }

        this.classList.add('active');
        document.getElementById('ProductImg').src = this.src;
    })
}



document.addEventListener('DOMContentLoaded', () => {
	const productsBtn = document.querySelectorAll('.cart__btn');
	const cartProductsList = document.querySelector('.cart-content__list');
	const cart = document.querySelector('.cart');
	const cartQuantity = cart.querySelector('.count');
	const fullPrice = document.querySelector('.fullprice');
	let idProduct = document.getElementById(['data-id']);
	
	const count = document.querySelector('.items_current');
	let price = 0;
	let id_item = document.querySelector('.del_id_item').getAttribute('id');
	console.log(id_item);

	const priceWithoutSpaces = (str) => {
		return str.replace(/\s/g, '');
	};

	const normalPrice = (str) => {
		return String(str).replace(/(\d)(?=(\d\d\d)+([^\d]|$))/g, '$1 ');
	};

	productsBtn.forEach(el => {

		el.addEventListener('click', (e) => {
			let self = e.currentTarget;
			let parent = self.closest('.row-cart-product');
			let id = parent.dataset.id;
			console.log(id);

			let img = parent.querySelector('.img-container img').getAttribute('src');
			console.log(img);
			let title = parent.querySelector('.showcase-title').textContent;
			console.log(title);
			let counter = parent.querySelector('[data-counter]').textContent;
			console.log(counter);
			
			let priceString = priceWithoutSpaces(parent.querySelector('.Price_price__qHqZv').textContent);
			console.log(priceString);
			let priceNumber = parseInt(priceWithoutSpaces(parent.querySelector('.Price_price__qHqZv').textContent));
			console.log(priceNumber);

			totalPriceCount(counter, priceNumber);
			// plusFullPrice(priceNumber);
			printFullPrice();
			let fullPrice = totalPriceCount(counter, priceNumber)
			console.log(fullPrice);

			// cartProductsList.querySelector('.simplebar-content').insertAdjacentHTML('afterbegin', generateCartProduct(img, title, priceString, id, counter));
			printQuantity();

			// updateStorage();

			
			self.disabled = true;

			$.ajax({
				url: '/add_cart',
				method: 'post',
				dataType: 'json',
				data: {
					id_cart: id,
					img_cart: img,
					title_cart: title,
					price_cart: priceNumber,
					count_cart: counter
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

	// cartProductsList.addEventListener('click', (e) => {
	// 	if (e.target.classList.contains('cart-product__delete')) {
	// 		deleteProducts(e.target.closest('.cart-content__item'));
	// 	}
	// });


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


// set variable of update button to queryset of that button
var updateBtns = document.getElementsByClassName('update-cart')

for (i=0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'action:', action)
        // user
        console.log('USER:', user)
        // anonomus user
        if(user == 'AnonymousUser'){
            addCookieItem(productId, action)
        }
        else{
            updateUserOrder(productId, action)
        }
    })
}

function addCookieItem(productId, action){
    console.log("Not log in...")
    
    if (action == 'add'){
        if (cart[productId] == undefined){
            cart[productId] = {'quantity':1}
        }
        else{
            cart[productId]['quantity'] += 1
        }
    }

    if(action=='remove'){
        cart[productId]['quantity'] -= 1
        
        if (cart[productId]['quantity'] <= 0){
            console.log('remove item')
            delete cart[productId]
        }
    }
    console.log('Cart', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"
}

function updateUserOrder(productId, action){
    console.log('User is logged in, sending data..')

    var url = '/update_item/'
    // fetch fun(url, data(headers_obj))
    fetch(url, {
        method:'POST',
        headers: {
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productId':productId, 'action': action})
    })
    // sending json data to the backend
    .then((response) =>{
        return response.json()
    })
    // recieved data from the backend as a promise
    .then((data) =>{
        console.log('data:', data)
        location.reload()
    })
}
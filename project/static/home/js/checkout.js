document.addEventListener('DOMContentLoaded', function() {
    var payButton = document.querySelector('.paywithrazorpay');

    payButton.addEventListener('click', function(event) {
        event.preventDefault();

        var selects = document.querySelector("[name='addressId']").value;

        if (selects === "") {
            swal("Alert", "Address field is needed", "error");
            return false;
        } else {
            fetch('/proceed-to-pay')
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    var options = {
                        key: 'rzp_test_PgZCwShrc9JIsA',
                        amount: data.total * 100,
                        currency: 'INR',
                        name: 'He & She',
                        description: 'Thank you for Placing an order ',
                        image: 'admin/admin/img/looogoo.png',
                        handler: function(responseb) {
                            window.location.href = '/razorpay/' + selects;
                        },
                        prefill: {
                            name: '',
                            email: '',
                            contact: ''
                        },
                        notes: {
                            address: 'Razorpay Corporate Office'
                        },
                        theme: {
                            color: '#D19C97'
                        }
                    };

                    var rzp1 = new Razorpay(options);
                    rzp1.open();
                })
                .catch(function(error) {
                    console.error('Error:', error);
                });
        }
    });
});
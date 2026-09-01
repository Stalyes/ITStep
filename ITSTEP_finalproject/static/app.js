document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.classList.contains('no-loading')) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitButton.disabled = true;

                setTimeout(function () {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 8000);
            }
        });
    });

    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function (event) {
            const sourceCity = document.getElementById('from_city').value;
            const destinationCity = document.getElementById('to_city').value;

            if (sourceCity && sourceCity === destinationCity) {
                event.preventDefault();
                alert('საიდან და სად ერთი და იგივე ვერ იქნება!');
            }
        });
    }

    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        const cardNumberInput = document.getElementById('cardNumber');
        const cardNameInput = document.getElementById('cardName');
        const cardExpiryInput = document.getElementById('cardExpiry');

        const updateCardPreview = function () {
            const cardNumberValue = cardNumberInput ? (cardNumberInput.value || '**** **** **** ****') : '**** **** **** ****';
            const cardNameValue = cardNameInput ? (cardNameInput.value || 'თქვენი სახელი').toUpperCase() : 'თქვენი სახელი';
            const cardExpiryValue = cardExpiryInput ? (cardExpiryInput.value || 'MM/YY') : 'MM/YY';

            const cardNumberDisplay = document.getElementById('cardNumDisplay');
            const cardNameDisplay = document.getElementById('cardNameDisplay');
            const cardExpiryDisplay = document.getElementById('cardExpDisplay');

            if (cardNumberDisplay) cardNumberDisplay.textContent = cardNumberValue;
            if (cardNameDisplay) cardNameDisplay.textContent = cardNameValue;
            if (cardExpiryDisplay) cardExpiryDisplay.textContent = cardExpiryValue;
        };

        if (cardNumberInput) {
            cardNumberInput.addEventListener('input', function () {
                const digits = this.value.replace(/\s/g, '').replace(/\D/g, '').slice(0, 16);
                this.value = digits.replace(/(.{4})/g, '$1 ').trim();
                updateCardPreview();
            });
        }

        if (cardExpiryInput) {
            cardExpiryInput.addEventListener('input', function () {
                const digits = this.value.replace(/\D/g, '').slice(0, 4);
                this.value = digits.length > 2 ? digits.slice(0, 2) + '/' + digits.slice(2) : digits;
                updateCardPreview();
            });
        }

        if (cardNameInput) {
            cardNameInput.addEventListener('input', updateCardPreview);
        }
    }

    const passengersForm = document.getElementById('passengersForm');
    if (passengersForm) {
        const passengerCount = Number(passengersForm.dataset.passengerCount || 0);
        const trainData = passengersForm.dataset.train ? JSON.parse(passengersForm.dataset.train) : {};
        const selectedSeats = {};
        let currentPassengerIndex = 0;
        let selectedSeat = null;
        let selectedWagonName = null;

        const seatModal = document.getElementById('seatModal');
        const wagonSelect = document.getElementById('vagonSelect');
        const seatsGrid = document.getElementById('seatsGrid');
        const confirmSeatButton = document.getElementById('confirmSeatButton');

        document.querySelectorAll('[data-seat-index]').forEach(function (button) {
            button.addEventListener('click', function () {
                currentPassengerIndex = Number(this.dataset.seatIndex);
                selectedSeat = null;
                seatModal.style.display = 'flex';
                wagonSelect.value = '';
                seatsGrid.innerHTML = '<p class="seats-placeholder">აირჩიეთ ვაგონი</p>';
            });
        });

        document.querySelectorAll('[data-close-seat-modal]').forEach(function (button) {
            button.addEventListener('click', function () {
                seatModal.style.display = 'none';
            });
        });

        if (wagonSelect) {
            wagonSelect.addEventListener('change', loadSeats);
        }

        if (confirmSeatButton) {
            confirmSeatButton.addEventListener('click', function () {
                if (!selectedSeat) {
                    alert('გთხოვთ აირჩიოთ ადგილი!');
                    return;
                }

                const seatIdInput = document.getElementById('seat_id_' + currentPassengerIndex);
                const seatNumberInput = document.getElementById('seat_number_' + currentPassengerIndex);
                const wagonNameInput = document.getElementById('vagon_name_' + currentPassengerIndex);
                const seatPriceInput = document.getElementById('seat_price_' + currentPassengerIndex);
                const seatDisplay = document.getElementById('seat_num_display_' + currentPassengerIndex);

                seatIdInput.value = selectedSeat.seatId;
                seatNumberInput.value = selectedSeat.number;
                wagonNameInput.value = selectedWagonName;
                seatPriceInput.value = selectedSeat.price;
                seatDisplay.textContent = selectedSeat.number;

                selectedSeats[currentPassengerIndex] = selectedSeat.seatId;
                updateInvoice();
                seatModal.style.display = 'none';
            });
        }

        function loadSeats() {
            const selectedVagonId = wagonSelect.value;
            if (!selectedVagonId) {
                seatsGrid.innerHTML = '<p class="seats-placeholder">აირჩიეთ ვაგონი</p>';
                return;
            }

            selectedWagonName = wagonSelect.options[wagonSelect.selectedIndex].dataset.vagonName;

            let selectedWagon = null;
            if (trainData.vagons) {
                for (let index = 0; index < trainData.vagons.length; index += 1) {
                    if (String(trainData.vagons[index].id) === String(selectedVagonId)) {
                        selectedWagon = trainData.vagons[index];
                        break;
                    }
                }
            }

            if (selectedWagon && selectedWagon.seats) {
                drawSeats(selectedWagon.seats);
                return;
            }

            seatsGrid.innerHTML = '<p class="seats-placeholder">იტვირთება...</p>';
            fetch('/api/vagon/' + selectedVagonId)
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.seats) {
                        drawSeats(data.seats);
                    } else {
                        seatsGrid.innerHTML = '<p class="seats-placeholder">ადგილები ვერ მოიძებნა</p>';
                    }
                });
        }

        function drawSeats(seats) {
            seatsGrid.innerHTML = '';

            seats.forEach(function (seat) {
                const seatElement = document.createElement('div');
                seatElement.className = 'seat';
                seatElement.textContent = seat.number;
                seatElement.title = seat.number + ' - ' + seat.price + ' ₾';

                const seatTakenByAnotherPassenger = Object.keys(selectedSeats).some(function (passengerIndex) {
                    return Number(passengerIndex) !== currentPassengerIndex && selectedSeats[passengerIndex] === seat.seatId;
                });

                if (seat.isOccupied || seatTakenByAnotherPassenger) {
                    seatElement.classList.add('occupied');
                } else {
                    seatElement.classList.add('available');
                    seatElement.addEventListener('click', function () {
                        const previousSelection = seatsGrid.querySelector('.seat.selected');
                        if (previousSelection) {
                            previousSelection.classList.replace('selected', 'available');
                        }
                        seatElement.classList.replace('available', 'selected');
                        selectedSeat = seat;
                    });
                }

                seatsGrid.appendChild(seatElement);
            });
        }

        function updateInvoice() {
            const invoiceBody = document.getElementById('invoiceBody');
            if (!invoiceBody) return;

            invoiceBody.innerHTML = '';
            let total = 0;

            for (let index = 0; index < passengerCount; index += 1) {
                const seatNumber = document.getElementById('seat_number_' + index)?.value;
                const price = Number(document.getElementById('seat_price_' + index)?.value || 0);

                if (seatNumber) {
                    total += price;
                    const row = document.createElement('div');
                    row.className = 'invoice-body-row';
                    row.innerHTML = '<span>ადგილი ' + seatNumber + '</span><span>' + price.toFixed(2) + '₾</span>';
                    invoiceBody.appendChild(row);
                }
            }

            const totalLabel = document.getElementById('invoiceTotal');
            if (totalLabel) {
                totalLabel.textContent = total.toFixed(2);
            }
        }

        passengersForm.addEventListener('submit', function (event) {
            for (let index = 0; index < passengerCount; index += 1) {
                const seatIdInput = document.getElementById('seat_id_' + index);
                if (!seatIdInput || !seatIdInput.value) {
                    event.preventDefault();
                    alert('გთხოვთ აირჩიოთ ადგილი მგზავრი ' + (index + 1) + '-სთვის');
                    return;
                }
            }
        });

        const submitBookingButton = document.querySelector('[data-submit-booking]');
        if (submitBookingButton) {
            submitBookingButton.addEventListener('click', function () {
                const agreement = document.getElementById('agreeTerms');
                for (let index = 0; index < passengerCount; index += 1) {
                    const seatIdInput = document.getElementById('seat_id_' + index);
                    if (!seatIdInput || !seatIdInput.value) {
                        alert('გთხოვთ აირჩიოთ ადგილი მგზავრი ' + (index + 1) + '-სთვის');
                        return;
                    }
                }

                if (!agreement || !agreement.checked) {
                    alert('გთხოვთ დაეთანხმოთ წესებს');
                    return;
                }

                if (passengersForm.checkValidity()) {
                    passengersForm.submit();
                } else {
                    passengersForm.reportValidity();
                }
            });
        }
    }

    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const targetSelector = this.getAttribute('href');
            const target = document.querySelector(targetSelector);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

function formatPhone(input) {
    const digits = input.value.replace(/\D/g, '');
    if (digits.length > 3 && digits.length <= 6) {
        input.value = digits.slice(0, 3) + ' ' + digits.slice(3);
    } else if (digits.length > 6) {
        input.value = digits.slice(0, 3) + ' ' + digits.slice(3, 6) + ' ' + digits.slice(6, 9);
    }
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = 'notification ' + (type || 'info');
    notification.textContent = message;
    notification.style.cssText = 'position:fixed;top:80px;right:20px;padding:15px 25px;border-radius:8px;z-index:9999;font-weight:600;animation:slideIn 0.3s ease;';

    if (type === 'error') {
        notification.style.background = '#f8d7da';
        notification.style.color = '#721c24';
    } else if (type === 'success') {
        notification.style.background = '#d4edda';
        notification.style.color = '#155724';
    } else {
        notification.style.background = '#cce5ff';
        notification.style.color = '#004085';
    }

    document.body.appendChild(notification);

    setTimeout(function () {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(function () {
            notification.remove();
        }, 300);
    }, 3000);
}
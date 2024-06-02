function search() {
    queryElement = document.getElementById('query');
    locationElement = document.getElementById('location');

    if (queryElement.value === '' || locationElement.value === '') {
        alert('Fill both fields');
        return;
    }

    loadingElement = document.getElementById('loading');
    loadingElement.style.display = '';
}

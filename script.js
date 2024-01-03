let candleCount = 0;

function addCandle() {
    const candles = document.getElementById('candles');
    const candle = document.createElement('div');
    candle.className = 'candle';
    candles.appendChild(candle);
    candleCount++;
}

document.querySelector('.birthday-cake').addEventListener('click', function () {
    addCandle();
});

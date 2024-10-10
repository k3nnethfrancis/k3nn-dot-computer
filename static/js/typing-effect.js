document.addEventListener('DOMContentLoaded', (event) => {
    const texts = ["technologist", "researcher", "developer", "entrepreneur"];
    const interests = ["ai", "memetics", "desci"];
    let textIndex = 0;
    let interestIndex = 0;

    function typeText(element, text, index, callback) {
        if (index < text.length) {
            element.innerHTML += text.charAt(index);
            setTimeout(() => typeText(element, text, index + 1, callback), 100);
        } else {
            setTimeout(callback, 1000);
        }
    }

    function eraseText(element, callback) {
        const text = element.innerHTML;
        if (text.length > 0) {
            element.innerHTML = text.substring(0, text.length - 1);
            setTimeout(() => eraseText(element, callback), 50);
        } else {
            callback();
        }
    }

    function changeText() {
        const element = document.getElementById('dynamic-text');
        eraseText(element, () => {
            textIndex = (textIndex + 1) % texts.length;
            typeText(element, texts[textIndex], 0, changeText);
        });
    }

    function changeInterest() {
        const element = document.getElementById('dynamic-interest');
        eraseText(element, () => {
            interestIndex = (interestIndex + 1) % interests.length;
            typeText(element, interests[interestIndex], 0, changeInterest);
        });
    }

    changeText();
    changeInterest();
});
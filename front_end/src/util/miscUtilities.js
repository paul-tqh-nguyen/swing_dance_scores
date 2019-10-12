export function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(window.location.search);
    let urlParameter = results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    return urlParameter;
};

/*
var assert = require('assert');

export function isEven(integerValue) {
    return (integerValue%2)===0;
}

export function isOdd(integerValue) {
    return (integerValue%2)===0;
}

export function randomChoice(inputArray) {
    return inputArray[randomInteger(inputArray.length)];
}

export function getRandomColor() {
    const letters = '0123456789ABCDEF';
    var color = '#';
    for(var i = 0; i < 6; i++) {
        color += randomChoice(letters);
    }
    return color;
}

export function rgbToHex (rgb) { 
  let hex = Number(rgb).toString(16);
  if (hex.length < 2) {
       hex = "0" + hex;
  }
  return hex;
};

export function sumOfSquaresDistance(inputArrayA,inputArrayB) {
    assert(inputArrayA.length === inputArrayB.length);
    let distance = 0;
    for(var dimensionIndex = 0; dimensionIndex<inputArrayB.length; dimensionIndex++) {
        distance += inputArrayA[dimensionIndex]*inputArrayA[dimensionIndex] + inputArrayB[dimensionIndex]*inputArrayB[dimensionIndex];
    }
    return distance;
}

export function randomInteger(integerInput) {
    return Math.floor(Math.random() * integerInput);
}

function capitalizeWords(string) {
    var words = string.toLowerCase().split(' ');
    words.forEach((word, wordIndex) => words[wordIndex] = word.charAt(0).toUpperCase() + word.substring(1));
    let conjoinedWords = words.join(' ');
    return conjoinedWords;
}

*/

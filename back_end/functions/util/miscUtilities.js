
const implies = (a,b) => ((!a) || b);

function isString(x) {
    return Object.prototype.toString.call(x) === "[object String]";
}

const isEmptyString = (string) => {
    return (isString(string) && (string.trim() === ""));
};

const emailRegEx = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

const isEmail = (string) => { // @todo use some library function
    return (string.match(emailRegEx));
};

const noOp = () => {};

module.exports = { implies, isString, isEmptyString, isEmail, noOp };

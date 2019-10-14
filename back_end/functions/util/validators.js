
const isEmptyString = (string) => { // @todo move to utilities or helper file
    return (string.trim() === "");
};

const emailRegEx = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

const isEmail = (string) => { // @todo use some library function
    return (string.match(emailRegEx));
};

const signupValidationErrors = (newUser) => {
    let errors = {}; // @todo abstract this out to a helper
    // @todo add a test for this validation
    if (isEmptyString(newUser.email)) {
        errors.email = "Email must not be empty.";
    } else if (!isEmail(newUser.email)){
        errors.email = `${newUser.email} is not a well formatted email address.`;
    }
    if (isEmptyString(newUser.password)) {
        errors.password = "Password must not be empty.";
    } else if (newUser.password !== newUser.confirmPassword) {
        errors.password = "Password does not match confirmed password.";
    }
    if (isEmptyString(newUser.handle)) {
        errors.handle = "Handle must not be empty.";
    }
    return errors;
};

const loginValidationErrors = (user) => {
    let errors = {}; // @todo abstract this out to a helper
    // @todo add a test for this validation
    if (isEmptyString(user.email)) {
        errors.email = "Email must not be empty.";
    } else if (!isEmail(user.email)){
        errors.email = `${user.email} is not a well formatted email address.`;
    }
    if (isEmptyString(user.password)) {
        errors.password = "Password must not be empty.";
    } 
    return errors;
};

const updateUserDataValidationErrors = (updateUserDataRequestBody) => {
    let errors = {};
    // @todo add a test for this validation
    let newEmail = updateUserDataRequestBody.newEmail;
    let password = updateUserDataRequestBody.password;
    if (newEmail) {
        if (!password) {
            errors.newEmail = "Cannot update email without authentication via password.";
        } else if (isEmptyString(password)) {
            errors.password = "Password must not be empty.";
        }
    }
    return errors;
};

const reduceUserDetails = (data) => { // @todo do we need this?
    let userDetails = {};
    if (!isEmptyString(data.organizationName.trim())) {
        userDetails.organizationName = data.organizationName;
    }
    // @todo add more cases
    return userDetails;
};

module.exports = { signupValidationErrors, loginValidationErrors, reduceUserDetails, updateUserDataValidationErrors };

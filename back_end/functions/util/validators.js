
const { db } = require("../util/admin");

const implies = (a,b) => ((!a) || b);

function isString(x) { // @todo move to utilities or helper file
    return Object.prototype.toString.call(x) === "[object String]";
}

const isEmptyString = (string) => { // @todo move to utilities or helper file
    return (isString(string) && (string.trim() === ""));
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

const createCompetitionValidationComplaintsWRTCompetitorInfo = (competitorInfo, judges, judgesInfoIsValid) => {
    let competitorInfoComplaints = [];
    if (!Array.isArray(competitorInfo)) {
        competitorInfoComplaints.push('competitorInfo must be specificed as a list of JSON objects with the form {"name": <string> , "competitorNumber": <integer>, "scores": [{"judge": <string>, "judgeScore": <integer>}, ...]}');
    } else {
        competitorInfo.forEach(competitorInfoDatum => {
            if (!competitorInfoDatum.name) {
                competitorInfoComplaints.push(`${JSON.stringify(competitorInfoDatum)} is missing name information.`);
            }
            if (!competitorInfoDatum.competitorNumber) {
                competitorInfoComplaints.push(`${JSON.stringify(competitorInfoDatum)} is missing competitor number information.`);
            } else if (!Number.isInteger(competitorInfoDatum.competitorNumber)) {
                competitorInfoComplaints.push(`${JSON.stringify(competitorInfoDatum)} is does not specify the competitor number as an integer.`);
            }
            if (!competitorInfoDatum.scores) {
                competitorInfoComplaints.push(`${JSON.stringify(competitorInfoDatum)} is missing score information.`);
            } else {
                competitorInfoDatum.scores.forEach((score) => {
                    if (!score.judge) {
                        competitorInfoComplaints.push(`${JSON.stringify(score)} does not specify a judge.`);
                    } else {
                        if (judgesInfoIsValid && !judges.includes(score.judge)) {
                            competitorInfoComplaints.push(`${JSON.stringify(score)} does not specify a judge from the specified list of judges.`);
                        }
                    }
                    if (!Number.isInteger(score.judgeScore)) {
                        competitorInfoComplaints.push(`${JSON.stringify(score)} does not specify a judge score.`);
                    }
                });
            }
        });
    }
    return competitorInfoComplaints;
};

const createCompetitionValidationComplaintsWRTUsersWithModificationPrivileges = (usersWithModificationPrivileges) => {
    let usersWithModificationPrivilegesComplaints = [];
    if (!Array.isArray(usersWithModificationPrivileges)) {
        usersWithModificationPrivilegesComplaints.push('User with privileges to modify this competition must come in the form of a list of handles.');
    } else {
        if (usersWithModificationPrivileges.length === 0) {
            usersWithModificationPrivilegesComplaints.push('No users are specified to be allowed to modify this competition.');
        } else {
            usersWithModificationPrivileges.forEach(userHandle => {
                if (!isString(userHandle)) {
                    usersWithModificationPrivilegesComplaints.push(`${userHandle} must be a string corresponding to a user's handle.`);
                } else {
                    db.doc(`/users/${userHandle}`).get()
                        .then(doc => {
                            if (!doc.exists) {
                                usersWithModificationPrivilegesComplaints.push(`${userHandle} does not correspond to an existing user.`);
                            }
                            return null;
                        })
                        .catch(err => {
                            console.log(err.code);
                            usersWithModificationPrivilegesComplaints.push(`${userHandle} could not be validated as an existing user handle.`);
                            return null;
                        });
                }
            });
        }
    }
    return usersWithModificationPrivilegesComplaints;
};

const competitionDataValidationErrors = (postBody, allFieldsAreRequired) => {
    let errors = {};
    let { name, category, judges, competitorInfo, usersWithModificationPrivileges, privacy } = postBody;
    if (allFieldsAreRequired || name) {
        if (isString(name)) {
            errors.name = `name must be specified as a string.`;
        }
    }
    if (allFieldsAreRequired || category) {
        if (! (category==='prelims' || category==='finals')) {
            errors.category = `category not specified as 'prelims' or 'finals'`;
        }
    }
    let judgesInfoIsValid;
    if (allFieldsAreRequired || judges) {
        let errorsWRTJudges = [];
        if (!judges) {
            errorsWRTJudges.push(`No judges specified`);
        } else {
            judges.forEach(judge => {
                if (!isString(judge)) {
                    errorsWRTJudges.push(`${judge} is not a string and cannot be stored as the name of a judge.`);
                }
            });
            let uniqueJudges = Array.from(new Set(judges));
            if (uniqueJudges.length !== judges.length) {
                errorsWRTJudges.push(`${judges} contains duplicates.`);
            }
        }
        if (errorsWRTJudges.length > 0) {
            errors.judges = errorsWRTJudges;
        }
        judgesInfoIsValid = errorsWRTJudges.length === 0;
    }
    if (allFieldsAreRequired || (judges && competitorInfo)) { // @todo validate that this invariant holds at the end of edits where we only change either of judges or competitorInfo
        let competitorInfoComplaints = createCompetitionValidationComplaintsWRTCompetitorInfo(competitorInfo, judges, judgesInfoIsValid);
        if (competitorInfoComplaints.length > 0) {
            errors.competitorInfo = competitorInfoComplaints;
        }
    }
    if (allFieldsAreRequired || usersWithModificationPrivileges) {
        let usersWithModificationPrivilegesComplaints = createCompetitionValidationComplaintsWRTUsersWithModificationPrivileges(usersWithModificationPrivileges);
        if (usersWithModificationPrivilegesComplaints.length > 0) {
            errors.usersWithModificationPrivileges = usersWithModificationPrivilegesComplaints;
        }
    }
    if (allFieldsAreRequired || privacy) {
        if (! (privacy==='private' || privacy==='public')) {
            errors.privacy = `privacy not specified as 'private' or 'public'`;
        }
    }
    return errors;
};

const allCompetitionInfoKeysModifiableByUser = [ "lastModifiedAt", "competitionName", "category", "judges", "competitorInfo", "usersWithModificationPrivileges", "privacy"];

const createCompetitionValidationErrors = (postBody) => { // @todo add a test for this validation ; also try invalid irrelevant keys
    let errors = competitionDataValidationErrors(postBody, true);
    return errors;
};

const editCompetitionValidationErrors = (competitionId, newCompetitionInfo) => { // @todo add a test for this validation
    let errors = {};
    if (!competitionId) {
        errors.competitionId = "No competition ID specified.";
    }
    let newCompetitionInfoErrors = competitionDataValidationErrors(newCompetitionInfo, false);
    errors = Object.assign({}, errors, newCompetitionInfoErrors);
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

module.exports = { signupValidationErrors, loginValidationErrors, reduceUserDetails, updateUserDataValidationErrors, createCompetitionValidationErrors, editCompetitionValidationErrors, allCompetitionInfoKeysModifiableByUser};

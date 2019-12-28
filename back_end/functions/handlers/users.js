
const { firebaseConfig } = require('../util/config.js');
const firebase = require('firebase');
const { db, admin } = require("../util/admin");
const { signupValidationErrors, loginValidationErrors, dwimUserDetails } = require("../util/validators");
const { isEmptyString, isEmail } = require("../util/miscUtilities");

const noImageFileName = "no_image.png";

exports.signup = (request, response) => {
    const newUser = {
        email: request.body.email,
        password: request.body.password,
        confirmPassword: request.body.confirmPassword,
        handle: request.body.handle,
    };
    let errors = signupValidationErrors(newUser);
    if (Object.keys(errors).length>0) {
        return response.status(400).json(errors);
    }
    let userId, token;
    let refreshToken;
    db.doc(`/users/${newUser.handle}`).get()
        .then(doc => {
            if (doc.exists) {
                let error = new Error(`The handle ${newUser.handle} is already taken.`);
                throw error;
            } else {
                return firebase.auth().createUserWithEmailAndPassword(newUser.email, newUser.password);
            }
        })
        .then(data => {
            userId = data.user.uid;
            refreshToken = data.user.refreshToken;
            return data.user.getIdToken();
        })
        .then(retrievedToken => {
            token = retrievedToken;
            const userCredentials = {
                handle: newUser.handle,
                email: newUser.email,
                createdAt: new Date().toISOString(),
                userId: userId,
                imageUrl: `https://firebasestorage.googleapis.com/v0/b/${firebaseConfig.storageBucket}/o/${noImageFileName}?alt=media`,
                modifiableCompetitionIds: [],
            };
            return db.doc(`/users/${newUser.handle}`).set(userCredentials);
        })
        .then(() => {
            return response.status(201).json({token: token, refreshToken: refreshToken});
        })
        .catch(err => {
            console.error(err);
            if (err.message) {
                return response.status(400).json({error: err.message});
            } else if (err.code === "auth/email-already-in-use") {
                return response.status(400).json({error: `The email address ${newUser.email} is already in use.`});
            } else {
                return response.status(500).json({error: err.code});
            }
        });
    return null;
};

const lastArrayElement = (array) => { // @todo move to helper file
    return array[array.length-1];
};

exports.login = (request, response) => {
    const user = {
        email: request.body.email,
        password: request.body.password,
    };
    let errors = loginValidationErrors(user);
    if (Object.keys(errors).length>0) {
        return response.status(400).json(errors);
    }
    let refreshToken;
    firebase.auth().signInWithEmailAndPassword(user.email, user.password)
        .then(data => {
            refreshToken = data.user.refreshToken;
            return data.user.getIdToken();
        })
        .then(token => {
            return response.json({token: token, refreshToken: refreshToken});
        })
        .catch(err => {
            console.error(err);
            if (err.code === "auth/wrong-password") {
                return response.status(403).json({ general: "Wrong credentials, please try again."});
            }
            return response.status(500).json({error: err.code});
        });
    return null;
};

exports.uploadImage = (request, response) => {
    const BusBoy = require('busboy');
    const path = require('path');
    const os = require('os');
    const fs = require('fs');
    const busboy = new BusBoy({ headers: request.headers });
    let imageFileName;
    let imageToBeUploaded = {};
    busboy.on('file', (fieldname, file, filename, encoding, mimetype) => {
        const imageExtension = lastArrayElement(filename.split('.'));
        if (mimetype !== 'image/jpeg') {
            return response.status(400).json({ error: 'Only JPEG images can be uploaded.' });
        }
        imageFileName = `${Date.now()}_${Math.floor(Math.random()*100000000000000)}.${imageExtension}`;
        const filepath = path.join(os.tmpdir(), imageFileName);
        imageToBeUploaded = {
            filepath: filepath,
            mimetype: mimetype,
        };
        file.pipe(fs.createWriteStream(filepath));
        return null;
    });
    busboy.on('finish', () => {
        admin.storage().bucket().upload(imageToBeUploaded.filepath, {
            resumable: false,
            metadata: {
                metadata: {
                    contentType: imageToBeUploaded.mimetype, 
                },
            },
        })
            .then(() => {
                const imageUrl = `https://firebasestorage.googleapis.com/v0/b/${firebaseConfig.storageBucket}/o/${imageFileName}?alt=media`;
                db.doc(`/users/${request.user.handle}`).update({ imageUrl: imageUrl});
                return imageUrl;
            })
            .then((imageUrl) => {
                return response.json({ message: "Image uploaded successfully.", imageUrl: imageUrl});
            })
            .catch((error) => {
                console.error(error);
                return response.status(500).json({error: error.code});
            });
    });
    busboy.end(request.rawBody);
};

exports.addUserDetails = (request, response) => {
    let [userDetails, complaintString] = dwimUserDetails(request.body);
    if (complaintString.length !== 0) {
        return response.status(500).json({ error: complaintString });
    } else {
        db.doc(`/users/${request.user.handle}`).update(userDetails)
            .then(() => { // @todo is this status code right? should we use a put or update instead of a post for this?
                return response.status(200).json({message: "Details added successfully."});
            })
            .catch(err => {
                console.error(err);
                return response.status(500).json({ error: err.code });
            });
    }
    return null;
};

exports.updateUserDetails = (request, response) => {
    // @todo abstract out the chunks below
    let [ userDetails, complaintString ] = dwimUserDetails(request.body);
    if (complaintString.length !== 0) {
        return response.status(500).json({ error: complaintString });
    }
    let handle = request.user.handle;
    let dbUpdatePromises = [];
    let newEmail = userDetails.newEmail;
    let password = userDetails.password;
    if (newEmail && password) {
        let oldEmail, docId;
        dbUpdatePromises.push(
            db.doc(`/users/${handle}`).get()
                .then(doc => {
                    if (!doc.exists) {
                        let error = new Error(`${handle} is not a valid handle.`);
                        throw error;
                    }
                    docId = doc.id;
                    let docData = doc.data();
                    oldEmail = docData.email;
                    return firebase.auth().signInWithEmailAndPassword(oldEmail, password);
                })
                .then(() => {
                    return firebase.auth().currentUser.updateEmail(newEmail);
                })
                .then(() => {
                    return db.collection("users").doc(docId).update({
                        email: newEmail,
                    });
                })
                .catch(err => {
                    console.error(err);
                    return response.status(500).json({
                        error: (err.message ? err.message : err.code)
                    });
                }));
    }
    if (userDetails.organizationName) { // @todo turn this into a loop over updatable fields ; write a test as well
        let docId;
        dbUpdatePromises.push(
            db.doc(`/users/${handle}`).get()
                .then(doc => {
                    if (!doc.exists) {
                        let error = new Error(`${handle} is not a valid handle.`);
                        throw error;
                    }
                    docId = doc.id;
                    return db.collection("users").doc(docId).update({
                        organizationName: userDetails.organizationName,
                    });
                })
                .catch(err => {
                    console.error(err);
                    return response.status(500).json({
                        error: (err.message ? err.message : err.code)
                    });
                }));
    }
    Promise.all(dbUpdatePromises)
        .then(() => {
            return response.status(200).json({message: "Update completed successfully."});
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({
                error: (err.message ? err.message : err.code)
            });
        });
    return null;
};

exports.getUserDetails = (request, response) => {
    db.doc(`/users/${request.user.handle}`)
        .get()
        .then(doc => {
            if (!doc.exists) {
                let error = new Error(`${request.user.handle} is not a valid handle.`);
                throw error;
            }
            let userData = doc.data();
            return response.status(200).json(userData);
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({
                error: (err.message ? err.message : err.code)
            });
        });
};

exports.deleteUser = (request, response) => {
    const user = {
        email: request.body.email,
        password: request.body.password,
    };
    let errors = loginValidationErrors(user);
    if (Object.keys(errors).length>0) {
        return response.status(400).json(errors);
    }
    firebase.auth().signInWithEmailAndPassword(user.email, user.password)
        .then(data => {
            let currentUser = firebase.auth().currentUser;
            return currentUser.delete();
        })
        .then(() => {
            // @todo is this status code right? should we use a put or update instead of a post for this?
            return response.status(200).json({message: "User deleted successfully."});
        })
        .catch(err => {
            console.error(err);
            if (err.code === "auth/wrong-password") {
                return response.status(403).json({ general: "Wrong credentials; cannot delete user."});
            }
            return response.status(500).json({error: err.code});
        });
    return null;
};
